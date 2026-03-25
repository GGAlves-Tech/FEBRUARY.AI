import trafilatura
import logging

logger = logging.getLogger("Feb-Tools")

async def web_extract(url: str) -> str:
    """
    Extrai o conteúdo principal (texto limpo) de uma URL. 
    Ideal para o RAG (Retrieval-Augmented Generation) do February.
    """
    logger.info(f"[Tesseract] Extraindo conteúdo de: {url}")
    
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            if content:
                # Retorna os primeiros 1000 caracteres para não estourar contexto
                return f"Conteúdo extraído de {url}:\n\n{content[:1000]}..."
            else:
                return "Não foi possível extrair texto útil desta URL."
        else:
            return "Falha ao baixar a página."
    except Exception as e:
        return f"Erro na extração: {str(e)}"
