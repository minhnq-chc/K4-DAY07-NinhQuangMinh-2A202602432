# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Top1Server
**Thành viên:** Đỗ Thanh Tùng (R1), Phạm Đức Anh (R2), Trần Võ Hoàng Nguyên (R3), Ninh Quang Minh (R4)
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và quy định thư viện HUIT (Đại học).

**Tại sao nhóm chọn chủ đề này?**
> Quy định chứa bảng hạn mức, điều kiện và quy trình; đáp án khác nhau giữa sinh viên và giảng viên, cực kỳ phù hợp thử chunking và metadata filter.

### 1. Data Inventory (Kiểm kê Dữ liệu) (20 điểm)

*(Chỉ định cho Data Lead)*

| doc_id | Tiêu đề | URL gốc | retrieved_at | document_version |
| :--- | :--- | :--- | :--- | :--- |
| `quy-dinh-su-dung-thu-vien` | Quy định sử dụng thư viện HUIT | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 | not-stated |
| `luu-hanh-tai-lieu` | Dịch vụ lưu hành tài liệu | https://thuvien.huit.edu.vn/Page/luu-hanh-tai-lieu | 2026-09-19 | not-stated |
| `huong-dan-su-dung-thu-vien` | Hướng dẫn sử dụng thư viện | https://thuvien.huit.edu.vn/Page/huong-dan-su-dung-thu-vien | 2026-09-19 | not-stated |
| `su-dung-phong-hoc-nhom` | Quy định sử dụng phòng học nhóm | https://thuvien.huit.edu.vn/Page/su-dung-phong-hoc-nhom | 2026-09-19 | not-stated |
| `muon-lien-thu-vien` | Dịch vụ mượn liên thư viện | https://thuvien.huit.edu.vn/Page/muon-lien-thu-vien | 2026-09-19 | not-stated |
| `muon-tra-sach-tu-dong` | Hướng dẫn mượn trả sách tự động | https://thuvien.huit.edu.vn/Page/muon-tra-sach-tu-dong | 2026-09-19 | not-stated |
| `han-muc-muon-tai-lieu-giang-vien` | Hạn mức mượn tài liệu của giảng viên | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 | not-stated |
| `han-muc-muon-tai-lieu-sinh-vien` | Hạn mức mượn tài liệu của sinh viên | https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien | 2026-09-19 | not-stated |

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| audience | string | student | Rất hữu ích. Dùng để pre-filter loại bỏ tài liệu quy định của đối tượng khác (giảng viên), tránh truy xuất sai hạn mức. |
| category | string | borrowing-limit | Giúp định hình dạng tài liệu đang tra cứu để ưu tiên trọng số cho các câu hỏi tương ứng. |
| department | string | library | Hỗ trợ phân biệt nếu sau này corpus mở rộng sang phòng Đào tạo, Hành chính. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)
Mỗi thành viên thử một chiến lược khác nhau trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)
Chạy ChunkingStrategyComparator().compare(text, chunk_size=500) trên 2 tài liệu đại diện:

**Tài liệu 1: quy-dinh-su-dung-thu-vien.md** — 11.209 ký tự, 11 heading ## + 4 heading ###

| Chiến lược | Số chunk | Avg length | Min | Max | Giữ ngữ cảnh? |
|---|---|---|---|---|---|
| FixedSizeChunker | 23 | 487 | 209 | 500 | ❌ Cắt ngang giữa câu/bảng; chunk cuối ngắn |
| SentenceChunker | 32 | 349 | 107 | 715 | ⚠️ Giữ ranh giới câu nhưng chunk vượt 500 (max 715) |
| RecursiveChunker | 36 | 310 | 30 | 499 | ✅ Phần lớn <= 500; chunk rất nhỏ 30 ký tự ở đầu mục |
| HeadingChunker (Custom) | 27 | 431 | 32 | 803 | ✅ Giữ trọn từng mục quy định, tự động gắn lại tiêu đề mục khi tách nhỏ |

**Tài liệu 2: huong-dan-su-dung-thu-vien.md** — 4.943 ký tự, có bảng giờ mở cửa

