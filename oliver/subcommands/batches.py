"""Explore batches of jobs submitted to Cromwell."""

import argparse

from collections import defaultdict
from logzero import logger
from typing import Dict

from ..lib import (
    api,
    args as _args,
    constants,
    oliver,
    reporting,
    workflows as _workflows,
)

SUBCOMMAND_NAME = "batches"
SUBCOMMAND_ALIASES = ["b"]


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    batches = True
    relative = None

    if args.get("batches_relative"):
        batches = args.get("batches_relative")
        relative = True
    elif args.get("batches_absolute"):
        batches = args.get("batches_absolute")
        relative = False

    workflows = await _workflows.get_workflows(
        cromwell,
        batches=batches,
        relative_batching=relative,
        batch_interval_mins=args.get("batch_interval_mins"),
    )

    aggregation = defaultdict(list)
    for w in workflows:
        aggregation[w.get("batch")].append(w)

    results = []

    if args.get("show_oliver_job_groups"):
        logger.warn(
            "You specified you'd like to see job group names. "
            + "This significantly increases runtime due to the need to query metadata about each workflow. "
            + "This may take a while!"
        )

    for batch_num, batch_workflows in aggregation.items():
        r = {"Batch": batch_num, "# of Jobs": len(batch_workflows)}

        # workflow statuses
        statuses = defaultdict(int)
        for status in [w.get("status") for w in batch_workflows]:
            statuses[status] += 1
        r["Statuses"] = ", ".join(
            sorted([f"{key} ({statuses[key]})" for key in statuses.keys()])
        )

        # job groups
        if args.get("show_oliver_job_groups"):
            metadatas = {
                w.get("id"): await cromwell.get_workflows_metadata(w.get("id"))
                for w in batch_workflows
            }
            r["Job Groups"] = ", ".join(
                list(
                    set(
                        [
                            oliver.get_oliver_group(metadatas.get(x.get("id")))
                            for x in batch_workflows
                        ]
                    )
                )
            )

        # start time
        _sorted_workflows = sorted(batch_workflows, key=lambda x: x["start"])
        earliest_start_time = min([x.get("start") for x in _sorted_workflows])
        r["Start Time"] = reporting.localize_date(earliest_start_time)

        # end time
        end_times = [x.get("end") for x in _sorted_workflows]
        if None in end_times:
            r["End Time"] = "Still running"
        else:
            latest_end_time = max(end_times)
            r["End Time"] = reporting.localize_date(latest_end_time)

        results.append(r)

    reporting.print_dicts_as_table(results)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        SUBCOMMAND_NAME, aliases=SUBCOMMAND_ALIASES, help=__doc__.split("\n")[0]
    )

    _args.add_batches_group(subcommand)
    subcommand.add_argument(
        "-g",
        "--show-oliver-job-groups",
        help="Show oliver job groups per batch (dramatically increases runtime).",
        default=False,
        action="store_true",
    )

    subcommand.set_defaults(func=call)
    return subcommand
