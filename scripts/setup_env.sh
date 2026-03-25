#!/bin/bash
# ==============================================================================
# PROJETO FEB - SCRIPT DE SETUP PARA TERMUX (ANDROID)
# ==============================================================================
# Objetivo: Preparar ambiente nativo C++/Python para I/O, IA e FastMCP.
# Dispositivo: Redmi Note 10S (MediaTek Helio G95) / MIUI 14
#
# AVISO [EdgeOps]: Execute este script com o aparelho conectado ao carregador
# devido a compilações pesadas de C++ (clang/cmake) que podem acionar o
# Thermal Throttling e derrubar a bateria (LPDDR4x/Helio G95).
# ==============================================================================

set -e

# Cores para logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}[EdgeOps] Iniciando setup das dependências de Base do Feb...${NC}"

# 1. Conceder Acesso ao Disco (File Watcher / Hot Reload MCP depende disso)
echo -e "${GREEN}[1/5] Requisitando acesso ao Armazenamento Local...${NC}"
termux-setup-storage
sleep 3

# 2. Impedir CPU Sleep via Termux-wake-lock (Proteção térmica/sleep)
echo -e "${GREEN}[2/5] Solicitando Wake-lock para evitar suspensão brusca...${NC}"
termux-wake-lock
echo -e "${YELLOW}>> ATENÇÃO: Wake-lock ativado. Desligue ao sair do session para poupar bateria.${NC}"

# 3. Atualizar Repositorios e Instalar Dependências Core
echo -e "${GREEN}[3/5] Atualizando pacotes via apt/pkg...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${GREEN}[3/5.1] Instalando dependências de Sistema, Compilação e Áudio...${NC}"
pkg install -y python python-pip \
    clang cmake git wget \
    libvulkan-dev \
    termux-api \
    ffmpeg # Necessário para tratamento de buffers de áudio do Whisper

# 4. Criando árvore estrutural na Home e Internals (`/sdcard`)
echo -e "${GREEN}[4/5] Estruturando Diretórios do FastMCP e Vector DB...${NC}"
mkdir -p /sdcard/mcp/tools
mkdir -p /sdcard/mcp/db/sqlite_vss

echo -e "Estrutura de pastas na Memória Interna (/sdcard/mcp/) foi criada."

# 5. Instalação das bibliotecas Python Básicas para Async/MCP
echo -e "${GREEN}[5/5] Instalando wheels Python e Orquestrador FastMCP...${NC}"
# Upgrade do PIP para evitar falhas de compilação C
python -m pip install --upgrade pip

pip install mcp \
    watchdog \
    aiohttp \
    pydantic

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}✓ Setup Ambiente Base (Sprint 1) concluído com sucesso.${NC}"
echo -e "${YELLOW}Próximo Passo Manual:${NC} Teste o TTS rodando: termux-tts-speak 'Instalação finalizada'"
echo -e "${GREEN}======================================================${NC}"
