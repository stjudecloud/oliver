import azure.batch._batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

import json
import os
import re
import sys

from .. import reporting


class AzureBatchAPI:
    def __init__(self, batch_name="", resource_group=""):
        stream = os.popen(
            "az batch account keys list --name "
            + batch_name
            + " --resource-group "
            + resource_group
        )
        key = stream.read()
        key = json.loads(key)
        self.key = key["primary"]
        stream = os.popen(
            "az batch account show --name "
            + batch_name
            + " --resource-group "
            + resource_group
        )
        url = stream.read()
        url = json.loads(url)
        self.url = "https://" + url["accountEndpoint"]

        self.credentials = batchauth.SharedKeyCredentials(batch_name, self.key)

        self.client = batch.BatchServiceClient(self.credentials, batch_url=self.url)


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    print("hi")

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
