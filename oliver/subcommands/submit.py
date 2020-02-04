import argparse
import os

from typing import Dict

from ..lib import api, args as _args, errors, reporting, utils
from ..lib.parsing import parse_workflow, parse_workflow_inputs


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    workflow_args = parse_workflow(args["workflow"])
    (
        workflow_args["workflowInputs"],
        workflow_args["workflowOptions"],
        workflow_args["labels"],
    ) = parse_workflow_inputs(
        args.get("workflowInputs"),
        job_name=args.get("job_name"),
        job_group=args.get("job_group"),
        output_dir=args.get("output_dir"),
    )

    if args.get("dry_run"):
        for key, value in workflow_args.items():
            print(f"{key} = {value}")
        return

    results = [await cromwell.post_workflows(**workflow_args)]
    reporting.print_dicts_as_table(results, args["grid_style"])


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "submit", aliases=["su"], help="Submit a workflow to the Cromwell server."
    )
    subcommand.add_argument("workflow", help="The workflow to run (URL or file).")
    subcommand.add_argument(
        "workflowInputs",
        nargs="+",
        help="JSON files or key=value pairs to add to inputs, options, or labels (see documentation for more information).",
    )
    subcommand.add_argument(
        "-d",
        "--dry-run",
        help="Print what would be submitted rather than actually submitting.",
        default=False,
        action="store_true",
    )
    _args.add_oliver_job_group_args(subcommand)
    _args.add_oliver_job_name_args(subcommand)
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.add_argument(
        "-o",
        "--output-dir",
        help="Coalesce outputs into the specified directory using `final_workflow_outputs_dir`.",
        type=str,
        default=None,
    )
    subcommand.set_defaults(func=call)
    return subcommand
