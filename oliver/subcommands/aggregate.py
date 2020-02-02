import argparse
import os

from typing import Dict

from ..lib import api, args as _args, oliver, errors, reporting, workflows as _workflows
from . import outputs as _outputs


def process_output(dest_folder: str, output: str, dry_run: bool = False):
    cmd = None

    if isinstance(output, list):
        for o in output:
            process_output(dest_folder, o, dry_run=dry_run)

        return

    if not output.startswith("s3://"):
        errors.report(
            f"Could not copy {output}. Only s3 buckets are currently supported!",
            fatal=False,
            exitcode=errors.ERROR_INVALID_INPUT,
        )

    cmd = f"aws s3 cp --sse AES256 {output} {dest_folder}"

    if dry_run:
        print(cmd)
    else:
        os.system(cmd)


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    output_folder = args.get("root-output-folder")
    workflows = []

    if args.get("workflow"):
        workflows = await _workflows.get_workflows(
            cromwell, cromwell_workflow_uuid=args.get("workflow"),
        )
    elif args.get("batches_absolute"):
        workflows = await _workflows.get_workflows(
            cromwell,
            batches=args.get("batches_absolute"),
            relative_batching=False,
            batch_interval_mins=args.get("batch_interval_mins"),
        )
    elif args.get("batches_relative"):
        workflows = await _workflows.get_workflows(
            cromwell,
            batches=args.get("batches_relative"),
            batch_interval_mins=args.get("batch_interval_mins"),
            relative_batching=True,
        )
    else:
        errors.report(
            f"Unhandled `retry` scope and predicate.",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
            suggest_report=True,
        )

    for workflow in workflows:
        outputs = _outputs.get_outputs(
            cromwell, workflow.get("id"), output_prefix=args.get("output_prefix"),
        )
        _this_output_folder = output_folder

        if args.get("append_job_name"):
            name = oliver.get_oliver_name(
                await cromwell.get_workflows_metadata(workflow.get("id"))
            )
            if name == "<not set>":
                name = "__UNKNOWN__"
            _this_output_folder = os.path.join(_this_output_folder, name)

        if not _this_output_folder.endswith(os.path.sep):
            _this_output_folder = _this_output_folder + os.path.sep

        for output in outputs:
            process_output(
                _this_output_folder, output["Location"], dry_run=args.get("dry_run")
            )


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "aggregate",
        aliases=["a"],
        help="Aggregate all results to a local or cloud folder for a run.",
    )
    scope_predicate = subcommand.add_mutually_exclusive_group(required=True)
    _args.add_batches_group(
        scope_predicate, add_batches_interval_arg_automatically=False
    )
    _args.add_batches_interval_arg(subcommand)
    scope_predicate.add_argument(
        "-w", "--workflow", help="Workflow UUID you wish to retry."
    )
    subcommand.add_argument(
        "root-output-folder",
        help="Root output folder to localize the files to (currently supports S3).",
    )
    subcommand.add_argument(
        "-j",
        "--append-job-name",
        help="Append job name to output folders.",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "-d",
        "--dry-run",
        help="Print commands that would be executed rather than actually executing them.",
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
