from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err

ASSETS_FILE = ROOT / "helpdesk_data" / "assets.json"

ASSET_ID_PATTERN = re.compile(r"^(LT|DT)-\d{3}$")

_STATUS_KEYWORDS = {
    "ok": ["online", "healthy", "current", "valid", "enabled", "latency"],
    "degraded": ["degraded", "delayed", "warning", "behind", "stale", "partial", "packet loss", "fallback"],
    "down": ["offline", "down", "unavailable", "disconnected", "stopped", "error", "failed", "link down"],
}


def _classify_network(text: str) -> str:
    """Deterministic network status classification from diagnostic text."""
    t = (text or "").lower()
    if not t:
        return "unknown"
    for level in ("down", "degraded", "ok"):
        for kw in _STATUS_KEYWORDS.get(level, []):
            if kw in t:
                return level
    return "unknown"


def _extract_latency(text: str) -> str | None:
    """Extract latency value from diagnostic text if present."""
    match = re.search(r"latency\s+(\d+\s*ms)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(\d+\s*ms)\s*latency", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_dns(text: str) -> str | None:
    """Extract DNS status from diagnostic text."""
    t = (text or "").lower()
    if "dns healthy" in t:
        return "healthy"
    if "dns fallback" in t:
        return "fallback_active"
    if "dns" in t:
        return "mentioned"
    return None


def diagnose_network(asset_id: str = "", checks: str = "all") -> dict[str, Any]:
    """Run detailed network diagnostics for a specific device.

    The tool is 100% deterministic: it only reads from ``assets.json``.
    No live network calls, no external API, no side effects.

    Args:
        asset_id: Device identifier, e.g. ``"LT-204"``. Must match pattern
            ``LT-XXX`` or ``DT-XXX`` where ``X`` is a digit.
        checks: Comma-separated list of checks to run: ``ping``, ``dns``,
            ``vpn``, ``gateway``, or ``all`` (default).

    Returns:
        A dict with ``tool``, ``asset_id``, per-check results, overall
        ``network_status``, ``snapshot_at``, and optional ``suggested_actions``.
    """
    try:
        asset_id = (asset_id or "").strip().upper()
        checks_list = [c.strip().lower() for c in (checks or "all").split(",")]

        if not ASSET_ID_PATTERN.fullmatch(asset_id):
            return {
                "tool": "diagnose_network",
                "asset_id": asset_id or None,
                "error": "invalid_asset_id_format",
                "message": (
                    "Asset ID must match LT-XXX or DT-XXX (e.g. LT-204). "
                    f"'{asset_id}' is not valid."
                ),
            }

        try:
            assets_data = json.loads(ASSETS_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "tool": "diagnose_network",
                "asset_id": asset_id,
                "error": "assets_load_failed",
                "message": f"Unable to load assets.json: {exc}",
            }

        device = next(
            (item for item in assets_data.get("assets", []) if item.get("asset_id") == asset_id),
            None,
        )
        if not device:
            return {
                "tool": "diagnose_network",
                "asset_id": asset_id,
                "error": "device_not_found",
                "message": f"Device '{asset_id}' not found in inventory.",
            }

        diagnostics = device.get("diagnostics", {})
        network_text = diagnostics.get("network", "")
        vpn_text = diagnostics.get("vpn", "")

        results: dict[str, Any] = {}
        issues: list[str] = []

        # Ping / connectivity check
        if "all" in checks_list or "ping" in checks_list:
            status = _classify_network(network_text)
            latency = _extract_latency(network_text)
            results["ping"] = {
                "status": status,
                "detail": network_text,
                "latency": latency,
            }
            if status in ("down", "degraded"):
                issues.append("ping")

        # DNS check
        if "all" in checks_list or "dns" in checks_list:
            dns_status = _extract_dns(network_text)
            dns_ok = dns_status == "healthy"
            results["dns"] = {
                "status": "ok" if dns_ok else ("degraded" if dns_status else "unknown"),
                "detail": network_text,
                "dns_state": dns_status,
            }
            if not dns_ok and dns_status:
                issues.append("dns")

        # VPN check
        if "all" in checks_list or "vpn" in checks_list:
            vpn_status = _classify_network(vpn_text)
            results["vpn"] = {
                "status": vpn_status,
                "detail": vpn_text,
            }
            if vpn_status in ("down", "degraded"):
                issues.append("vpn")

        # Gateway check (inferred from network text)
        if "all" in checks_list or "gateway" in checks_list:
            gateway_status = "ok"
            if "packet loss" in network_text.lower():
                gateway_status = "degraded"
            if "link down" in network_text.lower() or "offline" in network_text.lower():
                gateway_status = "down"
            results["gateway"] = {
                "status": gateway_status,
                "detail": network_text,
            }
            if gateway_status in ("down", "degraded"):
                issues.append("gateway")

        overall_status = "ok"
        if any(r.get("status") == "down" for r in results.values()):
            overall_status = "down"
        elif any(r.get("status") == "degraded" for r in results.values()):
            overall_status = "degraded"

        response: dict[str, Any] = {
            "tool": "diagnose_network",
            "asset_id": asset_id,
            "device_name": device.get("model", asset_id),
            "device_type": device.get("type", "unknown"),
            "location": device.get("location", "Unknown"),
            "assigned_to": device.get("assigned_to"),
            "checks_performed": checks_list,
            "results": results,
            "network_status": overall_status,
            "snapshot_at": assets_data.get("snapshot_at", "unknown"),
        }

        if issues:
            kb_suggestions = []
            for issue in issues:
                if issue == "ping":
                    kb_suggestions.append("wifi-windows")
                elif issue == "dns":
                    kb_suggestions.append("wifi-windows")
                elif issue == "vpn":
                    kb_suggestions.append("vpn-windows")
                elif issue == "gateway":
                    kb_suggestions.append("wifi-windows")
            response["suggested_actions"] = {
                "issues": issues,
                "kb_articles": kb_suggestions[:3],
            }

        return response

    except Exception as exc:
        return err("diagnose_network", exc)