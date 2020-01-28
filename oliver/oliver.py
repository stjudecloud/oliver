from typing import Dict, Optional

from . import constants


def get_oliver_name(workflow: Dict) -> Optional[str]:
    """Return the name Oliver has given the workflow in properties if it exists.
    
    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if constants.OLIVER_JOB_NAME_KEY in workflow.get("labels", {}):
        return workflow.get("labels", {}).get(constants.OLIVER_JOB_NAME_KEY)

    return "<not set>"


def get_oliver_group(workflow: Dict) -> Optional[str]:
    """Return the group name Oliver has given the workflow in properties if it exists.
    
    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if constants.OLIVER_JOB_GROUP_KEY in workflow.get("labels", {}):
        return workflow.get("labels", {}).get(constants.OLIVER_JOB_GROUP_KEY)

    return "<not set>"
