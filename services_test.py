import pytest

from services import is_valid_phone_number, read_prefix_file


@pytest.mark.parametrize(
    "phone_number, expected",
    [
        ("17490276403A", False),
        ("+17490276403+", False),
        ("+17490276403", "17490276403"),
        ("1 74   902 764 03   ", "17490276403"),
        ("001749027640300", False),
        ("+0 01749 027640 300", False),
        ("202-456-1414", "2024561414"),
        ("(202) 456-1414", "2024561414"),
        ("+1 (202) 456-1414", "12024561414"),
        ("202.456.1414", False),
        ("202/4561414", False),
        ("1 202 456 1414", "12024561414"),
        ("+12024561414", "12024561414"),
        ("1 202-456-1414", "12024561414"),
    ],
)
def test_is_valid_phone_number(phone_number, expected):
    assert is_valid_phone_number(phone_number) == expected


def test_read_prefix_file():
    assert len(read_prefix_file()) == 900005
