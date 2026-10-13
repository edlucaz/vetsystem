"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/tests/test_views.py
Função  : Testes das telas Django seguindo o fluxograma (login, cancelar x excluir,
          fluxo encadeado de cadastro, agendamento, lista de proprietários
          e ganchos do JavaScript da Fase 6).
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-13
"""
from django.urls import reverse
from django.utils import timezone
import pytest

from agendamentos.models import Animal, Consulta, Proprietario
from agendamentos.tests.utils import em

URLS_INTERNAS = [
    ('agendamentos:dashboard', {}),
    ('agendamentos:proprietario-list', {}),
    ('agendamentos:proprietario-detail', {'pk': 1}),
    ('agendamentos:proprietario-create', {}),
    ('agendamentos:proprietario-update', {'pk': 1}),
    ('agendamentos:proprietario-delete', {'pk': 1}),
    ('agendamentos:animal-list', {}),
    ('agendamentos:animal-detail', {'pk': 1}),
    ('agendamentos:animal-create', {}),
    ('agendamentos:animal-update', {'pk': 1}),
    ('agendamentos:animal-delete', {'pk': 1}),
    ('agendamentos:consulta-list', {}),
    ('agendamentos:consulta-detail', {'pk': 1}),
    ('agendamentos:consulta-create', {}),
    ('agendamentos:consulta-update', {'pk': 1}),
    ('agendamentos:consulta-cancelar', {'pk': 1}),
    ('agendamentos:consulta-delete', {'pk': 1}),
    ('agendamentos:disponibilidade-list', {}),
    ('agendamentos:disponibilidade-create', {}),
    ('agendamentos:disponibilidade-update', {'pk': 1}),
    ('agendamentos:disponibilidade-delete', {'pk': 1}),
]


@pytest.mark.django_db
@pytest.mark.parametrize('nome, kwargs', URLS_INTERNAS)
def test_telas_internas_exigem_login(client, nome, kwargs):
    resposta = client.get(reverse(nome, kwargs=kwargs))
    assert resposta.status_code == 302
    assert resposta.url.startswith('/login/')


@pytest.mark.django_db
def test_home_e_publica(client):
    assert client.get(reverse('agendamentos:home')).status_code == 200


def test_cancelar_muda_status_e_mantem_registro(cliente_logado, consulta_futura):
    resposta = cliente_logado.post(reverse('agendamentos:consulta-cancelar', args=[consulta_futura.pk]))
    assert resposta.status_code == 302
    consulta_futura.refresh_from_db()
    assert consulta_futura.status == 'cancelado'
    assert Consulta.objects.filter(pk=consulta_futura.pk).exists()


def test_excluir_apaga_registro(cliente_logado, consulta_futura):
    resposta = cliente_logado.post(reverse('agendamentos:consulta-delete', args=[consulta_futura.pk]))
    assert resposta.status_code == 302
    assert not Consulta.objects.filter(pk=consulta_futura.pk).exists()


def test_fluxo_proprietario_segue_para_animal(cliente_logado):
    url = reverse('agendamentos:proprietario-create') + '?fluxo=agendamento'
    resposta = cliente_logado.post(url, {'nome': 'Maria Souza', 'telefone': '(19) 98888-7777'})
    novo = Proprietario.objects.get(nome='Maria Souza')
    assert resposta.status_code == 302
    assert resposta.url == f"{reverse('agendamentos:animal-create')}?proprietario={novo.pk}&fluxo=agendamento"


def test_fluxo_animal_segue_para_consulta(cliente_logado, proprietario):
    url = reverse('agendamentos:animal-create') + '?fluxo=agendamento'
    resposta = cliente_logado.post(url, {'nome': 'Mimi', 'especie': 'gato', 'proprietario': proprietario.pk})
    novo = Animal.objects.get(nome='Mimi')
    assert resposta.status_code == 302
    assert resposta.url == f"{reverse('agendamentos:consulta-create')}?animal={novo.pk}"


def _dados_consulta(animal, data, hora):
    return {'animal': animal.pk, 'data_consulta': data.isoformat(), 'hora_consulta': hora,
            'tipo': 'consulta', 'observacoes': ''}


def test_criar_consulta_pela_tela(cliente_logado, horario_comercial, animal, segunda):
    resposta = cliente_logado.post(reverse('agendamentos:consulta-create'),
                                   _dados_consulta(animal, segunda, '09:00'))
    assert resposta.status_code == 302
    consulta = Consulta.objects.get(animal=animal)
    assert consulta.status == 'agendado'
    assert consulta.disponibilidade is not None


def test_criar_consulta_em_conflito_mostra_erro(cliente_logado, consulta_futura, animal, segunda):
    resposta = cliente_logado.post(reverse('agendamentos:consulta-create'),
                                   _dados_consulta(animal, segunda, '10:30'))
    assert resposta.status_code == 200
    assert 'Conflito de horário' in resposta.content.decode()
    assert Consulta.objects.count() == 1


def test_lista_proprietarios_total_de_animais_e_busca_por_email(cliente_logado, animal):
    Proprietario.objects.create(nome='Ana Lima', telefone='(19) 97777-6666', email='ana@exemplo.com')
    lista = cliente_logado.get(reverse('agendamentos:proprietario-list'))
    joao = next(p for p in lista.context['proprietarios'] if p.nome == 'João Silva')
    assert joao.total_animais == 1
    assert '1 animal(is)' in lista.content.decode()

    busca = cliente_logado.get(reverse('agendamentos:proprietario-list'), {'q': 'ana@exemplo'})
    assert [p.nome for p in busca.context['proprietarios']] == ['Ana Lima']


def test_nova_consulta_tem_ganchos_do_js_e_reserva_sem_js(cliente_logado):
    html = cliente_logado.get(reverse('agendamentos:consulta-create')).content.decode()
    assert 'data-url-horarios="/api/horarios-livres/"' in html
    assert '<select name="animal"' in html and 'id="id_animal"' in html


def test_dashboard_mostra_acoes_rapidas_da_consulta_de_hoje(cliente_logado, animal):
    consulta = Consulta.objects.create(animal=animal, data_hora=em(timezone.localdate(), 23), tipo='consulta')
    html = cliente_logado.get(reverse('agendamentos:dashboard')).content.decode()
    assert f'data-acoes-consulta="{consulta.pk}"' in html
