import sys

from ..config import get_default_config, read_config, write_config


def call(args):
    config = read_config()

    if args["action"] == "list":
        for k, v in config.items():
            print(f"{k}\t{v}")
    elif args["action"] == "rm":
        if len(args["value"]) != 1:
            raise RuntimeError('"rm" must take one value as "<key>".')
        [key] = args["value"]
        if key in config:
            del config[key]
        write_config(config)
    elif args["action"] == "get":
        if len(args["value"]) != 1:
            raise RuntimeError('"get" must take one value as "<key>".')
        [key] = args["value"]
        if key not in config:
            raise RuntimeError(f'"{key}" not in config.')
        print(config[key])
    elif args["action"] == "set":
        if len(args["value"]) != 2:
            raise RuntimeError('"set" must take two values as "<key> <value>".')
        [key, value] = args["value"]
        config[key] = value
        write_config(config)
    else:
        raise RuntimeError(f"Unhandled action: {args['actions']}")


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "config", help="Set or get a single config value from Oliver."
    )
    subcommand.add_argument(
        "action",
        choices=["list", "rm", "get", "set"],
        help="Action to take on the config.",
    )
    subcommand.add_argument(
        "value", nargs="*", help='"<key>" for "get" or "<key> <value>" for "set".'
    )
