---
tool_name: diagnose_network
version: v1.0
author: team
date: 2026-09-15
status: active
---

# Tool: diagnose_network

## Mô tả
Chạy **chẩn đoán mạng chi tiết** cho một thiết bị cụ thể (ping, DNS, VPN, gateway).
Tool **100% deterministic** (chỉ đọc từ `assets.json`), **không gọi network/external API**.

## Contract

### Input Parameters
| Tên | Loại | Mô tả | Required | Pattern | Example |
|-----|------|-------|----------|---------|---------|
| `asset_id` | string | Mã tài sản thiết bị | ✅ | `^(LT|DT)-\d{3}$` | `"LT-204"` |
| `checks` | string | Danh sách kiểm tra (phân cách bằng dấu phẩy): `ping`, `dns`, `vpn`, `gateway`, hoặc `all` | ❌ | - | `"all"`, `"ping,dns"`, `"vpn"` |

### Output Schema
```json
{
  "tool": "diagnose_network",
  "asset_id": "LT-204",
  "device_name": "ThinkPad T14 Gen 4",
  "device_type": "laptop",
  "location": "Bangkok floor 3",
  "assigned_to": "EMP-1001",
  "checks_performed": ["ping", "dns", "vpn", "gateway"],
  "results": {
    "ping": {
      "status": "ok" | "degraded" | "down" | "unknown",
      "detail": "online; latency 24 ms; DNS healthy",
      "latency": "24 ms"
    },
    "dns": {
      "status": "ok" | "degraded" | "down" | "unknown",
      "detail": "online; latency 24 ms; DNS healthy",
      "dns_state": "healthy"
    },
    "vpn": {
      "status": "ok" | "degraded" | "down" | "unknown",
      "detail": "client 5.2.1; last connection failed with AUTH_TIMEOUT"
    },
    "gateway": {
      "status": "ok" | "degraded" | "down" | "unknown",
      "detail": "online; latency 24 ms; DNS healthy"
    }
  },
  "network_status": "ok" | "degraded" | "down",
  "snapshot_at": "2026-09-14T09:00:00+07:00",
  "suggested_actions": {
    "issues": ["vpn"],
    "kb_articles": ["vpn-windows"]
  }
}
```

## Ví dụ

### ✅ Input: Thiết bị tồn tại, kiểm tra tất cả
```json
{"asset_id": "LT-204", "checks": "all"}
```

### ✅ Output: Thành công
```json
{
  "tool": "diagnose_network",
  "asset_id": "LT-204",
  "device_name": "ThinkPad T14 Gen 4",
  "device_type": "laptop",
  "location": "Bangkok floor 3",
  "assigned_to": "EMP-1001",
  "checks_performed": ["ping", "dns", "vpn", "gateway"],
  "results": {
    "ping": {
      "status": "ok",
      "detail": "online; latency 24 ms; DNS healthy",
      "latency": "24 ms"
    },
    "dns": {
      "status": "ok",
      "detail": "online; latency 24 ms; DNS healthy",
      "dns_state": "healthy"
    },
    "vpn": {
      "status": "down",
      "detail": "client 5.2.1; last connection failed with AUTH_TIMEOUT"
    },
    "gateway": {
      "status": "ok",
      "detail": "online; latency 24 ms; DNS healthy"
    }
  },
  "network_status": "degraded",
  "snapshot_at": "2026-09-14T09:00:00+07:00",
  "suggested_actions": {
    "issues": ["vpn"],
    "kb_articles": ["vpn-windows"]
  }
}
```

### ✅ Input: Chỉ kiểm tra ping và DNS
```json
{"asset_id": "DT-031", "checks": "ping,dns"}
```

### ✅ Output: Chỉ trả về ping và DNS
```json
{
  "tool": "diagnose_network",
  "asset_id": "DT-031",
  "device_name": "HP EliteDesk 800 G9",
  "device_type": "desktop",
  "location": "Bangkok floor 2",
  "assigned_to": "EMP-1003",
  "checks_performed": ["ping", "dns"],
  "results": {
    "ping": {
      "status": "ok",
      "detail": "online; latency 3 ms; DNS healthy",
      "latency": "3 ms"
    },
    "dns": {
      "status": "ok",
      "detail": "online; latency 3 ms; DNS healthy",
      "dns_state": "healthy"
    }
  },
  "network_status": "ok",
  "snapshot_at": "2026-09-14T09:00:00+07:00"
}
```

### ❌ Input: Asset ID không hợp lệ
```json
{"asset_id": "MY-LAPTOP"}
```

### ❌ Output: Lỗi format
```json
{
  "tool": "diagnose_network",
  "asset_id": "MY-LAPTOP",
  "error": "invalid_asset_id_format",
  "message": "Asset ID must match LT-XXX or DT-XXX (e.g. LT-204). 'MY-LAPTOP' is not valid."
}
```

### ❌ Input: Thiết bị không tìm thấy
```json
{"asset_id": "LT-999"}
```

### ❌ Output: Lỗi không tìm thấy
```json
{
  "tool": "diagnose_network",
  "asset_id": "LT-999",
  "error": "device_not_found",
  "message": "Device 'LT-999' not found in inventory."
}
```

## Error Handling
| Lỗi | Nguyên nhân | Output |
|-----|------------|--------|
| `invalid_asset_id_format` | asset_id không match `LT-XXX` hoặc `DT-XXX` | `{"error": "invalid_asset_id_format", "message": "..."}` |
| `device_not_found` | asset_id không có trong assets.json | `{"error": "device_not_found", "message": "..."}` |
| `assets_load_failed` | assets.json không thể đọc | `{"error": "assets_load_failed", "message": "..."}` |

## Side Effects
- **Không có**: Tool chỉ đọc (read-only), không ghi/thay đổi dữ liệu nào.

## Confirmation Boundary
- **Không yêu cầu**: Tool là read-only, không cần confirmation.

## Guardrails
- **Deterministic**: Chỉ đọc từ `assets.json` (tĩnh)
- **Input Validation**: Bắt buộc format `LT-XXX` hoặc `DT-XXX` (regex: `^(LT|DT)-\d{3}$`)
- **Error Handling**: Trả về error chi tiết (không crash)
- **Read-Only**: Không ghi file, không gọi external API
- **Scope**: Chỉ chẩn đoán mạng, không sửa chữa

## Smoke Test
```bash
python -c "from tools import TOOL_FUNCTIONS as T; import json; print(json.dumps(T['diagnose_network']('LT-204'), indent=2, default=str))"
```

## Eval Case Example
```json
{
  "id": "B03_diagnose_network",
  "phase": "B",
  "suite": "group",
  "query": "Chẩn đoán mạng chi tiết cho LT-204.",
  "failure_type": "wrong_tool",
  "expect": {
    "tool_calls": [{"name": "diagnose_network", "args": {"asset_id": "LT-204", "checks": "all"}}]
  },
  "metadata": {
    "skill": "network_diagnosis",
    "difficulty": "medium",
    "what_it_tests": "Kiểm tra chẩn đoán mạng chi tiết (ping, DNS, VPN, gateway) cho LT-204."
  }
}
```