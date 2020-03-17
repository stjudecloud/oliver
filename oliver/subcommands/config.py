import argparse

from typing import Any, Dict

from ..lib import api, errors
from ..lib.config import read_config, write_config


async def call(
    args: Dict[str, Any], cromwell: api.CromwellAPI  # pylint: disable=unused-argument
) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """
    config = read_config()

    if args["action"] == "list":
        for k, v in config.items():
            print(f"{k}\t{v}")
    elif args["action"] == "rm":
        if len(args["value"]) != 1:
            errors.report(
                '"rm" must take one value as "<key>".',
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )
        [key] = args["value"]
        if key in config:
            del config[key]
        write_config(config)
    elif args["action"] == "get":
        if len(args["value"]) != 1:
            errors.report(
                '"get" must take one value as "<key>".',
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )
        [key] = args["value"]
        if key not in config:
            errors.report(
                f'"{key}" not in config.',
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )
        print(config[key])
    elif args["action"] == "set":
        if len(args["value"]) != 2:
            errors.report(
                '"set" must take two values as "<key> <value>".',
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )
        [key, value] = args["value"]
        config[key] = value
        write_config(config)
    else:
        errors.report(
            f"Unhandled action: {args['actions']}",
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
        "config", help="Set or get a single config value from Oliver."
    )
    subcommand.add_argument(
        "action",
        choices=["list", "rm", "get", "set"],
        help="Action to take on the config.",
    )
    subcommand.add_argument(
        "value", nargs="*", help='"<key>" for "get" or "<key> <value>" for "set".'
    )
    subcommand.set_defaults(func=call)
    return subcommand
