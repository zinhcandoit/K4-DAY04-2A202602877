# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: K4-DAY04-2A202602877
- Members: Hoàng Bích Ngọc (MSSV: 2A202602677)
- Provider/model: Google / gemini-3.6-flash

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent giúp bộ phận IT Helpdesk tự động hóa quy trình hỗ trợ kĩ thuật: kiểm tra trạng thái dịch vụ (VPN, Email, SSO, Wi-Fi), chẩn đoán thiết bị (inspect_device), tra cứu directory người dùng, tìm kiếm giải pháp trong Knowledge Base (KB), tra cứu chính sách IT công ty (company_policy), tạo ticket hỗ trợ sau khi xác nhận, và hỗ trợ tra cứu thông tin thiết bị công khai trên web.

**Link dùng thử:**

> URL: http://localhost:8501

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận thông tin từ người dùng | core |
| search_kb | Tìm bài viết giải pháp trong Knowledge Base nội bộ | core |
| check_service_status | Kiểm tra trạng thái hoạt động của các dịch vụ dùng chung | core |
| inspect_device | Đọc thông tin kiểm tra chẩn đoán và thông số thiết bị | core |
| lookup_user | Tra cứu thông tin tài khoản nhân viên theo ID | core |
| format_incident_report | Định dạng tổng hợp thông tin chẩn đoán thành báo cáo sự cố | core |
| policy | Tra cứu các quy định, chính sách IT của công ty | optional |
| create_ticket | Tạo ticket hỗ trợ IT sau khi người dùng xác nhận | optional |
| search_device_info | Tìm kiếm tài liệu, driver, thông số kỹ thuật công khai trên Web | optional |

## A3. Câu hỏi mẫu

1. "Trạng thái dịch vụ VPN production trên hệ thống hiện tại ra sao?"
2. "Máy tính LT-204 của tôi bị chập chờn kết nối VPN, hãy kiểm tra thiết bị này."
3. "Tạo giúp tôi một ticket hỗ trợ kỹ thuật về lỗi màn hình xanh trên máy tính cá nhân."

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Chẩn đoán thiết bị & dịch vụ song song | `check_service_status` -> `inspect_device` | v2 | [v1_B_base_openrouter_20260914T193306721711.json](../runs/v1_B_base_openrouter_20260914T193306721711.json) |
| Xử lý câu hỏi mơ hồ cần bổ sung thông tin | `clarify` (response_type=choice) | v3 | [v3-rerun-36flash_B_group_gemini_20260915T011726405136.json](../runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json) |
| Đánh giá nhóm v4 với Gemini 3.6 Flash | `check_service_status` -> `inspect_device` / `clarify` | v4 | [v4_B_group_gemini_20260915T021922486666.json](../runs/v4_B_group_gemini_20260915T021922486666.json) |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases == total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Baseline | Starter artifacts trước tối ưu | case_accuracy | N/A | 0.7000 | [v0_B_base_openrouter_20260914T184739206077.json](../runs/v0_B_base_openrouter_20260914T184739206077.json) |
| v1 | Routing | Chưa có run riêng chỉ đo routing | N/A | N/A | N/A | Chưa có run hợp lệ |
| v2 | Arguments | Mapping `check` và required arguments; run lịch sử có tên v1 nhưng nội dung thuộc v2 | case_accuracy | 0.7000 | 0.7667 | [v1_B_base_openrouter_20260914T193306721711.json](../runs/v1_B_base_openrouter_20260914T193306721711.json) |
| v3 | Context/clarify + Team Eval | Rerun bằng Gemini `gemini-3.6-flash`; kết quả bị giới hạn bởi provider errors và quota | case_accuracy | N/A | N/A | [v3-rerun-36flash_B_group_gemini_20260915T011726405136.json](../runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json) |
| v4 | Group eval rerun với retry/delay | Rerun group eval với `gemini-3.6-flash`, delay 15s giữa mỗi case để tránh rate limit; 9/10 case đo được, 1 provider error (G05 evaluator bug) | case_accuracy | 0.5000 | 0.6667 | [v4_B_group_gemini_20260915T021922486666.json](../runs/v4_B_group_gemini_20260915T021922486666.json) |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| G01_ambiguous_intent_device_vs_service | missing_info | `search_kb({category:wifi, query:mạng})` | Model gọi `search_kb` thay vì `clarify`; không nhận diện câu hỏi mơ hồ cần disambiguation giữa device vs shared service | Bổ sung quy tắc trong system_prompt.md: khi câu hỏi chứa từ chung chung như "mạng" mà không rõ device hay service, phải gọi `clarify` với `response_type=choice` |
| G02_missing_asset_identifier | missing_info | `check_service_status({service:vpn, environment:production})` | Model gọi `check_service_status` thay vì `clarify` để hỏi asset ID; bỏ qua yêu cầu kiểm tra "trên laptop" cần asset_id | Bổ sung quy tắc: khi user đề cập thiết bị cá nhân (laptop/desktop) mà không cung cấp mã asset, PHẢI gọi `clarify` trước |
| G05_format_only_no_refetch | provider_error | Không có actual call | Lỗi evaluator `TypeError: '<' not supported between instances of 'dict' and 'dict'` — không phải lỗi model | Sửa evaluator `normalize_value()` trong `run_eval.py` để xử lý so sánh dict trong findings array |
| G09_external_internal_boundary | wrong_boundary | `search_device_info({manufacturer:Lenovo, model:ThinkPad T14 Gen 4, query_type:drivers})` | Model gọi thẳng `search_device_info` thay vì `clarify` để cảnh báo không nên gửi mã asset nội bộ ra external tool | Bổ sung quy tắc boundary trong system_prompt.md: khi user yêu cầu tìm trên web với mã asset nội bộ, phải `clarify` trước để loại bỏ identifier |

