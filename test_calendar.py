"""Plain-assert self-check for the date logic in generate.py. Run: python test_calendar.py"""
from datetime import datetime
from generate import parse_start, month_for_row, range_label


def test_parse_start():
    assert parse_start("2026") == datetime(2026, 1, 1)
    assert parse_start("2026-09") == datetime(2026, 9, 1)


def test_month_for_row_full_year():
    s = datetime(2026, 1, 1)
    assert month_for_row(s, 0) == datetime(2026, 1, 1)
    assert month_for_row(s, 11) == datetime(2026, 12, 1)


def test_month_for_row_school_year():
    s = datetime(2026, 9, 1)
    assert month_for_row(s, 0) == datetime(2026, 9, 1)
    assert month_for_row(s, 3) == datetime(2026, 12, 1)
    assert month_for_row(s, 4) == datetime(2027, 1, 1)   # rolls the year
    assert month_for_row(s, 11) == datetime(2027, 8, 1)


def test_range_label():
    assert range_label(datetime(2026, 1, 1), 12) == "2026"
    assert range_label(datetime(2026, 9, 1), 12) == "2026-2027"


if __name__ == "__main__":
    test_parse_start()
    test_month_for_row_full_year()
    test_month_for_row_school_year()
    test_range_label()
    print("ok")