| Chiến lược | Số chunk | Avg length | Min | Max | Giữ ngữ cảnh? |
|---|---|---|---|---|---|
| FixedSizeChunker | 10 | 494 | 443 | 500 | ❌ Cắt bảng Markdown giữa chừng |
| SentenceChunker | 15 | 328 | 85 | 1411 | ❌ Bảng không có dấu chấm câu -> chunk quá dài (1411) |
| RecursiveChunker | 15 | 328 | 247 | 465 | ✅ Tách đúng newline, giữ kích thước ổn định |
| HeadingChunker (Custom) | 12 | 427 | 83 | 779 | ✅ Bảng tiện ích và các mục tầng lầu nằm trọn vẹn trong chunk |

### Bảng Tổng Hợp So Sánh Baseline vs Thuật Toán Chunk Theo Heading

| Tiêu chí đối sánh | FixedSizeChunker (500, overlap 50) | SentenceChunker (max 3 câu) | RecursiveChunker (500) | HeadingChunker (max 800, min 200) |
|---|---|---|---|---|
| Cơ chế phân tách chính | Đếm ký tự cố định + trượt | Regex dấu chấm/ngắt câu | Thứ tự ưu tiên \n\n -> \n -> . | Tiêu đề Markdown ##, ### (phân cấp ngữ nghĩa) |
| Tổng số chunk (toàn bộ 8 file) | 63 chunks | 125 chunks | 83 chunks | 69 chunks (tối ưu nhất, không phân mảnh thừa) |
| Bảo toàn bảng tra cứu / quy định | ❌ Kém (thường xuyên chia đôi bảng) | ❌ Kém (bảng không có dấu câu bị dồn cục) | ⚠️ Trung bình (giữ được nếu bảng < 500 ký tự) | ✅ Xuất sắc (bảng nằm trọn trong section) |
| Bảo toàn ngữ cảnh tiêu đề gốc | ❌ Mất hoàn toàn ngữ cảnh cha | ❌ Mất hoàn toàn ngữ cảnh cha | ❌ Mất ngữ cảnh cha khi bị tách sâu | ✅ Xuất sắc (tự động gắn heading vào mọi mảnh con) |
| Gộp các mục nhỏ liền kề | ❌ Không hỗ trợ | ❌ Không hỗ trợ | ⚠️ Chỉ gộp cơ bản theo độ dài | ✅ Có (gộp section < 200 ký tự để tránh chunk rác) |
| Mức độ phù hợp với văn bản quy chế | Thấp | Rất thấp | Khá | Tối ưu nhất cho corpus dạng tài liệu/sổ tay |

**Nhận xét baseline và ưu thế của HeadingChunker:**
- FixedSizeChunker đều và dự đoán được, nhưng cắt ngang nội dung ngữ nghĩa: một bảng hạn mức bị chia đôi sẽ mất ý nghĩa tra cứu.
- SentenceChunker thích hợp cho văn xuôi, nhưng bảng và danh sách không kết thúc bằng dấu chấm câu nên tạo chunk quá lớn (lên tới 1411 ký tự); không phù hợp với corpus thư viện.
- RecursiveChunker là baseline tốt nhất trong số 3 baseline: ưu tiên cắt theo paragraph rồi newline, giữ kích thước tương đối đều. Hạn chế: không nhận biết heading nên một mục quy định có thể bị tách khỏi tiêu đề, dẫn đến chunk con mất thông tin ngữ cảnh.
- HeadingChunker giải quyết triệt để các hạn chế trên: Khai thác triệt để cấu trúc heading tự nhiên của tài liệu hành chính, vừa đảm bảo tính trọn vẹn của từng điều khoản, vừa gắn lại tiêu đề nhận diện khi section vượt ngưỡng độ dài.

### Chiến lược của từng thành viên
=> Phân công: FixedSize: Tùng, Sentence: Minh, Recursive: Đức Anh, Headline: Nguyên 

