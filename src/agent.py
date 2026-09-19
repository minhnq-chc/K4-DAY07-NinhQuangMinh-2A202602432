from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin nào trong cơ sở dữ liệu để trả lời câu hỏi của bạn."
            
        context_parts = []
        for i, res in enumerate(results, 1):
            source = res['metadata'].get('doc_id', 'Unknown')
            context_parts.append(f"[{i}] {res['content']} (Nguồn: {source})")
            
        context_str = "\n\n".join(context_parts)
        
        prompt = f"""Bạn là một trợ lý thông minh. Hãy trả lời câu hỏi dựa VÀO DUY NHẤT các ngữ cảnh được cung cấp dưới đây.
Tuyệt đối không sử dụng kiến thức bên ngoài hay suy đoán. 
Khi trả lời, hãy trích dẫn số thứ tự của tài liệu được tham khảo, ví dụ [1], [2].
Nếu ngữ cảnh không chứa thông tin để trả lời câu hỏi, hãy nói "Tôi không tìm thấy thông tin phù hợp".

Ngữ cảnh:
{context_str}

Câu hỏi: {question}
Trả lời:"""
        
        return self.llm_fn(prompt)
