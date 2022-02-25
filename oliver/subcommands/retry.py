import argparse
import json

from typing import Any, cast, Dict

from ..lib import api, args as _args, errors, reporting, utils, workflows as _workflows
from ..lib.parsing import parse_workflow_inputs


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    workflows = []
    show_only_aborted_and_failed = not args["all"]

    if args.get("workflow"):
        workflows = await _workflows.get_workflows(
            cromwell,
            cromwell_workflow_uuid=args.get("workflow"),
            opt_into_reporting_failed_jobs=show_only_aborted_and_failed,
            opt_into_reporting_aborted_jobs=show_only_aborted_and_failed,
        )
    elif args.get("batches_absolute"):
        workflows = await _workflows.get_workflows(
            cromwell,
            batches=args.get("batches_absolute"),
            relative_batching=False,
            batch_interval_mins=args.get("batch_interval_mins"),
            opt_into_reporting_failed_jobs=show_only_aborted_and_failed,
            opt_into_reporting_aborted_jobs=show_only_aborted_and_failed,
        )
    elif args.get("batches_relative"):
        workflows = await _workflows.get_workflows(
            cromwell,
            batches=args.get("batches_relative"),
            batch_interval_mins=args.get("batch_interval_mins"),
            relative_batching=True,
            opt_into_reporting_failed_jobs=show_only_aborted_and_failed,
            opt_into_reporting_aborted_jobs=show_only_aborted_and_failed,
        )
    elif args.get("retry_job_group"):
        workflows = await _workflows.get_workflows(
            cromwell,
            oliver_job_group_name=args.get("retry_job_group"),
            opt_into_reporting_failed_jobs=show_only_aborted_and_failed,
            opt_into_reporting_aborted_jobs=show_only_aborted_and_failed,
        )
    else:
        errors.report(
            "Unhandled `retry` scope and predicate.",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
            suggest_report=True,
        )

    if not args.get("dry_run"):
        if not args["yes"] and not utils.ask_boolean_question(
            f"Wishing to resubmit {len(workflows)} jobs. Continue?"
        ) in ["yes", "y"]:
            errors.report("User cancelled submission.", fatal=True, exitcode=0)

    results = []
    for w in workflows:
        metadata = await cromwell.get_workflows_metadata(w["id"])

        workflowUrl = metadata.get("submittedFiles", {}).get("workflowUrl", {})
        workflowInputs = metadata.get("submittedFiles", {}).get("inputs", {})
        workflowOptions = metadata.get("submittedFiles", {}).get("options", {})
        workflowLabels = metadata.get("submittedFiles", {}).get("labels", {})
        workflow_args = {}
        (
            workflow_args["workflowInputs"],
            workflow_args["workflowOptions"],
            workflow_args["workflowLabels"],
        ) = parse_workflow_inputs(
            args.get("workflowInputs", []),
            inputs=json.loads(workflowInputs),
            options=json.loads(workflowOptions),
            labels=json.loads(workflowLabels),
            job_name=args.get("job_name"),
            job_group=args.get("job_group"),
            output_dir=args.get("output_dir"),
        )

        if args.get("dry_run"):
            for key, value in workflow_args.items():
                print(f"{key} = {value}")
            continue

        results.append(
            await cromwell.post_workflows(
                workflowUrl=workflowUrl,
                workflowInputs=cast(Dict[str, str], workflow_args["workflowInputs"]),
                workflowOptions=cast(Dict[str, str], workflow_args["workflowOptions"]),
                labels=cast(Dict[str, str], workflow_args["workflowLabels"]),
            )
        )

    reporting.print_dicts_as_table(results)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "retry",
        aliases=["re"],
        help="Resubmit a workflow with the same parameters. By default, only restarts workflows which are 'Failed' or 'Aborted'.",
    )
    scope_predicate = subcommand.add_mutually_exclusive_group(required=True)
    _args.add_batches_group(scope_predicate)
    _args.add_batches_interval_arg(subcommand)
    scope_predicate.add_argument(
        "-w", "--workflow", help="Workflow UUID you wish to retry."
    )
    scope_predicate.add_argument(
        "-G", "--retry-job-group", help="Job group name you wish to retry."
    )
    subcommand.add_argument(
        "workflowInputs",
        nargs="*",
        help="JSON files or key=value pairs to add to inputs, options, or labels (see documentation for more information).",
    )
    subcommand.add_argument(
        "-a",
        "--all",
        help="Restart all workflows, not just 'Failed' and 'Aborted' workflows.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-d",
        "--dry-run",
        help="Print what would be submitted rather than actually submitting.",
        default=False,
        action="store_true",
    )
    _args.add_oliver_job_group_args(subcommand)
    _args.add_oliver_job_name_args(subcommand)
    subcommand.add_argument(
        "-o",
        "--output-dir",
        help="Coalesce outputs into the specified directory using `final_workflow_outputs_dir`.",
        type=str,
        default=None,
    )
    subcommand.add_argument(
        "-y",
        "--yes",
        help="Instead of prompting, go ahead and resubmit the jobs.",
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
