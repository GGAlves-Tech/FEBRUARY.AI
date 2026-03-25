from src.vector_engine import feb_memory
import logging

logger = logging.getLogger("Feb-Tools")

async def memory_learn(text: str) -> str:
    """
    Ensina um novo fato ou informação importante para a February.
    """
    logger.info(f"[Tesseract] Aprendendo: '{text}'")
    feb_memory.add_memory(text)
    return f"Registrado em meu núcleo de memória, Senhor. Não esquecerei: '{text}'"
