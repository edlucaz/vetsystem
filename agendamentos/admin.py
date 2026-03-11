"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/admin.py
Função  : Registra os models no painel administrativo do Django (/admin).
          Configura colunas, busca e filtros de cada entidade no admin.
Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from django.contrib import admin
from .models import Proprietario, Animal, Consulta, Disponibilidade


@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'telefone', 'email', 'cpf')
    search_fields = ('nome', 'telefone', 'cpf')


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'especie', 'raca', 'idade', 'peso', 'proprietario')
    search_fields = ('nome', 'proprietario__nome')
    list_filter   = ('especie',)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display  = ('data_hora', 'animal', 'tipo', 'status', 'duracao_minutos')
    search_fields = ('animal__nome', 'animal__proprietario__nome')
    list_filter   = ('status', 'tipo')
    ordering      = ('data_hora',)


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('dia_da_semana', 'hora_inicio', 'hora_fim', 'ativo')
    list_filter  = ('ativo',)
