"""
Account strategy resolution helpers.
Determines which account to use based on strategy type and available accounts.
"""
from typing import List, Optional


VALID_STRATEGIES = {"auto", "fixed", "rotate"}


def clean_account_state_file(value: Optional[str]) -> Optional[str]:
    """
    Clean account state file path.
    Returns None for empty, null, or undefined values.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"null", "undefined"}:
        return None
    return text


def normalize_account_strategy(
    strategy: Optional[str],
    account_state_file: Optional[str] = None,
) -> str:
    """
    Normalize account strategy to a valid value.
    Infers 'fixed' when account_state_file is provided.
    """
    raw = str(strategy or "").strip().lower()
    if raw in VALID_STRATEGIES:
        return raw
    if clean_account_state_file(account_state_file):
        return "fixed"
    return "auto"


def resolve_account_runtime_plan(
    *,
    strategy: Optional[str],
    account_state_file: Optional[str],
    has_root_state_file: bool,
    available_account_files: List[str],
) -> dict:
    """
    Resolve the runtime account selection plan.

    Returns dict with:
      - strategy: normalized strategy
      - forced_account: specific account to use (for fixed)
      - use_account_pool: whether to use account pool rotation
      - prefer_root_state: whether to prefer root state file
    """
    normalized_strategy = normalize_account_strategy(strategy, account_state_file)
    cleaned_account = clean_account_state_file(account_state_file)
    has_account_pool = len(available_account_files) > 0

    if normalized_strategy == "fixed":
        return {
            "strategy": normalized_strategy,
            "forced_account": cleaned_account,
            "use_account_pool": False,
            "prefer_root_state": False,
        }

    if normalized_strategy == "rotate":
        return {
            "strategy": normalized_strategy,
            "forced_account": None,
            "use_account_pool": has_account_pool,
            "prefer_root_state": False,
        }

    return {
        "strategy": normalized_strategy,
        "forced_account": None,
        "use_account_pool": (not has_root_state_file) and has_account_pool,
        "prefer_root_state": has_root_state_file,
    }
