"""Subcommand to do a thing!
"""

import argparse

from typing import Any, Dict, List

from ..lib import api

SUBCOMMAND_NAME = "__template__"
SUBCOMMAND_ALIASES: List[str] = []


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    print(f"Hello, {SUBCOMMAND_NAME}!")
    print(args)
    print(cromwell)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        SUBCOMMAND_NAME,
        aliases=SUBCOMMAND_ALIASES,
        help=__doc__.split("\n", maxsplit=1)[0],
    )

    subcommand.set_defaults(func=call)
    return subcommand
