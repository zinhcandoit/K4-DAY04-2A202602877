# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

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
| v0 | Baseline | Starter artifacts trước tối ưu | case_accuracy | N/A | 0.7000 | [v0_B_base_openrouter_20260914T184739206077.json](../runs/v0_B_base_openrouter_20260914T184739206077.json) |
| v1 | Routing | Chưa có run riêng chỉ đo routing | N/A | N/A | N/A | Chưa có run hợp lệ |
| v2 | Arguments | Mapping `check` và required arguments; run lịch sử có tên v1 nhưng nội dung thuộc v2 | case_accuracy | 0.7000 | 0.7667 | [v1_B_base_openrouter_20260914T193306721711.json](../runs/v1_B_base_openrouter_20260914T193306721711.json) |
| v3 | Context/clarify + Team Eval | Rerun bằng Gemini `gemini-3.6-flash`; kết quả bị giới hạn bởi provider errors và quota | case_accuracy | N/A | N/A | [v3-rerun-36flash_B_group_gemini_20260915T011726405136.json](../runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json) |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### Phân tích các mismatch `wrong_arg_value` trong baseline v0

Trong bốn file `data`, chỉ `eval_base.json` có các testcase dùng
`failure_type: wrong_arg_value`; `eval_group.json` chỉ liệt kê đây là một loại
lỗi được phép, còn `eval_helpdesk_extension.json` và `eval_adversarial.json`
không có testcase thuộc loại này. Trong run baseline, hai mismatch thực tế
được evaluator ghi là `observed_mismatch: wrong_arg_value` nằm ở `H13` và
`H17`. Lưu ý: cả hai case có `case_failure_type: wrong_tool` vì chúng kiểm thử
nhiều tool; lỗi cụ thể được phân tích ở đây là argument sai, không phải chọn sai
tên tool.

#### Case H13 — `H13_parallel_status_and_device`

```text
Case:
H13_parallel_status_and_device — VPN trên LT-204 lỗi; kiểm tra cả trạng thái
VPN production và máy đó.

Expected calls:
check_service_status({"service":"vpn","environment":"production"})
inspect_device({"asset_id":"LT-204","check":"vpn"})

Actual calls:
check_service_status({"service":"vpn","environment":"production"})
inspect_device({"asset_id":"LT-204"})

Observed mismatch:
`routing_correct=true`, nhưng `args_correct=false`: model chọn đúng hai tool
và truyền đúng service/environment/asset_id, nhưng thiếu argument check=vpn.
Evaluator ghi nhận: expected 'vpn', got None.

Tool execution result:
inspect_device vẫn chạy thành công và dùng giá trị mặc định check=all; kết quả
trả toàn bộ diagnostics thay vì chỉ nhóm VPN. Không có tool error, nhưng phạm vi
dữ liệu trả về rộng hơn yêu cầu.

Giả thuyết nguyên nhân:
Trong yêu cầu có hai nhánh song song, model đã ưu tiên chọn đúng tool nhưng
không giữ quy tắc ánh xạ "VPN trên một asset" thành check=vpn. Description của
inspect_device hiện còn chung chung và system prompt chưa quy định rõ cách
chọn giá trị check theo phạm vi chẩn đoán. Schema cho phép bỏ check vì chỉ
asset_id là required và default là all, nên omission không bị chặn ở interface.

Artifact dự định sửa:
Cách sửa đã áp dụng: thêm vào system_prompt.md quy tắc ánh xạ phạm vi chẩn đoán
sang giá trị check và yêu cầu truyền đủ argument cho từng nhánh. Đồng thời làm
rõ description của inspect_device trong tools.yaml và đổi check thành argument
bắt buộc; all chỉ còn là một enum hợp lệ cho yêu cầu tổng thể. Không sửa
implementation của tool.

Metric dự kiến thay đổi:
Giảm observed_mismatch_counts.wrong_arg_value từ 2 xuống 1 hoặc 0; tăng
argument_accuracy và case_accuracy, đồng thời giữ nguyên routing_accuracy.

Rủi ro regression:
Nếu bắt buộc truyền check trong mọi trường hợp, các yêu cầu kiểm tra tổng thể
có thể bị đổi thành một nhóm hẹp. Cần giữ ngoại lệ rõ ràng cho yêu cầu tổng
thể và kiểm tra lại H02 cùng các case inspect_device khác.
```

