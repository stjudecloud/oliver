from typing import Any, Dict, List, Tuple, Optional, Union

from . import errors


def _input(question: str) -> str:
    """Need a wrapper method for mocking during tests"""
    return input(question)


def ask_boolean_question(question: str, tries: int = 3) -> Optional[str]:
    choices: List[str] = ["yes", "y", "no", "n"]

    tried = 0
    while tried < tries:
        answer = _input(question + " (y/n) ").lower()
        if answer in choices:
            return answer
        tried += 1

    errors.report(
        message="Could not get valid user input!",
        fatal=True,
        exitcode=errors.ERROR_INVALID_INPUT,
    )
    # This function should return `answer` or exit from the report method.
    # The following return is just to silence mypy on missing return value.
    return None


def dict_to_aiohttp_tuples(
    d: Dict[str, Union[str, int, List[Any]]]
) -> List[Tuple[Any, Any]]:
    """aiohttp doesn't like dictionaries where the values are arrays.

    In particular, passing in a mapping parses all of the values with _query_var:

        https://github.com/aio-libs/yarl/blob/3e63b31b414aa9e47563692b36ba2024a15d43f4/yarl/__init__.py#L886

    and _query_var expects the value to be either a str or an int:

        https://github.com/aio-libs/yarl/blob/3e63b31b414aa9e47563692b36ba2024a15d43f4/yarl/__init__.py#L861

    The solution is to transform the dictionary to a list of tuples where
    the tuples are formed as (key, value). You can have multiple entries for
    (key, _) denoting an array.

    Args:
        d (Dict): a dictionary to be passed into aiohttp.

    Returns:
        List[Tuple]: the dictionary as a list of tuples as described above.
    """

    assert isinstance(d, dict), "Expected a dictionary for aiohttp!"
    results: List[Tuple[Any, Any]] = []

    def parse(k: Any, v: Any) -> List[Tuple[Any, Any]]:
        return [(k, v)]

    for k, v in d.items():
        # The following expression tests to make sure v doesn't match a bool
        # pylint: disable=unidiomatic-typecheck
        if type(v) is int or isinstance(v, str):
            results.extend(parse(k, v))
        elif isinstance(v, list):
            for item in v:
                results.extend(parse(k, item))
        else:
            errors.report(
                message=f"Can't prepare object of type '{type(v)}' for aiohttp.",
                fatal=True,
                exitcode=errors.ERROR_INTERNAL_ERROR,
                suggest_report=True,
            )

    return results
