"""Subcommand to do a thing!
"""

import argparse

from typing import Dict

from ..lib import api

SUBCOMMAND_NAME = "__template__"
SUBCOMMAND_ALIASES = []


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    print(f"Hello, {SUBCOMMAND_NAME}!")


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        SUBCOMMAND_NAME, aliases=SUBCOMMAND_ALIASES, help=__doc__.split("\n")[0]
    )

    subcommand.set_defaults(func=call)
    return subcommand
