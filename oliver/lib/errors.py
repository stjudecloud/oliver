import sys

from logzero import logger

from . import constants

ERROR_PRECAUTION = 1
ERROR_UNEXPECTED_RESPONSE = 2
ERROR_NO_RESPONSE = 3
ERROR_INVALID_INPUT = 4
ERROR_INTERNAL_ERROR = 255


def report(
    message: str, fatal: bool = True, exitcode: int = 1, suggest_report: bool = False
) -> None:
    """Reports an error to terminal and exits (if specified).

    Args:
        message (str): Message to output to the terminal.
        fatal (bool, optional): Whether to exit after reporting the error. Defaults to True.
        exitcode (int, optional): If exiting, the error code that will be
        reported. Defaults to 1.
        suggest_report(bool): Print a message to the screen asking the user to
        report the bug to constants.OLIVER_ISSUE_URL. Defaults to False.
    """

    logger.error(message)
    if suggest_report:
        logger.error("")
        logger.error("Please report this error at %s", constants.OLIVER_ISSUE_URL)
    if fatal:
        sys.exit(exitcode)
