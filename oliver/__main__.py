#!/usr/bin/env python3
import asyncio
import argparse
import logging
import sys

from typing import Any, cast, Dict
import logzero

from oliver.lib import api, args as _args, errors, config as _config
from oliver.subcommands import (
    abort,
    aggregate,
    aws,
    azure,
    batches,
    configure,
    config,
    inputs,
    inspect,
    logs,
    outputs,
    retry,
    runtime,
    status,
    submit,
)

SUBCOMMANDS = {
    "abort": abort,
    "aggregate": aggregate,
    "aws": aws,
    "azure": azure,
    "batches": batches,
    "configure": configure,
    "config": config,
    "inputs": inputs,
    "inspect": inspect,
    "logs": logs,
    "outputs": outputs,
    "retry": retry,
    "runtime": runtime,
    "status": status,
    "submit": submit,
}


def ensure_required_args(args: Dict[str, Any]) -> None:
    missing_args = []

    for a in _config.REQUIRED_ARGS:
        if not a in args or not args[a]:
            missing_args.append(a)

    if missing_args:
        errors.report(
            f"The following required arguments are missing: {', '.join(missing_args)}!\n\n"
            + "We recommend you run 'oliver configure' to ensure all required arguments are cached in the oliver configuration file.\n"
            + "If you choose not to do this, you will need to pass their respective flags on the command line.",
            fatal=True,
            exitcode=errors.ERROR_PRECAUTION,
        )


async def run() -> None:
    parser = argparse.ArgumentParser(
        description="An opinionated Cromwell orchestration system."
    )

    # Common arguments
    parser.add_argument("--cromwell-server", help="Cromwell host location.")
    parser.add_argument("--cromwell-api-version", help="Cromwell API version.")
    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Force running even with missing parameters.",
    )
    _args.add_batches_interval_arg(parser)
    _args.add_loglevel_group(parser)

    # Subparsers
    subparsers = parser.add_subparsers(dest="subcommand")

    for name, module in SUBCOMMANDS.items():
        if not hasattr(module, "register_subparser") or not hasattr(module, "call"):
            errors.report(
                f"Subcommand does not have required methods: {name}!",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
            )
        subparser = cast(Any, module).register_subparser(subparsers)
        _args.add_loglevel_group(subparser)

    args = vars(parser.parse_args())

    for k, v in _config.read_config().items():
        # if the user has not supplied a parameter on the command line, add the default
        # value from the config to `args`.
        if not k in args or not args[k]:
            args[k] = v

    if not args.get("force") and args.get("subcommand") not in ["configure", "config"]:
        ensure_required_args(args)

    if not args.get("subcommand"):
        parser.print_help()
        sys.exit(1)

    logzero.loglevel(logging.WARN)
    if args.get("verbose"):
        logzero.loglevel(logging.INFO)
    elif args.get("debug"):
        logzero.loglevel(logging.DEBUG)

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )

    try:
        await args["func"](args, cromwell)
    finally:
        await cromwell.close()


def main() -> None:
    asyncio.run(run())