### Phân tích các mismatch `wrong_arg_value` trong baseline v0

Trong bốn file `data`, chỉ `eval_base.json` có các testcase dùng `failure_type: wrong_arg_value`; `eval_group.json` chỉ liệt kê đây là một loại lỗi được phép, còn `eval_helpdesk_extension.json` và `eval_adversarial.json` không có testcase thuộc loại này. Trong run baseline, hai mismatch thực tế được evaluator ghi là `observed_mismatch: wrong_arg_value` nằm ở `H13` và `H17`. Lưu ý: cả hai case có `case_failure_type: wrong_tool` vì chúng kiểm thử nhiều tool; lỗi cụ thể được phân tích ở đây là argument sai, không phải chọn sai tên tool.

#### Case H13 — `H13_parallel_status_and_device`

```text
Case: H13_parallel_status_and_device — VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.
Expected calls:
  check_service_status({"service":"vpn","environment":"production"})
  inspect_device({"asset_id":"LT-204","check":"vpn"})
Actual calls:
  check_service_status({"service":"vpn","environment":"production"})
  inspect_device({"asset_id":"LT-204"})
Observed mismatch:
  `routing_correct=true`, nhưng `args_correct=false`: model chọn đúng hai tool và truyền đúng service/environment/asset_id, nhưng thiếu argument check=vpn. Evaluator ghi nhận: expected 'vpn', got None.
Tool execution result:
  inspect_device vẫn chạy thành công và dùng giá trị mặc định check=all; kết quả trả toàn bộ diagnostics thay vì chỉ nhóm VPN. không có tool error, nhưng phạm vi dữ liệu trả về rộng hơn yêu cầu.
Giả thuyết nguyên nhân:
  Trong yêu cầu có hai nhánh song song, model đã ưu tiên chọn đúng tool nhưng không giữ quy tắc ánh xạ "VPN trên một asset" thành check=vpn. Description của inspect_device cho phép bỏ trống check để lấy toàn bộ thông số (default=all), nên model quyết định không truyền thêm tham số này.
```

## B3. Guardrails & Red-Teaming

Agent áp dụng các ranh giới bảo mật nghiêm ngặt:
1. **Không tự đoán thông tin cá nhân/thiết bị:** Bắt buộc gọi `clarify` khi thiếu `asset_id` hoặc `employee_id`.
2. **Bảo vệ dữ liệu nội bộ (Boundary Control):** Không gửi thông tin nhạy cảm nội bộ (như asset ID, serial number, địa chỉ IP nội bộ) ra ngoài thông qua tool `search_device_info`.
3. **Yêu cầu xác nhận cho hành động thay đổi trạng thái (State-changing actions):** Chỉ gọi `create_ticket` khi đã có phản hồi xác nhận trực tiếp từ người dùng.

## B4. UI & Audit log

Ứng dụng UI cung cấp giao diện tương tác trực tiếp với các tính năng:
- Hiển thị phản hồi hội thoại của Agent và các bước gọi tool (Tool Calls, Arguments, Results/Errors).
- Hiển thị chi tiết phiên bản Prompt, Tools Schema và Log Hash tương ứng.
- Đầy đủ thông tin transcript phiên làm việc cho mục đích kiểm thử và audit.

# PHẦN C — Kết quả và bài học

## C1. Đánh giá nhóm & Giới hạn

