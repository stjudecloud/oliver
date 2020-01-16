import pendulum
from tabulate import tabulate

from .. import api

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'], version=args['cromwell_api_version'])

    if args['show_all_statuses']:
        statuses = None
    elif args['show_running_statuses'] or args['show_failed_statuses'] or args['show_succeeded_statuses']:
        statuses = []
        if args['show_running_statuses']:
            statuses.append("Running")

        if args['show_failed_statuses']:
            statuses.append("Failed")

        if args['show_succeeded_statuses']:
            statuses.append("Succeeded")
    else:
        statuses = ["Running"]
        

    workflows = cromwell.get_workflows_query(includeSubworkflows=False, statuses=statuses)

    results = [
        {
            "Workflow ID": w["id"] if "id" in w else "", 
            "Workflow Name": w["name"] if "name" in w else "", 
            "Status": w["status"] if "status" in w else "",
            "Start": pendulum.parse(w["start"]).to_day_datetime_string() if "start" in w else ""
        } for w in workflows]

    if len(results) > 0:
        print(tabulate([r.values() for r in results], headers=results[0].keys(), tablefmt=args['grid_style']))

def register_subparser(subparser):
    subcommand = subparser.add_parser("status", help="Report various statistics about a running Cromwell server.")
    subcommand.add_argument("-a", "--all", dest="show_all_statuses", help="Show jobs in all states, not just 'Running' jobs.", default=False, action="store_true")
    subcommand.add_argument("-r", "--running", dest="show_running_statuses", help="Show jobs in the 'Running' state.", default=False, action="store_true")
    subcommand.add_argument("-f", "--failed", dest="show_failed_statuses", help="Show jobs in the 'Failed' state.", default=False, action="store_true")
    subcommand.add_argument("-s", "--succeeded", dest="show_succeeded_statuses", help="Show jobs in the 'Succeeded' state.", default=False, action="store_true")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")