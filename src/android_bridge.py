import subprocess
import json
import logging
import asyncio
import os
from typing import Dict, Any

logger = logging.getLogger("Feb-AndroidBridge")

class AndroidBridge:
    def __init__(self):
        self.is_android = os.path.exists("/system/bin/app_process") # Check simples de ambiente Android

    async def _run_command(self, cmd: list) -> str:
        """
        Executa comandos do Termux-API ou Mock no Windows.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                logger.error(f"[Bridge] Erro no comando {cmd[0]}: {stderr.decode()}")
                return ""
        except FileNotFoundError:
            logger.warning(f"[Bridge] Comando {cmd[0]} não encontrado. Mock ativado.")
            return ""

    async def send_notification(self, title: str, content: str):
        """
        Envia uma notificação para a barra do Android via termux-notification.
        """
        logger.info(f"[Bridge] Notificação: {title} - {content}")
        if self.is_android:
            await self._run_command(["termux-notification", "--title", title, "--content", content, "--priority", "high"])
        else:
            # Mock Windows: Apenas log, opcionalmente Toast se necessário
            pass

    async def get_battery_status(self) -> Dict[str, Any]:
        """
        Retorna o status da bateria via termux-battery-status.
        """
        if self.is_android:
            res = await self._run_command(["termux-battery-status"])
            if res:
                return json.loads(res)
        
        # Mock Default (Saudável)
        return {"percentage": 85, "status": "DISCHARGING", "health": "GOOD"}

    async def vibrate(self, duration_ms: int = 200):
        """
        Feedback tátil via termux-vibrate.
        """
        if self.is_android:
            await self._run_command(["termux-vibrate", "-d", str(duration_ms)])
        else:
            logger.info(f"[Bridge] Vibração simulada: {duration_ms}ms")

# Instância Global
android_bridge = AndroidBridge()
