from tabulate import tabulate

from .. import api

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'], version=args['cromwell_api_version'])

    workflowUrl = args['workflowUrl']
    workflowInputs = args['workflowInputs']

    results = [cromwell.post_workflows(workflowUrl, workflowInputs)]

    if len(results) > 0:
        print(tabulate([r.values() for r in results], headers=results[0].keys(), tablefmt=args['grid_style']))


def register_subparser(subparser):
    subcommand = subparser.add_parser("submit", help="Submit a workflow to the Cromwell server")
    subcommand.add_argument("--workflowUrl", help="The URL to the workflow to run.")
    subcommand.add_argument("--workflowInputs", help="JSON file of workflow inputs.")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")