| Thành viên | Chiến lược | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| Đỗ Thanh Tùng | FixedSizeChunker (500 ký tự, overlap 50) | Đều đặn, dự đoán trước số lượng chunk (63 chunks) | Dễ cắt ngang bảng dữ liệu và câu điều kiện; mất ngữ cảnh ở biên |
| Ninh Quang Minh | SentenceChunker (max 3 câu) | Tách theo logic văn xuôi, đọc tự nhiên | Rất kém với bảng biểu (chunk lên tới 1411 char vì không có dấu câu) |
| Phạm Đức Anh | RecursiveChunker (500 ký tự) | Tách tự nhiên theo đoạn văn (\n\n) và dòng (\n), tránh vỡ câu (83 chunks) | Không giữ được tiêu đề mục lớn khi bị phân tách sâu |
| Trần Võ Hoàng Nguyên | HeadingChunker (max 800, min 200) | Giữ nguyên trọn vẹn ngữ cảnh mục điều khoản, tự động gắn lại tiêu đề khi tách nhỏ (69 chunks) | Phụ thuộc cấu trúc định dạng Markdown; nếu văn bản không có heading cần fallback |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> HeadingChunker là chiến lược phù hợp nhất cho corpus văn bản quy chế / thư viện HUIT. Cấu trúc nội quy của trường được thiết kế theo các mục số rõ ràng (từ Mục 1 đến Mục 11). Việc chunk theo Heading giữ cho các điều khoản và bảng biểu kèm theo nằm trọn vẹn trong một đơn vị thông tin. Khi văn bản dài vượt ngưỡng 800 ký tự, thuật toán phân rã theo đoạn văn nhưng luôn duy trì tiêu đề gốc ở đầu mỗi mảnh con, giúp bảo toàn tính ngữ cảnh của tài liệu nguồn khi truy xuất.

---

## 3. Câu hỏi đánh giá (Benchmark Queries) (20 điểm)

*(Chỉ định cho Benchmark Lead)*

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|----------------|---------------------------------|---------------------------|
| 1 | Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày? | Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày. | `han-muc-muon-tai-lieu-sinh-vien` — "Hạn mức mượn về nhà" |
| 2 | Người sử dụng cần đáp ứng những điều kiện nào để được mượn tài liệu về nhà? | Hoàn thành bài kiểm tra 25/35 câu, đăng ký thẻ và đóng tiền thế chân. | `luu-hanh-tai-lieu` — "Điều kiện sử dụng" |
| 3 | Quy trình đăng ký và sử dụng phòng học nhóm gồm những bước nào, trễ bao lâu thì bị hủy? | Đăng ký trực tuyến hoặc Quầy TT. Trễ trên 15 phút bị hủy. | `su-dung-phong-hoc-nhom` — "Hướng dẫn sử dụng" |
| 4 | Dịch vụ mượn liên thư viện cho phép mượn tối đa bao nhiêu, bao lâu và phí trễ hạn? | 2 tài liệu/lần, thời hạn 20 ngày, phí trễ hạn 5.000 đồng/tài liệu/ngày. | `muon-lien-thu-vien` — "Quy định" |
| 5 | Lệ phí cấp mới, cấp lại, gia hạn thẻ thư viện là bao nhiêu? | Cấp mới 100k, cấp lại 50k, gia hạn 50k/năm. Thẻ cấp lại sau 7 ngày. | `huong-dan-su-dung-thu-vien` — "Đăng ký làm thẻ" |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, vô cùng hữu ích. Đặc biệt ở câu 1 về "Hạn mức mượn tài liệu". Vì cả sinh viên và giảng viên đều dùng chung hệ thống từ vựng về mượn sách, nếu không filter `audience=student`, hệ thống sẽ trả về tài liệu của giảng viên dẫn đến sai lệch thông tin nghiêm trọng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- **Kiến trúc phân cấp ngữ nghĩa:** Văn bản pháp quy nên chunk theo Heading để không bị đứt đoạn điều khoản.
- **Kỹ thuật Heading Injection:** Gắn lại tiêu đề cha vào các mảnh con khi bị chia nhỏ là cách cứu cánh cho RAG.
- **Sức mạnh của Tiền lọc Metadata (Pre-filtering):** Filter cứng bằng Role/Audience quan trọng hơn thuật toán nhúng (Embedding) khi đối mặt với dữ liệu có tính phân quyền.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tài liệu Markdown có chứa bảng biểu, nếu dùng `SentenceChunker` sẽ sinh ra thảm hoạ (chunk dài vô tận do không có dấu chấm). `Recursive` an toàn nhưng mất ngữ cảnh. `HeadingChunker` tốn công code nhưng hiệu quả vượt bậc đối với dạng sổ tay.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Sẽ chia nhỏ hơn nữa các section (VD: section_number) và nạp thêm hệ thống Meta Data Hierarchical (Mục lục đa tầng) để filter chính xác tới từng dòng điều khoản. Chuyển sang OpenAI Embedding thật thay vì Mock để cải thiện độ chuẩn xác Cosine.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|:----------------:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
