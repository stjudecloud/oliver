import argparse

from typing import Any, cast, DefaultDict, Dict, List, Optional, Union

from collections import defaultdict

from ..lib import (
    api,
    args as _args,
    errors,
    reporting,
    oliver,
    workflows as _workflows,
)


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    batches = None
    relative = None

    if args.get("batches_relative"):
        batches = args.get("batches_relative")
        relative = True
    elif args.get("batches_absolute"):
        batches = args.get("batches_absolute")
        relative = False

    workflows = await _workflows.get_workflows(
        cromwell=cromwell,
        submission_time_hours_ago=args["submission_time"],
        oliver_job_name=args["job_name"],
        oliver_job_group_name=args["job_group"],
        cromwell_workflow_uuid=args["cromwell_workflow_uuid"],
        cromwell_workflow_name=args["cromwell_workflow_name"],
        batches=batches,
        batch_interval_mins=args["batch_interval_mins"],
        relative_batching=relative,
        opt_into_reporting_aborted_jobs=args["show_aborted_jobs"],
        opt_into_reporting_failed_jobs=args["show_failed_jobs"],
        opt_into_reporting_running_jobs=args["show_running_jobs"],
        opt_into_reporting_succeeded_jobs=args["show_succeeded_jobs"],
    )

    metadatas = {
        w["id"]: await cromwell.get_workflows_metadata(w["id"]) for w in workflows
    }

    call_names_to_consider = args.get("failed_calls")
    if call_names_to_consider:
        new_workflows = []
        for workflow in workflows:
            keep_workflow = False
            for call_name, calls in (
                metadatas.get(workflow.get("id"), {}).get("calls", {}).items()
            ):
                if call_name in call_names_to_consider:
                    if any([c.get("executionStatus") == "Failed" for c in calls]):
                        keep_workflow = True
                        break

            if keep_workflow:
                new_workflows.append(workflow)

        workflows = new_workflows

    if args.get("steps_view"):
        print_workflow_steps_view(
            workflows, metadatas, grid_style=args.get("grid_style")
        )
    elif args.get("detail_view"):
        print_workflow_detail_view(
            workflows, metadatas, grid_style=args["grid_style"],
        )
    else:
        print_workflow_summary(workflows, metadatas, grid_style=args["grid_style"])


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "status",
        aliases=["st"],
        help="Report various statistics about a running Cromwell server.",
    )

    view = subcommand.add_mutually_exclusive_group()
    view.add_argument(
        "-d",
        "--detail-view",
        help="Show detailed view which displays information about each individual job.",
        default=False,
        action="store_true",
    )
    view.add_argument(
        "-z",
        "--steps-view",
        help="Show the 'steps' view which displays summary information about how many jobs are at each step.",
        default=False,
        action="store_true",
    )

    subcommand.add_argument(
        "-a",
        "--aborted",
        dest="show_aborted_jobs",
        help="Show jobs in the 'Aborted' state.",
        default=False,
        action="store_true",
    )
    _args.add_batches_group(subcommand)
    subcommand.add_argument(
        "--failed-calls",
        help="Only show calls with the given name that failed (useful in restarting failed steps).",
        nargs="+",
        type=str,
    )
    subcommand.add_argument(
        "-f",
        "--failed",
        dest="show_failed_jobs",
        help="Show jobs in the 'Failed' state.",
        default=False,
        action="store_true",
    )
    _args.add_oliver_job_group_args(subcommand)
    subcommand.add_argument(
        "-i",
        "--cromwell-workflow-uuid",
        type=str,
        help="Filter by workflow id matching argument.",
    )
    _args.add_oliver_job_name_args(subcommand)
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
        default=None,
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
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand


def print_workflow_summary(
    workflows: List[Dict[str, Any]],
    metadatas: Dict[str, Any],
    grid_style: Optional[str] = "fancy_grid",
) -> None:
    """Print a summary of workflow statuses.

    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
    """

    agg: DefaultDict[str, DefaultDict[str, int]] = defaultdict(lambda: defaultdict(int))

    for w in workflows:
        m = metadatas[w["id"]]
        job_group = oliver.get_oliver_group(m)
        agg[job_group][m["status"]] += 1

    results = []
    keys = set()
    for group in agg.keys():
        for k in agg[group]:
            keys.add(k)
        obj: Dict[str, Union[str, int]] = {"Job Group": group}
        obj.update(agg[group])
        results.append(obj)

    for r in results:
        for k in keys:
            if not k in r:
                r[k] = 0

    reporting.print_dicts_as_table(results, grid_style)


def print_workflow_detail_view(
    workflows: List[Dict[str, Any]],
    metadatas: Dict[str, Any],
    grid_style: str = "fancy_grid",
) -> None:
    """Print a detailed table of workflow statuses.

    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
    """

    results = [
        {
            "Job Name": oliver.get_oliver_name(metadatas.get(w.get("id", ""), {})),
            "Job Group": oliver.get_oliver_group(metadatas.get(w.get("id", ""), {})),
            "Workflow ID": w.get("id", ""),
            "Workflow Name": w.get("name", ""),
            "Status": w.get("status", ""),
            "Start": reporting.localize_date(w.get("start", ""))
            if "start" in w
            else "",
        }
        for w in workflows
    ]

    reporting.print_dicts_as_table(results, grid_style)


def print_workflow_steps_view(
    workflows: List[Dict[str, Any]],
    metadatas: Dict[str, Any],
    grid_style: Optional[str] = "fancy_grid",
) -> None:
    """Print a table summarizing which steps (calls) are in progress.

    Args:
        workflows (List): List of workflows returned from the API call.
        metadatas (Dict): Dictionary of metadatas indexed by workflow id.
    """

    results: DefaultDict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for w in workflows:
        uuid = cast(str, w.get("id", ""))
        if not uuid:
            errors.report(
                "`id` not found for workflow.",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        m = metadatas.get(uuid, {})
        if not m:
            errors.report(
                f"'{uuid}' not found in metadatas.",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        for call_name, calls in m.get("calls").items():
            most_recent_call = sorted(calls, key=lambda x: x["start"])[-1]
            results[call_name][most_recent_call.get("executionStatus")] += 1

    _results: List[Dict[str, Union[str, int]]] = [
        {"Call Name": call_name, **results[call_name]} for call_name in results.keys()
    ]

    reporting.print_dicts_as_table(_results, grid_style)
