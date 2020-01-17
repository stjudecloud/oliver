from .. import api, reporting


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    metadata = cromwell.get_workflows_metadata(args["workflow-id"])

    workflowUrl = (
        metadata["submittedFiles"]["workflowUrl"]
        if "submittedFiles" in metadata and "workflowUrl" in metadata["submittedFiles"]
        else {}
    )
    workflowInputs = (
        metadata["submittedFiles"]["inputs"]
        if "submittedFiles" in metadata and "inputs" in metadata["submittedFiles"]
        else {}
    )
    workflowOptions = (
        metadata["submittedFiles"]["options"]
        if "submittedFiles" in metadata and "options" in metadata["submittedFiles"]
        else {}
    )
    labels = (
        metadata["submittedFiles"]["labels"]
        if "submittedFiles" in metadata and "labels" in metadata["submittedFiles"]
        else {}
    )

    results = [
        cromwell.post_workflows(
            workflowUrl=workflowUrl,
            workflowInputs=workflowInputs,
            workflowOptions=workflowOptions,
            labels=labels,
        )
    ]

    reporting.print_dicts_as_table(results)


def register_subparser(subparser):
    subcommand = subparser.add_parser(
        "retry", aliases=["re"], help="Resubmit a workflow with the same parameters."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
