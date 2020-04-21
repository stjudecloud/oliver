import argparse

from typing import Any, Dict

from ..lib import api, errors, reporting


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    metadata = await cromwell.get_workflows_metadata(args["workflow-id"])
    if not metadata.get("calls"):
        reporting.print_error_as_table(metadata["status"], metadata["message"])
        return

    calls_that_match = []
    for name, call in metadata["calls"].items():
        for process in call:
            attempt = process.get("attempt")
            shard = process.get("shardIndex")

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt:
                errors.report(
                    "Expected key is missing! The code needs to be updated, please contact the author!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )

            if (
                attempt == args["attempt"]
                and shard == args["shard"]
                and name == args["call-name"]
            ):
                if not process.get("runtimeAttributes"):
                    calls_that_match.append(
                        [
                            {
                                "Status": "Error",
                                "Message": "Job did not have any runtime attributes set at the time of query.",
                            }
                        ]
                    )
                else:
                    calls_that_match.append(
                        [
                            {"Key": k, "Value": v}
                            for k, v in process["runtimeAttributes"].items()
                        ]
                    )

    if calls_that_match:
        if len(calls_that_match) > 1:
            errors.report(
                "Multiple calls match this criteria!",
                fatal=True,
                exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
            )

        calls = calls_that_match[0]
        reporting.print_dicts_as_table(calls)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "runtime",
        aliases=["ru"],
        help="Get the runtime attributes used for a specific call.",
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "call-name", help="Name of the call executed within the workflow."
    )
    subcommand.add_argument("--attempt", default=1, help="Attempt number for call.")
    subcommand.add_argument("--shard", default=-1, help="Shard number for call.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
