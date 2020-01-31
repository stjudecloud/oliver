import argparse

from typing import Dict

from ..lib import api, reporting


def get_outputs(
    cromwell_api: api.CromwellAPI, workflow_id: str, output_prefix: str = None
):
    outputs = cromwell_api.get_workflows_outputs(workflow_id)
    results = [{"Output Name": k, "Location": v} for k, v in outputs["outputs"].items()]

    if output_prefix:
        for result in results:
            result["Location"] = args["output_prefix"] + result["Location"]

    return results


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    results = get_outputs(
        cromwell, args["workflow-id"], output_prefix=args.get("output_prefix"),
    )
    reporting.print_dicts_as_table(results)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "outputs", aliases=["o"], help="Find all reported outputs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
