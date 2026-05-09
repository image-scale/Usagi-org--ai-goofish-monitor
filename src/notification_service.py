"""
Notification service and client abstractions.
Supports multiple notification channels with concurrent sending.
"""
import asyncio
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import quote

from src.utils import convert_goofish_link


@dataclass(frozen=True)
class NotificationMessage:
    title: str
    price: str
    reason: str
    desktop_link: str
    mobile_link: Optional[str]
    notification_title: str
    content: str
    image_url: Optional[str]


class NotificationClient(ABC):
    """Abstract base class for notification clients."""

    channel_key = "unknown"
    display_name = "Unknown Channel"

    def __init__(self, enabled: bool = False, pcurl_to_mobile: bool = True):
        self._enabled = enabled
        self._pcurl_to_mobile = pcurl_to_mobile

    def is_enabled(self) -> bool:
        """Check if client is enabled."""
        return self._enabled

    @abstractmethod
    async def send(self, product_data: Dict, reason: str) -> bool:
        """Send notification."""
        raise NotImplementedError

    def _build_message(self, product_data: Dict, reason: str) -> NotificationMessage:
        """Format message content from product data."""
        title = product_data.get('商品标题', 'N/A')
        price = product_data.get('当前售价', 'N/A')
        desktop_link = product_data.get('商品链接', '#')
        mobile_link = None

        if self._pcurl_to_mobile and desktop_link and desktop_link != "#":
            mobile_link = convert_goofish_link(desktop_link)

        content_lines = [
            f"价格: {price}",
            f"原因: {reason}",
        ]
        if mobile_link:
            content_lines.append(f"手机端链接: {mobile_link}")
            content_lines.append(f"电脑端链接: {desktop_link}")
        else:
            content_lines.append(f"链接: {desktop_link}")

        short_title = title[:30]
        suffix = "..." if len(title) > 30 else ""
        notification_title = f"🚨 新推荐! {short_title}{suffix}"

        main_image = product_data.get('商品主图链接')
        if not main_image:
            image_list = product_data.get('商品图片列表', [])
            if image_list:
                main_image = image_list[0]

        return NotificationMessage(
            title=title,
            price=price,
            reason=reason,
            desktop_link=desktop_link,
            mobile_link=mobile_link,
            notification_title=notification_title,
            content="\n".join(content_lines),
            image_url=main_image,
        )


class WebhookClient(NotificationClient):
    """Webhook notification client with template rendering."""

    channel_key = "webhook"
    display_name = "Webhook"

    def __init__(
        self,
        webhook_url: str,
        webhook_method: str = "POST",
        webhook_headers: Optional[str] = None,
        webhook_content_type: str = "JSON",
        webhook_query_parameters: Optional[str] = None,
        webhook_body: Optional[str] = None,
        pcurl_to_mobile: bool = True,
    ):
        super().__init__(enabled=bool(webhook_url), pcurl_to_mobile=pcurl_to_mobile)
        self._url = webhook_url
        self._method = webhook_method.upper()
        self._headers = self._parse_json(webhook_headers) or {}
        self._content_type = webhook_content_type.upper()
        self._query_params = webhook_query_parameters
        self._body_template = webhook_body

    def _parse_json(self, value: Optional[str]) -> Optional[dict]:
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def _render_template(self, template: str, message: NotificationMessage) -> str:
        """Replace template placeholders with message values."""
        replacements = {
            "{{title}}": message.notification_title,
            "{{content}}": message.content.replace("\n", "\\n"),
            "{{desktop_link}}": message.desktop_link,
            "{{mobile_link}}": message.mobile_link or message.desktop_link,
            "{{price}}": message.price,
            "{{reason}}": message.reason,
            "{{product_title}}": message.title,
        }
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        return result

    def _build_url_with_params(self, message: NotificationMessage) -> str:
        if not self._query_params:
            return self._url

        try:
            params = json.loads(self._render_template(self._query_params, message))
            query_parts = []
            for key, value in params.items():
                query_parts.append(f"{quote(key)}={quote(str(value))}")
            separator = "&" if "?" in self._url else "?"
            return f"{self._url}{separator}{'&'.join(query_parts)}"
        except (json.JSONDecodeError, TypeError):
            return self._url

    async def send(self, product_data: Dict, reason: str) -> bool:
        import requests

        message = self._build_message(product_data, reason)
        url = self._build_url_with_params(message)

        headers = dict(self._headers)
        json_data = None
        form_data = None

        if self._body_template:
            rendered = self._render_template(self._body_template, message)
            if self._content_type == "JSON":
                json_data = json.loads(rendered)
            else:
                form_data = rendered

        response = requests.post(
            url,
            headers=headers,
            json=json_data,
            data=form_data,
            timeout=30,
        )
        response.raise_for_status()
        return True


class NotificationService:
    """Service for sending notifications to multiple channels."""

    def __init__(self, clients: List[NotificationClient]):
        self.clients = [client for client in clients if client.is_enabled()]

    async def send_notification(
        self,
        product_data: Dict,
        reason: str,
    ) -> Dict[str, Dict[str, str | bool]]:
        """Send notification to all enabled channels."""
        if not self.clients:
            return {}

        tasks = [
            self._send_with_result(client, product_data, reason)
            for client in self.clients
        ]
        results = await asyncio.gather(*tasks)
        return {result["channel"]: result for result in results}

    async def _send_with_result(
        self,
        client: NotificationClient,
        product_data: Dict,
        reason: str,
    ) -> Dict[str, str | bool]:
        try:
            await client.send(product_data, reason)
            return {
                "channel": client.channel_key,
                "label": client.display_name,
                "success": True,
                "message": "发送成功",
            }
        except Exception as exc:
            return {
                "channel": client.channel_key,
                "label": client.display_name,
                "success": False,
                "message": str(exc),
            }
