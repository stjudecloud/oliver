import sys

from collections import OrderedDict
from tabulate import tabulate
from typing import List, Dict

from . import errors


def print_dicts_as_table(
    data: List[Dict],
    grid_style: str = "fancy_grid",
    clean_shard_col: bool = True,
    fill=0,
):
    """Format a list of dicts and print as a table using `tabulate`.
    
    Args:
        data (List[Dict]): Data to be printed structured as a list of dicts.
        grid_style (str, optional): Any valid `tabulate` table format. 
                                    See https://github.com/astanin/python-tabulate#table-format 
                                    for more information. Defaults to "fancy_grid".
        clean_shard_col (bool, optional): Remove the column named "Shard" if all values are -1.
                                          Defaults to True.
        fill: value to fill for missing cells.
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

    # todo: this part could be much cleaner, but can't be bothered to
    # to make an elegant solution at this moment.

    # use ordered dict as ordered set (again, laziness)
    ordered_set = OrderedDict()
    for d in data:
        for k in d.keys():
            ordered_set[k] = None

    headers = list(ordered_set.keys())

    for d in data:
        for k in headers:
            if not d.get(k):
                d[k] = fill

    print(tabulate([d.values() for d in data], headers=headers, tablefmt=grid_style))


def print_error_as_table(status: str, message: str, grid_style: str = "fancy_grid"):
    """Prints an error message as a table.
    
    Args:
        status (str): string to put in the "Status" column.
        message (str): string to put in the "Message" column.
        grid_style (str, optional): Any valid `tabulate` table format. 
                                    See https://github.com/astanin/python-tabulate#table-format 
                                    for more information. Defaults to "fancy_grid".
    """
    results = [{"Status": status, "Message": message}]
    print_dicts_as_table(results, grid_style=grid_style)
