import json
import os

DEFAULT_LOCATION = "~/.oliver_config"
DEFAULT_CONFIG = {
    "cromwell_server": "http://localhost:8000",
    "cromwell_api_version": "v1",
    "batch_interval_mins": 2,
}


def get_default_config():
    return DEFAULT_CONFIG


def read_config(config_file=DEFAULT_LOCATION):
    path = os.path.expanduser(config_file)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def write_config(config, config_file=DEFAULT_LOCATION):
    path = os.path.expanduser(config_file)
    with open(path, "w") as f:
        json.dump(config, f, indent=4, sort_keys=True)
