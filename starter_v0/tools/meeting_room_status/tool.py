from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err

ASSETS_FILE = ROOT / "helpdesk_data" / "assets.json"
KB_DIR = ROOT / "helpdesk_data" / "knowledge_base"

ROOM_ID_PATTERN = re.compile(r"^RM-\d{3}$")

# Deterministic mapping of diagnostic text to status level.
# Status levels are derived from the raw diagnostic strings so the output is
# stable across runs as long as the fixture does not change.
_STATUS_KEYWORDS = {
    "ok": ["online; latency", "healthy", "current", "signed in", "valid", "enabled"],
    "degraded": ["degraded", "delayed", "warning", "behind", "stale", "offline on", "partial_outage"],
    "down": ["down", "unavailable", "disconnected", "stopped", "error", "failed", "link down", "packet loss"],
}


def _classify(diagnostic_text: str) -> str:
    """Deterministic status classification from a raw diagnostic string."""
    text = (diagnostic_text or "").lower()
    if not text:
        return "unknown"
    for level in ("down", "degraded", "ok"):
        for keyword in _STATUS_KEYWORDS.get(level, []):
            if keyword in text:
                return level
    return "unknown"


def _summarize(diagnostic_text: str) -> str:
    """Return a short deterministic summary of the raw diagnostic string."""
    text = (diagnostic_text or "").strip()
    if not text:
        return "No diagnostic data available."
    return text


def meeting_room_status(room_id: str = "") -> dict[str, Any]:
    """Check the full status of a meeting room from static inventory data.

    The tool is 100% deterministic: it only reads ``assets.json`` and the
    knowledge-base markdown files. No network calls, no external API, no
    side effects.

    Args:
        room_id: Meeting-room identifier, e.g. ``"RM-501"``. Must match the
            pattern ``RM-XXX`` where ``X`` is a digit.

    Returns:
        A dict with ``tool``, ``room_id``, per-component ``status``, raw
        ``diagnostics``, ``snapshot_at`` and, when issues are detected,
        ``suggested_actions`` with matching KB articles.
    """
    try:
        room_id = (room_id or "").strip().upper()

        if not ROOM_ID_PATTERN.fullmatch(room_id):
            return {
                "tool": "meeting_room_status",
                "room_id": room_id or None,
                "error": "invalid_room_id_format",
                "message": (
                    "Room ID must match RM-XXX (7 characters, e.g. RM-501). "
                    f"'{room_id}' is not valid."
                ),
            }

        try:
            assets_data = json.loads(ASSETS_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "tool": "meeting_room_status",
                "room_id": room_id,
                "error": "assets_load_failed",
                "message": f"Unable to load assets.json: {exc}",
            }

        room = next(
            (item for item in assets_data.get("assets", []) if item.get("asset_id") == room_id),
            None,
        )
        if not room:
            return {
                "tool": "meeting_room_status",
                "room_id": room_id,
                "error": "room_not_found",
                "message": f"Meeting room '{room_id}' not found in inventory.",
            }

        diagnostics = room.get("diagnostics", {})

        components = {
            "network": diagnostics.get("network", ""),
            "calendar": diagnostics.get("software", ""),
            "hardware": diagnostics.get("hardware", ""),
            "audio": diagnostics.get("hardware", ""),
        }

        status = {name: _classify(value) for name, value in components.items()}

        issues = [name for name, level in status.items() if level in ("down", "degraded")]

        kb_articles: list[dict[str, Any]] = []
        if issues:
            for kb_path in sorted(KB_DIR.glob("*.md")):
                try:
                    content = kb_path.read_text(encoding="utf-8")
                except Exception:
                    continue
                haystack = f"{kb_path.stem} {content}".lower()
                if any(token in haystack for token in ("meeting", "room", "audio", "camera", "microphone", "calendar")):
                    kb_articles.append({
                        "article_id": kb_path.stem,
                        "title": kb_path.stem.replace("-", " ").title(),
                        "content_preview": content[:200].strip() + "...",
                    })

        response: dict[str, Any] = {
            "tool": "meeting_room_status",
            "room_id": room_id,
            "name": room.get("model", room_id),
            "location": room.get("location", "Unknown"),
            "manufacturer": room.get("manufacturer", "Unknown"),
            "os": room.get("os", "Unknown"),
            "status": status,
            "diagnostics": {
                name: _summarize(value) for name, value in components.items()
            },
            "snapshot_at": assets_data.get("snapshot_at", "unknown"),
        }

        if issues:
            response["suggested_actions"] = {
                "issues": issues,
                "kb_articles": kb_articles[:3],
            }

        return response

    except Exception as exc:
        return err("meeting_room_status", exc)