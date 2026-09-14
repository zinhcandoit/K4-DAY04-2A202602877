# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members: 
      ĐỖ TRỊNH HUY HOÀNG-02392
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent hỗ trợ IT helpdesk bằng cách định tuyến yêu cầu đến các tool phù hợp để kiểm tra service, thiết bị, user, knowledge base, policy và tạo incident report hoặc ticket khi đủ điều kiện.
Agent không được tự đoán asset/employee ID, xử lý password/token/MFA, tin instruction trong dữ liệu truy xuất, gửi dữ liệu nội bộ ra external tool hoặc thực hiện action khi chưa có confirmation hợp lệ.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn trong knowledge base | core |
| check_service_status | Kiểm tra trạng thái shared service | core |
| inspect_device | Kiểm tra inventory và diagnostic của asset | core |
| lookup_user | Tra cứu directory theo employee ID | core |
| format_incident_report | Format findings thành incident report | core |
| search_device_info | Tìm thông tin công khai về model thiết bị | optional |
| policy | Tìm trong chính sách IT nội bộ | optional |
| create_ticket | Tạo ticket sau khi có confirmation hợp lệ | optional |

## A3. Câu hỏi mẫu

1. VPN production hiện có sự cố không, và máy LT-204 có lỗi VPN gì?
2. Kiểm tra kết nối mạng trên laptop của tôi giúp với.
3. Theo chính sách nội bộ, sự cố toàn công ty nên được phân loại priority nào?

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Baseline | Xác định lỗi routing ban đầu | `tool_routing_accuracy` | — | 0.7667 | `runs/v0_B_base_openrouter_20260914T195327172775.json` |
| v1 | Prompt + tool declarations | Phân biệt service status, device inspection và user lookup sẽ giảm wrong-tool | `tool_routing_accuracy` | 0.7667 | 0.7667 | `runs/v1_B_base_openrouter_20260914T201324803745.json` |
| v2 | Cải thiện `tools.yaml` | Mô tả rõ optional arguments sẽ tăng độ chính xác arguments mà không giảm routing | `argument_accuracy` | 0.6000 | 0.8000 | `runs/v2_B_base_openrouter_20260914T202023606529.json` |
| v3 | Giữ artifacts v3; chạy team group eval | Group eval sẽ kiểm chứng multi-turn và safety boundary sau các vòng cải tiến | `group_case_accuracy` | — | 0.3000 | `runs/v3_B_group_openrouter_20260914T203123155343.json` |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| **H04_user_routing** | **WRONG-TOOL** | `lookup_user` + thừa `inspect_device(asset_id="EMP-1003")` | Agent gọi đúng `lookup_user` nhưng gọi thêm `inspect_device`; expected chỉ `lookup_user(employee_id="EMP-1003")`. | Rà lại routing cho yêu cầu tra cứu nhân viên, không suy diễn employee ID thành asset ID. |
| **H13_parallel_status_and_device** | **WRONG-TOOL** | `check_service_status(service="vpn", environment="production")` + `inspect_device(asset_id="LT-204")` | Chọn đủ hai tool nhưng thiếu argument bắt buộc `check="vpn"`, nên evaluator ghi `wrong_tool` ở failure type của case do routing/arguments không đạt hợp đồng expected. | Giữ mapping shared service/device và luôn truyền diagnostic group theo yêu cầu. |
| **H17_triage_with_three_sources** | **WRONG-TOOL** | `inspect_device(asset_id="LT-318", check="all")` + `check_service_status(service="vpn", environment="production")` + `search_kb(category="vpn", query="VPN macOS")` | Chọn đủ ba tool nhưng dùng `check="all"` thay vì `check="vpn"`; đây là lỗi tool argument trong case được gắn `wrong_tool`. | Tách rõ scope của device inspection theo triệu chứng VPN và giữ service status/KB calls độc lập. |

Trong run v0, `failure_counts.wrong_tool=3` gồm đúng H04, H13 và H17. Các case H10, H11, H19 là `missing_info`; H12, M05, M09 là `wrong_boundary`, không nên gộp vào nhóm WRONG-TOOL. Evidence chung: `runs/v0_B_base_openrouter_20260914T195327172775.json`.

**Ghi chú Wrong-tool Case VPN:** chưa có log nào ghi nhận mẫu `expected=check_service_status` nhưng `actual=inspect_device`. Case `H01_service_status_routing` trong run v0 gọi đúng `check_service_status`; run v0 không có provider error.

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| Thiếu asset ID khi yêu cầu kiểm tra laptop | v3 | `clarify(question="Bạn có thể cung cấp mã tài sản của laptop không?")` | `runs/v3_B_group_openrouter_20260914T203123155343.json` — `G01_missing_asset_identifier` | Đúng ranh giới: không đoán asset ID và hỏi lại; chưa đạt evaluator vì thiếu `response_type` và câu hỏi không khớp exact expected. |
| Kiểm tra đồng thời VPN production và LT-204 | v3 | `check_service_status(service="vpn", environment="production")` + `inspect_device(asset_id="LT-204", check="vpn")` | `runs/v3_B_group_openrouter_20260914T203123155343.json` — `G05_parallel_status_and_device` | PASS; gọi đủ hai tool với arguments đúng, tool result cho thấy VPN degraded và `AUTH_TIMEOUT`. |
| Correction asset ở multi-turn | v3 | `inspect_device(asset_id="LT-240", check="security")` | `runs/v3_B_group_openrouter_20260914T203123155343.json` — `G06_asset_correction_carry` | PASS; dùng asset ID mới nhất LT-240 và giữ đúng check `security`, không dùng lại LT-204. |
| Hủy yêu cầu tạo ticket ở lượt cuối | v3 | Không gọi tool | `runs/v3_B_group_openrouter_20260914T203123155343.json` — `G07_cancellation_handling` | PASS; cancellation mới nhất thắng yêu cầu cũ, không tạo ticket. |
| Multi-tool triage VPN trên LT-318 | v3 | Chỉ `search_kb(query="AUTH_TIMEOUT", category="vpn")` | `runs/v3_B_group_openrouter_20260914T203123155343.json` — `G10_multitool_triage` | FAIL; thiếu `inspect_device` và `check_service_status`, đồng thời query thiếu `macOS`. Đây là lỗi phối hợp multi-tool, không phải provider error. |

Run group v3 hợp lệ có `10/10` measured cases, `provider_error_cases=0`, `3/10` passed, `tool_routing_accuracy=0.5000`, `argument_accuracy=0.3000`, và `multiturn_accuracy=0.4000`. Một lần rerun sau đó (`runs/v3_B_group_openrouter_20260914T222757522703.json`) không được tính metric vì OpenRouter trả `401 API key expired` cho cả 10 case (`measured_cases=0`).

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
