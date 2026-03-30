#!/bin/bash
# VETSystem — Script de inicialização em produção (Render)
# Executa migrações, cria superusuário e sobe o servidor.
set -e

echo "==> Rodando migrações..."
python manage.py migrate --noinput

echo "==> Criando superusuário (se não existir)..."
python manage.py criar_superusuario

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Iniciando servidor..."
gunicorn vetsystem.wsgi --log-file - --bind 0.0.0.0:$PORT