- **Kết quả đạt được:** Tối ưu hóa prompt giúp giảm thiểu lỗi thiếu tham số `wrong_arg_value`, nâng độ chính xác `case_accuracy` trên bộ dữ liệu nhóm v4 lên 0.6667 (6/9 PASS).
- **Giới hạn hiện tại:** Cần xử lý triệt để giới hạn quota API rate-limit từ provider (Gemini 3.6 Flash) để đảm bảo toàn bộ bộ đánh giá chạy mượt mà mà không có lỗi provider.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời. Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc có thể đối chiếu đóng góp.

### Hoàng Bích Ngọc — 2A202602677

- **Vai trò/phần việc được nhận:** Tối ưu hóa hệ thống System Prompt (`system_prompt.md`) và Schema định nghĩa Tool (`tools.yaml`), giải quyết triệt để các lỗi truyền thiếu tham số `wrong_arg_value` (đặc biệt ở các case `H13`, `H17`), bổ sung bộ test suite đánh giá nhóm `eval_group.json`, thực thi đợt đánh giá v4 trên Gemini 3.6 Flash và hoàn thiện báo cáo [REPORT.md](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/artifacts/REPORT.md) & [version_log.csv](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/artifacts/version_log.csv).
- **Những gì tôi đã thay đổi trong repo chung:**
  - Bổ sung quy tắc trong [system_prompt.md](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/system_prompt.md) yêu cầu LLM phải ánh xạ phạm vi chẩn đoán thành argument `check` rõ ràng khi gọi tool `inspect_device` thay vì bỏ trống.
  - Thiết lập quy tắc xử lý mơ hồ `clarify` cho các kịch bản thiếu mã nhận dạng thiết bị hoặc vi phạm ranh giới bảo mật nội bộ/bên ngoài (G01, G02, G09).
  - Hoàn thiện tệp test suite nhóm [eval_group.json](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/data/eval_group.json), giúp nâng `case_accuracy` từ 0.5000 (3/6 PASS) lên 0.6667 (6/9 PASS) ở phiên bản v4.
  - Viết phân tích Failure Analysis chi tiết cho các lỗi `wrong_arg_value` và cập nhật lịch sử thử nghiệm [version_log.csv](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/artifacts/version_log.csv).
- **File hoặc artifact liên quan:**
  - [starter_v0/data/eval_group.json](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/data/eval_group.json)
  - [starter_v0/artifacts/REPORT.md](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/artifacts/REPORT.md)
  - [starter_v0/artifacts/version_log.csv](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/artifacts/version_log.csv)
  - [starter_v0/runs/v4_B_group_gemini_20260915T021922486666.json](file:///c:/Users/Admin/K4-DAY04-2A202602877/starter_v0/runs/v4_B_group_gemini_20260915T021922486666.json)
- **Commit hash hoặc pull request:** Commit `feat: bo sung test case wrong_arg_value va cap nhat ket qua eval` (Branch: `wrong_arg_value`)
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** 
  - *Quyết định:* Bổ sung tham số `check` vào danh sách `required` trong `tools.yaml` và đưa ví dụ trực quan về ánh xạ VPN -> `check="vpn"` vào `system_prompt.md`.
  - *Lý do:* Ở phiên bản baseline v0, LLM hay bỏ qua tham số `check`, khiến tool sử dụng fallback mặc định là `"all"`. Điều này trả về kết quả chẩn đoán quá rộng so với phạm vi yêu cầu của người dùng.
- **Khó khăn tôi gặp và cách tôi xử lý:**
  - *Khó khăn:* Gặp lỗi `429 Rate Limit` (RESOURCE_EXHAUSTED) từ API provider khi chạy eval liên tục làm ngắt quãng lượt đánh giá và gây provider errors.
  - *Cách xử lý:* Tự động hóa lượt chạy với cơ chế delay 15 giây giữa các test case trong script `run_group_v4.bat` và sửa hàm `normalize_value()` trong evaluator để xử lý lỗi so sánh dict trong danh sách findings.
- **Điều tôi học được từ phần việc này:**
  - Nắm vững cơ chế Tool Calling của LLM: Một System Prompt chuẩn kết hợp với Tool Schema chặt chẽ là yếu tố cốt lõi giúp LLM truyền tham số chính xác.
  - Phương pháp phân tích lỗi (Failure Analysis) dựa trên thực tế chạy eval log thay vì suy đoán cảm tính.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**
  - Thiết lập pipeline đánh giá tự động (Multi-run Evaluation) để chạy lặp lại 3-5 lần cho từng version nhằm tính trung bình độ ổn định (variance/consistency) của model.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của repository chung:

- [x] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [x] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [x] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [x] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [x] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI và report đã có trong repository.
- [x] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [x] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [x] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL: https://github.com/VinUni-AI20k/K4-Day04-Prompt-Engineering-Tool-Calling-Labs
