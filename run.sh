#!/usr/bin/env bash

# Pindah ke direktori tempat skrip ini disimpan
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=============================================="
echo "🚀 Memulai Asisten PDF Lokal"
echo "=============================================="

# 1. Cek dan jalankan service Ollama jika belum aktif
if ! systemctl is-active --quiet ollama; then
    echo "⚙️  Layanan Ollama belum aktif. Memulai service..."
    sudo systemctl start ollama
    sleep 2
else
    echo "✅ Layanan Ollama sudah aktif."
fi

# 2. Aktifkan Virtual Environment
if [ -f "venv/bin/activate" ]; then
    echo "🐍 Mengaktifkan Virtual Environment..."
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment (venv) tidak ditemukan di $PROJECT_DIR"
    exit 1
fi

# 3. Jalankan Terminal Chat
if [ -f "chat_terminal.py" ]; then
    echo "🤖 Membuka chat_terminal.py..."
    echo "=============================================="
    python chat_terminal.py
else
    echo "❌ Error: File chat_terminal.py tidak ditemukan!"
    exit 1
fi
