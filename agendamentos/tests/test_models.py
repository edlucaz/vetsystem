"""Testes dos models: relacionamento "verifica", idade calculada e link do WhatsApp."""
import datetime

from django.db import IntegrityError, transaction
from django.utils import timezone
import pytest

from agendamentos.models import Animal, Consulta, Disponibilidade
from agendamentos.tests.utils import em

HOJE_FIXO = datetime.date(2026, 10, 13)


def test_consulta_verifica_disponibilidade_do_dia(consulta_futura):
    segunda = Disponibilidade.objects.get(dia_da_semana=0)
    assert consulta_futura.disponibilidade == segunda
    assert segunda.consultas.count() == 1


def test_sem_disponibilidade_cadastrada_fk_fica_nula(db, animal, segunda):
    Disponibilidade.objects.all().delete()
    consulta = Consulta.objects.create(animal=animal, data_hora=em(segunda, 10), tipo='consulta')
    assert consulta.disponibilidade is None


def test_apagar_disponibilidade_deixa_fk_nula(consulta_futura):
    Disponibilidade.objects.filter(dia_da_semana=0).delete()
    consulta_futura.refresh_from_db()
    assert consulta_futura.disponibilidade is None


def test_disponibilidade_unica_por_dia(horario_comercial):
    with pytest.raises(IntegrityError), transaction.atomic():
        Disponibilidade.objects.create(dia_da_semana=0, hora_inicio=datetime.time(9),
                                       hora_fim=datetime.time(12))


@pytest.mark.parametrize('nascimento, idade, texto', [
    (datetime.date(2023, 10, 13), 3, '3 anos'),
    (datetime.date(2025, 10, 1), 1, '1 ano'),
    (datetime.date(2026, 3, 10), 0, '7 meses'),
    (None, None, '—'),
])
def test_idade_calculada(proprietario, monkeypatch, nascimento, idade, texto):
    monkeypatch.setattr(timezone, 'localdate', lambda *a, **k: HOJE_FIXO)
    animal = Animal(nome='Mia', especie='gato', proprietario=proprietario, data_nascimento=nascimento)
    assert animal.idade == idade
    assert animal.idade_formatada == texto


def test_link_whatsapp(consulta_futura):
    assert consulta_futura.link_whatsapp.startswith('https://wa.me/5519999999999?text=')


def test_link_whatsapp_vazio_com_telefone_de_8_digitos(consulta_futura):
    consulta_futura.animal.proprietario.telefone = '9999-9999'
    assert consulta_futura.link_whatsapp == ''
