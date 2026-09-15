---
tool_name: meeting_room_status
version: v1.0
author: team
date: 2026-09-14
status: active
---

# Tool: meeting_room_status

## Mô tả
Kiểm tra **trạng thái đầy đủ** của phòng họp trong hệ thống IT của Northstar Labs.
Tool **100% deterministic** (chỉ đọc từ `assets.json` và `knowledge_base/`), **không gọi network/external API**.

## Contract

### Input Parameters
| Tên | Loại | Mô tả | Required | Pattern | Example |
|-----|------|-------|----------|---------|---------|
| `room_id` | string | Mã phòng họp | ✅ | `^RM-\d{3}$` | `"RM-501"` |

### Output Schema
```json
{
  "tool": "meeting_room_status",
  "room_id": "RM-501",
  "name": "Rally Bar",
  "location": "Bangkok room BKK-501",
  "manufacturer": "Logitech",
  "os": "CollabOS 1.13",
  "status": {
    "network": "ok" | "degraded" | "down" | "unknown",
    "calendar": "ok" | "degraded" | "down" | "unknown",
    "hardware": "ok" | "degraded" | "down" | "unknown",
    "audio": "ok" | "degraded" | "down" | "unknown"
  },
  "diagnostics": {
    "network": "online; latency 5 ms; VLAN correct",
    "calendar": "Teams Rooms signed in; calendar sync delayed by 8 minutes",
    "hardware": "camera healthy; right microphone pod disconnected",
    "audio": "camera healthy; right microphone pod disconnected"
  },
  "snapshot_at": "2026-09-14T09:00:00+07:00",
  "suggested_actions": {
    "issues": ["calendar", "hardware", "audio"],
    "kb_articles": [
      {"article_id": "meeting-room-audio", "title": "Meeting Room Audio Troubleshooting", "content_preview": "..."}
    ]
  }
}
```

## Ví dụ

### ✅ Input: Phòng họp tồn tại
```json
{"room_id": "RM-501"}
```

### ✅ Output: Thành công
```json
{
  "tool": "meeting_room_status",
  "room_id": "RM-501",
  "name": "Rally Bar",
  "location": "Bangkok room BKK-501",
  "manufacturer": "Logitech",
  "os": "CollabOS 1.13",
  "status": {
    "network": "ok",
    "calendar": "degraded",
    "hardware": "down",
    "audio": "down"
  },
  "diagnostics": {
    "network": "online; latency 5 ms; VLAN correct",
    "calendar": "Teams Rooms signed in; calendar sync delayed by 8 minutes",
    "hardware": "camera healthy; right microphone pod disconnected",
    "audio": "camera healthy; right microphone pod disconnected"
  },
  "snapshot_at": "2026-09-14T09:00:00+07:00",
  "suggested_actions": {
    "issues": ["calendar", "hardware", "audio"],
    "kb_articles": [
      {
        "article_id": "meeting-room-audio",
        "title": "Meeting Room Audio Troubleshooting",
        "content_preview": "---\narticle_id: KB-ROOM-010\ntitle: Chẩn đoán microphone và camera phòng họp\ncategory: meeting_room\n..."
      }
    ]
  }
}
```

### ❌ Input: Room ID không hợp lệ
```json
{"room_id": "PHONG-A"}
```

### ❌ Output: Lỗi format
```json
{
  "tool": "meeting_room_status",
  "room_id": "PHONG-A",
  "error": "invalid_room_id_format",
  "message": "Room ID must match RM-XXX (7 characters, e.g. RM-501). 'PHONG-A' is not valid."
}
```

## Error Handling
| Lỗi | Nguyên nhân | Output |
|-----|------------|--------|
| `invalid_room_id_format` | room_id không match `RM-XXX` | `{"error": "invalid_room_id_format", "message": "..."}` |
| `room_not_found` | room_id không có trong assets.json | `{"error": "room_not_found", "message": "..."}` |
| `assets_load_failed` | assets.json không thể đọc | `{"error": "assets_load_failed", "message": "..."}` |

## Side Effects
- **Không có**: Tool chỉ đọc (read-only), không ghi/thay đổi dữ liệu nào.

## Confirmation Boundary
- **Không yêu cầu**: Tool là read-only, không cần confirmation.

## Guardrails
- **Deterministic**: Chỉ đọc từ `assets.json` (tĩnh) + `knowledge_base/` (tĩnh)
- **Input Validation**: Bắt buộc format `RM-XXX` (regex: `^RM-\d{3}$`)
- **Error Handling**: Trả về error chi tiết (không crash)
- **Read-Only**: Không ghi file, không gọi external API

## Smoke Test
```bash
python -c "from tools import TOOL_FUNCTIONS as T; import json; print(json.dumps(T['meeting_room_status']('RM-501'), indent=2, default=str))"
```

## Eval Case Example
```json
{
  "id": "B01_meeting_room_status",
  "phase": "B",
  "suite": "group",
  "query": "Kiểm tra trạng thái phòng họp RM-501.",
  "failure_type": "wrong_tool",
  "expect": {
    "tool_calls": [{"name": "meeting_room_status", "args": {"room_id": "RM-501"}}]
  },
  "metadata": {
    "skill": "meeting_room_diagnosis",
    "difficulty": "medium",
    "what_it_tests": "Kiểm tra trạng thái đầy đủ của phòng họp RM-501."
  }
}
```