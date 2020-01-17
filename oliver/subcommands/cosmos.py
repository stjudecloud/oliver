import argparse
import json
import os

from typing import Dict

from .. import cosmos, reporting


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    client = cosmos.CosmosAPI(
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
            if "logs" in item and item["logs"] is not None:
                log = item["logs"][0]["system_logs"][0]
            size = ""
            if "resource" in item: 
                size = item["resources"]["vm_info"]["vm_size"]

            res.append(
                {
                    "Call Name": item["name"],
                    "State": item["state"],
                    "VM": size,
                    "Log": log,
                }
            )

        reporting.print_dicts_as_table(res)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "cosmos", help="Get cosmos DB entries for a workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--failures", action="store_true", help="Return only failed tasks"
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.add_argument(
        "--json",
        help="Print the full JSON objects for Cosmos records",
        action="store_true",
    )
    subcommand.add_argument("-o", "--outfile", help="File to save JSON records to")
    subcommand.set_defaults(func=call)
