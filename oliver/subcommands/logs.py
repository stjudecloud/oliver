from tabulate import tabulate

from .. import api


def call(args):
    cromwell = api.CromwellAPI(
        server=args["cromwell_server"], version=args["cromwell_api_version"]
    )
    logs = cromwell.get_workflows_logs(args["workflow-id"])
    results = []

    for name, call in logs["calls"].items():
        for process in call:
            attempt = process["attempt"] if "attempt" in process else None
            shard = process["shardIndex"] if "shardIndex" in process else None

            # TODO: experimental, this code can be removed in the future if no
            # runtime errors are raised. If they are raised, we'll need to
            # further flesh out how Cromwell is reporting results.
            if not attempt or not shard:
                raise RuntimeError(
                    "Expected key is missing! The code needs to be updated, please contact the author!"
                )

            stdout = process["stdout"] if "stdout" in process else ""
            stderr = process["stderr"] if "stderr" in process else ""
            results.append(
                {
                    "Call Name": name,
                    "Attempt": attempt,
                    "Shard": shard,
                    "Log Name": "stdout",
                    "Location": stdout,
                }
            )
            results.append(
                {
                    "Call Name": name,
                    "Attempt": attempt,
                    "Shard": shard,
                    "Log Name": "stderr",
                    "Location": stderr,
                }
            )

    if "output_prefix" in args:
        for result in results:
            result["Location"] = args["output_prefix"] + result["Location"]

    if "call_name" in args and args["call_name"]:
        results = list(filter(lambda r: r["Call Name"] == args["call_name"], results))

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
        "logs", help="Find all reported logs for a given workflow."
    )
    subcommand.add_argument("workflow-id", help="Cromwell workflow ID.")
    subcommand.add_argument(
        "-c", "--call-name", help="Call name from the Cromwell workflow instance."
    )
    subcommand.add_argument(
        "--grid-style",
        help="Any valid `tablefmt` for python-tabulate.",
        default="fancy_grid",
    )
