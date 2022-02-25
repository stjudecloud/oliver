import os
import argparse

from typing import Any, Dict

from ..integrations.aws import aggregate, clean, debug
from ..lib import api, args as _args, errors


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    aws_subcommand = args.get("aws-subcommand")

    if aws_subcommand == "aggregate":
        await aggregate.call(args, cromwell)
    elif aws_subcommand == "clean":
        await clean.call(args, cromwell)
    elif aws_subcommand == "debug":
        await debug.call(args, cromwell)
    else:
        errors.report(
            message=f"Unknown aws subcommand: '{aws_subcommand}'",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "aws",
        help="All subcommands related to Cromwell on AWS.",
    )

    aws_subcommands = subcommand.add_subparsers(dest="aws-subcommand")
    # https://bugs.python.org/issue9253#msg186387
    aws_subcommands.required = True

    # aggregate output files
    aggregate_subcommand = aws_subcommands.add_parser(
        "aggregate",
        aliases=["a"],
        help="Aggregate all results to a local or cloud folder for a run.",
    )
    scope_predicate = aggregate_subcommand.add_mutually_exclusive_group(required=True)
    _args.add_batches_group(scope_predicate)
    _args.add_batches_interval_arg(subcommand)
    scope_predicate.add_argument(
        "-w", "--workflow", help="Workflow UUID you wish to retry."
    )
    aggregate_subcommand.add_argument(
        "root-output-folder",
        help="Root output folder to localize the files to (currently supports S3).",
    )
    aggregate_subcommand.add_argument(
        "-j",
        "--append-job-name",
        help="Append job name to output folders.",
        default=False,
        action="store_true",
    )
    aggregate_subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    _args.add_loglevel_group(aggregate_subcommand)

    # clean up s3 resources for failed and aborted workflows
    clean_subcommand = aws_subcommands.add_parser(
        "clean", aliases=["c"], help=clean.__doc__.split("\n", maxsplit=1)[0]
    )
    clean_subcommand.add_argument(
        "workflow-root-folder",
        help="Currently, the `cromwell-execution` directory cannot be "
        "queried from Cromwell. Thus, you'll need to supply it here. "
        "Make sure it starts with \"s3://\"! Ex: 's3://[BUCKET]/cromwell-execution/[PIPELINE]'",
    )
    clean_subcommand.add_argument(
        "--all",
        help="Clean all workflows, not just failed or aborted ones.",
        default=False,
        action="store_true",
    )
    _args.add_loglevel_group(clean_subcommand)

    # debug subcommand
    debug_subcommand = aws_subcommands.add_parser(
        "debug",
        aliases=["d"],
        description="Gathers information about AWS Batch failures "
        + "and puts them in a folder for analysis.",
    )
    debug_subcommand.add_argument(
        "queue", help="Which AWS batch queue to query?", type=str
    )
    _args.add_batches_group(debug_subcommand, required=True)
    debug_subcommand.add_argument(
        "-o",
        "--output-folder",
        help="Output folder to write results to.",
        type=str,
        default=os.path.join(os.getcwd(), "debug"),
    )
    debug_subcommand.add_argument(
        "-s",
        "--status",
        help="Which status to query?",
        nargs="+",
        type=str,
        default=["SUCCEEDED", "FAILED"],
    )
    debug_subcommand.add_argument(
        "-t",
        "--submission-time",
        help="Show only jobs which were submitted at most N hours ago.",
        default=None,
        type=int,
    )
    _args.add_loglevel_group(debug_subcommand)

    subcommand.set_defaults(func=call)
    return subcommand
