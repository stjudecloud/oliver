import sys

from tabulate import tabulate
from typing import List, Dict

from . import errors


def print_dicts_as_table(data: List[Dict], tablefmt: str = "fancy_grid"):
    """Format a list of dicts and print as a table using `tabulate`.
    
    Args:
        data (List[Dict]): Data to be printed structured as a list of dicts.
        tablefmt (str, optional): Any valid `tabulate` table format. 
                                  See https://github.com/astanin/python-tabulate#table-format 
                                  for more information. Defaults to "fancy_grid".
    """

    if len(data) <= 0:
        return

    if not isinstance(data, list) or not isinstance(data[0], dict):
        errors.report(
            "Expected 'data' to be a list of dicts!",
            fatal=True,
            exitcode=errors.ERROR_INTERNAL_ERROR,
        )

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
