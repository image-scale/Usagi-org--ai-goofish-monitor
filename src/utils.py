"""
Utility functions for text processing, link conversion, and async retry.
"""
import asyncio
import math
import re
from functools import wraps
from urllib.parse import quote


def retry_on_failure(retries=3, delay=5):
    """
    Async retry decorator for functions that may fail with HTTP errors.
    Retries the function up to `retries` times with `delay` seconds between attempts.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        return None
            return None
        return wrapper
    return decorator


async def safe_get(data, *keys, default="N/A"):
    """Safely get nested dict/list values, returning default on missing keys."""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data


def sanitize_filename(value: str) -> str:
    """Generate a safe filename fragment by removing/replacing unsafe characters."""
    if not value:
        return "task"
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "task"


def get_link_unique_key(link: str) -> str:
    """Extract unique portion of link (content before first &)."""
    return link.split('&', 1)[0]


def convert_goofish_link(url: str) -> str:
    """
    Convert Goofish product link to mobile format.
    Extracts item ID and creates encoded mobile URL.
    """
    match = re.search(r'item\?id=(\d+)', url)
    if match:
        item_id = match.group(1)
        bfp_json = f'{{"id":{item_id}}}'
        return f"https://pages.goofish.com/sharexy?loadingVisible=false&bft=item&bfs=idlepc.item&spm=a21ybx.item.0.0&bfp={quote(bfp_json)}"
    return url


def format_registration_days(total_days: int) -> str:
    """
    Format total days as "X years Y months" display string.
    Handles invalid input gracefully.
    """
    if not isinstance(total_days, int) or total_days <= 0:
        return 'Unknown'

    DAYS_IN_YEAR = 365.25
    DAYS_IN_MONTH = DAYS_IN_YEAR / 12

    years = math.floor(total_days / DAYS_IN_YEAR)
    remaining_days = total_days - (years * DAYS_IN_YEAR)
    months = round(remaining_days / DAYS_IN_MONTH)

    if months == 12:
        years += 1
        months = 0

    if years > 0 and months > 0:
        return f"{years} years {months} months"
    elif years > 0 and months == 0:
        return f"{years} years"
    elif years == 0 and months > 0:
        return f"{months} months"
    else:
        return "Less than a month"
