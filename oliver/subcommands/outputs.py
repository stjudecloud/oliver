from tabulate import tabulate

from .. import api


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    outputs = cromwell.get_workflows_outputs(args["workflow-id"])
    results = [{"Output Name": k, "Location": v} for k, v in outputs["outputs"].items()]

    if "output_prefix" in args:
        for result in results:
            result["Location"] = args["output_prefix"] + result["Location"]

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
        "outputs", help="Find all reported outputs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
