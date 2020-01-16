from tabulate import tabulate
import re
import json

from .. import api

def call(args):
    cromwell = api.CromwellAPI(server=args['cromwell_server'], version=args['cromwell_api_version'])

    workflow_args = parse_workflow(args["workflow"])
    workflow_args['workflowInputs'], workflow_args['workflowOptions'], workflow_args['labels'] = parse_workflow_inputs_source(args["workflowInputs"])

    results = [cromwell.post_workflows(**workflow_args)]

    if len(results) > 0:
        print(tabulate([r.values() for r in results], headers=results[0].keys(), tablefmt=args['grid_style']))

def parse_workflow(workflow):
    # Source: https://stackoverflow.com/a/7160778
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(url_regex, workflow):
        return { 'workflowUrl': workflow }
    else:
        # Add a check for file else error
        pass
    return { 'workflowSource': workflow }

def parse_workflow_inputs_source(workflow_inputs):
    if len(workflow_inputs) == 1:
        try:
            workflowInputs_file = open(workflow_inputs[0], "rb")
            workflowInputs_text = workflowInputs_file.read()

            json.loads(workflowInputs_text)

            return workflowInputs_text, {}, {}
        except (ValueError, FileNotFoundError) as e:
            inputs, runtime_inputs, properties = parse_workflow_inputs(workflow_inputs)
            if len(inputs) == 0:
                raise RuntimeError(f"Unexpected input: {workflow_inputs[0]}")
    else:
        inputs, runtime_inputs, properties = parse_workflow_inputs(workflow_inputs)

    return json.dumps(inputs), json.dumps(runtime_inputs), json.dumps(properties)

def parse_workflow_inputs(workflow_inputs):
    input_regex = r"^([\w\-\/.]*)=([\w\-\/.]*)$"
    runtime_input_regex = r"^\@([\w\-\/.]*)=([\w\-\/.]*)$"
    property_regex = r"^\%([\w\-\/.]*)=([\w\-\/.]*)$"

    inputs, runtime_inputs, properties = {}, {}, {}
    for input in workflow_inputs:
        if re.match(input_regex, input):
            result = re.match(input_regex, input)
            inputs[result.group(1)] = result.group(2)
        elif re.match(runtime_input_regex, input):
            result = re.match(runtime_input_regex, input)
            runtime_inputs[result.group(1)] = result.group(2)
        elif re.match(property_regex, input):
            result = re.match(property_regex, input)
            properties[result.group(1)] = result.group(2)
        else:
            raise RuntimeError(f"Unknown input argument: {input}")

    return inputs, runtime_inputs, properties

def register_subparser(subparser):
    subcommand = subparser.add_parser("submit", help="Submit a workflow to the Cromwell server")
    subcommand.add_argument("workflow", help="The workflow to run (URL or file).")
    subcommand.add_argument("workflowInputs", nargs='+', help="JSON file of workflow inputs.")
    subcommand.add_argument("-j", help="Name of workflow.")
    subcommand.add_argument("-m", help="Default memory for workflow (in MB)")
    subcommand.add_argument("-n", help="Default number of cpus")
    subcommand.add_argument("--grid-style", help="Any valid `tablefmt` for python-tabulate.", default="fancy_grid")