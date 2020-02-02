import argparse
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import json
import os

from typing import Dict

from ...lib import api, reporting


class CosmosAPI:
    def __init__(self, cosmos_name="", resource_group=""):
        stream = os.popen(
            "az cosmosdb show --name "
            + cosmos_name
            + " --resource-group "
            + resource_group
        )
        server = stream.read()
        server = json.loads(server)
        self.server = server["documentEndpoint"]
        stream = os.popen(
            "az cosmosdb keys list --name "
            + cosmos_name
            + " --resource-group "
            + resource_group
        )
        key = stream.read()
        key = json.loads(key)
        self.key = key["primaryMasterKey"]
        self.client = cosmos_client.CosmosClient(self.server, {"masterKey": self.key})

    def _api_call(self, route, params={}, data=None, files=None, method="GET"):
        url = urljoin(self.server, route).format(version=self.version)

        response = request(
            method, url, headers=self.headers, params=params, data=data, files=files
        )
        return response.status_code, json.loads(response.content)

    def query(self, database_id="TES", container_id="Tasks", where=""):
        return self.client.QueryItems(
            "dbs/" + database_id + "/colls/" + container_id,
            "SELECT * FROM " + container_id + " r " + where,
            {"enableCrossPartitionQuery": True},
        )


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    client = CosmosAPI(
        cosmos_name=args["cosmos_account_name"],
        resource_group=args["azure_resource_group"],
    )
    workflow_prefix = args["workflow-id"][0:8]
    res = []

    query = 'WHERE STARTSWITH(r.description, "' + workflow_prefix + '")'
    if args["failures"]:
        query += " AND r.state = 'SYSTEM_ERROR'"
    results = client.query("TES", "Tasks", query)

    if args["json"]:
        output = ""
        for item in results:
            output += json.dumps(item, indent=True)
        if args["outfile"] and args["outfile"] is not None:
            f = open(args["outfile"], "w")
            f.write(output)
            f.close()
        else:
            print(output)
    else:
        for item in results:
            log = ""
            if item.get("logs"):
                log = item.get("logs", [])[0]["system_logs"][0]
            size = ""
            if item.get("resources"):
                vm_info = item.get("resources", {}).get("vm_info", {})
                size = "<not set>"
                if vm_info:
                    size = vm_info.get("vm_size", "<not set>")

            res.append(
                {
                    "Call Name": item["name"],
                    "State": item["state"],
                    "VM": size,
                    "Log": log,
                }
            )

        reporting.print_dicts_as_table(res)
