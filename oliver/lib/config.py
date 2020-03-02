import json
import os

from typing import Any, Dict, Tuple

DEFAULT_LOCATION = "~/.oliver_config"
DEFAULT_CONFIG = {
    "cromwell_server": (str, "http://localhost:8000"),
    "cromwell_api_version": (str, "v1"),
    "batch_interval_mins": (int, 2),
}
REQUIRED_ARGS = ["cromwell_server", "cromwell_api_version", "batch_interval_mins"]


def get_default_config() -> Dict[str, Any]:
    default_config = {}
    for k, (_, v) in DEFAULT_CONFIG.items():
        default_config[k] = v
    return default_config


def read_config(config_file: str = DEFAULT_LOCATION) -> Any:
    path = os.path.expanduser(config_file)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def write_config(
    config: Dict[str, Tuple[Any, Any]], config_file: str = DEFAULT_LOCATION
) -> None:
    path = os.path.expanduser(config_file)
    for key in config.keys():
        if DEFAULT_CONFIG.get(key):
            (_type, _default) = DEFAULT_CONFIG[key]
            if not isinstance(config.get(key), _type):
                config[key] = _type(config.get(key))

    with open(path, "w") as f:
        json.dump(config, f, indent=4, sort_keys=True)
