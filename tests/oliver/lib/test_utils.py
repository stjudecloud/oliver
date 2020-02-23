from unittest.mock import patch

import pytest

from oliver.lib import utils


@patch("oliver.lib.utils._input", return_value="yes")
def test_ask_boolean_question_yes(_):
    assert utils.ask_boolean_question("sample question") == "yes"


@patch("oliver.lib.utils._input", return_value="no")
def test_ask_boolean_question_no(_):
    assert utils.ask_boolean_question("sample question") == "no"


@patch("oliver.lib.utils._input", return_value="foo")
def test_ask_boolean_question_bad_input(_):
    with pytest.raises(SystemExit):
        utils.ask_boolean_question("sample question")


def test_dict_to_aiohttp_tuples_non_dict():
    with pytest.raises(AssertionError):
        utils.dict_to_aiohttp_tuples([])


def test_dict_to_aiohttp_tuples_accepts_standard_kv():
    assert utils.dict_to_aiohttp_tuples({"key": "value"}) == [("key", "value")]


def test_dict_to_aiohttp_tuples_accepts_value_array():
    assert utils.dict_to_aiohttp_tuples({"key": ["value1", "value2"]}) == [
        ("key", "value1"),
        ("key", "value2"),
    ]


def test_dict_to_aiohttp_tuples_does_not_accept_bool_value():
    with pytest.raises(SystemExit):
        utils.dict_to_aiohttp_tuples({"key": True})
