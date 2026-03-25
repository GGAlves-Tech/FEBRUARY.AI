from src.vector_engine import feb_memory
import logging

logger = logging.getLogger("Feb-Tools")

async def memory_remember(query: str) -> str:
    """
    Busca na memória de longo prazo informações relacionadas à pergunta do usuário.
    """
    logger.info(f"[Tesseract] Buscando memória para: '{query}'")
    results = feb_memory.search_memory(query, top_k=2)
    
    if not results or results[0]["similarity"] < 0.3:
        return "Não encontrei registros específicos sobre isso em meu banco de dados, Senhor."
    
    response = "Aqui está o que lembrei, Senhor:\n"
    for res in results:
        response += f"- {res['content']} (Confiabilidade: {res['similarity']:.2f})\n"
        
    return response
