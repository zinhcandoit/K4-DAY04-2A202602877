# Danh sách thành viên và phân công đóng góp — Lab Day 04

## 1. Thông tin chung

- **Tên repository:** K4-DAY04-2A202602877
- **Bài Lab:** Day 04 — IT Helpdesk Agent
- **Model Provider:** OpenRouter (`openai/gpt-4o-mini`)

## 2. Danh sách thành viên

| STT | Họ và tên | MSSV | GitHub Username | Branch đóng góp | Vai trò chính |
|:---:|---|:---:|---|---|---|
| 1 | Thiều Quang Vinh | 2A202602877 | zinhcandoit | `main` / `contrib/zinhcandoit` | Trưởng nhóm, Version control & Quản trị repository |
| 2 | Đỗ Trịnh Huy Hoàng | 2A202602392 | HuyHoang1977 | `contrib/HuyHoang1977` | Phát triển giao diện người dùng (UI) |
| 3 | Hoàng Bích Ngọc | 2A202602766 | Ngocngoc12 | `contrib/Ngocngoc12` | Thiết kế bộ đánh giá nhóm (Group eval set) |
| 4 | Vũ Hiếu Thiên | 2A202602867 | Soraishiro | `contrib/Soraishiro` | Tool & Schema Engineer / Eval & Red-Team / Security & Bonus Tool / Report |
| 5 | Lê Tuấn Hưng | 2A202602665 | Justroamming | `contrib/Justroamming` | Tinh chỉnh Prompt, Tool schema & Version log |

## 3. Phân công nhiệm vụ chi tiết

### 1. Thiều Quang Vinh (Trưởng nhóm)
- **Quản trị repository:** Tạo fork, quản lý quyền cộng tác của các thành viên, thiết lập quy trình làm việc trên Git.
- **Version control:** Theo dõi tiến độ các branch `contrib/<username>`, thực hiện code review và merge đóng góp vào branch `main`.
- **Điều phối chung:** Khởi tạo file `TEAMMATES.md`, kiểm tra repository checklist trước khi nộp và nộp URL trên VLearn.

### 2. Lê Tuấn Hưng
- **Tinh chỉnh System Prompt:** Nghiên cứu và tối ưu hóa các quy tắc trong `starter_v0/artifacts/system_prompt.md` (điều hướng ngữ cảnh đa lượt, multi-turn correction, cancellation, confirmation boundary).
- **Chuẩn hóa Tool Schema:** Tinh chỉnh các định nghĩa trong `starter_v0/artifacts/tools.yaml` (ngữ nghĩa tham số, enum phân loại, ranh giới ghi dữ liệu write action, phòng tránh overfitting).
- **Ghi nhận Version Log:** Cập nhật file `starter_v0/artifacts/version_log.csv` theo sát chu trình thực nghiệm các phiên bản `v0`, `v1`, `v2`, `v3`.

### 3. Hoàng Bích Ngọc
- **Thiết kế Group Eval Set:** Xây dựng bộ test case đánh giá riêng của nhóm trong `starter_v0/data/eval_group.json` gồm đúng 10 case (5 single-turn và 5 multi-turn).
- **Bao phủ Failure Modes:** Đảm bảo bộ eval bao quát các kịch bản quan trọng được nêu trong `LAB-GUIDE.md` (ambiguous intent, missing identifier, stale confirmation, cancellation, parallel tool calls).
- **Thực nghiệm đánh giá:** Chạy eval trên bộ case nhóm và đối chiếu tính chính xác của tool routing và arguments.

### 4. Đỗ Trịnh Huy Hoàng
- **Phát triển giao diện UI:** Xây dựng và hoàn thiện giao diện chat tương tác người dùng (`starter_v0/chat.py` hoặc UI mở rộng).
- **Kiểm thử tương tác:** Kiểm tra hiển thị chi tiết các lượt gọi tool, tham số truyền vào, kết quả thực thi và trạng thái an toàn.
- **Trải nghiệm người dùng:** Tối ưu hóa phản hồi của agent trên giao diện, hỗ trợ hiển thị artifact version và hash kiểm tra.

### 5. Vũ Hiếu Thiên
- **Tạo Bonus Tools (2 tools hoàn chỉnh):** `meeting_room_status` & `diagnose_network` — code, TOOL.md, schema, `__init__.py`, register vào `tools.yaml` & `tools/__init__.py` (commit `3487762`)
- **System Prompt Engineering (v1→v6):** Refactor hoàn toàn `system_prompt.md` thành 6 sections (Confirmation, No-Guessing, Invalid Format, Safety, Routing, Arguments); fix routing boundary `inspect_device` vs `diagnose_network`; argument extraction rules; confirmation single-use; invalid format → immediate refuse; user-initiated confirmation flow (fix E05/E08/B02/B05)
- **Tools.yaml Overhaul:** Thêm schema 2 bonus tools, làm rõ boundary, mapping policy_area (configuration→service_operations), argument extraction hints (check mapping: pin/battery→hardware)
- **Eval Set Design:** Thiết kế 10 cases G01-G10 trong `eval_group.json` (5 single-turn, 5 multi-turn) bao phủ ambiguous intent, missing identifier, stale confirmation, cancellation, parallel calls, external boundary; Tách 5 bonus cases B01-B05 ra `eval_bonus.json` riêng
- **Adversarial Suite (12 cases A01-A12):** Stale confirmation, role spoofing, forged tool results, argument smuggling, sensitive data, injection probes, external ID smuggling
- **Evidence & Reporting:** `case_eval_evidence.md` (mapping 67 cases), B4 Live chat evidence (28 scenarios), B4a Adversarial analysis, version_log.csv tracking, REPORT.md (Phần A, B, C)
- **Security Hardening & Cleanup:** Fix H04/H17/M06 routing, E05/E08 confirmation, B02/B05 invalid format refuse, A10/A11 attacks blocked; Clean `.env`, `tickets/` leakage; Restore eval_group.json 10 cases

## 4. Bảng đối chiếu commit đóng góp

Theo quy định tại `SUBMISSION-GUIDE.md`, mỗi thành viên phải có ít nhất một commit được merge vào branch nộp bài (`main`), kiểm tra qua lệnh:

```powershell
git log --format="%h | %an <%ae> | %s"
```

| STT | Họ và tên | MSSV | Git Author Name | Commit Hash tiêu biểu | Nội dung đóng góp trong commit |
|:---:|---|:---:|---|---|---|
| 1 | Thiều Quang Vinh | 2A202602877 | `zinhcandoit` | `8dc876b` | `report(reflect): add reflection for group (khởi tạo TEAMMATES.md và hoàn thiện reflection nhóm)` |
| 2 | Đỗ Trịnh Huy Hoàng | 2A202602392 | `HuyHoang1977` | `a154332` | `Add Streamlit helpdesk demo UI (phát triển streamlit_app.py và cập nhật requirements.txt)` |
| 3 | Hoàng Bích Ngọc | 2A202602677 | `Ngocngoc12` | `50641c9` | `feat(eval): thiết kế 10 test cases trong eval_group.json` |
| 4 | Vũ Hiếu Thiên | 2A202602867 | `Soraishiro` | `3487762` `abe4191` `1978849` `f35e230` | `v5: fix routing boundary, bonus tools, eval cases`; `integrate group reflection`; `separate eval_bonus.json, clean .env/tickets`; `update self-reflection` |
| 5 | Lê Tuấn Hưng | 2A202602665 | `Justroamming` | `755679c` | `feat(chu trình tối ưu khoa học V1,V2,V3): Hoàn thành việc nêu hypothesis, sửa file, và chạy eval suite 30/30 pass test case` |

