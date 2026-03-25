import asyncio
import logging
import sys
import os
import glob
from mcp.server.fastmcp import FastMCP  # type: ignore

try:
    from src.audio_io import stt_listen_loop  # type: ignore
except ImportError:
    # Ajuste de PYTHONPATH caso seja rodado diretamente fora do projeto raiz
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.audio_io import stt_listen_loop, tts_speak  # type: ignore

from src.llm_controller import feb_brain  # type: ignore
from src.plugin_loader import PluginLoader  # type: ignore
from src.android_bridge import android_bridge  # type: ignore

# Configuração Padrão EdgeOps para debug de hardware
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("Feb-Orquestrador")

# Instanciação do Kernel FastMCP
mcp = FastMCP(
    "Feb Assistant Native",
    dependencies=["mcp", "pydantic"] # Dependencias reais sao resolvidas pelo setup_env.sh
)

# ------------------------------------------------------------------------------
# MÓDULOS FIXOS (Sprint 1)
# As rotinas dinâmicas do /sdcard/mcp/tools serão injetadas via inotify na Sprint 3
# ------------------------------------------------------------------------------

@mcp.tool()
async def edgeops_system_check() -> str:
    """
    Retorna o status base do orquestrador validando se o ambiente
    Android está seguro para iniciar a carga da LLM na GPU.
    """
    logger.info("Interceptado pedido de Validação Térmica e de RAM.")
    
    # 1. Validação de RAM (Kernel Linux)
    ram_available_gb = "Desconhecido"
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        kb = int(line.split()[1])
                        ram_available_gb = f"{kb / (1024 * 1024):.2f}GB"
                        break
        except Exception as e:
            logger.error(f"Erro ao ler meminfo: {e}")
    else:
        # Fallback local para desenvolvimento no Windows
        ram_available_gb = "4.20GB (Mock Win)"

    # 2. Validação Termal (MediaTek / Android SoC)
    thermal_temp = "Desconhecido"
    thermal_zones = glob.glob("/sys/class/thermal/thermal_zone*/temp")
    if thermal_zones:
        try:
            max_temp = 0.0
            for zone in thermal_zones:
                with open(zone, "r") as f:
                    temp_mC = int(f.read().strip())
                    temp_C = temp_mC / 1000.0
                    if 0 < temp_C < 150: # Filtra leituras irreais
                        max_temp = max(max_temp, temp_C)
            if max_temp > 0:
                thermal_temp = f"{max_temp:.1f}°C"
        except Exception as e:
            logger.error(f"Erro térmico: {e}")
    else:
        # Fallback local para desenvolvimento no Windows
        thermal_temp = "40.5°C (Mock Win)"

    # Avaliação final de sobrevivência do Agente (EdgeOps)
    status = "VERDE (SEGURO)"
    if "Mock" not in thermal_temp and thermal_temp != "Desconhecido":
        if float(thermal_temp.replace("°C", "")) > 45.0:
            status = "VERMELHO (OOM/THROTTLING EMINENTE)"

    return f"Status: {status} | RAM Livre: {ram_available_gb} | SoC Temp: {thermal_temp}"

@mcp.tool()
async def inject_voice_command(text: str) -> str:
    """
    Simula uma entrada de áudio do usuário (Voice Injection).
    Útil para testes de diálogo enquanto o driver ALSA/Termux não está ativo.
    """
    logger.info(f"[Manual-Voice] Injetando: '{text}'")
    
    # Roda a inteligência (Sprint 2)
    response = await feb_brain.generate(text)
    
    # Roda o Output de Áudio (Sprint 1)
    await tts_speak(response)
    
    return f"Feb ouviu e respondeu: {response}"

@mcp.tool()
async def get_system_status() -> str:
    """
    Retorna a telemetria completa do Android (Bateria, RAM, Temperatura). 
    Útil para a February informar o estado tático do Senhor.
    """
    battery = await android_bridge.get_battery_status()
    # Reutiliza a lógica existente de HW no mesmo arquivo
    hw_stats = await edgeops_system_check()
    
    status_report = (
        f"Relatório Tático, Senhor:\n"
        f"- Bateria: {battery.get('percentage')}% [{battery.get('status')}]\n"
        f"- {hw_stats}"
    )
    
    # Notificação visual paralela
    await android_bridge.send_notification("Relatório de Sistema", f"Bateria em {battery.get('percentage')}%")
    
    return status_report

# ------------------------------------------------------------------------------
# EVENT LOOP
# ------------------------------------------------------------------------------

async def main():
    logger.info("=========== BOOT DO PROJETO FEB (SPRINT 1) ===========")
    logger.warning("[EdgeOps] Aviso: Certifique-se que o processo termux-wake-lock está vivo.")
    
    # O FastMCP por padrão roda o app stdio ou sse.
    # No mobile, usaremos preferencialmente o protocolo nativo por IPC/stdio.
    logger.info("Injetando loop assíncrono do FastMCP...")
    
    # Lançar rotinas de Hardware I/O (Microfone/TTS) em Background
    audio_task = asyncio.create_task(stt_listen_loop(mcp))
    
    # Lançar monitor de inatividade da LLM (Sprint 2 - EdgeOps)
    llm_idle_task = asyncio.create_task(feb_brain.check_idle_unload())
    
    # Lançar o Tesseract Plugin Loader (Sprint 3)
    async def notify_plugin(name):
        await tts_speak(f"Senhor, o módulo {name} foi integrado com sucesso ao meu núcleo.")
        await android_bridge.vibrate(100) # Feedback tátil

    plugin_mgr = PluginLoader(mcp, watch_dir="tools", on_plugin_load=notify_plugin)
    plugin_task = asyncio.create_task(plugin_mgr.watch_loop())
    
    # Notificação de Boot (Protocolo Sentinel)
    await android_bridge.send_notification("February AI", "Sistemas iniciados. Às suas ordens, Senhor.")
    
    try:
        # Iniciando o listener MCP
        await mcp.run_stdio_async()
    except Exception as e:
        logger.error(f"Falha Crítica no EventLoop MCP: {e}")
    finally:
        audio_task.cancel()
        llm_idle_task.cancel()
        plugin_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sinal de encerramento. Liberando locks do subsistema Android.")
        # TODO: Encerrar buffers gRPC do TTS e ALSA (Sprint 1 áudio).
        sys.exit(0)
