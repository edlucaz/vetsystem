"""Testes dos formulários (telas Django) que usam as regras de services.py."""
import datetime

from django.utils import timezone

from agendamentos.forms import AnimalForm, ConsultaForm, ProprietarioForm
from agendamentos.models import Consulta
from agendamentos.tests.utils import em


def dados_consulta(animal, data, hora='10:00', **extra):
    return {'animal': animal.pk, 'tipo': 'consulta', 'data_consulta': data.isoformat(),
            'hora_consulta': hora, 'observacoes': '', **extra}


def test_criacao_sem_status_e_consulta_nasce_agendada(horario_comercial, animal, segunda):
    form = ConsultaForm(data=dados_consulta(animal, segunda))
    assert 'status' not in form.fields
    assert form.is_valid(), form.errors
    assert form.save().status == 'agendado'


def test_criacao_em_conflito_e_invalida(consulta_futura, animal, segunda):
    form = ConsultaForm(data=dados_consulta(animal, segunda, '10:30'))
    assert not form.is_valid()
    assert 'Conflito' in ' '.join(form.non_field_errors())


def test_edicao_de_consulta_passada_mudando_so_observacoes(horario_comercial, animal):
    passado = timezone.localdate() - datetime.timedelta(days=7)
    consulta = Consulta.objects.create(animal=animal, data_hora=em(passado, 10), tipo='consulta')
    form = ConsultaForm(instance=consulta, data=dados_consulta(
        animal, passado, status='realizado', observacoes='Retorno em 30 dias'))
    assert form.is_valid(), form.errors


def test_animal_form_aceita_peso_com_virgula(proprietario):
    form = AnimalForm(data={'nome': 'Rex', 'especie': 'cao', 'peso': '12,50',
                            'proprietario': proprietario.pk})
    assert form.is_valid(), form.errors
    assert str(form.cleaned_data['peso']) == '12.50'


def test_animal_form_recusa_nascimento_futuro(proprietario):
    amanha = timezone.localdate() + datetime.timedelta(days=1)
    form = AnimalForm(data={'nome': 'Rex', 'especie': 'cao', 'data_nascimento': amanha.isoformat(),
                            'proprietario': proprietario.pk})
    assert not form.is_valid()
    assert 'data_nascimento' in form.errors


def test_proprietario_form_recusa_telefone_curto(db):
    form = ProprietarioForm(data={'nome': 'Ana', 'telefone': '1234'})
    assert not form.is_valid()
    assert 'telefone' in form.errors