#### Case H17 — `H17_triage_with_three_sources`

```text
Case:
H17_triage_with_three_sources — kiểm tra VPN của LT-318, status VPN production
và tìm hướng dẫn VPN macOS.

Expected calls:
inspect_device({"asset_id":"LT-318","check":"vpn"})
check_service_status({"service":"vpn","environment":"production"})
search_kb({"category":"vpn"})

Actual calls:
inspect_device({"asset_id":"LT-318","check":"all"})
check_service_status({"service":"vpn","environment":"production"})
search_kb({"query":"VPN macOS","category":"vpn"})

Observed mismatch:
`routing_correct=true`, nhưng `args_correct=false`: đã gọi đủ ba tool và các
service/category đúng. Sai duy nhất ở inspect_device: check=all thay vì
check=vpn. Evaluator ghi nhận: expected 'vpn', got 'all'.

Tool execution result:
inspect_device trả thành công snapshot đầy đủ của LT-318, trong đó có thông tin
certificate VPN; search_kb cũng trả kết quả thành công. Không có tool error,
nhưng agent thu thập dư các nhóm diagnostics không được yêu cầu.

Giả thuyết nguyên nhân:
Khi phải phối hợp ba nguồn, model nhận diện đúng các intent nhưng dùng default
check=all cho nhánh device thay vì trích xuất phạm vi VPN từ câu "kiểm tra máy"
trong ngữ cảnh VPN. Đây là cùng một lỗi contract/routing argument như H13,
không phải lỗi dữ liệu hay lỗi search_kb.

Artifact dự định sửa:
Cách sửa đã áp dụng: system_prompt.md yêu cầu tách từng nhánh trong
multi-tool request và truyền argument cụ thể cho từng nhánh. tools.yaml mô tả
mapping của check và đánh dấu check là required để model không bỏ qua phạm vi
kiểm tra. Không sửa code tool.

Metric dự kiến thay đổi:
Giảm wrong_arg_value thêm một case; tăng argument_accuracy, multi-tool
accuracy và case_accuracy mà không làm tăng số tool call.

Rủi ro regression:
Prompt quá mạnh tay có thể khiến model bỏ sót các nhánh khác trong yêu cầu ba
nguồn hoặc biến mọi đề cập đến VPN thành inspect_device check=vpn dù người dùng
chỉ hỏi shared service. Cần regression-test H01, H02, H13 và H17.
```

Ghi chú: các case `H05`, `H06`, `M02`, `M03`, `M04` và `M08` có
`case_failure_type: wrong_arg_value` để kiểm thử, nhưng run v0 đều PASS và
không ghi nhận chúng là `observed_mismatch`; không nên báo cáo chúng như lỗi
baseline thực tế. Vì vậy không được suy ra rằng cả 7 testcase đều thất bại.

### Testcase dùng để kiểm chứng vòng sửa argument

Các testcase dưới đây là fixed eval trong `data/eval_base.json`, không phải
team-authored cases. Chúng được ghi lại để đối chiếu trực tiếp giữa baseline v0
và vòng v2 Arguments.

| Case | Input | Expected argument | Actual v0 | Kết quả v2 |
|---|---|---|---|---|
| H13 | VPN trên LT-204 lỗi; kiểm tra status VPN production và máy đó | `inspect_device(asset_id=LT-204, check=vpn)` | `inspect_device(asset_id=LT-204)`; thiếu `check` | PASS; truyền `check=vpn` |
| H17 | VPN trên LT-318 sắp hết certificate; kiểm tra máy, status VPN production và hướng dẫn VPN macOS | `inspect_device(asset_id=LT-318, check=vpn)` cùng `check_service_status(vpn, production)` và `search_kb(category=vpn)` | `inspect_device(asset_id=LT-318, check=all)`; các tool còn lại đúng | PASS; truyền `check=vpn` và giữ đủ 3 tool call |

Tiêu chí kiểm chứng: routing của từng nhánh phải giữ nguyên, argument `check`
phải phản ánh phạm vi người dùng yêu cầu, và số tool call không được tăng.

