import argparse
import re
import json
import os

from typing import Dict

from .. import api, constants, errors, reporting, utils


def call(args: Dict):
    """Execute the subcommand.
    
    Args:
        args (Dict): Arguments parsed from the command line.
    """

    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )

    workflow_args = parse_workflow(args["workflow"])
    (
        workflow_args["workflowInputs"],
        workflow_args["workflowOptions"],
        workflow_args["labels"],
    ) = prepare_workflow_inputs(args)

    results = [cromwell.post_workflows(**workflow_args)]
    reporting.print_dicts_as_table(results, args["grid_style"])


def parse_workflow(workflow: str) -> Dict[str, str]:
    """Determine if the workflow is a source file or URL.

    Args:
        workflow (str): Workflow source input from the command line.

    Returns:
        Dict[str, str]: Arguments for API call which consists of either
        workflowSource or workflowUrl, but not both.
    """
    if utils.is_url(workflow):
        return {"workflowUrl": workflow}
    elif os.path.isfile(workflow):
        return {"workflowSource": workflow}
    else:
        errors.report(
            "Workflow is not a valid file or URL!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )


def prepare_workflow_inputs(args):

    inputs, options, labels = {}, {}, {}

    for i in args["workflowInputs"]:
        arg_type, source_type, result = parse_cmdline_arg(i)
        if arg_type == "input":
            inputs.update(result)
        elif arg_type == "option":
            options.update(result)
        elif arg_type == "label":
            labels.update(result)

    if "job_name" in args and args["job_name"]:
        labels[constants.OLIVER_JOB_NAME_KEY] = args["job_name"]

    if "job_group" in args and args["job_group"]:
        labels[constants.OLIVER_JOB_GROUP_KEY] = args["job_group"]

    return json.dumps(inputs), json.dumps(options), json.dumps(labels)


def parse_cmdline_arg(arg):
    # We step through this list in order and check if it matches. In this scenario, its
    # important that `inputs` remains last as it matches the patterns before it
    # (including the prefix characters).
    patterns = [
        ("option", r"^\@(\S+)$"),
        ("label", r"^\%(\S+)$"),
        ("input", r"^(\S+)$"),
    ]

    arg_type = None
    source_type = None
    result = {}

    for type, regex in patterns:
        arg_match = re.match(regex, arg)
        if arg_match:
            arg_type = type
            suffix = arg_match.group(1)
            source_match = re.match(r"(\S+)=(\S+)", suffix)
            if source_match:
                # key value pairs
                source_type = "key-value pair"
                k, v = source_match.group(1), source_match.group(2)
                result[k] = v
                break
            elif os.path.exists(suffix):
                # file
                source_type = "file"
                try:
                    result = json.loads(open(suffix, "rb").read())
                except:
                    errors.report(
                        f"Could not parse JSON for file: {arg}.",
                        fatal=True,
                        exitcode=errors.ERROR_INVALID_INPUT,
                    )
                break
            else:
                source_type = "unknown"
                errors.report(
                    f"Not a valid input: {arg}.",
                    fatal=True,
                    exitcode=errors.ERROR_INVALID_INPUT,
                )

    return arg_type, source_type, result


def register_subparser(subparser: argparse._SubParsersAction):
    """Registers a subparser for the current command.
    
    Args:
        subparser (argparse._SubParsersAction): Subparsers action.
    """

    subcommand = subparser.add_parser(
        "submit", aliases=["su"], help="Submit a workflow to the Cromwell server."
    )
    subcommand.add_argument("workflow", help="The workflow to run (URL or file).")
    subcommand.add_argument(
        "workflowInputs", nargs="+", help="JSON file of workflow inputs."
    )
    subcommand.add_argument(
        "-g", "--job-group", help="Job Group", type=str, default=None
    )
    subcommand.add_argument("-j", "--job-name", help="Job Name", type=str, default=None)
    subcommand.add_argument("-m", help="Default memory for workflow (in MB)")
    subcommand.add_argument("-n", help="Default number of cpus")
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
    subcommand.set_defaults(func=call)
