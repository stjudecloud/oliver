import argparse
import os

from typing import Any, Dict

from ..lib import (
    api,
    workflows as _workflows,
)
from ..subcommands import outputs as _outputs


def process_output(dest_folder: str, output: str, dry_run: bool = False) -> None:
    cmd = None

    if isinstance(output, list):
        for o in output:
            process_output(dest_folder, o, dry_run)

        return

    if output:
        cmd = f"cp {output} {dest_folder}"
        if dry_run:
            print(cmd)
        else:
            os.system(cmd)


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
        cromwell (CromwellAPI): The cromwell API server to use.
    """

    output_folder = args.get("output-folder", "")
    workflows = []

    workflows = await _workflows.get_workflows(
        cromwell, cromwell_workflow_uuid=args.get("workflow-id"),
    )

    for workflow in workflows:
        outputs = await _outputs.get_outputs(cromwell, workflow.get("id", ""),)
        _this_output_folder = output_folder

        if _this_output_folder and not _this_output_folder.endswith(os.path.sep):
            _this_output_folder = _this_output_folder + os.path.sep

        for output in outputs:
            process_output(
                _this_output_folder, output["Location"], args.get("dry_run", False)
            )


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "aggregate", help="Aggregate outputs from local cromwell run"
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "output-folder", help="Output folder to aggregate outputs to."
    )
    subcommand.add_argument(
        "--dry-run",
        "-d",
        help="Print the copy commands instead of running them.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
