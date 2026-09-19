# 🎤 KỊCH BẢN THUYẾT TRÌNH (DEMO) - NHÓM TOP1SERVER

**Thời lượng:** 6–8 phút
**Người điều phối (MC):** Ninh Quang Minh (R4 - Report & Demo Lead)
**Mục tiêu:** Trình bày trôi chảy, không vấp, mọi thành viên đều có phần nói, trả lời mượt 3 câu hỏi của Giảng viên.

---

## PHẦN 1: CHUẨN BỊ TRƯỚC KHI LÊN BỤC (0 phút - Rất quan trọng)

1. **Mở sẵn 2 cửa sổ (chia đôi màn hình):**
   - **Bên trái:** Terminal / VSCode đã chạy sẵn lệnh `pytest tests/ -v` (để khoe 42 pass) và lệnh `python bench.py` (hiện sẵn kết quả top 3).
   - **Bên phải:** Báo cáo `REPORT_NHOM.md` mở bằng chế độ Preview Markdown.
2. **Setup Terminal để không bị lỗi tiếng Việt (bắt buộc):**
   ```bash
   $env:PYTHONIOENCODING="utf-8"
   python bench.py
   ```
   *(Tuyệt đối không gõ lệnh chạy code trong lúc đang thuyết trình để tránh rủi ro văng lỗi. Mọi thứ phải có sẵn trên màn hình).*

---

## PHẦN 2: KỊCH BẢN CHI TIẾT (6 - 8 phút)

### 1. Mở đầu: Chủ đề & Dữ liệu (1 phút) - MINH (R4)
> **Minh:** "Dạ em chào Thầy và các bạn, nhóm Top1Server xin phép trình bày Lab 7. Nhóm em chọn chủ đề **Quy định và dịch vụ thư viện HUIT**. Bộ dữ liệu gồm 8 tài liệu (quy định mượn trả, học nhóm, thẻ thư viện, v.v.). Lý do nhóm chọn chủ đề này vì nội quy có cấu trúc rõ ràng, chứa nhiều bảng biểu phức tạp và có sự phân biệt rạch ròi về hạn mức giữa 2 đối tượng `student` và `faculty`. Điều này vô cùng lý tưởng để nhóm em test thuật toán phân mảnh (chunking) và bộ lọc (metadata filter)."

### 2. Tóm tắt chiến lược của từng người (2 phút) - CẢ NHÓM
> **Tùng (R1):** "Về chiến lược cắt dữ liệu (Chunking), em sử dụng **FixedSizeChunker** (cắt cố định 500 ký tự). Code chạy rất đều và ổn định. Nhưng điểm yếu chí mạng là nó cắt vỡ bảng biểu và làm đứt câu điều kiện ra làm hai nửa."

> **Minh (R4):** "Em phụ trách **SentenceChunker** (cắt theo dấu chấm câu). Đọc thì rất tự nhiên theo văn xuôi, nhưng đối với các Bảng biểu mở cửa thư viện (không có dấu chấm câu), nó gom cục thành một chunk khổng lồ lến tới 1400 ký tự."

> **Đức Anh (R2):** "Em sử dụng **RecursiveChunker** (cắt ưu tiên đoạn văn `\n\n` rồi tới dòng `\n`). Đây là thuật toán an toàn nhất, giữ được đoạn văn. Tuy nhiên, nếu một mục quy định dài quá, nó cắt ra làm 2 đoạn và đoạn thứ 2 bị mất ngữ cảnh (không biết đoạn này thuộc tiêu đề nào)."

> **Nguyên (R3):** "Để khắc phục tất cả, em viết **HeadingChunker** (cắt theo thẻ `#`). Nó bóc tách chính xác từng mục (Ví dụ: Điều 1, Điều 2). Điểm đặc biệt của em là kỹ thuật **Heading Injection**: Nếu một điều khoản quá dài phải cắt nhỏ, code của em sẽ tự động copy tiêu đề gốc dán vào đầu các mảnh con bị cắt. Giúp RAG không bao giờ quên ngữ cảnh."

### 3. Giải thích chiến lược thắng & Demo (2 phút) - MINH (R4)
> **Minh (MC chỉ vào màn hình Terminal):** "Và rõ ràng, **HeadingChunker của bạn Nguyên là chiến lược thắng cuộc**. Nó hiểu cấu trúc tài liệu quy phạm pháp luật tốt hơn các cách cắt mù mờ. 
> Bây giờ em xin demo 1 câu hỏi đánh bẫy: *'Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày?'*
> - Như thầy thấy trên màn hình: Khi **KHÔNG LỌC** (filter=None), kết quả bị nhiễu do sinh viên và giảng viên đều có tài liệu quy định mượn sách riêng. Trọng số loạn xạ.
> - Nhưng khi em ép thêm `metadata_filter={'audience': 'student'}` (Câu Query số 2 trên Terminal), không gian tìm kiếm được thu hẹp 100% vào tài liệu sinh viên. Tốc độ nhanh hơn và kết quả không bao giờ sai đối tượng."

---

## PHẦN 3: BỘ CÂU TRẢ LỜI ĐỠ ĐẠN (Q&A TỪ GIẢNG VIÊN)

Giảng viên thường hỏi 3 câu sau, anh hãy phân công sẵn người trả lời để ghi điểm phong cách chuyên nghiệp:

**🔴 Câu 1 (Thầy hỏi): Nếu đổi sang chủ đề khác (ví dụ: truyện tiểu thuyết hoặc tin tức thời sự), thì chiến lược `HeadingChunker` của các em còn xịn không?**
> **Nguyên (R3) hoặc Minh trả lời:** "Dạ thưa thầy là KHÔNG. Nếu chuyển sang tiểu thuyết (văn xuôi, không có tiêu đề rõ ràng), HeadingChunker sẽ phá sản vì không tìm thấy thẻ Markdown nào để bám vào. Khi đó, chiến lược `SentenceChunker` của bạn Minh hoặc `RecursiveChunker` của bạn Đức Anh mới là vua, vì chúng cắt theo logic dấu chấm câu và đoạn văn."

**🔴 Câu 2 (Thầy hỏi): Metadata Filter nãy em nói là giúp loại bỏ tài liệu giảng viên. Vậy có trường hợp nào dùng Filter lại làm hỏng (mất) kết quả không?**
> **Tùng (R1) trả lời:** "Dạ CÓ thưa thầy. Rủi ro lớn nhất (trade-off) là giảm độ phủ (Recall). Ví dụ: Có một tài liệu quy định chung (audience: `all`) chứa một điều khoản áp dụng chung cho cả trường. Nếu em hard-code filter quá gắt bằng `audience: student`, em sẽ vô tình lọc bỏ mất tài liệu `all` kia, khiến RAG vĩnh viễn không tìm ra được câu trả lời dù tài liệu đó có tồn tại trong kho."

**🔴 Câu 3 (Thầy hỏi): Nhóm em học được gì từ các nhóm khác?**
> **Đức Anh (R2) trả lời:** "Dạ xem các nhóm khác demo, tụi em thấy việc áp dụng Cây mục lục đa tầng (Metadata Hierarchical - thêm các trường như `section`, `sub_section`) vào metadata rất hay, giúp lọc chính xác tới từng dòng điều khoản. Hơn nữa, việc dùng bộ nhúng (Embedding) xịn của OpenAI thay cho MockEmbedder giả lập của tụi em sẽ giúp điểm số Cosine đo lường về mặt ngữ nghĩa phản ánh đúng thực tế hơn rất nhiều ạ."

---
*Chúc nhóm Top1Server tự tin ẵm trọn điểm tuyệt đối nhé!*
