import argparse
import pendulum

from typing import Dict

from ..lib import api, constants, errors, reporting, utils


def report_failure(failure, indent, step=2, offset=2):
    print((" " * offset) + "| " + (" " * indent) + failure["message"])
    for f in failure["causedBy"]:
        report_failure(f, indent + step)


async def call(args: Dict, cromwell: api.CromwellAPI):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    metadata = await cromwell.get_workflows_metadata(args["workflow-id"])

    oliver_job_name = metadata.get("labels", {}).get(constants.OLIVER_JOB_NAME_KEY, "")
    oliver_group_name = metadata.get("labels", {}).get(
        constants.OLIVER_JOB_GROUP_KEY, ""
    )

    workflow_name = metadata.get("workflowName", "")
    workflow_id = metadata.get("id", "")
    workflow_language = metadata.get("actualWorkflowLanguage", "")

    if workflow_language:
        workflow_language += " " + metadata.get("actualWorkflowLanguageVersion", "")

    workflow_submission_date = metadata.get("submission")
    workflow_start_date = metadata.get("start")
    workflow_end_date = metadata.get("end")
    workflow_start_to_report = ""
    workflow_duration_to_report = ""

    if workflow_start_date:
        workflow_start_to_report = reporting.localize_date(workflow_start_date)
        workflow_duration_to_report = (
            reporting.duration_to_text(
                pendulum.now() - pendulum.parse(workflow_start_date)
            )
            + " (In progress)"
        )

    if workflow_start_date and workflow_end_date:
        workflow_duration_to_report = reporting.duration_to_text(
            pendulum.parse(workflow_end_date) - pendulum.parse(workflow_start_date)
        )

    calls = []
    for name, call in metadata["calls"].items():
        for process in call:
            attempt = process.get("attempt")
            shard = process.get("shardIndex")

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt or not shard:
                errors.report(
                    "Expected key is missing! The code needs to be updated, please contact the author!",
                    fatal=True,
                    exitcode=errors.ERROR_UNEXPECTED_RESPONSE,
                )

            call_start_date = process.get("start")
            call_end_date = process.get("end")

            call_duration_to_report = ""

            if call_start_date:
                call_duration_to_report = (
                    reporting.duration_to_text(
                        pendulum.now() - pendulum.parse(call_start_date)
                    )
                    + " (In progress)"
                )

            if call_start_date and call_end_date:
                call_duration_to_report = reporting.duration_to_text(
                    pendulum.parse(call_end_date) - pendulum.parse(call_start_date)
                )

            result = {
                "Call Name": name,
                "Attempt": attempt,
                "Shard": shard,
                "Status": process.get("executionStatus", ""),
                "Start": call_start_date,
                "Duration": call_duration_to_report,
            }

            calls.append(result)

    calls = sorted(calls, key=lambda k: k["Start"])

    for call in calls:
        call["Start"] = reporting.localize_date(call_start_date)

    if oliver_job_name:
        print(f"Job Name: {oliver_job_name}")
    if oliver_group_name:
        print(f"Group Name: {oliver_group_name}")
    print(f"Workflow Name: {workflow_name}")
    print(f"Workflow ID: {workflow_id}")
    print(f"Workflow Version: {workflow_language}")
    print(f"Submission: {reporting.localize_date(workflow_submission_date)}")
    print(f"Start: {workflow_start_to_report}")
    print(f"Duration: {workflow_duration_to_report}")

    # Show labels if they exist
    if args["show_labels"]:
        if not metadata.get("labels"):
            print("Labels: None")
        else:
            print("Labels:")
            print()
            for k, v in metadata["labels"].items():
                print(f"  {k} = {v}")
            print()

    # Show failures if they exist
    if len(metadata.get("failures", [])) > 0:
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
    return subcommand
