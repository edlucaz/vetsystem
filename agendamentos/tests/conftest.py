"""Fixtures compartilhadas pelos testes do VETSystem (pytest-django)."""
import datetime

import pytest

from agendamentos.models import Animal, Consulta, Disponibilidade, Proprietario
from agendamentos.tests.utils import em, proxima_data


@pytest.fixture
def usuario(django_user_model):
    return django_user_model.objects.create_user(username='fernanda', password='senha-de-teste-123')


@pytest.fixture
def cliente_logado(client, usuario):
    client.force_login(usuario)
    return client


@pytest.fixture
def horario_comercial(db):
    """Expediente padrão da ATIVO PET: segunda a sexta, 08:00–19:00."""
    Disponibilidade.objects.all().delete()
    return [Disponibilidade.objects.create(dia_da_semana=dia, hora_inicio=datetime.time(8),
                                           hora_fim=datetime.time(19)) for dia in range(5)]


@pytest.fixture
def proprietario(db):
    return Proprietario.objects.create(nome='João Silva', telefone='(19) 99999-9999')


@pytest.fixture
def animal(proprietario):
    return Animal.objects.create(nome='Rex', especie='cao', proprietario=proprietario)


@pytest.fixture
def segunda():
    return proxima_data(0)


@pytest.fixture
def consulta_futura(horario_comercial, animal, segunda):
    return Consulta.objects.create(animal=animal, data_hora=em(segunda, 10), tipo='fisioterapia')
