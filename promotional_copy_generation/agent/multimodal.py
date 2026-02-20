"""Multimodal message utilities - build text+image content for LLM calls."""

import base64
from typing import Any

from langchain_core.messages import HumanMessage


def _guess_image_media_type(data: bytes) -> str:
    """Guess media type from image bytes."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:2] in (b"\xff\xd8",):
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def build_multimodal_content(text: str, images: list[bytes] | None = None) -> list[dict[str, Any]]:
    """
    Build content for HumanMessage - supports text-only or text+images.
    Used for text-only and text+image (text + images).
    """
    content: list[dict[str, Any]] = [{"type": "text", "text": text}]
    if images:
        for img in images:
            b64 = base64.b64encode(img).decode("ascii")
            media = _guess_image_media_type(img)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{media};base64,{b64}"},
            })
    return content


def build_human_message(text: str, images: list[bytes] | None = None) -> HumanMessage:
    """Build HumanMessage with optional images for multimodal LLM."""
    content = build_multimodal_content(text, images)
    return HumanMessage(content=content)
