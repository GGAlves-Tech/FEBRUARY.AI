import sqlite3
import numpy as np
import os
import logging
import json
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

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        BGE-Micro Mock: Simula embeddings usando frequência de termos.
        No Android/ARM64 será substituído pelo ONNXRuntime + BGE Real.
        """
        # Simplificação extrema para o Mock:
        # Cria um vetor baseado em caracteres/palavras chave para simular proximidade
        terms = text.lower().split()
        vector = np.zeros(128) # BGE-Micro-esque dimension
        for i, term in enumerate(terms):
            idx = hash(term) % 128
            vector[idx] += 1
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        vector = self._get_embedding(text)
        vector_json = json.dumps(vector.tolist())
        meta_json = json.dumps(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories (content, vector, metadata) VALUES (?, ?, ?)",
                (text, vector_json, meta_json)
            )
            conn.commit()
        logger.info(f"[Tesseract] Nova memória armazenada: '{text[:30]}...'")

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