#### Khai báo testcase

```json
{
      "id": "H13_parallel_status_and_device",
      "query": "VPN trên LT-204 lỗi; kiểm tra cả trạng thái VPN production và máy đó.",
      "failure_type": "wrong_tool",
      "expect": {
            "tool_calls": [
                  {"name": "check_service_status", "args": {"service": "vpn", "environment": "production"}},
                  {"name": "inspect_device", "args": {"asset_id": "LT-204", "check": "vpn"}}
            ]
      }
}
```

```json
{
      "id": "H17_triage_with_three_sources",
      "query": "VPN trên LT-318 sắp hết certificate; kiểm tra máy, status VPN production và tìm hướng dẫn VPN macOS.",
      "failure_type": "wrong_tool",
      "expect": {
            "tool_calls": [
                  {"name": "inspect_device", "args": {"asset_id": "LT-318", "check": "vpn"}},
                  {"name": "check_service_status", "args": {"service": "vpn", "environment": "production"}},
                  {"name": "search_kb", "args": {"category": "vpn"}}
            ]
      }
}
```

### Kết luận file data và cách fix H13-H17

**File chứa testcase:** cả H13 và H17 nằm trong
[data/eval_base.json](../data/eval_base.json). Đây là fixed eval nên expected
arguments không được sửa.

**Các file data còn lại:**

- `data/eval_group.json` chỉ là template rỗng; `wrong_arg_value` chỉ nằm trong
      `allowed_failure_types`.
- `data/eval_helpdesk_extension.json` không có testcase `wrong_arg_value`.
- `data/eval_adversarial.json` không có testcase `wrong_arg_value`.

**Lỗi quan sát được:**

- H13: model gọi đúng `inspect_device` nhưng bỏ thiếu `check=vpn`, nên tool dùng
      default `all`.
- H17: model gọi đúng cả ba tool nhưng truyền `check=all` cho nhánh LT-318
      thay vì `check=vpn`.

**Nguyên nhân:** `tools.yaml` ban đầu cho phép bỏ `check` vì chỉ yêu cầu
`asset_id`, đồng thời dùng default `all`. `system_prompt.md` cũng chưa có quy
tắc ánh xạ phạm vi chẩn đoán sang enum `check`, đặc biệt khi request có nhiều
nhánh độc lập.

**Cách fix:**

1. Trong `system_prompt.md`, thêm mapping `VPN -> vpn`, Wi-Fi/kết nối ->
       `network`, security -> `security`, hardware -> `hardware`, software ->
       `software`; chỉ dùng `all` khi người dùng yêu cầu kiểm tra tổng thể.
2. Trong `tools.yaml`, mô tả rõ semantics của `inspect_device.check` và đổi
       `check` thành required: `[asset_id, check]`.
3. Chạy lại base suite sau thay đổi v2 để kiểm tra regression. H13 và H17 đã PASS, không còn
       `observed_mismatch: wrong_arg_value`; `case_accuracy` tăng từ `0.7000` lên
       `0.7667`, với `provider_error_cases=0` và đủ 30 case được đo.

Không sửa các file trong `data` vì chúng đang mô tả đúng expected behavior; sửa
data để làm điểm tăng sẽ làm mất giá trị của fixed evaluation.

### Kết quả vòng v2 — Arguments theo slide

- Hypothesis: làm rõ mapping `check` và bắt buộc argument này sẽ sửa lỗi
      `wrong_arg_value` của H13/H17.
- Evidence: run lịch sử được tạo bằng nhãn v1 nhưng được phân loại là evidence v2; đo đủ 30 case, `provider_error_cases=0`; H13 và H17 đều
      PASS, `wrong_arg_value` không còn trong observed mismatch.
- Metric: `case_accuracy` tăng từ 0.7000 lên 0.7667; `argument_accuracy` tăng
      từ 0.7000 lên 0.7667.
- Regression cần xử lý ở vòng sau: H04, H10, H11, H12, M05, M09 và H19 vẫn
      FAIL hoặc bị ảnh hưởng ở routing/clarify/boundary. Vì vậy v2 xác nhận giả
      thuyết cho argument scope nhưng chưa phải phiên bản cuối.

