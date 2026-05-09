"""Tests for cron expression utilities."""
import pytest
from src.cron_utils import (
    normalize_cron_expression,
    build_cron_trigger,
    validate_cron_expression,
)


def test_normalize_cron_expression_expands_alias():
    assert normalize_cron_expression("@daily") == "0 0 * * *"
    assert normalize_cron_expression("@hourly") == "0 * * * *"
    assert normalize_cron_expression("@weekly") == "0 0 * * 0"
    assert normalize_cron_expression("@monthly") == "0 0 1 * *"
    assert normalize_cron_expression("@yearly") == "0 0 1 1 *"


def test_normalize_cron_expression_returns_none_for_empty():
    assert normalize_cron_expression(None) is None
    assert normalize_cron_expression("") is None
    assert normalize_cron_expression("   ") is None


def test_normalize_cron_expression_preserves_valid_expression():
    assert normalize_cron_expression("*/15 * * * *") == "*/15 * * * *"
    assert normalize_cron_expression("0 8 * * *") == "0 8 * * *"


def test_build_cron_trigger_five_fields():
    trigger = build_cron_trigger("0 8 * * *")
    assert trigger is not None


def test_build_cron_trigger_six_fields():
    trigger = build_cron_trigger("0 0 8 * * *")
    assert trigger is not None


def test_build_cron_trigger_accepts_alias():
    trigger = build_cron_trigger("@hourly", timezone="Asia/Shanghai")
    assert trigger is not None
    assert str(trigger.timezone) == "Asia/Shanghai"


def test_validate_cron_expression_normalizes_alias():
    assert validate_cron_expression("@daily") == "0 0 * * *"


def test_validate_cron_expression_accepts_six_fields():
    assert validate_cron_expression("0 0 8 * * *") == "0 0 8 * * *"


def test_validate_cron_expression_rejects_invalid():
    with pytest.raises(ValueError) as exc_info:
        validate_cron_expression("not-a-cron")
    assert "5 fields" in str(exc_info.value)


def test_validate_cron_expression_returns_none_for_empty():
    assert validate_cron_expression(None) is None
    assert validate_cron_expression("") is None
