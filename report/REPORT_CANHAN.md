# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ninh Quang Minh - 2A202602432
**Nhóm:** Top1Server
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Nghĩa là hai vector (đại diện cho hai đoạn văn bản) có hướng rất gần nhau trong không gian vector. Trong NLP, điều này chứng tỏ hai đoạn văn bản có sự tương đồng rất lớn về mặt ngữ nghĩa (cùng nói về một chủ đề hoặc ý nghĩa).

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên nộp học phí qua tài khoản ngân hàng."
- Câu B: "Học phí phải được sinh viên chuyển khoản."
- Tại sao tương đồng: Mặc dù sử dụng từ vựng khác nhau ("nộp", "tài khoản ngân hàng" vs "chuyển khoản"), nhưng embedding model hiểu được ngữ nghĩa cốt lõi của chúng là giống hệt nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên nộp học phí qua tài khoản ngân hàng."
- Câu B: "Sinh viên mở tài khoản ngân hàng nhận học bổng."
- Tại sao khác: Có sự trùng lặp từ vựng ("Sinh viên", "tài khoản ngân hàng") nhưng ý nghĩa hoàn toàn trái ngược (Nộp tiền học vs Nhận tiền thưởng).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Vì cosine similarity tập trung vào **góc** giữa hai vector để so sánh ý nghĩa, bất chấp độ dài văn bản (magnitude). Ngược lại, Euclidean distance bị ảnh hưởng rất mạnh bởi độ dài vector (một câu rất dài và một câu ngắn có thể có khoảng cách xa dù cùng ý).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23` (Đã kiểm tra chéo bằng mã nguồn).
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên thành 25 `ceil((10000 - 100) / 400)`. Ta thường muốn overlap lớn hơn để duy trì trọn vẹn mạch ngữ cảnh giữa các chunk liền kề, tránh rủi ro một ý tưởng hay câu văn quan trọng bị cắt làm đôi và mất nghĩa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu:* Dùng regex lookbehind `(?<=[.!?])\s+` để bắt khoảng trắng ngay sau dấu kết thúc câu, nhờ đó tách được câu mà không bị "nuốt" mất dấu câu. Tuy nhiên, edge case chưa xử lý được là các chữ viết tắt (VD: "TS.", "v.v.") và các số thập phân (đôi khi bị gõ nhầm với dấu cách) sẽ bị thuật toán nhận diện nhầm thành cuối câu và cắt sai.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu:* Thuật toán triển khai theo 2 chiều: đệ quy xuống sâu (cắt text bằng separator lớn, nếu mảnh vẫn dài hơn chunk_size thì gọi lại đệ quy với separator nhỏ hơn) và chiều gom lên (nối các mảnh nhỏ sát lại nhau cho vừa chunk_size để tránh sinh ra các mẩu vụn 5-10 ký tự). Base case dừng đệ quy khi mảnh hiện tại đã <= chunk_size, hoặc khi danh sách separator truyền vào bị rỗng `[]`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu:* `add_documents` biến Document thành một dict (record) lưu vào danh sách in-memory, chú ý copy metadata và cấp `doc_id` bằng id gốc. `search` tính toán độ tương đồng (dot product) giữa query và tất cả record, sau đó sort giảm dần. Khi trả về kết quả, em chủ động bỏ đi trường `embedding` (vector 1536 chiều) để giữ output sạch gọn.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu:* Trong `search_with_filter`, phải **lọc bằng metadata trước**, lấy ra tập ứng viên đạt chuẩn rồi mới search similarity. Nếu làm ngược lại (lấy top K rồi mới bỏ), ta có nguy cơ mất kết quả hợp lệ do các ứng viên sai đã chiếm hết K vị trí. `delete_document` chỉ đơn giản duyệt mảng và loại các record có `metadata['doc_id'] == doc_id`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu:* Nhịp 1: Truy xuất Top-K, nếu store rỗng trả về thông báo lỗi, tránh gọi LLM vô ích. Nhịp 2: Đóng gói các đoạn context, đánh số thứ tự `[1], [2]` kèm theo tên nguồn. Nhịp 3: Gài lệnh trong Prompt ép mô hình LLM phải trích dẫn theo đúng format `[x]` để phục vụ truy vết nguồn, đồng thời chặn việc LLM tự phịa ra kiến thức ngoài ngữ cảnh.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

### 5. Kết quả Benchmark (Benchmark Results) (20 điểm)

*(Điền bảng sau dựa trên kết quả chạy file `bench.py` của riêng bạn)*

| # | Câu hỏi (Query) | Lọc Metadata | Điểm số (0/1/2) | Lý do chấm điểm (Top-3 và Chuỗi đặc trưng) |
|---|----------------|--------------|----------------|-----------------|
| 1 | Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày? | KHÔNG | 0đ | Top 1 trả về quy-dinh-su-dung-thu-vien, không có chuỗi đáp án (do lỗi nhiễu MockEmbedder). |
| 1 | Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày? | CÓ (student) | 0đ | Top 3 có tài liệu đúng (han-muc...sinh-vien) nhưng không chứa chuỗi '03 tài liệu'. |
| 2 | Người sử dụng cần đáp ứng những điều kiện nào để được mượn tài liệu về nhà? | KHÔNG | 0đ | Top 3 không chứa chunk nào có chuỗi '25/35 câu'. |
| 3 | Quy trình đăng ký và sử dụng phòng học nhóm gồm những bước nào...? | KHÔNG | 0đ | Trả về sai tài liệu hoàn toàn (quy-dinh-su-dung...). |
| 4 | Dịch vụ mượn liên thư viện cho phép mượn tối đa bao nhiêu tài liệu...? | KHÔNG | 0đ | Sai tài liệu, không chứa thông tin '20 ngày'. |
| 5 | Lệ phí cấp mới, cấp lại, gia hạn thẻ thư viện là bao nhiêu...? | KHÔNG | 0đ | Top 3 có chứa tài liệu hướng dẫn nhưng không chứa chuỗi '50.000'. |

**Tự đánh giá chiến lược Chunking của bạn:**
> *Chiến lược của bạn (VD: Recursive) có điểm mạnh gì và điểm yếu gì khi đối mặt với 5 câu hỏi trên? Đề xuất cách khắc phục.*
Chiến lược sử dụng: **SentenceChunker** (ưu tiên cắt theo dấu chấm câu)..
Điểm mạnh: Code chạy mượt, chia chunk khá tự nhiên theo cấu trúc đoạn văn, không làm đứt gãy những đoạn văn dài.
Điểm yếu: Vì đang sử dụng MockEmbedder băm MD5 giả lập nên kết quả chấm điểm Similarity hoàn toàn là nhiễu, điểm số về 0 hết do vector không biểu diễn ngữ nghĩa. Ngoài ra, SentenceChunker không xử lý được các bảng biểu Markdown không có dấu chấm, tạo ra chunk quá dài và vỡ khối bảng biểu.
Đề xuất khắc phục: Chạy lại bài test với OpenAI Key hợp lệ. Đổi sang dùng HeadingChunker (như R3) để giữ ngữ cảnh quy định tốt hơn.
Điểm mạnh: Code chạy mượt, không bị lỗi cấu trúc, Document ID được ánh xạ đúng về nguồn gốc.
Điểm yếu: Vì đang sử dụng `MockEmbedder` băm MD5 giả lập nên kết quả chấm điểm Similarity hoàn toàn là nhiễu, điểm số về 0 hết. Thêm nữa, phần Metadata Filter thiết lập chưa tối ưu dẫn đến loại nhầm hoặc lọc quá chặt.
Đề xuất khắc phục: Chạy lại bài test với môi trường mạng ổn định và cấu hình OpenAI Key hợp lệ. Đồng thời tăng Overlap để tăng cơ hội khớp từ khóa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)
Chạy 5 câu hỏi đánh giá của nhóm trên mã nguồn cá nhân của bạn trong gói src. 5 câu hỏi này phải trùng với các thành viên cùng nhóm (xem REPORT_NHOM.md).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày? | muon-lien-thu-vien: Điền thông tin vào Phiếu đăng ký... | 0đ | Không | (Agent không thể trả lời do nhiễu từ MockEmbedder đưa thông tin sai lệch) |
| 2 | Người sử dụng cần đáp ứng những điều kiện nào để được mượn tài liệu về nhà? | su-dung-phong-hoc-nhom: Quy định sử dụng phòng học nhóm... | 0đ | Không | (Dữ liệu nhiễu, không liên quan) |
| 3 | Quy trình đăng ký và sử dụng phòng học nhóm gồm những bước nào... | quy-dinh-su-dung-thu-vien: Chỉ khi nào thanh toán xong các tài liệu... | 0đ | Không | (Dữ liệu nhiễu, không liên quan) |
| 4 | Dịch vụ mượn liên thư viện cho phép mượn tối đa bao nhiêu tài liệu... | muon-tra-sach-tu-dong: Chọn nút MƯỢN trên màn hình... | 0đ | Không | (Dữ liệu nhiễu, không liên quan) |
| 5 | Lệ phí cấp mới, cấp lại, gia hạn thẻ thư viện là bao nhiêu... | huong-dan-su-dung-thu-vien: Mượn liên thư viện. Các nguồn tài liệu điện tử... | 0đ | Không | (Dữ liệu nhiễu, không liên quan) |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Điều hay nhất em học được là từ chiến lược HeadingChunker của Nguyên (R3). Việc xử lý cắt văn bản pháp quy theo đoạn văn xuôi tuy nhanh nhưng làm mất đi ngữ cảnh, nhất là các bảng biểu. Việc chịu khó code regex bóc tách Heading và gán (inject) lại tiêu đề gốc vào từng chunk nhỏ giúp RAG hiểu rõ ngữ cảnh của đoạn text con đó thuộc về quy định nào.

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|:---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
