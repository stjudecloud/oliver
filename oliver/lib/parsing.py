import json
import os
import re

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from ..lib import constants, errors


def is_url(url_string: str) -> bool:
    try:
        scheme = urlparse(url_string).scheme
        return scheme in ("http", "https")
    # pylint: disable=broad-exception-caught
    except Exception:
        return False
    # pylint: enable=broad-exception-caught


def parse_workflow(workflow: str) -> Dict[str, str]:
    """Determine if the workflow is a source file or URL.

    Args:
        workflow (str): Workflow source input from the command line.

    Returns:
        Dict[str, str]: Arguments for API call which consists of either
        workflowSource or workflowUrl, but not both.
    """
    if is_url(workflow):
        return {"workflowUrl": workflow}
    if os.path.isfile(workflow):
        return {"workflowSource": os.path.abspath(workflow)}
    errors.report(
        "Workflow is not a valid file or URL!",
        fatal=True,
        exitcode=errors.ERROR_INVALID_INPUT,
    )
    return {}


# pylint: disable=too-many-arguments
def parse_workflow_inputs(
    workflow_inputs: List[str],
    job_name: Optional[str] = None,
    job_group: Optional[str] = None,
    output_dir: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    labels: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str, str]:
    if inputs is None:
        inputs = {}
    if options is None:
        options = {}
    if labels is None:
        labels = {}

    for i in workflow_inputs:
        arg_type, _, result = parse_cmdline_arg(i)
        if arg_type == "input":
            inputs.update(result)
        elif arg_type == "option":
            options.update(result)
        elif arg_type == "label":
            labels.update(result)

    if job_name:
        labels[constants.OLIVER_JOB_NAME_KEY] = job_name

    if job_group:
        labels[constants.OLIVER_JOB_GROUP_KEY] = job_group

    if output_dir:
        options["final_workflow_outputs_dir"] = output_dir

    return json.dumps(inputs), json.dumps(options), json.dumps(labels)


def parse_cmdline_arg(arg: str) -> Tuple[str, str, Dict[str, Any]]:
    # We step through this list in order and check if it matches. In this scenario, its
    # important that `inputs` remains last as it matches the patterns before it
    # (including the prefix characters).
    patterns = [
        ("option", r"^\@(\S+)$"),
        ("label", r"^\%(\S+)$"),
        ("input", r"^(\S+)$"),
    ]

    arg_type = ""
    source_type = ""
    result = {}

    for _type, regex in patterns:
        arg_match = re.match(regex, arg)
        if arg_match:
            arg_type = _type
            suffix = arg_match.group(1)
            source_match = re.match(r"(\S+)=(\S+)", suffix)
            if source_match:
                # key value pairs
                source_type = "key-value pair"
                k, v = source_match.group(1), source_match.group(2)
                result[k] = v
                break
            if os.path.exists(suffix):
                # file
                source_type = "file"
                try:
                    with open(suffix, "rb") as f:
                        result = json.loads(f.read())
                # pylint: disable=broad-exception-caught
                except Exception:
                    errors.report(
                        f"Could not parse JSON for file: {arg}.",
                        fatal=True,
                        exitcode=errors.ERROR_INVALID_INPUT,
                    )
                break
                # pylint: enable=broad-exception-caught
            # source_type = "unknown"
            errors.report(
                f"Not a valid input: {arg}.",
                fatal=True,
                exitcode=errors.ERROR_INVALID_INPUT,
            )

    return arg_type, source_type, result
