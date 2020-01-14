import json
import os

DEFAULT_LOCATION="~/.oliver_config"

def read_config(config_file=DEFAULT_LOCATION, default={}):
    path = os.path.expanduser(config_file)

    if not os.path.exists(path):
        return default
    
    with open(config_file, "r") as f:
        return json.load(f)


def write_config(config, config_file=DEFAULT_LOCATION):
    path = os.path.expanduser(config_file)
    with open(path, "w") as f:
        json.dump(config, f, indent=4, sort_keys=True)