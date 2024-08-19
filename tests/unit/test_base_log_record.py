from dataclasses import dataclass, field
from typing import Dict, List

from http_log_record import BaseLogRecord


def test_to_dict_should_not_omit_any_present_fields():
    record = TestLogRecordWithPopulatedFields()

    assert record.to_dict() == {
        "int_field": 10,
        "float_field": 10.0,
        "str_field": "not-empty",
        "none_field": record.none_field,
        "dict_field": {"key": "value"},
        "list_field": [1, 2, 3],
    }


def test_to_dict_should_omit_none_fields():
    record = TestLogRecordWithPopulatedFields(none_field=None)
    assert record.to_dict().get("none_field") is None


def test_to_dict_should_omit_empty_dict_field():
    record = TestLogRecordWithPopulatedFields(dict_field={})
    assert record.to_dict().get("dict_field") is None


def test_to_dict_should_omit_empty_list_field():
    record = TestLogRecordWithPopulatedFields(list_field=[])
    assert record.to_dict().get("list_field") is None


def test_to_dict_should_omit_empty_str_field():
    record = TestLogRecordWithPopulatedFields(str_field="")
    assert record.to_dict().get("str_field") is None


def test_to_dict_should_omit_zero_int_field():
    record = TestLogRecordWithPopulatedFields(int_field=0)
    assert record.to_dict().get("int_field") is None


def test_to_dict_should_omit_zero_float_field():
    record = TestLogRecordWithPopulatedFields(float_field=0.0)
    assert record.to_dict().get("float_field") is None


@dataclass
class TestLogRecordWithEmptyFields(BaseLogRecord):
    int_field: int = 0
    float_field: float = 0.0
    str_field: str = ""
    none_field: object = None
    dict_field: dict = None
    list_field: list = None


@dataclass
class TestLogRecordWithPopulatedFields(BaseLogRecord):
    int_field: int = 10
    float_field: float = 10.0
    str_field: str = "not-empty"
    none_field: object = object().__class__
    dict_field: Dict[str, str] = field(default_factory=lambda: {"key": "value"})
    list_field: List[int] = field(default_factory=lambda: [1, 2, 3])
