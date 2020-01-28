import argparse
import json
import os

from typing import Dict

from .. import azbatch, reporting
import azure.batch.models as batchmodels
import re


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    client = azbatch.AzureBatchAPI(
        batch_name=args["batch_account_name"],
        resource_group=args["azure_resource_group"],
    )

    results = []
    opts = batchmodels.JobListOptions(filter="state ne 'completed'")
    for job in client.client.job.list(opts):
        if job.state != "completed":
            top_wf = ""
            if job.job_preparation_task:
                regex = re.compile("cromwell-executions")
                cmd = regex.split(job.job_preparation_task.command_line)[1]
                regex = re.compile("/")
                top_wf = regex.split(cmd)[2]
            # print(job.id, job.state, job.execution_info.pool_id, top_wf)
            results.append(
                {
                    "Job ID": job.id,
                    "State": job.state,
                    "Pool ID": job.execution_info.pool_id,
                    "Top-level workflow ID": top_wf,
                }
            )
    reporting.print_dicts_as_table(results)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser("azbatch", help="Get azure batch information.")
    # subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    # )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
