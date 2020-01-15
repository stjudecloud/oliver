import pendulum

from tabulate import tabulate

from .. import api, utils

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'], version=args['cromwell_api_version'])
    metadata = cromwell.get_workflows_metadata(args['workflow-id'])
    if not "calls" in metadata:
        utils.print_error_as_table(metadata["status"], metadata["message"])
        return

    calls_that_match = []
    for name, call in metadata["calls"].items():
        for process in call:
            attempt = process["attempt"] if "attempt" in process else None
            shard = process["shardIndex"] if "shardIndex" in process else None

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt or not shard:
                raise RuntimeError("Expected key is missing! The code needs to be updated, please contact the author!")

            if attempt == args['attempt'] and shard == args['shard'] and name == args['call-name']:
                if "runtimeAttributes" not in process:
                    calls_that_match.append([{"Status": "Error", "Message": "Job did not have any runtime attributes set at the time of query."}])
                else:
                    calls_that_match.append([{"Key": k, "Value": v} for k, v in process['runtimeAttributes'].items()])

    if len(calls_that_match) > 0:
        if len(calls_that_match) > 1:
            raise RuntimeError("Multiple calls match this criteria!")
        calls = calls_that_match[0]
        print(tabulate([call.values() for call in calls], headers=calls[0].keys(), tablefmt=args['grid_style']))

def register_subparser(subparser):
    subcommand = subparser.add_parser("runtime", help="Get the runtime attributes used for a specific call.")
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument("call-name", help="Name of the call executed within the workflow.")
    subcommand.add_argument("--attempt", default=1, help="Attempt number for call.")
    subcommand.add_argument("--shard", default=-1, help="Shard number for call.")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")