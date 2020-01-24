import argparse
import datetime
import pendulum

from collections import defaultdict
from logzero import logger
from typing import Dict, List, Optional

from .. import api, batch, constants, errors, reporting, oliver, workflows as _workflows


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"],
    )

    workflows = _workflows.get_workflows(
        cromwell=cromwell,
        submission_time_hours_ago=args["submission_time"],
        oliver_job_name=args["oliver_job_name"],
        oliver_job_group_name=args["oliver_job_group_name"],
        cromwell_workflow_uuid=args["cromwell_workflow_uuid"],
        cromwell_workflow_name=args["cromwell_workflow_name"],
        batch_number_ago=args["batch_number_ago"],
        batch_interval_mins=args["batch_interval_mins"],
        opt_into_reporting_aborted_jobs=args["show_aborted_jobs"],
        opt_into_reporting_failed_jobs=args["show_failed_jobs"],
        opt_into_reporting_running_jobs=args["show_running_jobs"],
        opt_into_reporting_succeeded_jobs=args["show_succeeded_jobs"],
    )

    metadatas = {w["id"]: cromwell.get_workflows_metadata(w["id"]) for w in workflows}
    print_workflow_summary(workflows, metadatas, grid_style=args["grid_style"])

    if args.get("steps_view"):
        print()
        print_workflow_steps_view(
            workflows, metadatas, grid_style=args.get("grid_style")
        )

    if args.get("detail_view"):
        print()
        print_workflow_detail_view(
            workflows,
            metadatas,
            show_job_name=args.get("show_job_name"),
            show_job_group=args.get("show_job_group"),
            grid_style=args["grid_style"],
        )


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "status",
        aliases=["st"],
        help="Report various statistics about a running Cromwell server.",
    )
    subcommand.add_argument(
        "-a",
        "--aborted",
        dest="show_aborted_jobs",
        help="Show jobs in the 'Aborted' state.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-b",
        "--batch-number-ago",
        help="(experimental) Show outputs from N batches ago.",
        default=None,
        type=int,
    )
    subcommand.add_argument(
        "--batch-interval-mins",
        help="(experimental) Split batches by any two jobs separated by N minutes.",
        default=5,
        type=int,
    )
    subcommand.add_argument(
        "-d",
        "--detail-view",
        help="Show detailed view.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-f",
        "--failed",
        dest="show_failed_jobs",
        help="Show jobs in the 'Failed' state.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-g",
        "--oliver-job-group-name",
        help="Job group name assigned by user and attached to the job.",
        type=str,
        default=None,
    )
    subcommand.add_argument(
        "-i",
        "--cromwell-workflow-uuid",
        type=str,
        help="Filter by workflow id matching argument.",
    )
    subcommand.add_argument(
        "-j",
        "--oliver-job-name",
        help="Job name assigned by user and attached to the job.",
        type=str,
        default=None,
    )
    subcommand.add_argument(
        "-n",
        "--cromwell-workflow-name",
        type=str,
        help="Filter by workflow name matching argument.",
    )
    subcommand.add_argument(
        "-r",
        "--running",
        dest="show_running_jobs",
        help="Show jobs in the 'Running' state.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-t",
        "--submission-time",
        help="Show only jobs which were submitted at most N hours ago.",
        default=24,
        type=int,
    )
    subcommand.add_argument(
        "-s",
        "--succeeded",
        dest="show_succeeded_jobs",
        help="Show jobs in the 'Succeeded' state.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "--steps-view",
        help="Show the 'steps' view.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)


def print_workflow_summary(workflows: List, metadatas: Dict, grid_style="fancy_grid"):
    """Print a summary of workflow statuses.
    
    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
    """

    agg = defaultdict(lambda: defaultdict(int))

    for w in workflows:
        m = metadatas[w["id"]]
        job_group = oliver.get_oliver_group(m)
        if not job_group:
            job_group = "<not set>"

        agg[job_group][m["status"]] += 1

    results = []
    keys = set()
    for group in agg.keys():
        for k in agg[group]:
            keys.add(k)
        obj = {"Job Group": group}
        obj.update(agg[group])
        results.append(obj)

    for r in results:
        for k in keys:
            if not k in r:
                r[k] = 0

    reporting.print_dicts_as_table(results, grid_style)


def print_workflow_detail_view(
    workflows: List,
    metadatas: Dict,
    show_job_name: bool = False,
    show_job_group: bool = False,
    grid_style="fancy_grid",
):
    """Print a detailed table of workflow statuses.
    
    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
        show_job_name(bool): include Oliver job name in results.
        show_job_group(bool): include Oliver job group in results.
    """

    results = [
        {
            "Job Name": oliver.get_oliver_name(metadatas.get(w.get("id"))),
            "Job Group": oliver.get_oliver_group(metadatas.get(w.get("id"))),
            "Workflow ID": w.get("id", ""),
            "Workflow Name": w.get("name", ""),
            "Status": w.get("status", ""),
            "Start": reporting.localize_date(w.get("start"))
            if "start" in w
            else "",
        }
        for w in workflows
    ]

    reporting.print_dicts_as_table(results, grid_style)


def print_workflow_steps_view(
    workflows: List, metadatas: Dict, grid_style="fancy_grid"
):
    """Print a table summarizing which steps (calls) are in progress.
    
    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
    """

    results = defaultdict(lambda: defaultdict(int))

    for w in workflows:
        uuid = w.get("id")
        if not uuid:
            errors.report(
                "`id` not found for workflow.",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        m = metadatas.get(uuid)
        if not m:
            errors.report(
                f"'{uuid}' not found in metadatas.",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        for call_name, calls in m.get("calls").items():
            most_recent_call = sorted(calls, key=lambda x: x["start"])[-1]
            results[call_name][most_recent_call.get("executionStatus")] += 1

    _results = [
        {"Call Name": call_name, **results[call_name]} for call_name in results.keys()
    ]
    
    reporting.print_dicts_as_table(_results, grid_style)
