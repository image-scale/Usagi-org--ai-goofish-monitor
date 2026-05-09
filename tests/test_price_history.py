"""Tests for price history service."""
from src.price_history import (
    PriceHistoryStore,
    parse_price_value,
    build_item_price_context,
    build_price_history_insights,
)


def test_parse_price_value_handles_currency_symbols():
    assert parse_price_value("¥10000") == 10000.0
    assert parse_price_value("10,000") == 10000.0


def test_parse_price_value_handles_wan_notation():
    assert parse_price_value("1.5万") == 15000.0


def test_parse_price_value_handles_invalid():
    assert parse_price_value(None) is None
    assert parse_price_value("暂无") is None
    assert parse_price_value("N/A") is None
    assert parse_price_value("-") is None


def test_parse_price_value_handles_numbers():
    assert parse_price_value(9999) == 9999.0
    assert parse_price_value(9999.99) == 9999.99


def test_record_and_load_snapshots():
    store = PriceHistoryStore()

    items = [
        {"商品ID": "1001", "商品标题": "Sony A7M4", "当前售价": "¥10000"},
        {"商品ID": "1002", "商品标题": "Sony A7CR", "当前售价": "¥12000"},
    ]

    records = store.record_market_snapshots(
        keyword="sony camera",
        task_name="Camera Monitor",
        items=items,
        run_id="run-1",
        snapshot_time="2026-01-01T12:00:00",
    )

    assert len(records) == 2
    assert records[0]["item_id"] == "1001"
    assert records[0]["price"] == 10000.0

    loaded = store.load_price_snapshots("sony camera")
    assert len(loaded) == 2


def test_record_snapshots_deduplicates():
    store = PriceHistoryStore()
    seen = set()

    items = [
        {"商品ID": "1001", "商品标题": "Sony A7M4", "当前售价": "¥10000"},
        {"商品ID": "1001", "商品标题": "Sony A7M4 Dup", "当前售价": "¥9999"},
    ]

    records = store.record_market_snapshots(
        keyword="sony",
        task_name="Test",
        items=items,
        run_id="run-1",
        snapshot_time="2026-01-01T12:00:00",
        seen_item_ids=seen,
    )

    assert len(records) == 1


def test_build_price_history_insights():
    store = PriceHistoryStore()

    store.record_market_snapshots(
        keyword="test-insights",
        task_name="Test",
        items=[
            {"商品ID": "1", "商品标题": "Item1", "当前售价": "100"},
            {"商品ID": "2", "商品标题": "Item2", "当前售价": "200"},
        ],
        run_id="run-1",
        snapshot_time="2026-01-01T12:00:00",
    )

    store.record_market_snapshots(
        keyword="test-insights",
        task_name="Test",
        items=[
            {"商品ID": "1", "商品标题": "Item1", "当前售价": "90"},
            {"商品ID": "3", "商品标题": "Item3", "当前售价": "300"},
        ],
        run_id="run-2",
        snapshot_time="2026-01-02T12:00:00",
    )

    snapshots = store.load_price_snapshots("test-insights")

    from src import price_history
    original_load = price_history.load_price_snapshots
    price_history.load_price_snapshots = lambda k: snapshots

    insights = build_price_history_insights("test-insights")

    price_history.load_price_snapshots = original_load

    assert insights["market_summary"]["sample_count"] == 2
    assert insights["history_summary"]["unique_items"] == 3
    assert len(insights["daily_trend"]) == 2


def test_build_item_price_context():
    snapshots = [
        {"item_id": "1001", "price": 10000, "snapshot_time": "2026-01-01T12:00:00", "run_id": "run-1"},
        {"item_id": "1002", "price": 12000, "snapshot_time": "2026-01-01T12:00:00", "run_id": "run-1"},
        {"item_id": "1001", "price": 9500, "snapshot_time": "2026-01-02T12:00:00", "run_id": "run-2"},
        {"item_id": "1003", "price": 13000, "snapshot_time": "2026-01-02T12:00:00", "run_id": "run-2"},
    ]

    context = build_item_price_context(
        snapshots,
        item_id="1001",
        current_price=9500.0,
    )

    assert context["observation_count"] == 2
    assert context["min_price"] == 9500.0
    assert context["max_price"] == 10000.0
    assert context["price_change_amount"] == -500.0
    assert context["deal_label"] == "Great Deal"
