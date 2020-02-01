import argparse

from typing import Dict

from ..lib import api
from ..lib.config import get_default_config, read_config, write_config

QUESTION_MAPPING = {
    "cromwell_server": "What is the Cromwell server address",
    "cromwell_api_version": "What is the Cromwell API version",
    "batch_interval_mins": "When splitting batches, how many minutes apart should two jobs be",
}


def ask(question, default):
    return input(f"{question} (default: {default})? ")


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    starting_config = get_default_config()
    starting_config.update(read_config())
    use_defaults = args.get("defaults")
    final_config = {}

    for k, _default in starting_config.items():
        if not use_defaults:
            question = "What is the value for '{k}'"
            if k in QUESTION_MAPPING:
                question = QUESTION_MAPPING[k]

            answer = ask(question, _default)
            if answer:
                _default = answer
        final_config[k] = _default

    write_config(final_config)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "configure", help="Configure Oliver with default options."
    )
    subcommand.add_argument(
        "--defaults",
        help="Store the default values without prompting the user.",
        default=False,
        action="store_true",
    )
    subcommand.set_defaults(func=call)
    return subcommand
