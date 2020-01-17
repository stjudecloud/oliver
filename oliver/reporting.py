import sys

from tabulate import tabulate
from typing import List, Dict

from . import errors


def print_dicts_as_table(
    data: List[Dict], tablefmt: str = "fancy_grid", clean_shard_col: bool = True
):
    """Format a list of dicts and print as a table using `tabulate`.
    
    Args:
        data (List[Dict]): Data to be printed structured as a list of dicts.
        tablefmt (str, optional): Any valid `tabulate` table format. 
                                  See https://github.com/astanin/python-tabulate#table-format 
                                  for more information. Defaults to "fancy_grid".
        clean_shard_col (bool, optional): Remove the column named "Shard" if all values are -1.
                                          Defaults to True.
    """

    if len(data) <= 0:
        return

    if not isinstance(data, list) or not isinstance(data[0], dict):
        errors.report(
            "Expected 'data' to be a list of dicts!",
            fatal=True,
            exitcode=errors.ERROR_INTERNAL_ERROR,
        )

    # Remove Shard column if all values are -1, it's generally
    # not helpful if this is the case.
    if clean_shard_col:
        to_remove = True
        for item in data:
            if "Shard" in item and item["Shard"] != -1:
                to_remove = False
                break

        if to_remove:
            for item in data:
                if "Shard" in item:
                    del item["Shard"]

    print(
        tabulate([d.values() for d in data], headers=data[0].keys(), tablefmt=tablefmt)
    )


def print_error_as_table(status: str, message: str, tablefmt: str = "fancy_grid"):
    """Prints an error message as a table.
    
    Args:
        status (str): string to put in the "Status" column.
        message (str): string to put in the "Message" column.
        tablefmt (str, optional): Any valid `tabulate` table format. 
                                  See https://github.com/astanin/python-tabulate#table-format 
                                  for more information. Defaults to "fancy_grid".
    """
    results = [{"Status": status, "Message": message}]
    print_dicts_as_table(results)
