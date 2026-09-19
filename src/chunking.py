from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        
        # Lookbehind to split after punctuation + whitespace
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        separator = ""
        for sep in remaining_separators:
            if sep == "":
                separator = sep
                break
            if sep in current_text:
                separator = sep
                break
        else:
            # Fallback to strict slicing if no separator matched
            return [current_text[i:i+self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]
            
        next_separators = remaining_separators[remaining_separators.index(separator)+1:] if separator in remaining_separators else []
        
        splits = current_text.split(separator) if separator else list(current_text)
        
        good_splits = []
        for s in splits:
            if len(s) <= self.chunk_size:
                good_splits.append(s)
            else:
                if s:
                    good_splits.extend(self._split(s, next_separators))
                    
        # Merge small chunks together
        merged = []
        current_chunk = ""
        for s in good_splits:
            if not current_chunk:
                current_chunk = s
            elif len(current_chunk) + len(separator) + len(s) <= self.chunk_size:
                current_chunk += separator + s
            else:
                merged.append(current_chunk)
                current_chunk = s
        if current_chunk:
            merged.append(current_chunk)
            
        return merged


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    mag_a = math.sqrt(sum(x*x for x in vec_a))
    mag_b = math.sqrt(sum(x*x for x in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text:
            return {
                "fixed_size": {"count": 0, "avg_length": 0.0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0.0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0.0, "chunks": []},
            }
        
        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size, overlap=20).chunk(text)
        sentence_chunks = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        
        def stats(chunks):
            if not chunks: 
                return {"count": 0, "avg_length": 0.0, "chunks": chunks}
            avg = sum(len(c) for c in chunks) / len(chunks)
            return {"count": len(chunks), "avg_length": avg, "chunks": chunks}
            
        return {
            "fixed_size": stats(fixed_chunks),
            "by_sentences": stats(sentence_chunks),
            "recursive": stats(recursive_chunks),
        }

import re

class HeadingChunker:
    """Chunk theo heading Markdown (##, ###).

    Mỗi heading bắt đầu một section mới. Section quá dài (> max_chunk_size)
    được tách nhỏ theo paragraph rồi newline, mỗi mảnh con gắn lại tiêu đề
    gốc. Section ngắn liền kề (tổng <= min_chunk_size) được gộp.

    Thiết kế cho corpus quy định/sổ tay: tiêu đề do người soạn chia sẵn là
    ranh giới ngữ nghĩa tốt hơn so với cắt ký tự hay câu.
    """

    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 200) -> None:
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        import re
        # Tách theo heading ## hoặc ###
        sections = re.split(r'(?=^#{2,3}\s)', text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        chunks: list[str] = []
        buffer = ""

        for section in sections:
            # Nếu gộp vào buffer vẫn nhỏ -> gộp
            if buffer and len(buffer) + len(section) <= self.min_chunk_size:
                buffer = buffer + "\n\n" + section
                continue

            # Flush buffer trước khi xử lý section mới
            if buffer:
                chunks.extend(self._split_large(buffer))
                buffer = ""

            if len(section) <= self.max_chunk_size:
                buffer = section
            else:
                chunks.extend(self._split_large(section))

        if buffer:
            chunks.extend(self._split_large(buffer))

        return chunks

    def _split_large(self, text: str) -> list[str]:
        """Tách section quá dài, gắn lại tiêu đề vào mỗi mảnh."""
        if len(text) <= self.max_chunk_size:
            return [text]

        # Lấy tiêu đề (dòng đầu tiên nếu bắt đầu bằng #)
        lines = text.split('\n', 1)
        heading = lines[0] if lines[0].startswith('#') else ""
        body = lines[1] if len(lines) > 1 else text

        # Tách theo paragraph trước, rồi newline đơn nếu vẫn lớn
        paragraphs = body.split('\n\n')
        chunks: list[str] = []
        current = heading

        for para in paragraphs:
            candidate = current + "\n\n" + para if current else para
            if len(candidate) <= self.max_chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                # Nếu paragraph đơn lẻ vẫn quá dài, tách theo newline đơn
                if len(para) > self.max_chunk_size:
                    sub_lines = para.split('\n')
                    current = heading
                    for line in sub_lines:
                        sub_candidate = current + "\n" + line if current else line
                        if len(sub_candidate) <= self.max_chunk_size:
                            current = sub_candidate
                        else:
                            if current:
                                chunks.append(current.strip())
                            current = (heading + "\n" + line) if heading else line
                else:
                    current = (heading + "\n\n" + para) if heading else para

        if current.strip():
            chunks.append(current.strip())

        return chunks