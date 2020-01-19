from typing import Dict, Optional
from urllib.parse import urlparse

from . import constants, reporting


def duration_to_text(duration):
    parts = []
    attrs = ["years", "months", "days", "hours", "minutes", "remaining_seconds"]
    for attr in attrs:
        if hasattr(duration, attr):
            value = getattr(duration, attr)
            # hack to get the correct formatting out. Pendulum appears to inconsistently
            # name its methods: https://github.com/sdispater/pendulum/blob/master/pendulum/duration.py#L163
            if attr == "remaining_seconds":
                attr = "seconds"

            if value > 0:
                parts.append(f"{value} {attr}")

    return " ".join(parts)


def is_url(url_string: str) -> bool:
    return (
        urlparse(url_string).scheme == "http" or urlparse(url_string).scheme == "https"
    )


def get_oliver_name(workflow: Dict) -> Optional[str]:
    """Return the name Oliver has given the workflow in properties if it exists.
    
    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if "labels" in workflow and constants.OLIVER_JOB_NAME_KEY in workflow["labels"]:
        return workflow["labels"][constants.OLIVER_JOB_NAME_KEY]

    return None


def get_oliver_group(workflow: Dict) -> Optional[str]:
    """Return the group name Oliver has given the workflow in properties if it exists.
    
    Args:
        workflow (Dict): Workflow returned from the API call.
    """

    if "labels" in workflow and constants.OLIVER_JOB_GROUP_KEY in workflow["labels"]:
        return workflow["labels"][constants.OLIVER_JOB_GROUP_KEY]

    return None
