import azure.batch._batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

import json
import os
import sys


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
