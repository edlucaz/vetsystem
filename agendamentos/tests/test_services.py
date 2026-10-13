"""Testes das regras de negócio do agendamento (agendamentos/services.py)."""
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytest

from agendamentos import services
from agendamentos.models import Consulta, Disponibilidade
from agendamentos.tests.utils import em, proxima_data


def horas(livres):
    return [f'{h:%H:%M}' for h in livres]


def test_grade_completa_de_08_as_18(horario_comercial, segunda):
    livres = horas(services.horarios_livres(segunda))
    assert livres[:3] == ['08:00', '08:30', '09:00']
    assert livres[-1] == '18:00'          # sessão de 60 min termina às 19:00
    assert len(livres) == 21


def test_conflito_remove_horarios_sobrepostos(horario_comercial, animal, segunda):
    Consulta.objects.create(animal=animal, data_hora=em(segunda, 10), tipo='consulta')
    livres = horas(services.horarios_livres(segunda))
    assert {'09:30', '10:00', '10:30'}.isdisjoint(livres)
    assert '09:00' in livres and '11:00' in livres


def test_hoje_nao_oferece_horarios_passados(horario_comercial, segunda, monkeypatch):
    monkeypatch.setattr(timezone, 'now', lambda: em(segunda, 10, 15))
    assert horas(services.horarios_livres(segunda))[0] == '10:30'


def test_validar_agendamento_rejeita_conflito(consulta_futura, segunda):
    with pytest.raises(ValidationError, match='Conflito'):
        services.validar_agendamento(em(segunda, 10, 30))


def test_sabado_nao_tem_horarios(horario_comercial):
    assert services.horarios_livres(proxima_data(5)) == []


def test_dia_inativo_nao_tem_horarios(horario_comercial, segunda):
    Disponibilidade.objects.filter(dia_da_semana=0).update(ativo=False)
    assert services.horarios_livres(segunda) == []


def test_consulta_cancelada_libera_horario(consulta_futura, segunda):
    consulta_futura.status = 'cancelado'
    consulta_futura.save()
    assert '10:00' in horas(services.horarios_livres(segunda))


def test_ignorar_id_devolve_horario_da_propria_consulta(consulta_futura, segunda):
    livres = horas(services.horarios_livres(segunda, ignorar_id=consulta_futura.pk))
    assert '10:00' in livres


def test_validar_agendamento_rejeita_data_passada(horario_comercial):
    with pytest.raises(ValidationError, match='futuro'):
        services.validar_agendamento(timezone.now() - timezone.timedelta(hours=1))


def test_validar_agendamento_rejeita_dia_fechado(horario_comercial):
    with pytest.raises(ValidationError, match='não atende'):
        services.validar_agendamento(em(proxima_data(5), 10))


def test_validar_agendamento_rejeita_antes_da_abertura(horario_comercial, segunda):
    with pytest.raises(ValidationError, match='fora do expediente'):
        services.validar_agendamento(em(segunda, 7, 30))


def test_validar_agendamento_rejeita_sessao_que_passa_do_fechamento(horario_comercial, segunda):
    with pytest.raises(ValidationError, match='fora do expediente'):
        services.validar_agendamento(em(segunda, 18, 30))


def test_validar_agendamento_permite_encostar_no_fim_de_outra(consulta_futura, segunda):
    disponibilidade = services.validar_agendamento(em(segunda, 11))
    assert disponibilidade == Disponibilidade.objects.get(dia_da_semana=0)


def test_atualizar_status_confirma_e_carimba_observacao(consulta_futura):
    services.atualizar_status(consulta_futura, 'confirmado', 'Tutor confirmou pelo WhatsApp')
    consulta_futura.refresh_from_db()
    assert consulta_futura.status == 'confirmado'
    assert consulta_futura.observacoes.startswith('[')
    assert consulta_futura.observacoes.endswith('] Tutor confirmou pelo WhatsApp')


def test_atualizar_status_rejeita_transicao_invalida(consulta_futura):
    consulta_futura.status = 'realizado'
    consulta_futura.save()
    with pytest.raises(ValidationError):
        services.atualizar_status(consulta_futura, 'agendado')


def test_validar_telefone_rejeita_numero_curto():
    with pytest.raises(ValidationError):
        services.validar_telefone('1234')
