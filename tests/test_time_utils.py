
from course_scheduler.utils.time_utils import format_minutes, to_minutes


def test_to_minutes_valid():
    assert to_minutes("08:30") == 510


def test_to_minutes_invalid():
    assert to_minutes("", default=7) == 7
    assert to_minutes("xx:yy", default=9) == 9


def test_format_minutes():
    assert format_minutes(510) == "08:30"
