"""Tests for seller profile cache."""
import asyncio

from src.seller_cache import SellerProfileCache


def test_cache_reuses_value_and_returns_copy():
    clock = {"value": 100.0}
    cache = SellerProfileCache(ttl_seconds=60, time_source=lambda: clock["value"])
    loader_calls = 0

    async def loader(user_id: str):
        nonlocal loader_calls
        loader_calls += 1
        return {"user_id": user_id, "items": []}

    async def run():
        first = await cache.get_or_load("seller-1", loader)
        first["items"].append("mutated")
        second = await cache.get_or_load("seller-1", loader)
        return second

    second = asyncio.run(run())
    assert loader_calls == 1
    assert second == {"user_id": "seller-1", "items": []}


def test_cache_coalesces_inflight_requests():
    cache = SellerProfileCache(ttl_seconds=60)
    loader_calls = 0

    async def loader(user_id: str):
        nonlocal loader_calls
        loader_calls += 1
        await asyncio.sleep(0.02)
        return {"user_id": user_id}

    async def run():
        return await asyncio.gather(
            cache.get_or_load("seller-2", loader),
            cache.get_or_load("seller-2", loader),
        )

    results = asyncio.run(run())
    assert loader_calls == 1
    assert results == [{"user_id": "seller-2"}, {"user_id": "seller-2"}]


def test_cache_evicts_expired_entries():
    clock = {"value": 100.0}
    cache = SellerProfileCache(ttl_seconds=60, time_source=lambda: clock["value"])
    loader_calls = 0

    async def loader(user_id: str):
        nonlocal loader_calls
        loader_calls += 1
        return {"user_id": user_id, "load_count": loader_calls}

    async def run():
        first = await cache.get_or_load("seller-3", loader)
        clock["value"] = 200.0  # Advance past TTL
        second = await cache.get_or_load("seller-3", loader)
        return first, second

    first, second = asyncio.run(run())
    assert loader_calls == 2
    assert first["load_count"] == 1
    assert second["load_count"] == 2
