import numpy as np
import json
import os
import sys

# Adiciona o diretório src ao path para importar os módulos
sys.path.append(os.path.abspath("src"))

try:
    from vector_engine import VectorEngine
    from plugin_loader import PluginLoader
except ImportError as e:
    print(f"Erro ao importar: {e}")
    sys.exit(1)

def test_stable_hashing():
    print("--- Testando Stable Hashing ---")
    db_test = "data/test_memory.db"
    if os.path.exists(db_test):
        os.remove(db_test)
        
    engine = VectorEngine(db_test)
    text = "teste de embedding estável"
    vec1 = engine._get_embedding(text)
    vec2 = engine._get_embedding(text)
    
    if np.allclose(vec1, vec2):
        print("PASS: Embeddings idênticos para o mesmo texto.")
    else:
        print("FAIL: Embeddings variaram!")
    
    # Simula reinicialização (novo objeto engine)
    engine2 = VectorEngine(db_test)
    vec3 = engine2._get_embedding(text)
    if np.allclose(vec1, vec3):
        print("PASS: Embeddings estáveis após 'reinicialização'.")
    else:
        print("FAIL: Embeddings instáveis após reinicialização!")

def test_chunking():
    print("\n--- Testando Chunking ---")
    db_test = "data/test_memory.db"
    engine = VectorEngine(db_test)
    # Texto com ~1100 caracteres para forçar pelo menos 3 chunks (default 500, overlap 50)
    long_text = "Esta é uma frase de teste que será repetida muitas vezes para criar um texto longo o suficiente para disparar o mecanismo de chunking do nosso motor vetorial. " * 10
    print(f"Tamanho do texto: {len(long_text)}")
    
    engine.add_memory(long_text)
    
    # Verifica no DB local (usando o próprio search ou listando)
    results = engine.search_memory("frase de teste", top_k=10)
    print(f"Resultados encontrados: {len(results)}")
    
    chunked_results = [r for r in results if r['metadata'].get('is_chunked')]
    if len(chunked_results) > 1:
        print(f"PASS: {len(chunked_results)} chunks detectados.")
    else:
        print(f"FAIL: Chunking não detectado ou insuficiente ({len(chunked_results)} chunks).")

if __name__ == "__main__":
    test_stable_hashing()
    test_chunking()