### Đối chiếu với chu trình v1-v2-v3 trong slide

Theo slide, lỗi H13 và H17 thuộc **v2 — Arguments** vì lỗi nằm ở giá trị
argument `inspect_device.check`, không nằm ở việc chọn tên tool:

- **v1 — Routing:** phân biệt `check_service_status` cho shared service với
      `inspect_device` cho asset cụ thể. H13/H17 đã chọn đúng các tool cần thiết.
- **v2 — Arguments:** ánh xạ VPN thành `check=vpn`, Wi-Fi/kết nối thành
      `check=network`, security thành `check=security`, hardware thành
      `check=hardware`; chỉ dùng `check=all` cho kiểm tra tổng thể. Đây là fix
      trực tiếp cho H13/H17.
- **v3 — Context & Clarify:** xử lý thiếu asset ID, carry-over/correction ở
      multi-turn và yêu cầu clarify khi thiếu thông tin. Đây không phải nguyên nhân
      chính của mismatch H13/H17.

Run evidence lịch sử hiện lưu với nhãn `v1`
([v1_B_base_openrouter_20260914T193306721711.json](../runs/v1_B_base_openrouter_20260914T193306721711.json)),
nhưng nội dung thay đổi được phân loại theo CSV và slide là **v2 — Argument
refinement**. Không đổi tên run cũ để giữ nguyên tính truy xuất của evidence.

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| G01_ambiguous_intent_device_vs_service | Ambiguous intent | Clarify device vs shared service | FAIL — missing tool call |
| G02_missing_asset_identifier | Missing identifier | Clarify asset ID | FAIL — missing tool call |
| G03_duplicate_tool_different_args | Duplicate tool args | Hai status calls: production và staging | PASS |
| G04_multiple_assets_comparison | Multiple assets | Hai inspect calls với hai asset IDs | PASS |
| G05_format_only_no_refetch | Format-only | Chỉ format findings, không refetch | Provider error — `TypeError` trong evaluator |
| G06_correction_turn_asset | Multi-turn correction | Asset mới nhất thắng asset cũ | Provider error — `503 UNAVAILABLE` |
| G07_cancellation_before_action | Cancellation | Không gọi action sau khi hủy | Provider error — `429 RESOURCE_EXHAUSTED` |
| G08_stale_confirmation_payload_change | Stale confirmation | Hỏi lại sau khi payload đổi | PASS |
| G09_external_internal_boundary | External boundary | Không gửi asset ID ra web | FAIL — wrong boundary / missing tool call |
| G10_policy_priority_mapping | Policy routing | `policy_area=incident_response` | Provider error — `429 RESOURCE_EXHAUSTED` |

**Latest evidence run:**
[v3-rerun-36flash_B_group_gemini_20260915T011726405136.json](../runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json)

Rerun bằng artifact `v3-rerun-36flash+p63f48c5a8389+t547e5780c423` và model
`gemini-3.6-flash` cho `10/10` case. Có `6` case được đo, `4` provider errors,
`3/6` PASS, `case_accuracy=0.5000`, `tool_routing_accuracy=0.5000`,
`argument_accuracy=0.5000`, `multiturn_accuracy=0.5000`. Theo quy ước của
lab, run này **không đủ điều kiện làm metric chính thức** vì chưa đo đủ 10 case
và vẫn có provider errors. Nó vẫn là evidence mới nhất để review hành vi model.

Provider errors gồm `503 UNAVAILABLE` ở G06 và `429 RESOURCE_EXHAUSTED` ở G07,
G10. G05 có lỗi evaluator `TypeError: '<' not supported between instances of
dict and dict`, không phải lỗi routing của model.

Các run OpenRouter trước đó vẫn là historical evidence; version log hiện trỏ
v3 vào rerun mới nhất này, không thay thế kết quả cũ bằng một metric không hợp lệ.

#### Phân tích failure của team eval

