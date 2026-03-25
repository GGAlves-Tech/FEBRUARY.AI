#!/data/data/com.termux/files/usr/bin/bash

# 💎 February AI - Zero-Touch Onboarding Script
# Esse script automatiza as etapas manuais e verifica a saúde do sistema.

echo "--- [SENTINEL] Operação Despertar: Iniciando Automação ---"

# 1. Verificação de Permissões (Diagnóstico)
echo "[1/5] Verificando permissões do Android..."
if ! command -v termux-battery-status &> /dev/null; then
    echo "⚠️  ERRO: Termux:API não encontrado. Por favor, instale o app Termux:API do F-Droid."
    exit 1
fi

# Solicitar Wake Lock para evitar que o Android mate a February
termux-wake-lock
echo "✅ Wake Lock ativado (Prevenção de suspensão)."

# 2. Configuração de Identidade (Git Local)
echo "[2/5] Configurando identidade February..."
GIT_NAME=$(git config user.name)
GIT_EMAIL=$(git config user.email)

if [ -z "$GIT_NAME" ]; then
    read -p "Senhor, informe seu Nome para o Git Local: " NEW_NAME
    git config --local user.name "$NEW_NAME"
fi

if [ -z "$GIT_EMAIL" ]; then
    read -p "Senhor, informe seu E-mail para o Git Local: " NEW_EMAIL
    git config --local user.email "$NEW_EMAIL"
fi
echo "✅ Identidade Git configurada localmente."

# 3. Setup de Ambiente e Dependências
echo "[3/5] Instalando dependências táticas..."
pkg update -y && pkg install -y python ndk-sysroot clang make libjpeg-turbo libandroid-spawn termux-api ffmpeg

# 4. Virtualenv e Core
echo "[4/5] Preparando Cérebro Python..."
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Teste de Hardware Final
echo "[5/5] Testando sistemas..."
BATTERY=$(termux-battery-status | grep percentage | awk '{print $2}' | tr -d ',')
echo "✅ Sistemas Verdes. Bateria em $BATTERY%."

echo "--- [ONBOARDING CONCLUÍDO] ---"
echo "A February está pronta. Para iniciar a inteligência:"
echo "python src/server.py"
