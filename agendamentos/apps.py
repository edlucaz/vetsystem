"""
VETSystem — Configuração do App de Agendamentos
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/apps.py
Função  : Registra o app 'agendamentos' no Django com nome legível
          exibido no painel administrativo (/admin).
Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""
from django.apps import AppConfig


class AgendamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agendamentos'
    verbose_name = 'Agendamentos — ATIVO PET'
