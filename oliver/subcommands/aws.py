import argparse
import os

from typing import Dict

from ..integrations.aws import debug
from ..lib import api, args as _args, errors


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    aws_subcommand = args.get("aws-subcommand")

    if aws_subcommand == "debug-failures":
        debug.failures(args)
    else:
        errors.report(
            message=f"Unknown aws subcommand: '{aws_subcommand}'",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "aws", help="All subcommands related to Cromwell on AWS.",
    )

    aws_subcommands = subcommand.add_subparsers(dest="aws-subcommand")
    # https://bugs.python.org/issue9253#msg186387
    aws_subcommands.required = True

    # debug-failures subcommand
    debug = aws_subcommands.add_parser(
        "debug-failures",
        description="Gathers information about AWS Batch failures and puts them in a folder for analysis.",
    )
    _args.add_batches_group(debug, required=True)
    debug.add_argument(
        "-o",
        "--output-folder",
        help="Output folder to write results to.",
        type=str,
        default=os.path.join(os.getcwd(), "debug-failures"),
    )
    debug.add_argument(
        "-q",
        "--queue",
        help="Which queue to query?",
        type=str,
        default="default-e31bdbd0-3c77-11ea-bb0a-0a1540e225b5",
    )
    debug.add_argument(
        "-s",
        "--status",
        help="Which status to query?",
        nargs="+",
        type=str,
        default=["SUCCEEDED", "FAILED"],
    )
    subcommand.add_argument(
        "-t",
        "--submission-time",
        help="Show only jobs which were submitted at most N hours ago.",
        default=None,
        type=int,
    )

    subcommand.set_defaults(func=call)
    return subcommand
