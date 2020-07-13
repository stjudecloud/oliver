import argparse

from typing import Any, Dict, List

from ..lib import api, errors, reporting


async def get_logs(cromwell: api.CromwellAPI, workflow_id: str) -> List[Dict[str, str]]:
    """Get logs from a workflow ID.

    Cromwell has REST API for getting logs, but it excludes sub-workflows.
    To obtain sub-workflows as well, use the metadata API recursively when
    calls to sub-worfklows are encountered.

    Args:
        cromwell (api.CromwellAPI): Cromwell API
        workflow_id (str): Workflow ID

    Returns:
        List[Dict]: List of log files for the workflow
    """
    metadata = await cromwell.get_workflows_metadata(workflow_id)
    results: List[Dict[str, str]] = []
    for name, call in metadata["calls"].items():
        for process in call:
            if "subWorkflowId" in process:
                results += await get_logs(cromwell, process.get("subWorkflowId"))
                continue

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

            stdout = process.get("stdout", "")
            stderr = process.get("stderr", "")
            results.append(
                {
                    "Call Name": name,
                    "Attempt": attempt,
                    "Shard": shard,
                    "Log Name": "stdout",
                    "Location": stdout,
                }
            )
            results.append(
                {
                    "Call Name": name,
                    "Attempt": attempt,
                    "Shard": shard,
                    "Log Name": "stderr",
                    "Location": stderr,
                }
            )
    return results


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """
    results = await get_logs(cromwell, args["workflow-id"])
    if args.get("output_prefix"):
        for result in results:
            result["Location"] = args["output_prefix"] + result["Location"]

    if args.get("call_name"):
        results = list(filter(lambda r: args["call_name"] in r["Call Name"], results))

    reporting.print_dicts_as_table(results)


def register_subparser(
    subparser: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """Registers a subparser for the current command.

    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "logs", aliases=["l"], help="Find all reported logs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "-c", "--call-name", help="Call name from the Cromwell workflow instance."
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
    return subcommand
