"""
Keyword rule matching engine for product filtering.
Uses OR logic: any keyword match results in recommendation.
Pure alphanumeric keywords match as complete tokens to prevent false positives.
"""
import re
from typing import Any, Dict, List

ALPHANUMERIC_PATTERN = re.compile(r"^[a-z0-9 ]+$")
TOKEN_CHAR = r"[a-z0-9]"


def normalize_text(value: str) -> str:
    """Normalize text to lowercase with single spaces."""
    return " ".join((value or "").lower().split())


def _collect_text_parts(value: Any, parts: List[str]) -> None:
    """Recursively collect all string values from nested data structures."""
    if value is None:
        return
    if isinstance(value, str):
        text = value.strip()
        if text:
            parts.append(text)
        return
    if isinstance(value, (int, float, bool)):
        parts.append(str(value))
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_text_parts(item, parts)
        return
    if isinstance(value, list):
        for item in value:
            _collect_text_parts(item, parts)


def build_search_text(record: Dict[str, Any]) -> str:
    """
    Build a searchable text string from a product record.
    Extracts text from product info and seller info sections.
    """
    parts: List[str] = []
    product_info = record.get("商品信息", {})
    seller_info = record.get("卖家信息", {})

    _collect_text_parts(product_info.get("商品标题"), parts)
    _collect_text_parts(product_info, parts)
    _collect_text_parts(seller_info, parts)

    return normalize_text(" ".join(parts))


def _dedupe_keywords(values: List[str]) -> List[str]:
    """Normalize and deduplicate keywords."""
    result: List[str] = []
    seen = set()
    for raw in values or []:
        text = normalize_text(str(raw).strip())
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _is_alphanumeric_token(keyword: str) -> bool:
    """Check if keyword should use whole-token matching."""
    return bool(keyword) and ALPHANUMERIC_PATTERN.fullmatch(keyword) is not None


def _keyword_matches(keyword: str, text: str) -> bool:
    """Check if keyword matches in text."""
    if not _is_alphanumeric_token(keyword):
        return keyword in text
    pattern = rf"(?<!{TOKEN_CHAR}){re.escape(keyword)}(?!{TOKEN_CHAR})"
    return re.search(pattern, text) is not None


def evaluate_keyword_rules(keywords: List[str], search_text: str) -> Dict[str, Any]:
    """
    Evaluate keyword rules against search text.
    Uses OR logic: any keyword match results in recommendation.

    Returns dict with:
      - analysis_source: "keyword"
      - is_recommended: bool
      - reason: str
      - matched_keywords: list of matched keywords
      - keyword_hit_count: number of matches
    """
    normalized_text = normalize_text(search_text)
    normalized_keywords = _dedupe_keywords(keywords)

    if not normalized_text:
        return {
            "analysis_source": "keyword",
            "is_recommended": False,
            "reason": "Search text is empty, keyword rules cannot execute.",
            "matched_keywords": [],
            "keyword_hit_count": 0,
        }

    if not normalized_keywords:
        return {
            "analysis_source": "keyword",
            "is_recommended": False,
            "reason": "No keyword rules configured.",
            "matched_keywords": [],
            "keyword_hit_count": 0,
        }

    matched = [kw for kw in normalized_keywords if _keyword_matches(kw, normalized_text)]
    hit_count = len(matched)
    is_recommended = hit_count > 0

    if is_recommended:
        reason = f"Matched {hit_count} keyword(s): {', '.join(matched)}"
    else:
        reason = "No keywords matched."

    return {
        "analysis_source": "keyword",
        "is_recommended": is_recommended,
        "reason": reason,
        "matched_keywords": matched,
        "keyword_hit_count": hit_count,
    }
