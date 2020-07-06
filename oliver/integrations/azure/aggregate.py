import os

from typing import Any, Dict, Optional

from ...lib import api, errors
from ...subcommands import outputs as _outputs


def process_output_azure(
    dest_folder: str,
    output: str,
    azure_storage_account: str,
    sas_token: Optional[str] = "",
    dry_run: Optional[bool] = False,
) -> None:
    if isinstance(output, list):
        for o in output:
            process_output_azure(
                dest_folder, o, azure_storage_account, sas_token, dry_run
            )
        return

    if not output:
        return

    if not azure_storage_account:
        errors.report(
            f"Must include Azure blob storage account name in config!",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )

    source_url = f"https://{azure_storage_account}.blob.core.windows.net{output}"
    file_name = os.path.basename(output)

    if not sas_token:
        cmd = f"az storage copy -s {source_url} -d {dest_folder}/{file_name}"
    else:
        cmd = f"azcopy copy --recursive '{source_url}{sas_token}' {dest_folder}/{file_name}"

    if dry_run:
        print(cmd)
    else:
        os.system(cmd)


async def call(args: Dict[str, Any], cromwell: api.CromwellAPI) -> None:
    """Execute the subcommand.

    Args:
        args (Dict): Arguments parsed from the command line.
        cromwell (api.CromwellAPI): Cromwell server to use for subcommand.
    """
    outputs = await _outputs.get_outputs(
        cromwell, args["workflow-id"], output_prefix=args.get("output_prefix", "")
    )
    if not args.get("storage_account_name"):
        errors.report(
            f"Must include Azure blob storage account name in config! [oliver config set storage_account_name cromwell-XXXXX]",
            fatal=True,
            exitcode=errors.ERROR_INVALID_INPUT,
        )

    for output in outputs:
        process_output_azure(
            args.get("output-folder", ""),
            output["Location"],
            args.get("storage_account_name", ""),
            args.get("sas_token"),
            args.get("dry_run"),
        )
