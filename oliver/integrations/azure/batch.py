import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.batch import BatchManagementClient

import json
import os
import re
import sys

from typing import Dict

from ...lib import reporting


class AzureBatchAPI:
    def __init__(self, batch_name="", resource_group=""):
        mgmtclient = get_client_from_cli_profile(BatchManagementClient)
        key = mgmtclient.batch_account.get_keys(resource_group, batch_name).primary
        uri = mgmtclient.batch_account.get(resource_group, batch_name).account_endpoint
        uri = "https://" + uri
        self.credentials = batchauth.SharedKeyCredentials(batch_name, key)
        self.client = batch.BatchServiceClient(self.credentials, base_url=uri)


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    client = AzureBatchAPI(
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
