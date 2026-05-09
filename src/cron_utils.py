"""
Cron expression parsing and validation utilities.
Supports 5-field, 6-field cron expressions and common aliases.
"""
from typing import Optional

from apscheduler.triggers.cron import CronTrigger

CRON_ALIASES = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

CRON_FORMAT_ERROR = (
    "Invalid cron expression. Supports 5 fields (min hour day month weekday), "
    "6 fields (sec min hour day month weekday), and common aliases "
    "(@hourly/@daily/@weekly/@monthly/@yearly). "
    "Examples: */15 * * * *, 0 8 * * *, 0 0 8 * * *, @daily."
)


def normalize_cron_expression(value: Optional[str]) -> Optional[str]:
    """
    Normalize cron expression, expanding aliases.
    Returns None for empty/None input.
    """
    if value is None:
        return None

    normalized = " ".join(str(value).strip().split())
    if not normalized:
        return None

    return CRON_ALIASES.get(normalized.lower(), normalized)


def build_cron_trigger(
    expression: str,
    *,
    timezone=None,
) -> CronTrigger:
    """
    Build an APScheduler CronTrigger from a cron expression.
    Supports 5-field, 6-field expressions and aliases.
    """
    normalized = normalize_cron_expression(expression)
    if normalized is None:
        raise ValueError(CRON_FORMAT_ERROR)

    parts = normalized.split()
    try:
        if len(parts) == 5:
            return CronTrigger.from_crontab(normalized, timezone=timezone)

        if len(parts) == 6:
            second, minute, hour, day, month, day_of_week = parts
            return CronTrigger(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone=timezone,
            )
    except ValueError as exc:
        raise ValueError(CRON_FORMAT_ERROR) from exc

    raise ValueError(CRON_FORMAT_ERROR)


def validate_cron_expression(value: Optional[str]) -> Optional[str]:
    """
    Validate a cron expression and return its normalized form.
    Returns None for empty input, raises ValueError for invalid expressions.
    """
    normalized = normalize_cron_expression(value)
    if normalized is None:
        return None

    build_cron_trigger(normalized)
    return normalized
