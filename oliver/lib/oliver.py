from typing import Any, cast, Dict

from . import constants


def get_oliver_name(workflow: Dict[str, Any]) -> str:
    """Return the name Oliver has given the workflow in properties if it exists.

    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if "labels" in workflow:
        workflow_labels = cast(Dict[str, str], workflow["labels"])

        if constants.OLIVER_JOB_NAME_KEY in workflow_labels:
            return workflow_labels[constants.OLIVER_JOB_NAME_KEY]

    return "<not set>"


def get_oliver_group(workflow: Dict[str, Any]) -> str:
    """Return the group name Oliver has given the workflow in properties if it exists.

    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if "labels" in workflow:
        workflow_labels = cast(Dict[str, str], workflow["labels"])

        if constants.OLIVER_JOB_GROUP_KEY in workflow_labels:
            return workflow_labels[constants.OLIVER_JOB_GROUP_KEY]

    return "<not set>"
