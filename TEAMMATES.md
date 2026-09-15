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
| 4 | Vũ Hiếu Thiên | 2A202602867 | Soraishiro | `contrib/Soraishiro` | Tổng hợp và biên soạn báo cáo (Report) |
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
- **Biên soạn Báo cáo (Report):** Hoàn thiện nội dung chi tiết trong `starter_v0/artifacts/REPORT.md` (Phần A và Phần B).
- **Phân tích lỗi (Failure Analysis):** Tổng hợp và phân tích nguyên nhân các trường hợp thất bại ở mục B2, ghi nhận hướng khắc phục và các limitation.
- **Thu thập Evidence:** Ghi nhận số liệu Version evidence (B1), trích xuất Live chat transcripts (B4) và phân tích tối thiểu 3 case Adversarial testing (B4a).

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
| 4 | Vũ Hiếu Thiên | 2A202602867 | `Soraishiro` |  |  |
| 5 | Lê Tuấn Hưng | 2A202602665 | `Justroamming` | `755679c` | `feat(chu trình tối ưu khoa học V1,V2,V3): Hoàn thành việc nêu hypothesis, sửa file, và chạy eval suite 30/30 pass test case` |

