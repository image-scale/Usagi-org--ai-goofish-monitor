"""
Price history service for recording market snapshots and computing analytics.
Tracks price trends, market summaries, and deal scores for products.
"""
from collections import defaultdict
from datetime import datetime
from statistics import median
from typing import Any, Dict, Iterable, List, Optional
import math


def parse_price_value(value: Any) -> Optional[float]:
    """
    Parse price value handling currency symbols and wan notation.
    Returns None for invalid or missing values.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)

    text = str(value).strip().replace("¥", "").replace(",", "")
    if not text or text in {"价格异常", "暂无", "-", "N/A", "Unknown"}:
        return None
    if text.endswith("万"):
        text = str(float(text[:-1]) * 10000)
    try:
        return round(float(text), 2)
    except (TypeError, ValueError):
        return None


def _safe_iso_datetime(value: Optional[str]) -> str:
    if value:
        return value
    return datetime.now().isoformat()


def _to_day(iso_text: str) -> str:
    return iso_text[:10]


class PriceHistoryStore:
    """In-memory store for price history snapshots."""

    def __init__(self):
        self._snapshots: Dict[str, List[dict]] = defaultdict(list)

    def normalize_keyword_slug(self, keyword: str) -> str:
        text = "".join(
            char for char in str(keyword or "").lower().replace(" ", "_")
            if char.isalnum() or char in "_-"
        ).rstrip("_")
        return text or "unknown"

    def record_market_snapshots(
        self,
        *,
        keyword: str,
        task_name: str,
        items: Iterable[dict],
        run_id: str,
        snapshot_time: Optional[str] = None,
        seen_item_ids: Optional[set] = None,
    ) -> List[dict]:
        """Record market snapshots with deduplication."""
        snapshot_time = _safe_iso_datetime(snapshot_time)
        seen = seen_item_ids if seen_item_ids is not None else set()
        records: List[dict] = []
        keyword_slug = self.normalize_keyword_slug(keyword)

        for item in items:
            item_id = str(item.get("商品ID") or "").strip()
            link = str(item.get("商品链接") or "").strip()
            unique_id = item_id or link
            price_value = parse_price_value(item.get("当前售价"))

            if not unique_id or price_value is None:
                continue
            if unique_id in seen:
                continue
            seen.add(unique_id)

            record = {
                "snapshot_time": snapshot_time,
                "snapshot_day": _to_day(snapshot_time),
                "run_id": run_id,
                "task_name": task_name,
                "keyword": keyword,
                "item_id": unique_id,
                "title": item.get("商品标题") or "",
                "price": price_value,
                "price_display": item.get("当前售价") or "",
                "tags": item.get("商品标签") or [],
                "region": item.get("发货地区") or "",
                "seller": item.get("卖家昵称") or "",
                "publish_time": item.get("发布时间") or "",
                "link": link,
            }
            records.append(record)
            self._snapshots[keyword_slug].append(record)

        return records

    def load_price_snapshots(self, keyword: str) -> List[dict]:
        """Load all snapshots for a keyword."""
        keyword_slug = self.normalize_keyword_slug(keyword)
        return list(self._snapshots.get(keyword_slug, []))


_default_store = PriceHistoryStore()


def record_market_snapshots(**kwargs) -> List[dict]:
    return _default_store.record_market_snapshots(**kwargs)


def load_price_snapshots(keyword: str) -> List[dict]:
    return _default_store.load_price_snapshots(keyword)


def _dedupe_latest(records: Iterable[dict], group_key: str) -> List[dict]:
    """Keep only the latest record for each unique key."""
    latest_by_key: Dict[str, dict] = {}
    for record in records:
        key = str(record.get(group_key) or "").strip()
        if not key:
            continue
        latest_by_key[key] = record
    return list(latest_by_key.values())


def _summarize_prices(records: Iterable[dict]) -> dict:
    """Compute price statistics for a set of records."""
    entries = [r for r in records if parse_price_value(r.get("price")) is not None]
    prices = [float(r["price"]) for r in entries]
    if not prices:
        return {
            "sample_count": 0,
            "avg_price": None,
            "median_price": None,
            "min_price": None,
            "max_price": None,
        }

    return {
        "sample_count": len(prices),
        "avg_price": round(sum(prices) / len(prices), 2),
        "median_price": round(float(median(prices)), 2),
        "min_price": round(min(prices), 2),
        "max_price": round(max(prices), 2),
    }


def _build_daily_trend(snapshots: List[dict]) -> List[dict]:
    """Build daily price trend from snapshots."""
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for snapshot in snapshots:
        grouped[str(snapshot.get("snapshot_day") or "")].append(snapshot)

    points: List[dict] = []
    for day in sorted(grouped.keys()):
        day_records = _dedupe_latest(grouped[day], "item_id")
        summary = _summarize_prices(day_records)
        summary["day"] = day
        points.append(summary)
    return points


def _resolve_deal_label(score: int) -> str:
    """Map deal score to label."""
    if score >= 65:
        return "Great Deal"
    if score >= 50:
        return "Worth Watching"
    if score >= 40:
        return "Fair Price"
    return "Overpriced"


def build_item_price_context(
    snapshots: List[dict],
    *,
    item_id: str,
    current_price: Optional[float],
) -> dict:
    """Build price context and deal score for a specific item."""
    if not item_id:
        return {"observation_count": 0, "deal_score": None, "deal_label": "No Data"}

    item_snapshots = [r for r in snapshots if str(r.get("item_id")) == str(item_id)]
    if not item_snapshots:
        return {"observation_count": 0, "deal_score": None, "deal_label": "No Data"}

    latest_item_snapshot = item_snapshots[-1]
    price_now = current_price if current_price is not None else parse_price_value(latest_item_snapshot.get("price"))
    historical_prices = [float(r["price"]) for r in item_snapshots if parse_price_value(r.get("price")) is not None]

    if not snapshots:
        latest_run_id = ""
    else:
        latest_run_id = str(snapshots[-1].get("run_id") or "")
    latest_market = _dedupe_latest(
        [r for r in snapshots if str(r.get("run_id") or "") == latest_run_id],
        "item_id",
    )
    market_summary = _summarize_prices(latest_market)
    market_avg = market_summary.get("avg_price")

    score = 50
    if price_now is not None and market_avg:
        score += int(((market_avg - price_now) / market_avg) * 60)
    if price_now is not None and historical_prices:
        historical_max = max(historical_prices)
        if historical_max > 0:
            score += int(((historical_max - price_now) / historical_max) * 20)
        if math.isclose(price_now, min(historical_prices), rel_tol=0.001):
            score += 8
    score = max(0, min(100, score))

    previous_price = historical_prices[-2] if len(historical_prices) >= 2 else None
    change_amount = None if previous_price is None or price_now is None else round(price_now - previous_price, 2)
    change_percent = None
    if change_amount is not None and previous_price:
        change_percent = round(change_amount / previous_price * 100, 2)

    return {
        "observation_count": len(historical_prices),
        "current_price": price_now,
        "avg_price": round(sum(historical_prices) / len(historical_prices), 2) if historical_prices else None,
        "median_price": round(float(median(historical_prices)), 2) if historical_prices else None,
        "min_price": round(min(historical_prices), 2) if historical_prices else None,
        "max_price": round(max(historical_prices), 2) if historical_prices else None,
        "first_seen_at": item_snapshots[0].get("snapshot_time"),
        "last_seen_at": latest_item_snapshot.get("snapshot_time"),
        "market_avg_price": market_avg,
        "price_change_amount": change_amount,
        "price_change_percent": change_percent,
        "deal_score": score,
        "deal_label": _resolve_deal_label(score),
    }


def build_price_history_insights(keyword: str, *, window_days: int = 30) -> dict:
    """Build comprehensive price history insights for a keyword."""
    snapshots = load_price_snapshots(keyword)
    if not snapshots:
        return {
            "market_summary": _summarize_prices([]),
            "history_summary": {"unique_items": 0, **_summarize_prices([])},
            "daily_trend": [],
            "latest_snapshot_at": None,
        }

    latest_run_id = str(snapshots[-1].get("run_id") or "")
    latest_run_snapshots = _dedupe_latest(
        [r for r in snapshots if str(r.get("run_id") or "") == latest_run_id],
        "item_id",
    )
    all_deduped = _dedupe_latest(snapshots, "item_id")

    return {
        "market_summary": {
            **_summarize_prices(latest_run_snapshots),
            "snapshot_time": snapshots[-1].get("snapshot_time"),
        },
        "history_summary": {
            "unique_items": len(all_deduped),
            **_summarize_prices(all_deduped),
        },
        "daily_trend": _build_daily_trend(snapshots),
        "latest_snapshot_at": snapshots[-1].get("snapshot_time"),
    }
