import argparse

from typing import Any, Dict
from logzero import logger

from ..lib import api, reporting, args as _args, workflows as _workflows


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    if args.get("cromwell_workflow_uuid"):
        resp = await cromwell.post_workflows_abort(args["cromwell_workflow_uuid"])

        if not resp.get("id"):
            reporting.print_error_as_table(resp["status"], resp["message"])
        else:
            results = [{"Workflow ID": resp["id"], "Status": resp["status"]}]
            reporting.print_dicts_as_table(results)
        return

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
        oliver_job_name=args["job_name"],
        oliver_job_group_name=args["job_group"],
        cromwell_workflow_uuid=args["cromwell_workflow_uuid"],
        batches=batches,
        batch_interval_mins=args["batch_interval_mins"],
        relative_batching=relative,
        opt_into_reporting_running_jobs=True,
    )

    if not workflows:
        logger.warning("No running jobs matching criteria found.")
        return

    for w in workflows:
        resp = await cromwell.post_workflows_abort(w["id"])

        if not resp.get("id"):
            reporting.print_error_as_table(resp["status"], resp["message"])
            continue

        results = [{"Workflow ID": resp["id"], "Status": resp["status"]}]
        reporting.print_dicts_as_table(results)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "abort",
        aliases=["kill", "k"],
        help="Abort workflows running on a Cromwell server.",
    )
    scope_predicate = subcommand.add_mutually_exclusive_group(required=True)
    _args.add_batches_group(scope_predicate)
    _args.add_batches_interval_arg(subcommand)
    scope_predicate.add_argument(
        "-w", "--cromwell-workflow-uuid", help="Workflow UUID you wish to abort."
    )
    scope_predicate.add_argument(
        "-g", "--job-group", help="Job group name you wish to abort."
    )
    scope_predicate.add_argument("-j", "--job-name", help="Job name you wish to abort.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
