import argparse
import pendulum

from typing import Dict

from .. import api, errors, reporting, utils


def report_failure(failure, indent, step=2, offset=2):
    print((" " * offset) + "| " + (" " * indent) + failure["message"])
    for f in failure["causedBy"]:
        report_failure(f, indent + step)


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    metadata = cromwell.get_workflows_metadata(args["workflow-id"])

    workflow_name = metadata["workflowName"] if "workflowName" in metadata else ""
    workflow_id = metadata["id"] if "id" in metadata else ""
    workflow_language = (
        metadata["actualWorkflowLanguage"]
        if "actualWorkflowLanguage" in metadata
        else ""
    )
    if workflow_language:
        workflow_language += (
            " " + metadata["actualWorkflowLanguageVersion"]
            if "actualWorkflowLanguageVersion" in metadata
            else ""
        )
    workflow_submission = pendulum.parse(
        metadata["submission"] if "submission" in metadata else ""
    ).to_day_datetime_string()

    workflow_start_date = (
        pendulum.parse(metadata["start"]) if "start" in metadata else None
    )
    workflow_end_date = pendulum.parse(metadata["end"]) if "end" in metadata else None
    workflow_start = ""
    workflow_duration = ""

    if workflow_start_date:
        workflow_start = workflow_start_date.to_day_datetime_string()
        workflow_duration = (
            utils.duration_to_text(pendulum.now() - workflow_start_date)
            + " (In progress)"
        )

    if workflow_start_date and workflow_end_date:
        workflow_duration = utils.duration_to_text(
            workflow_end_date - workflow_start_date
        )

    calls = []
    for name, call in metadata["calls"].items():
        for process in call:
            attempt = process["attempt"] if "attempt" in process else None
            shard = process["shardIndex"] if "shardIndex" in process else None

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt or not shard:
                errors.report(
                    "Expected key is missing! The code needs to be updated, please contact the author!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )

            call_start_date = (
                pendulum.parse(process["start"]) if "start" in process else None
            )
            call_end_date = pendulum.parse(process["end"]) if "end" in process else None

            call_start = ""
            duration = ""

            if call_start_date:
                duration = (
                    utils.duration_to_text(pendulum.now() - call_start_date)
                    + " (In progress)"
                )

            if call_start_date and call_end_date:
                duration = utils.duration_to_text(call_end_date - call_start_date)

            result = {
                "Call Name": name,
                "Attempt": attempt,
                "Shard": shard,
                "Status": process["executionStatus"]
                if "executionStatus" in process
                else "",
                "Start": call_start_date,
                "Duration": duration,
            }

            calls.append(result)

    calls = sorted(calls, key=lambda k: k["Start"])

    for call in calls:
        call["Start"] = call["Start"].to_day_datetime_string()

    print(f"Workflow Name: {workflow_name}")
    print(f"Workflow ID: {workflow_id}")
    print(f"Workflow Version: {workflow_language}")
    print(f"Submission: {workflow_submission}")
    print(f"Duration: {workflow_duration}")

    # Show labels if they exist
    if args["show_labels"]:
        if "labels" not in metadata:
            print("Labels: None")
        else:
            print("Labels:")
            print()
            for k, v in metadata["labels"].items():
                print(f"  {k} = {v}")
            print()

    # Show failures if they exist
    if "failures" in metadata and len(metadata["failures"]) > 0:
        print("Failures:")
        print()
        for i, failure in enumerate(metadata["failures"]):
            print(f"  == Failure {i + 1} ==")
            report_failure(failure, 0, offset=2)
            print()

    if len(calls) > 0:
        print()
        reporting.print_dicts_as_table(calls)


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "inspect", aliases=["i"], help="Describe the state of a Cromwell workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "-l",
        "--show-labels",
        help="Show labels associated with the workflow",
        default=False,
        action="store_true",
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
