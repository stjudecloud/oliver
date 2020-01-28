import argparse
import json

from typing import Dict

from .. import api, errors


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    metadata = cromwell.get_workflows_metadata(args["workflow-id"])

    if not metadata.get("submittedFiles", {}).get("inputs"):
        errors.report(
            "Could not retrieve inputs!",
            fatal=True,
            exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
        )

    print(json.dumps(json.loads(metadata["submittedFiles"]["inputs"]), indent=2))


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "inputs", help="Find all reported outputs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
