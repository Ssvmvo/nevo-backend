#!/bin/bash
set -e

echo "=== Instalando pip ==="
python -m ensurepip --upgrade

echo "=== Atualizando pip ==="
python -m pip install --upgrade pip

echo "=== Instalando dependências ==="
python -m pip install -r requirements.txt

echo "=== Verificando uvicorn ==="
python -m uvicorn --version

echo "=== Iniciando servidor ==="
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}