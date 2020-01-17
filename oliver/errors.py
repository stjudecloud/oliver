from logzero import logger
import sys

ERROR_PRECAUTION = 1
ERROR_UNEXPECTED_RESPONSE = 2
ERROR_INVALID_INPUT = 3
ERROR_INTERNAL_ERROR = 255


def report(message: str, fatal: bool = True, exitcode: int = 1):
    """Reports an error to terminal and exits (if specified).
    
    Args:
        message (str): Message to output to the terminal.
        fatal (bool, optional): Whether to exit after reporting the error. Defaults to True.
        exitcode (int, optional): If exiting, the error code that will be reported. Defaults to 1.
    """

    logger.error(message)
    if fatal:
        sys.exit(exitcode)
