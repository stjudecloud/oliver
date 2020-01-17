from tabulate import tabulate

from .. import api, utils


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    resp = cromwell.post_workflows_abort(args["workflow-id"])

    if not "id" in resp:
        utils.print_error_as_table(resp["status"], resp["message"])
        return

    results = [{"Workflow ID": resp["id"], "Status": resp["status"]}]

    if len(results) > 0:
        print(
            tabulate(
                [r.values() for r in results],
                headers=results[0].keys(),
                tablefmt=args["grid_style"],
            )
        )


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "kill", aliases=["k"], help="Kill a workflow running on a Cromwell server."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
