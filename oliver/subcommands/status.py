import pendulum
from tabulate import tabulate

from .. import api

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'])

    statuses = None
    if not args['show_all_statuses']:
        statuses = ["Running"]

    workflows = cromwell.get_workflows_query(includeSubworkflows=False, statuses=statuses)

    results = [(
        w["id"] if "id" in w else "", 
        w["name"] if "name" in w else "", 
        w["status"] if "status" in w else "",
        pendulum.parse(w["start"]).diff_for_humans() if "start" in w else "") for w in workflows]
    print(tabulate(results, headers=["ID", "Name", "Status", "Start"], tablefmt=args['grid_style']))

def register_subparser(subparser):
    subcommand = subparser.add_parser("status", help="Report various statistics about a running Cromwell server.")
    subcommand.add_argument("-a", "--all", dest="show_all_statuses", help="Show jobs in all states, not just 'Running' jobs.", default=False, action="store_true")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")