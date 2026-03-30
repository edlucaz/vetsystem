#!/bin/bash
# VETSystem — Script de inicialização em produção (Railway)
# Executa migrações e coleta estáticos antes de subir o servidor.
set -e

echo "==> Rodando migrações..."
python manage.py migrate --noinput

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Iniciando servidor..."
gunicorn vetsystem.wsgi --log-file - --bind 0.0.0.0:$PORT
