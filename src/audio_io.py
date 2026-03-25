import subprocess
import asyncio
import logging
import os
from src.llm_controller import feb_brain  # type: ignore

logger = logging.getLogger("Feb-AudioIO")

async def tts_speak(text: str):
    """
    Motor Text-to-Speech nativo híbrido (Termux / Windows).
    """
    logger.info(f"[TTS] Falando: '{text}'")
    if os.path.exists("/data/data/com.termux/files/usr/bin/termux-tts-speak"):
        try:
            process = await asyncio.create_subprocess_exec(
                "termux-tts-speak", text,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            await process.communicate()
        except Exception as e:
            logger.error(f"[TTS] Falha no Termux TTS: {e}")
    else:
        # Fallback Windows: usa Powershell Speech Synthesizer (Resiliente)
        try:
            # Escapa aspas simples do texto para não quebrar o comando PowerShell
            clean_text = text.replace("'", "''")
            ps_script = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$voice = $synth.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Gender -eq 'Female' } | Select-Object -First 1; "
                "if($voice){ $synth.SelectVoice($voice.VoiceInfo.Name) }; "
                "$synth.Rate = -1; " # Velocidade elegante
                f"$synth.Speak('{clean_text}')"
            )
            process = await asyncio.create_subprocess_exec(
                "powershell.exe", "-Command", ps_script,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            await process.communicate()
        except Exception as e:
            logger.error(f"[TTS] Falha no Windows Mock TTS (Feb): {e}")

async def stt_listen_loop(mcp_server):
    """
    Loop simulado de STT (Speech-to-Text). Fica rodando em background 
    escutando 'microfones' virtuais ou ALSA do Android.
    """
    # Para Sprint 1 Acceptance: Mock -> Responde "Oi".
    logger.info("[STT] Microfone inicializado. Aguardando a hotword...")
    
    # Aguarda 5 segundos para simular tempo de boot do ALSA/Microfone e o tempo
    # que o usuario leva ate abrir o inspetor.
    await asyncio.sleep(5)
    
    # Simulação da captura de áudio rodando (Whisper.cpp pipeline future mock)
    user_text = "Me diga quem é você"
    logger.info(f"[STT] (Mock) Whisper detectou: '{user_text}'")
    
    # CHADA DA LLM (SPRTIN 2)
    response_text = await feb_brain.generate(user_text)
    
    # Critério de Aceite da Sprint 1: Hardcoded < 2.0s
    await tts_speak(response_text)
    logger.info("[Sprint 2] Fluxo de Inteligência Volátil Concluído.")

