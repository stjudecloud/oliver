from collections import OrderedDict

from typing import List, Dict, OrderedDict as OrderedDictType

import pendulum
from logzero import logger
from tzlocal import get_localzone
from tabulate import tabulate

from . import errors

DEFAULT_HEADER_ORDER = [
    "Job Name",
    "Job Group",
    "Call Name",
    "QueuedInCromwell",
    "Starting",
    "Running",
    "Aborted",
    "Failed",
    "Succeeded",
]


def localize_date(given_date: str):
    "Returns a localized date given any date that is parsable by pedulum."
    return pendulum.parse(given_date).in_tz(get_localzone()).to_day_datetime_string()


def localize_date_from_timestamp(timestamp: int, already_localized=False):
    "Returns a localized date given a UNIX timestamp."

    tz = "UTC"
    if already_localized:
        tz = get_localzone()

    logger.debug(f"Converting using timezone: {tz}")

    return (
        pendulum.from_timestamp(timestamp, tz=tz)
        .in_tz(get_localzone())
        .to_day_datetime_string()
    )


def duration_to_text(duration):
    parts = []
    attrs = ["years", "months", "days", "hours", "minutes", "remaining_seconds"]
    for attr in attrs:
        if hasattr(duration, attr):
            value = getattr(duration, attr)
            # hack to get the correct formatting out. Pendulum appears to inconsistently
            # name its methods: https://github.com/sdispater/pendulum/blob/master/pendulum/duration.py#L163
            if attr == "remaining_seconds":
                attr = "seconds"

            if value > 0:
                parts.append(f"{value} {attr}")

    return " ".join(parts)


def print_dicts_as_table(
    rows: List[Dict],
    grid_style: str = "fancy_grid",
    clean: bool = True,
    fill=None,
    header_order: list = None,
):
    """Format a list of dicts and print as a table using `tabulate`.

    Args:
        rows (List[Dict]): Data to be printed structured as a list of dicts.
        grid_style (str, optional): Any valid `tabulate` table format.
                                    See https://github.com/astanin/python-tabulate#table-format
                                    for more information. Defaults to "fancy_grid".
        clean (bool, optional): Remove all columns consisting of -1 or None.
        fill: value to fill for missing cells.
        header_order (list, optional): if headers exist, these will be put in
        the front.
    """

    if len(rows) <= 0:
        return

    if header_order is None:
        header_order = DEFAULT_HEADER_ORDER

    if not isinstance(rows, list) or not isinstance(rows[0], dict):
        errors.report(
            "Expected 'data' to be a list of dicts!",
            fatal=True,
            exitcode=errors.ERROR_INTERNAL_ERROR,
        )

    # TODO: this part could be much cleaner, but can't be bothered to
    # to make an elegant solution at this moment.

    # use ordered dict as ordered set (again, laziness)
    ordered_set: OrderedDictType[str, None] = OrderedDict()
    for row in rows:
        for h in row.keys():
            ordered_set[h] = None

    headers = list(ordered_set.keys())
    for _h in reversed(header_order):
        if _h in headers:
            headers.remove(_h)
            headers = [_h] + headers

    # clean uninteresting columns
    uninteresting_values = [-1, None, "<not set>"]
    headers_to_remove = []

    if clean:
        for header in headers:
            results = [row.get(header) in uninteresting_values for row in rows]
            to_remove = all(results)
            if to_remove:
                headers_to_remove.append(header)

    for header in headers_to_remove:
        for row in rows:
            if header in headers:
                headers.remove(header)
            if header in row:
                del row[header]

    results = []

    # definitely a more elegant solution for this...
    for row in rows:
        r = {}
        for header in headers:
            r[header] = row.get(header, fill)
        results.append(r)

    print(
        tabulate(
            [result.values() for result in results],
            headers=headers,
            tablefmt=grid_style,
        )
    )


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
