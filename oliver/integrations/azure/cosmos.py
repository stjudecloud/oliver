import os
import json

from typing import Any, Dict
from azure.cosmos import cosmos_client

from ...lib import api, reporting


class CosmosAPI:
    def __init__(self, cosmos_name: str = "", resource_group: str = "") -> None:
        stream = os.popen(
            "az cosmosdb show --name "
            + cosmos_name
            + " --resource-group "
            + resource_group
        )
        server = stream.read()
        server_obj = json.loads(server)
        self.server = server_obj["documentEndpoint"]
        stream = os.popen(
            "az cosmosdb keys list --name "
            + cosmos_name
            + " --resource-group "
            + resource_group
        )
        key = stream.read()
        key_obj = json.loads(key)
        self.key = key_obj["primaryMasterKey"]
        self.client = cosmos_client.CosmosClient(self.server, {"masterKey": self.key})

    def query(
        self, database_id: str = "TES", container_id: str = "Tasks", where: str = ""
    ) -> Any:
        # pylint: disable=no-member
        return self.client.QueryItems(  # type: ignore
            "dbs/" + database_id + "/colls/" + container_id,
            "SELECT * FROM " + container_id + " r " + where,
            {"enableCrossPartitionQuery": True},
        )
        # pylint: enable=no-member


async def call(
    args: Dict[str, Any], cromwell: api.CromwellAPI  # pylint: disable=unused-argument
) -> None:
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
            f = open(args["outfile"], mode="w", encoding="utf-8")
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
