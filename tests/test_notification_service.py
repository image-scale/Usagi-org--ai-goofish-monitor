"""Tests for notification service."""
import asyncio
from typing import Dict

from src.notification_service import (
    NotificationClient,
    NotificationService,
    WebhookClient,
)


class _OkClient(NotificationClient):
    channel_key = "ok"
    display_name = "OK"

    async def send(self, product_data: Dict, reason: str) -> bool:
        return True


class _FailClient(NotificationClient):
    channel_key = "fail"
    display_name = "FAIL"

    async def send(self, product_data: Dict, reason: str) -> bool:
        raise RuntimeError("boom")


def test_notification_service_collects_success_and_failure():
    service = NotificationService([_OkClient(enabled=True), _FailClient(enabled=True)])

    results = asyncio.run(
        service.send_notification({"商品标题": "Sony A7M4"}, "价格合适")
    )

    assert results["ok"]["success"] is True
    assert results["ok"]["message"] == "发送成功"
    assert results["fail"]["success"] is False
    assert results["fail"]["message"] == "boom"


def test_notification_service_filters_disabled_clients():
    service = NotificationService([_OkClient(enabled=False), _FailClient(enabled=True)])

    results = asyncio.run(
        service.send_notification({"商品标题": "Sony A7M4"}, "价格合适")
    )

    assert "ok" not in results
    assert "fail" in results


def test_notification_client_builds_message_with_mobile_link():
    client = _OkClient(enabled=True, pcurl_to_mobile=True)
    message = client._build_message(
        {
            "商品标题": "Sony A7M4 Full Frame Camera",
            "当前售价": "9999",
            "商品链接": "https://www.goofish.com/item?id=123456",
        },
        "价格合适",
    )

    assert message.title == "Sony A7M4 Full Frame Camera"
    assert message.price == "9999"
    assert message.reason == "价格合适"
    assert "pages.goofish.com" in message.mobile_link
    assert message.notification_title.startswith("🚨 新推荐!")


def test_webhook_client_renders_json_templates(monkeypatch):
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            return None

    def _fake_post(url, headers=None, json=None, data=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["data"] = data
        return _FakeResponse()

    monkeypatch.setattr("requests.post", _fake_post)

    client = WebhookClient(
        webhook_url="https://hooks.example.com/notify",
        webhook_method="POST",
        webhook_headers='{"Authorization":"Bearer token"}',
        webhook_content_type="JSON",
        webhook_query_parameters='{"task":"{{title}}"}',
        webhook_body='{"message":"{{content}}","link":"{{desktop_link}}"}',
        pcurl_to_mobile=False,
    )

    asyncio.run(
        client.send(
            {
                "商品标题": "Sony A7M4",
                "当前售价": "9999",
                "商品链接": "https://www.goofish.com/item/123",
            },
            "价格合适",
        )
    )

    assert "task=" in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer token"
    assert "9999" in captured["json"]["message"]
    assert captured["json"]["link"] == "https://www.goofish.com/item/123"
    assert captured["data"] is None