```text
Case:
G07_environment_carry_over

Expected calls:
check_service_status({"service":"email","environment":"staging"})

Actual calls:
check_service_status({"service":"email"})

Observed mismatch:
Đúng service=email nhưng thiếu environment=staging; evaluator ghi nhận
environment: expected 'staging', got None.

Tool execution result:
Không có tool result hợp lệ được dùng để chấm vì argument environment bị thiếu.

Giả thuyết nguyên nhân:
Model không giữ lại environment từ context multi-turn sau khi service đổi từ
VPN sang email; schema có default production ở service-status tool nên việc
bỏ argument không bị chặn trong call.

Artifact dự định sửa:
Ở vòng v3, bổ sung quy tắc context carry-over trong system_prompt.md: khi user
đổi service nhưng nói giữ nguyên môi trường, phải truyền lại environment mới
nhất trong call cuối. Có thể làm rõ tools.yaml rằng environment phải được truyền
explicit khi context đã nêu staging.

Metric dự kiến thay đổi:
Tăng argument_accuracy và multiturn_accuracy của group suite; giảm observed
wrong_arg_value từ 2 xuống 1 hoặc 0.

Rủi ro regression:
Không được giữ staging khi user đổi sang production, và yêu cầu mới nhất phải
thắng context cũ. Regression-test H06, M02 và G07.
```

```text
Case:
G09_device_and_status_parallel

Expected calls:
inspect_device({"asset_id":"LT-240","check":"vpn"})
check_service_status({"service":"vpn","environment":"production"})

Actual calls:
inspect_device({"asset_id":"LT-240","check":"vpn"})
check_service_status({"service":"vpn"})

Observed mismatch:
Đúng cả hai tool và đúng asset/check/service, nhưng status call thiếu
environment=production; evaluator ghi nhận environment: expected 'production',
got None.

Tool execution result:
Nhánh inspect_device có thể chạy đúng; nhánh status không truyền environment
explicit và có nguy cơ dùng default production, nên argument trace vẫn không
đúng contract dù giá trị runtime có thể trùng.

Giả thuyết nguyên nhân:
Trong multi-tool request, model trích xuất environment production nhưng không
lặp lại argument đó vào nhánh check_service_status. Đây là lỗi argument
completeness trong parallel call, không phải thiếu tool.

Artifact dự định sửa:
Bổ sung vào system_prompt.md quy tắc mỗi tool call độc lập phải chứa đầy đủ
arguments được yêu cầu trong câu hiện tại. Làm rõ tools.yaml rằng environment
phải truyền explicit khi người dùng nêu production/staging, kể cả khi có
default.

Metric dự kiến thay đổi:
Giảm observed wrong_arg_value và tăng argument_accuracy; giữ nguyên số tool
call và tool_routing_accuracy.

Rủi ro regression:
Prompt không được làm model thêm tool call hoặc đổi environment của nhánh
khác. Regression-test H01, H06, H13 và G09.
```

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| Shared service status: VPN production | v3 | Chưa có tool call; provider trả `429 RESOURCE_EXHAUSTED` trước khi model phản hồi | [v3_gemini_20260915T004450743946.transcript.json](../transcripts/v3_gemini_20260915T004450743946.transcript.json) | Historical transcript; không phải kết quả của rerun mới |
| G01-G10 team eval, rerun `gemini-3.6-flash` | v3-rerun-36flash | 3 PASS, 3 measured failures, 4 provider errors | [v3-rerun-36flash_B_group_gemini_20260915T011726405136.json](../runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json) | Latest rerun; không đủ điều kiện tính metric chính thức |

### Phân tích rerun mới nhất
Rerun mới nhất dùng cùng `data/eval_group.json` và cùng artifact hash đã ghi
trong `version_log.csv`. Run có `measured_cases=6` và `provider_error_cases=4`,
do đó không được dùng `case_accuracy=0.5000` như một metric chính thức. Ba
case PASS là G03, G04 và G08; G01, G02 và G09 là các failure hành vi/model.
G05 cần sửa evaluator trước khi đánh giá lại. G06, G07 và G10 cần rerun sau khi
Gemini ổn định hoặc dùng provider/model có quota phù hợp.

Version log hiện ghi đúng một run mới nhất cho v3:
`runs/v3-rerun-36flash_B_group_gemini_20260915T011726405136.json`. Các run
OpenRouter và Gemini cũ vẫn được giữ trong repository như historical evidence,
nhưng không được trộn vào summary của rerun này.

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
