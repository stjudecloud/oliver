import pytest

from oliver.lib import utils


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
