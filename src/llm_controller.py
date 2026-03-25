import time
import logging
import asyncio
from src.vector_engine import feb_memory  # type: ignore

logger = logging.getLogger("Feb-LLM")

class FebLLM:
    def __init__(self, model_path: str = "Gemma-2b-IT-Q4_K_M"):
        self.model_path = model_path
        self.is_loaded = False
        self.last_access_time = 0
        self.idle_timeout = 300  # 5 minutos para descarregar da GPU (EdgeOps check)
        self.max_tokens = 250    # HARD-CAP Térmico para o MediaTek (Sprint 2)
        
        # System Prompt com restrições térmicas para o MediaTek (Persona: February)
        self.system_prompt = (
            "Você é a February (ou Feb), uma inteligência artificial de elite. "
            "Sua personalidade é feminina, mantendo elegância, calma absoluta e assistência tática imediata. "
            "Trate o usuário estritamente como 'Senhor'. Seja polida, formal e focada na eficiência operacional. "
            "RESTRIÇÃO TÉRMICA: Seja concisa. Responda em no máximo 2 parágrafos curtos. "
            "Responda sempre em Português do Brasil."
        )

    async def _ensure_model_loaded(self):
        """
        Lógica de Lazy Loading: Só carrega na VRAM quando necessário.
        """
        if not self.is_loaded:
            logger.info(f"[EdgeOps] Carregando {self.model_path} na GPU (Mali-G76/Vulkan)...")
            # Simulação do tempo de carga do MLC-LLM
            await asyncio.sleep(1.5)
            self.is_loaded = True
        
        self.last_access_time = int(time.time())

    async def generate(self, user_input: str) -> str:
        """
        Geração de texto com injeção automática de memória (RAG).
        """
        await self._ensure_model_loaded()
        
        # BUSCA SEMÂNTICA (Sprint 3 - Tesseract)
        memories = feb_memory.search_memory(user_input, top_k=2)
        context = ""
        if memories and memories[0]["similarity"] > 0.4:
            context = "\n[CONTEXTO RECUPERADO]: " + " | ".join([m["content"] for m in memories])
            logger.info(f"[Tesseract] Contexto injetado: {len(memories)} memórias.")

        full_prompt = self.system_prompt + context + "\nUsuário: " + user_input
        logger.info(f"[LLM] Processando com contexto: {user_input}")
        
        # Simulação de processamento (Time-to-First-Token)
        await asyncio.sleep(0.8)
        
        # Mock de resposta (Aqui futuramente entrará a chamada real do mlc_llm no Termux)
        # Para o Windows, simulamos a inteligência baseada na intenção
        if "oi" in user_input.lower():
            response = "Olá! Sou a Feb. Sistema operacional estável, RAM disponível e pronta para suas ordens localmente."
        elif "quem é você" in user_input.lower():
            response = "Sou a Feb, sua assistente local. Fui projetada para rodar sem internet, respeitando sua privacidade e o hardware do seu Android."
        else:
            response = "Entendido. No momento estou operando em modo de teste da Sprint 2. Logo terei meu cérebro completo via MLC-LLM."

        return response

    async def check_idle_unload(self):
        """
        Tarefa de background para monitorar inatividade e liberar VRAM.
        """
        while True:
            await asyncio.sleep(60) # Checa a cada minuto
            if self.is_loaded and (time.time() - self.last_access_time > self.idle_timeout):
                logger.warning("[EdgeOps] Inatividade detectada. Descarregando LLM para prevenir Thermal Throttling e salvar bateria.")
                self.is_loaded = False

# Instância global do cérebro
feb_brain = FebLLM()
