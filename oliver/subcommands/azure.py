import argparse

from typing import Any, Dict

from ..integrations.azure import aggregate, cosmos
from ..lib import api, errors


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the cosmos.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    azure_subcommand = args.get("azure-subcommand")

    if azure_subcommand == "cosmos":
        await cosmos.call(args, cromwell)
    elif azure_subcommand == "aggregate":
        await aggregate.call(args, cromwell)
    else:
        errors.report(
            message=f"Unknown azure subcommand: '{azure_subcommand}'",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "azure",
        help="All subcommands related to Cromwell on Azure.",
    )

    azure_subcommands = subcommand.add_subparsers(dest="azure-subcommand")
    # https://bugs.python.org/issue9253#msg186387
    azure_subcommands.required = True

    cosmos_parser = azure_subcommands.add_parser(
        "cosmos",
        description="Gathers information about azure Batch failures "
        + "and puts them in a folder for analysis.",
    )
    cosmos_parser.add_argument("workflow-id", help="Cromwell workflow ID.")
    cosmos_parser.add_argument(
        "--failures", action="store_true", help="Return only failed tasks"
    )
    cosmos_parser.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    cosmos_parser.add_argument(
        "--json",
        help="Print the full JSON objects for Cosmos records",
        action="store_true",
    )
    cosmos_parser.add_argument("-o", "--outfile", help="File to save JSON records to")

    aggregate_parser = azure_subcommands.add_parser(
        "aggregate", description="Aggregate outputs from Azure blob container."
    )
    aggregate_parser.add_argument("workflow-id", help="Cromwell workflow ID.")
    aggregate_parser.add_argument(
        "output-folder", help="Output folder to download the files to."
    )
    aggregate_parser.add_argument(
        "--sas-token", help="Valid SAS token for the `cromwell-executions` container."
    )
    aggregate_parser.add_argument(
        "-d",
        "--dry-run",
        help="Print what would be submitted rather than actually submitting.",
        default=False,
        action="store_true",
    )

    subcommand.set_defaults(func=call)
    return subcommand
