"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/tests/test_comandos.py
Função  : Testes dos comandos de gerenciamento (expediente padrão).
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-13
"""
from django.core.management import call_command
import pytest

from agendamentos.models import Disponibilidade


@pytest.mark.django_db
def test_criar_horarios_padrao_e_idempotente():
    Disponibilidade.objects.all().delete()
    call_command('criar_horarios_padrao')
    call_command('criar_horarios_padrao')
    assert Disponibilidade.objects.count() == 5
