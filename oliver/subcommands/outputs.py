from .. import api, reporting


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    outputs = cromwell.get_workflows_outputs(args["workflow-id"])
    results = [{"Output Name": k, "Location": v} for k, v in outputs["outputs"].items()]

    if "output_prefix" in args:
        for result in results:
            result["Location"] = args["output_prefix"] + result["Location"]

    reporting.print_dicts_as_table(results)


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "outputs", aliases=["o"], help="Find all reported outputs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
