import argparse

from typing import Any, Dict, List, Optional

from ..lib import api, reporting


async def get_outputs(
    cromwell_api: api.CromwellAPI, workflow_id: str, output_prefix: Optional[str] = ""
) -> List[Dict[str, str]]:
    outputs = await cromwell_api.get_workflows_outputs(workflow_id)
    results = [{"Output Name": k, "Location": v} for k, v in outputs["outputs"].items()]

    if output_prefix:
        for result in results:
            result["Location"] = output_prefix + result["Location"]

    return results


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    results = await get_outputs(
        cromwell, args["workflow-id"], output_prefix=args.get("output_prefix", ""),
    )
    reporting.print_dicts_as_table(results)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
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
