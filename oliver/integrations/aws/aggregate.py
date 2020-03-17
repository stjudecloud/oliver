import os

from typing import Any, Dict

from ...lib import (
    api,
    oliver,
    errors,
    workflows as _workflows,
)
from ...subcommands import outputs as _outputs


def process_output(dest_folder: str, output: str) -> None:
    cmd = None

    if isinstance(output, list):
        for o in output:
            process_output(dest_folder, o)

        return

    if not output.startswith("s3://"):
        errors.report(
            f"Could not copy {output}. Only s3 buckets are currently supported!",
            fatal=False,
            exitcode=errors.ERROR_INVALID_INPUT,
        )

    cmd = f"aws s3 cp --sse AES256 {output} {dest_folder}"
    print(cmd)


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    output_folder = args.get("root-output-folder", "")
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
        outputs = await _outputs.get_outputs(
            cromwell, workflow.get("id", ""), output_prefix=args.get("output_prefix"),
        )
        _this_output_folder = output_folder

        if args.get("append_job_name"):
            name = oliver.get_oliver_name(
                await cromwell.get_workflows_metadata(workflow.get("id", ""))
            )
            if not name or name == "<not set>":
                name = "__UNKNOWN__"
            _this_output_folder = os.path.join(_this_output_folder, name)

        if not _this_output_folder.endswith(os.path.sep):
            _this_output_folder = _this_output_folder + os.path.sep

        for output in outputs:
            process_output(_this_output_folder, output["Location"])
