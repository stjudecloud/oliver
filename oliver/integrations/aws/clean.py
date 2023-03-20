"""Remove outputs for all failed or aborted workflows.
"""

from typing import Any, Dict, Mapping
from logzero import logger

from ...lib import api, errors, workflows as _workflows


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
    """

    workflow_root_folder = args.get("workflow-root-folder", "")
    if not workflow_root_folder.startswith("s3://"):
        errors.report(
            message="Workflow root folder must start with 's3://'!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )
    elif "cromwell-execution" not in workflow_root_folder:
        errors.report(
            message="Workflow root folder must contain the string 'cromwell-execution'!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )
    elif workflow_root_folder.endswith("/"):
        while workflow_root_folder.endswith("/"):
            workflow_root_folder = workflow_root_folder[:-1]

    # Relevant issue: https://github.com/python/mypy/issues/1969
    # mypy maps kwargs to arguments in the function and therefore is an incompatible type.
    # The issue states that mypy does not error if the type is set to Mapping
    kwargs: Mapping[str, bool] = {}
    if not args.get("all"):
        kwargs = {
            "opt_into_reporting_aborted_jobs": True,
            "opt_into_reporting_failed_jobs": True,
        }

    workflows = await _workflows.get_workflows(cromwell, **kwargs)

    for workflow in workflows:
        cmd = f"aws s3 rm --recursive {workflow_root_folder}/{workflow.get('id')}/"
        print(cmd)

    logger.info("Found %d workflows.", len(workflows))
