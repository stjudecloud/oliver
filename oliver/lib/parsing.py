import json
import os
import re

from typing import Dict, List
from urllib.parse import urlparse

from ..lib import constants, errors


def is_url(url_string: str) -> bool:
    try:
        scheme = urlparse(url_string).scheme
        return scheme == "http" or scheme == "https"
    except:
        return False


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
    elif os.path.isfile(workflow):
        return {"workflowSource": workflow}
    else:
        errors.report(
            "Workflow is not a valid file or URL!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def parse_workflow_inputs(
    workflow_inputs: List,
    job_name: str = None,
    job_group: str = None,
    output_dir: str = None,
    inputs: Dict = {},
    options: Dict = {},
    labels: Dict = {},
):
    for i in workflow_inputs:
        arg_type, source_type, result = parse_cmdline_arg(i)
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


def parse_cmdline_arg(arg):
    # We step through this list in order and check if it matches. In this scenario, its
    # important that `inputs` remains last as it matches the patterns before it
    # (including the prefix characters).
    patterns = [
        ("option", r"^\@(\S+)$"),
        ("label", r"^\%(\S+)$"),
        ("input", r"^(\S+)$"),
    ]

    arg_type = None
    source_type = None
    result = {}

    for type, regex in patterns:
        arg_match = re.match(regex, arg)
        if arg_match:
            arg_type = type
            suffix = arg_match.group(1)
            source_match = re.match(r"(\S+)=(\S+)", suffix)
            if source_match:
                # key value pairs
                source_type = "key-value pair"
                k, v = source_match.group(1), source_match.group(2)
                result[k] = v
                break
            elif os.path.exists(suffix):
                # file
                source_type = "file"
                try:
                    result = json.loads(open(suffix, "rb").read())
                except:
                    errors.report(
                        f"Could not parse JSON for file: {arg}.",
                        fatal=True,
                        exitcode=errors.ERROR_INVALID_INPUT,
                    )
                break
            else:
                source_type = "unknown"
                errors.report(
                    f"Not a valid input: {arg}.",
                    fatal=True,
                    exitcode=errors.ERROR_INVALID_INPUT,
                )

    return arg_type, source_type, result
