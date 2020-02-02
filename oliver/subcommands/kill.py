import argparse

from typing import Dict

from ..lib import api, reporting


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    resp = await cromwell.post_workflows_abort(args["workflow-id"])

    if not resp.get("id"):
        reporting.print_error_as_table(resp["status"], resp["message"])
        return

    results = [{"Workflow ID": resp["id"], "Status": resp["status"]}]
    reporting.print_dicts_as_table(results)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "kill", aliases=["k"], help="Kill a workflow running on a Cromwell server."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
