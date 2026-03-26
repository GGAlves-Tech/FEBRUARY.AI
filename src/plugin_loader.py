import os
import importlib.util
import inspect
import asyncio
import logging
import sys
from typing import Dict, Any

logger = logging.getLogger("Feb-PluginLoader")

class PluginLoader:
    def __init__(self, mcp_server, watch_dir: str = "tools", on_plugin_load=None):
        self.mcp = mcp_server
        self.watch_dir = os.path.abspath(watch_dir)
        self.on_plugin_load = on_plugin_load
        self.loaded_plugins: Dict[str, float] = {}
        
        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)
            logger.info(f"[Tesseract] Criado diretório de ferramentas: {self.watch_dir}")

    async def _load_plugin(self, file_path: str):
        """
        Carrega ou recarrega um módulo Python e registra suas ferramentas no MCP.
        """
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if spec is None:
            logger.error(f"[Tesseract] Não foi possível criar o spec para: {file_path}")
            return False

        if spec.loader is None:
            logger.error(f"[Tesseract] O spec para {module_name} não possui um loader válido.")
            return False

        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Registro dinâmico de ferramentas (Sprint 3)
            tools_added_list = []
            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
                # Se a função não estiver registrada, nós a registramos como tool
                if not name.startswith("_"):
                    self.mcp.tool()(func)
                    tools_added_list.append(name)
            
            tools_added = len(tools_added_list)
            
            logger.info(f"[Tesseract] Plugin '{module_name}' processado. {tools_added} ferramentas injetadas.")
            
            if self.on_plugin_load and tools_added > 0:
                asyncio.create_task(self.on_plugin_load(module_name))
            
            return True
        except Exception as e:
            logger.error(f"[Tesseract] Erro ao carregar plugin {module_name}: {e}")
        return False

    async def watch_loop(self):
        """
        Loop de observação de arquivos (Polling para compatibilidade Android/MIUI).
        """
        logger.info(f"[Tesseract] Watcher iniciado em: {self.watch_dir}")
        
        while True:
            try:
                for filename in os.listdir(self.watch_dir):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        file_path = os.path.join(self.watch_dir, filename)
                        mtime = os.path.getmtime(file_path)
                        
                        if filename not in self.loaded_plugins or mtime > self.loaded_plugins[filename]:
                            logger.info(f"[Tesseract] Detetada alteração em: {filename}. Recarregando...")
                            success = await self._load_plugin(file_path)
                            if success:
                                self.loaded_plugins[filename] = mtime
                                # Notificação sonora da Feb (Opcional, disparada pelo server)
                                
            except Exception as e:
                logger.error(f"[Tesseract] Erro no loop de watch: {e}")
                
            await asyncio.sleep(3) # Checagem a cada 3 segundos

