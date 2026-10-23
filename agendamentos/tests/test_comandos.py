"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/tests/test_comandos.py
Função  : Testes dos comandos de gerenciamento (expediente padrão e dados demo).
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-13
"""
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from agendamentos.models import Animal, Consulta, Disponibilidade, Proprietario, RegistroPeso


@pytest.mark.django_db
def test_criar_horarios_padrao_e_idempotente():
    Disponibilidade.objects.all().delete()
    call_command('criar_horarios_padrao')
    call_command('criar_horarios_padrao')
    assert Disponibilidade.objects.count() == 5


@pytest.mark.django_db
def test_popular_demo_cria_e_apaga():
    call_command('popular_demo', '--forcar')
    demo = Proprietario.objects.filter(email__endswith='@demo.vetsystem.local')
    assert demo.count() == 8
    assert Animal.objects.filter(proprietario__in=demo).count() == 12
    assert RegistroPeso.objects.count() >= 12 * 4
    assert Consulta.objects.filter(observacoes='[demo]').exists()
    call_command('popular_demo', '--forcar')          # rodar de novo não duplica
    assert demo.count() == 8

    call_command('popular_demo', '--apagar')
    assert not demo.exists() and not Animal.objects.exists() and not Consulta.objects.exists()


@pytest.mark.django_db
def test_popular_demo_recusa_sem_debug():
    with pytest.raises(CommandError):
        call_command('popular_demo')
