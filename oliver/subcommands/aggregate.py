import argparse
import os

from typing import Dict

from .. import api, errors, reporting
from . import outputs as _outputs


def process_output(dest_folder: str, output: str):
    if isinstance(output, list):
        for o in output:
            process_output(dest_folder, o)
    else:
        if not output.startswith("s3://"):
            errors.report(
                f"Could not copy {output}. Only s3 buckets are currently supported!",
                fatal=False,
                exitcode=errors.ERROR_INVALID_INPUT,
            )

        os.system(f"aws s3 cp --sse AES256 {output} {dest_folder}")


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

    for output in outputs:
        process_output(args["output-folder"], output["Location"])


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
        "output-folder",
        help="Output folder to localize the files to (currently supports S3).",
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
