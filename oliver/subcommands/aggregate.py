import argparse
import os

from typing import Dict

from ..lib import api, oliver, errors, reporting, workflows as _workflows
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


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    outputs = _outputs.get_outputs(
        cromwell, args["workflow-id"], output_prefix=args.get("output_prefix"),
    )

    output_folder = args.get("root-output-folder")

    if args.get("append_job_name"):
        name = oliver.get_oliver_name(
            cromwell.get_workflows_metadata(args.get("workflow-id"))
        )
        if name == "<not set>":
            name = "__UNKNOWN__"
        output_folder = os.path.join(output_folder, name)

    if not output_folder.endswith(os.path.sep):
        output_folder = output_folder + os.path.sep

    for output in outputs:
        process_output(output_folder, output["Location"], dry_run=args.get("dry_run"))


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
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
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
