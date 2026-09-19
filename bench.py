import os
import re
import json
import hashlib
from pathlib import Path

# Cấu hình cache cho OpenAI embeddings để tránh tốn tiền gọi nhiều lần
CACHE_FILE = ".embedding_cache.json"
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

_cache = load_cache()

def cached_embed(text: str) -> list[float]:
    """Hàm nhúng (embedding) có sử dụng cache"""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    if text_hash in _cache:
        return _cache[text_hash]
    
    # Sử dụng OpenAI API
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    try:
        response = openai.embeddings.create(input=[text], model="text-embedding-3-small")
        emb = response.data[0].embedding
    except Exception as e:
        print("Lỗi OpenAI (Fall back to mock):", e)
        from src.embeddings import _mock_embed
        emb = _mock_embed(text)

    
    _cache[text_hash] = emb
    return emb


from src.models import Document
from src.store import EmbeddingStore
from src.chunking import SentenceChunker # R4 Minh phụ trách SentenceChunker

def parse_markdown(filepath: Path):
    """Đọc file md, tách frontmatter và nội dung"""
    content = filepath.read_text(encoding="utf-8")
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = '---'.join(parts[2:]).strip()
        metadata = dict(re.findall(r'^(\w+):\s*(.+)$', frontmatter, re.M))
        for k, v in metadata.items():
            metadata[k] = v.strip('"\'')
    else:
        metadata = {}
        body = content.strip()
    return metadata, body


def main():
    store = EmbeddingStore(embedding_fn=cached_embed)
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    
    data_dir = Path("data/university")
    
    # 1 & 2. Đọc file, chunking và nạp vào Store
    all_docs = []
    if data_dir.exists():
        for md_file in data_dir.glob("*.md"):
            metadata, body = parse_markdown(md_file)
            metadata["doc_id"] = metadata.get("doc_id", md_file.stem)
            
            # Cắt phần thân thành các chunk nhỏ
            chunks = chunker.chunk(body)
            for i, chunk_text in enumerate(chunks):
                doc_chunk = Document(
                    id=f"{md_file.stem}#{i}",
                    content=chunk_text,
                    metadata=metadata.copy()
                )
                all_docs.append(doc_chunk)
                
    store.add_documents(all_docs)
    print(f"Đã nạp {store.get_collection_size()} chunks vào EmbeddingStore.\n")
    
    save_cache(_cache) # Lưu cache sau khi nhúng
    
    # 3. Mảng Query của R2 (Đức Anh)
        # 3. Mảng Query của R2 (Đức Anh)
    benchmark_queries = [
        {
            "q": "Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày?", 
            "filter": None,
            "gold_doc": "han-muc-muon-tai-lieu-sinh-vien",
            "gold_string": "03 tài liệu"
        },
        {
            "q": "Được mượn tối đa bao nhiêu tài liệu và trong bao nhiêu ngày?", 
            "filter": {"audience": "student"},
            "gold_doc": "han-muc-muon-tai-lieu-sinh-vien",
            "gold_string": "03 tài liệu"
        },
        {
            "q": "Người sử dụng cần đáp ứng những điều kiện nào để được mượn tài liệu về nhà?", 
            "filter": None,
            "gold_doc": "luu-hanh-tai-lieu",
            "gold_string": "25/35 câu"
        },
        {
            "q": "Quy trình đăng ký và sử dụng phòng học nhóm gồm những bước nào, và đến trễ bao lâu thì kết quả đặt phòng bị hủy?", 
            "filter": None,
            "gold_doc": "su-dung-phong-hoc-nhom",
            "gold_string": "trễ trên 15 phút"
        },
        {
            "q": "Dịch vụ mượn liên thư viện cho phép mượn tối đa bao nhiêu tài liệu, trong bao lâu và phí trễ hạn là bao nhiêu?", 
            "filter": None,
            "gold_doc": "muon-lien-thu-vien",
            "gold_string": "20 ngày"
        },
        {
            "q": "Lệ phí cấp mới, cấp lại, gia hạn thẻ thư viện là bao nhiêu và thời gian trả thẻ được quy định thế nào?", 
            "filter": None,
            "gold_doc": "huong-dan-su-dung-thu-vien",
            "gold_string": "50.000"
        }
    ]
    
    # 4. In kết quả Top-3
    for i, item in enumerate(benchmark_queries, 1):
        query = item["q"]
        m_filter = item["filter"]
        gold_doc = item["gold_doc"]
        gold_string = item["gold_string"]
        
        print(f"=== Query {i}: {query} ===")
        if m_filter:
            print(f"   (Filter: {m_filter})")
            
        results = store.search_with_filter(query, top_k=3, metadata_filter=m_filter)
        if not results:
            print("   => Không có kết quả!")
            print(f"   => Điểm: 0đ")
            print()
            continue
            
        score_points = 0
        gold_in_top3 = False
        gold_in_top1 = False
        string_found = False
        
        for rank, res in enumerate(results, 1):
            did = res['metadata'].get('doc_id', '')
            content = res['content']
            
            print(f"   Top {rank}: score={res['score']:.3f} | doc_id={did}")
            print(f"       Preview: {content[:100].replace(chr(10), ' ')}...")
            
            if did == gold_doc:
                gold_in_top3 = True
                if rank == 1:
                    gold_in_top1 = True
            
            if gold_string.lower() in content.lower():
                string_found = True
        
        if gold_in_top1 and string_found:
            score_points = 2
        elif gold_in_top3 and string_found:
            score_points = 1
        elif string_found: # Trương hợp hiếm: có chứa thông tin nhưng tài liệu khác
            score_points = 1
        else:
            score_points = 0
            
        print(f"   => Điểm: {score_points}đ (gold_doc_in_top3: {gold_in_top3}, string_found: {string_found})")
        print()
if __name__ == "__main__":
    main()
