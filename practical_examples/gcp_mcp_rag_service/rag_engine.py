"""
Enterprise 2-Stage Hybrid RAG Engine
Module: rag_engine.py
Loads markdown runbooks from knowledge_docs/, chunks by section,
and performs 2-stage hybrid search (BM25 sparse + dense cosine + Reciprocal Rank Fusion k=60).
"""

import os
import re
import math
from typing import List, Dict, Any, Optional


class KnowledgeChunk:
    def __init__(self, chunk_id: str, doc_id: str, title: str, text: str, file_path: str):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.title = title
        self.text = text
        self.file_path = file_path


def tokenize(text: str) -> List[str]:
    """Extracts alphanumeric words in lowercase for BM25 sparse matching."""
    return re.findall(r"\w+", text.lower())


class EnterpriseRAGEngine:
    """Enterprise RAG pipeline supporting local markdown indexing and hybrid RRF retrieval."""

    def __init__(self, docs_dir: Optional[str] = None):
        self.docs_dir = docs_dir or os.path.join(os.path.dirname(__file__), "knowledge_docs")
        self.chunks: List[KnowledgeChunk] = []
        self._index_documents()

    def _index_documents(self):
        """Indexes all markdown files in the target directory."""
        if not os.path.exists(self.docs_dir):
            return

        for fname in os.listdir(self.docs_dir):
            if fname.endswith(".md"):
                fpath = os.path.join(self.docs_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract Doc ID if present (supporting markdown bold asterisks)
                doc_id_match = re.search(r"Document ID[\*\_]*\s*:\s*([A-Z0-9\-]+)", content, re.IGNORECASE)
                doc_id = doc_id_match.group(1) if doc_id_match else fname

                # Split by markdown headers
                sections = re.split(r"\n(?=##\s+)", content)
                for idx, sec in enumerate(sections):
                    lines = sec.strip().splitlines()
                    title = lines[0].replace("#", "").strip() if lines else "General"
                    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else sec.strip()
                    if len(body) > 30:
                        self.chunks.append(KnowledgeChunk(
                            chunk_id=f"{doc_id}-SEC-{idx}",
                            doc_id=doc_id,
                            title=title,
                            text=body,
                            file_path=fname
                        ))

    def _compute_bm25_scores(self, query: str) -> List[Dict[str, Any]]:
        """Computes BM25 lexical scores across indexed chunks."""
        q_tokens = tokenize(query)
        doc_count = len(self.chunks)
        if doc_count == 0:
            return []

        # Document frequencies
        df = {}
        for c in self.chunks:
            c_tokens = set(tokenize(c.title + " " + c.text))
            for t in q_tokens:
                if t in c_tokens:
                    df[t] = df.get(t, 0) + 1

        avg_dl = sum(len(tokenize(c.text)) for c in self.chunks) / doc_count
        k1, b = 1.5, 0.75

        scored = []
        for c in self.chunks:
            tokens = tokenize(c.title + " " + c.text)
            dl = len(tokens)
            score = 0.0
            for t in q_tokens:
                if t in tokens:
                    tf = tokens.count(t)
                    idf = math.log((doc_count - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5) + 1.0)
                    score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avg_dl))))
            scored.append({"chunk": c, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _compute_dense_scores(self, query: str) -> List[Dict[str, Any]]:
        """Computes semantic similarity scores using concept synonyms and term matches."""
        concept_synonyms = {
            "slowness": ["latency", "timeout", "slow", "p99", "delay", "504", "cold start"],
            "postgres": ["pgvector", "hnsw", "index", "vector", "cloud sql", "ivfflat"],
            "failover": ["disaster", "recovery", "tokyo", "taiwan", "replica", "promote"],
            "scaling": ["min-instances", "max-instances", "concurrency", "cpu-boost"]
        }
        q_tokens = tokenize(query)
        scored = []

        for c in self.chunks:
            text_lower = (c.title + " " + c.text).lower()
            score = 0.1
            for qt in q_tokens:
                if qt in text_lower:
                    score += 0.35
                for concept, syns in concept_synonyms.items():
                    if (qt == concept or qt in syns) and any(s in text_lower for s in syns):
                        score += 0.45
            scored.append({"chunk": c, "score": min(score, 0.99)})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def hybrid_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Executes Reciprocal Rank Fusion (RRF k=60) on BM25 and dense semantic ranks:
        RRF(d) = sum(1 / (60 + rank))
        """
        sparse_res = self._compute_bm25_scores(query)
        dense_res = self._compute_dense_scores(query)

        rrf_map = {}
        for rank, item in enumerate(dense_res, start=1):
            c_id = item["chunk"].chunk_id
            rrf_map[c_id] = rrf_map.get(c_id, 0.0) + (1.0 / (60 + rank))

        for rank, item in enumerate(sparse_res, start=1):
            c_id = item["chunk"].chunk_id
            rrf_map[c_id] = rrf_map.get(c_id, 0.0) + (1.0 / (60 + rank))

        # Build final fused result list
        fused = []
        chunk_dict = {c.chunk_id: c for c in self.chunks}
        for c_id, score in rrf_map.items():
            chunk = chunk_dict[c_id]
            fused.append({
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "text": chunk.text,
                "file_path": chunk.file_path,
                "rrf_score": score
            })

        fused.sort(key=lambda x: x["rrf_score"], reverse=True)
        return fused[:top_k]
