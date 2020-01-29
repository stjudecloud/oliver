import argparse
import os

from typing import Dict

from ..integrations.azure import batch, cosmos
from .. import errors


def call(args: Dict):
    """Execute the cosmos.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    azure_subcommand = args.get("azure-subcommand")

    if azure_subcommand == "batch":
        batch.call(args)
    elif azure_subcommand == "cosmos":
        cosmos.call(args)
    else:
        errors.report(
            message=f"Unknown azure subcommand: '{azure_subcommand}'",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "azure", help="All subcommands related to Cromwell on Azure.",
    )

    azure_subcommands = subcommand.add_subparsers(
        dest="azure-subcommand", required=True
    )

    batch = azure_subcommands.add_parser("batch", help="Get azure batch information.")
    batch.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )

    cosmos = azure_subcommands.add_parser(
        "cosmos",
        description="Gathers information about azure Batch failures and puts them in a folder for analysis.",
    )
    cosmos.add_argument("workflow-id", help="Cromwell workflow ID.")
    cosmos.add_argument(
        "--failures", action="store_true", help="Return only failed tasks"
    )
    cosmos.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    cosmos.add_argument(
        "--json",
        help="Print the full JSON objects for Cosmos records",
        action="store_true",
    )
    cosmos.add_argument("-o", "--outfile", help="File to save JSON records to")

    subcommand.set_defaults(func=call)