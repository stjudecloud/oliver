import argparse

from typing import Dict

from ..lib.config import get_default_config, read_config, write_config

QUESTION_MAPPING = {
    "cromwell_server": "What is the Cromwell server address",
    "cromwell_api_version": "What is the Cromwell API version",
    "batch_interval_mins": "When splitting batches, how many minutes apart should two jobs be",
}


def ask(question, default):
    return input(f"{question} (default: {default})? ")


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    starting_config = get_default_config()
    starting_config.update(read_config())
    final_config = {}

    for k, _default in starting_config.items():
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
    subcommand.set_defaults(func=call)
    return subcommand
