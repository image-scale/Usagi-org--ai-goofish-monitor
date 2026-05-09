"""Tests for account strategy resolver."""
from src.account_strategy import (
    clean_account_state_file,
    normalize_account_strategy,
    resolve_account_runtime_plan,
)


def test_clean_account_state_file_returns_none_for_empty():
    assert clean_account_state_file(None) is None
    assert clean_account_state_file("") is None
    assert clean_account_state_file("   ") is None


def test_clean_account_state_file_returns_none_for_null_string():
    assert clean_account_state_file("null") is None
    assert clean_account_state_file("undefined") is None


def test_clean_account_state_file_returns_cleaned_path():
    assert clean_account_state_file("state/acc.json") == "state/acc.json"
    assert clean_account_state_file("  state/acc.json  ") == "state/acc.json"


def test_normalize_strategy_valid_values():
    assert normalize_account_strategy("auto") == "auto"
    assert normalize_account_strategy("fixed") == "fixed"
    assert normalize_account_strategy("rotate") == "rotate"


def test_normalize_strategy_infers_fixed_from_state_file():
    assert normalize_account_strategy("", "state/acc.json") == "fixed"
    assert normalize_account_strategy(None, "state/acc.json") == "fixed"


def test_normalize_strategy_defaults_to_auto():
    assert normalize_account_strategy("") == "auto"
    assert normalize_account_strategy(None) == "auto"
    assert normalize_account_strategy("invalid") == "auto"


def test_resolve_runtime_plan_fixed():
    plan = resolve_account_runtime_plan(
        strategy="fixed",
        account_state_file="state/acc_1.json",
        has_root_state_file=False,
        available_account_files=["state/acc_1.json", "state/acc_2.json"],
    )
    assert plan["strategy"] == "fixed"
    assert plan["forced_account"] == "state/acc_1.json"
    assert plan["use_account_pool"] is False


def test_resolve_runtime_plan_rotate():
    plan = resolve_account_runtime_plan(
        strategy="rotate",
        account_state_file=None,
        has_root_state_file=True,
        available_account_files=["state/acc_1.json", "state/acc_2.json"],
    )
    assert plan["strategy"] == "rotate"
    assert plan["forced_account"] is None
    assert plan["use_account_pool"] is True
    assert plan["prefer_root_state"] is False


def test_resolve_runtime_plan_auto_prefers_root():
    plan = resolve_account_runtime_plan(
        strategy="auto",
        account_state_file=None,
        has_root_state_file=True,
        available_account_files=["state/acc_1.json"],
    )
    assert plan["strategy"] == "auto"
    assert plan["prefer_root_state"] is True
    assert plan["use_account_pool"] is False


def test_resolve_runtime_plan_auto_uses_pool_when_no_root():
    plan = resolve_account_runtime_plan(
        strategy="auto",
        account_state_file=None,
        has_root_state_file=False,
        available_account_files=["state/acc_1.json"],
    )
    assert plan["strategy"] == "auto"
    assert plan["prefer_root_state"] is False
    assert plan["use_account_pool"] is True
