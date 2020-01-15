import pendulum

from tabulate import tabulate

from .. import api, utils

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'], version=args['cromwell_api_version'])
    metadata = cromwell.get_workflows_metadata(args['workflow-id'])

    workflow_name = metadata['workflowName'] if 'workflowName' in metadata else ''
    workflow_id = metadata['id'] if 'id' in metadata else ''
    workflow_language = metadata['actualWorkflowLanguage'] if 'actualWorkflowLanguage' in metadata else ''
    if workflow_language:
        workflow_language += " " + metadata['actualWorkflowLanguageVersion'] if 'actualWorkflowLanguageVersion' in metadata else ''
    workflow_labels = ', '.join(metadata['labels'] if 'labels' in metadata else [])
    workflow_submission = metadata['submission'] if "submission" in metadata else ""

    workflow_start_date = pendulum.parse(metadata["start"]) if "start" in metadata else None
    workflow_end_date = pendulum.parse(metadata["end"]) if "end" in metadata else None
    workflow_start = ""
    workflow_duration = "Not Started"

    if workflow_start_date:
        workflow_start = workflow_start_date.diff_for_humans()
        workflow_duration = "In Progress"

    if workflow_start_date and workflow_end_date:
        workflow_duration = utils.duration_to_text(workflow_end_date - workflow_start_date)

    calls = []
    for name, call in metadata["calls"].items():
        for process in call:
            attempt = process["attempt"] if "attempt" in process else None
            shard = process["shardIndex"] if "shardIndex" in process else None

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt or not shard:
                raise RuntimeError("Expected key is missing! The code needs to be updated, please contact the author!")

            call_start_date = pendulum.parse(process["start"]) if "start" in process else None
            call_end_date = pendulum.parse(process["end"]) if "end" in process else None

            call_start = ""
            duration = "Not Started"

            if call_start_date:
                call_start = call_start_date.diff_for_humans()
                duration = "In Progress"

            if call_start_date and call_end_date:
                duration = utils.duration_to_text(call_end_date - call_start_date)

            result = {
                "Call Name": name,
                "Attempt": attempt,
                "Shard": shard,
                "Status": process["executionStatus"] if "executionStatus" in process else "",
                "Start": call_start,
                "Duration": duration
            }
            
            calls.append(result)

    print()
    print(f"Workflow Name: {workflow_name}")
    print(f"Workflow ID: {workflow_id}")
    print(f"Workflow Version: {workflow_language}")
    print(f"Labels: {workflow_labels}")
    print(f"Submission: {workflow_submission}")
    print(f"Duration: {workflow_duration}")
    print()

    if len(calls) > 0:
        print(tabulate([call.values() for call in calls], headers=calls[0].keys(), tablefmt=args['grid_style']))

def register_subparser(subparser):
    subcommand = subparser.add_parser("inspect", help="Inspect a workflow.")
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")