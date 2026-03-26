import sqlite3
import numpy as np
import os
import logging
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("Feb-VectorEngine")

class VectorEngine:
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    vector TEXT, -- Armazenado como JSON para o Mock Windows
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.commit()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Divide o texto em pedaços (chunks) para processamento RAG.
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            
            # Evita loops infinitos se overlap >= chunk_size
            if start >= len(text) or chunk_size <= overlap:
                break
        return chunks

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        BGE-Micro Mock Estável: Usa SHA256 para garantir que o mesmo texto
        sempre gere o mesmo vetor, independente de reinicialização.
        """
        terms = text.lower().split()
        vector = np.zeros(128)
        for term in terms:
            # Hash estável usando SHA256
            hash_val = int(hashlib.sha256(term.encode()).hexdigest(), 16)
            idx = hash_val % 128
            vector[idx] += 1
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        # Chunking automático para RAG
        chunks = self.chunk_text(text)
        
        with sqlite3.connect(self.db_path) as conn:
            for i, chunk in enumerate(chunks):
                vector = self._get_embedding(chunk)
                vector_json = json.dumps(vector.tolist())
                
                # Adiciona metadados de chunking
                chunk_meta = (metadata or {}).copy()
                chunk_meta.update({
                    "chunk": i,
                    "total_chunks": len(chunks),
                    "is_chunked": len(chunks) > 1
                })
                meta_json = json.dumps(chunk_meta)
                
                conn.execute(
                    "INSERT INTO memories (content, vector, metadata) VALUES (?, ?, ?)",
                    (chunk, vector_json, meta_json)
                )
            conn.commit()
        
        chunk_info = f" ({len(chunks)} chunks)" if len(chunks) > 1 else ""
        logger.info(f"[Tesseract] Memória processada{chunk_info}: '{text[:30]}...'")

    def search_memory(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vec = self._get_embedding(query)
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, content, vector, metadata FROM memories")
            for row in cursor:
                id, content, vector_str, meta_str = row
                vec = np.array(json.loads(vector_str))
                
                # Simetria de Cosseno manual para o Mock
                similarity = np.dot(query_vec, vec)
                
                results.append({
                    "id": id,
                    "content": content,
                    "similarity": float(similarity),
                    "metadata": json.loads(meta_str)
                })
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

# Instância Global
feb_memory = VectorEngine()
