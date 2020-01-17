import json

from tabulate import tabulate

from .. import api, errors


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    metadata = cromwell.get_workflows_metadata(args["workflow-id"])

    if not "submittedFiles" in metadata or "inputs" not in metadata["submittedFiles"]:
        errors.report(
            "Could not retrieve inputs!",
            fatal=True,
            exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
        )

    print(json.dumps(json.loads(metadata["submittedFiles"]["inputs"]), indent=2))


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "inputs", help="Find all reported outputs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
