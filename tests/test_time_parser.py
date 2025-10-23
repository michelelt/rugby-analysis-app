from app.core.utils import parse_minuto_to_ms


def test_integer_minutes():
    assert parse_minuto_to_ms("3") == 3 * 60 * 1000


def test_minute_seconds():
    assert parse_minuto_to_ms("1:23") == (1 * 60 + 23) * 1000


def test_zero_seconds():
    assert parse_minuto_to_ms("0:30") == 30 * 1000


def test_float_minutes():
    assert parse_minuto_to_ms("2.5") == 2 * 60 * 1000


def test_invalid():
    assert parse_minuto_to_ms("abc") == 0
