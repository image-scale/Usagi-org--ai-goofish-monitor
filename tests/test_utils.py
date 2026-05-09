"""Tests for utility functions."""
import asyncio

from src.utils import (
    safe_get,
    sanitize_filename,
    get_link_unique_key,
    convert_goofish_link,
    format_registration_days,
    retry_on_failure,
)


def test_safe_get_nested_dict():
    data = {"a": {"b": [{"c": "value"}]}}
    assert asyncio.run(safe_get(data, "a", "b", 0, "c")) == "value"


def test_safe_get_missing_key():
    data = {"a": {"b": [{"c": "value"}]}}
    assert asyncio.run(safe_get(data, "a", "b", 1, "c", default="missing")) == "missing"


def test_safe_get_default():
    data = {"a": 1}
    assert asyncio.run(safe_get(data, "x", default="default")) == "default"


def test_sanitize_filename_removes_unsafe():
    assert sanitize_filename("task@name!#$%") == "task_name"


def test_sanitize_filename_empty():
    assert sanitize_filename("") == "task"
    assert sanitize_filename(None) == "task"


def test_sanitize_filename_preserves_valid():
    assert sanitize_filename("my-task_123") == "my-task_123"


def test_get_link_unique_key():
    link = "https://www.goofish.com/item?id=123&foo=bar"
    assert get_link_unique_key(link) == "https://www.goofish.com/item?id=123"


def test_get_link_unique_key_no_params():
    link = "https://www.goofish.com/item?id=123"
    assert get_link_unique_key(link) == "https://www.goofish.com/item?id=123"


def test_convert_goofish_link_with_item_id():
    url = "https://www.goofish.com/item?id=123456"
    result = convert_goofish_link(url)
    assert "pages.goofish.com/sharexy" in result
    assert "%7B%22id%22%3A123456%7D" in result


def test_convert_goofish_link_without_id():
    url = "https://www.example.com/other"
    assert convert_goofish_link(url) == url


def test_format_registration_days_years_and_months():
    result = format_registration_days(400)
    assert "year" in result.lower()


def test_format_registration_days_invalid():
    assert format_registration_days(-1) == "Unknown"
    assert format_registration_days(0) == "Unknown"


def test_format_registration_days_months_only():
    result = format_registration_days(60)
    assert "month" in result.lower()


def test_retry_on_failure_retries_and_returns_none():
    call_count = 0

    @retry_on_failure(retries=3, delay=0.01)
    async def failing_func():
        nonlocal call_count
        call_count += 1
        raise Exception("test error")

    result = asyncio.run(failing_func())
    assert result is None
    assert call_count == 3


def test_retry_on_failure_succeeds_on_retry():
    call_count = 0

    @retry_on_failure(retries=3, delay=0.01)
    async def sometimes_fails():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("test error")
        return "success"

    result = asyncio.run(sometimes_fails())
    assert result == "success"
    assert call_count == 2
