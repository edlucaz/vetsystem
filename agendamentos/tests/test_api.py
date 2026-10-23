"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/tests/test_api.py
Função  : Testes da API REST (DRF): autenticação por sessão + CSRF, CRUD,
          busca/filtros, "Horário disponível?", status e horários livres.
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-13
"""
import datetime
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
import pytest

from agendamentos.models import Animal, Consulta, Proprietario
from agendamentos.tests.utils import em, proxima_data


def _resultados(resposta):
    return resposta.json()['results']


@pytest.mark.django_db
def test_sem_login_retorna_403():
    resposta = APIClient().get(reverse('api:consulta-list'))
    assert resposta.status_code == 403


def test_post_sem_token_csrf_retorna_403(usuario):
    cliente = APIClient(enforce_csrf_checks=True)
    cliente.force_login(usuario)
    resposta = cliente.post(reverse('api:proprietario-list'),
                            {'nome': 'Maria', 'telefone': '(19) 98888-7777'}, format='json')
    assert resposta.status_code == 403


def test_lista_de_proprietarios_traz_total_animais(api, animal):
    resposta = api.get(reverse('api:proprietario-list'))
    assert resposta.status_code == 200
    assert _resultados(resposta)[0]['total_animais'] == 1


def test_criar_proprietario_com_telefone_curto_retorna_400(api):
    resposta = api.post(reverse('api:proprietario-list'),
                        {'nome': 'Maria', 'telefone': '1234'}, format='json')
    assert resposta.status_code == 400
    assert 'telefone' in resposta.json()
    assert not Proprietario.objects.filter(nome='Maria').exists()


def test_busca_de_animal_pelo_nome_do_tutor(api, animal):
    resposta = api.get(reverse('api:animal-list'), {'search': 'João'})
    assert [a['nome'] for a in _resultados(resposta)] == ['Rex']


def test_filtro_de_animais_por_proprietario(api, animal):
    outro = Proprietario.objects.create(nome='Ana', telefone='(19) 97777-6666')
    Animal.objects.create(nome='Mimi', especie='gato', proprietario=outro)
    resposta = api.get(reverse('api:animal-list'), {'proprietario': outro.pk})
    assert [a['nome'] for a in _resultados(resposta)] == ['Mimi']


def test_criar_consulta_nasce_agendada_com_disponibilidade(api, horario_comercial, animal, segunda):
    resposta = api.post(reverse('api:consulta-list'),
                        {'animal': animal.pk, 'data_hora': em(segunda, 9).isoformat(),
                         'tipo': 'fisioterapia'}, format='json')
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados['status'] == 'agendado'
    assert dados['disponibilidade'] == horario_comercial[0].pk


def test_criar_consulta_em_conflito_retorna_400(api, consulta_futura, animal, segunda):
    resposta = api.post(reverse('api:consulta-list'),
                        {'animal': animal.pk, 'data_hora': em(segunda, 10, 30).isoformat(),
                         'tipo': 'consulta'}, format='json')
    assert resposta.status_code == 400
    assert 'data_hora' in resposta.json()


def test_criar_consulta_fora_do_expediente_retorna_400(api, horario_comercial, animal, segunda):
    resposta = api.post(reverse('api:consulta-list'),
                        {'animal': animal.pk, 'data_hora': em(segunda, 18, 30).isoformat(),
                         'tipo': 'consulta'}, format='json')
    assert resposta.status_code == 400
    assert 'data_hora' in resposta.json()


def test_criar_consulta_no_passado_retorna_400(api, horario_comercial, animal):
    ontem = timezone.localtime() - datetime.timedelta(days=1)
    resposta = api.post(reverse('api:consulta-list'),
                        {'animal': animal.pk, 'data_hora': ontem.isoformat(), 'tipo': 'consulta'},
                        format='json')
    assert resposta.status_code == 400
    assert 'data_hora' in resposta.json()


def test_filtros_de_consulta_por_data_e_periodo(api, consulta_futura, animal, segunda):
    outra_segunda = proxima_data(0, semanas=2)
    Consulta.objects.create(animal=animal, data_hora=em(outra_segunda, 10), tipo='consulta')
    url = reverse('api:consulta-list')

    por_data = _resultados(api.get(url, {'data': segunda.isoformat()}))
    assert [c['id'] for c in por_data] == [consulta_futura.pk]

    periodo = _resultados(api.get(url, {'inicio': segunda.isoformat(),
                                        'fim': outra_segunda.isoformat()}))
    assert len(periodo) == 2

    so_a_segunda = _resultados(api.get(url, {'inicio': outra_segunda.isoformat()}))
    assert [c['data_hora'][:10] for c in so_a_segunda] == [outra_segunda.isoformat()]


def test_confirmar_consulta_pela_acao_de_status(api, consulta_futura):
    resposta = api.post(reverse('api:consulta-status', args=[consulta_futura.pk]),
                        {'status': 'confirmado'}, format='json')
    assert resposta.status_code == 200
    assert resposta.json()['status'] == 'confirmado'
    consulta_futura.refresh_from_db()
    assert consulta_futura.status == 'confirmado'


def test_transicao_de_realizado_para_agendado_retorna_400(api, consulta_futura):
    Consulta.objects.filter(pk=consulta_futura.pk).update(status='realizado')
    resposta = api.post(reverse('api:consulta-status', args=[consulta_futura.pk]),
                        {'status': 'agendado'}, format='json')
    assert resposta.status_code == 400
    assert 'status' in resposta.json()


def test_horarios_livres_em_segunda(api, horario_comercial, segunda):
    resposta = api.get(reverse('api:horarios-livres'), {'data': segunda.isoformat()})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados['aberto'] is True
    assert len(dados['horarios']) == 21


def test_horarios_livres_em_sabado(api, horario_comercial):
    sabado = proxima_data(5)
    dados = api.get(reverse('api:horarios-livres'), {'data': sabado.isoformat()}).json()
    assert dados['aberto'] is False
    assert dados['horarios'] == []


def test_horarios_livres_com_data_invalida_retorna_400(api, horario_comercial):
    resposta = api.get(reverse('api:horarios-livres'), {'data': '31/02/2026'})
    assert resposta.status_code == 400


def test_disponibilidade_duplicada_retorna_400(api, horario_comercial):
    resposta = api.post(reverse('api:disponibilidade-list'),
                        {'dia_da_semana': 0, 'hora_inicio': '09:00', 'hora_fim': '12:00'},
                        format='json')
    assert resposta.status_code == 400
    assert 'dia_da_semana' in resposta.json()


def test_schema_openapi_responde(api):
    resposta = api.get(reverse('schema'))
    assert resposta.status_code == 200


def test_pesos_do_animal_requer_login():
    cliente_anonimo = APIClient()
    resposta = cliente_anonimo.get('/api/animais/1/pesos/')
    assert resposta.status_code == 403


def test_pesos_do_animal_retorna_lista(api, animal):
    animal.peso = Decimal('11.50')
    animal.save()
    resposta = api.get(reverse('api:animal-pesos', args=[animal.pk]))
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]['peso'] == '11.50'
    assert 'data' in dados[0]


def test_patch_animal_com_peso_atualiza_historico(api, animal):
    resposta = api.patch(reverse('api:animal-detail', args=[animal.pk]), {'peso': '13.25'}, format='json')
    assert resposta.status_code == 200
    assert animal.pesos.count() == 1
    assert animal.pesos.first().peso == Decimal('13.25')


def test_busca_proprietarios_por_termo(api, proprietario):
    resposta = api.get(reverse('api:proprietario-list'), {'search': 'Silva'})
    assert resposta.status_code == 200
    assert [p['nome'] for p in _resultados(resposta)] == ['João Silva']


def test_filtro_animal_por_especie_e_termo(api, animal):
    resposta = api.get(reverse('api:animal-list'), {'especie': 'cao', 'search': 'Rex'})
    assert resposta.status_code == 200
    assert [a['nome'] for a in _resultados(resposta)] == ['Rex']



# --- Fase 7: estatísticas e horários públicos ---------------------------------

@pytest.mark.django_db
def test_estatisticas_exige_login():
    assert APIClient().get(reverse('api:estatisticas')).status_code == 403


def test_estatisticas_devolve_indicadores(api, horario_comercial):
    resposta = api.get(reverse('api:estatisticas'), {'meses': 'abc'})
    assert resposta.status_code == 200
    assert resposta.json()['periodo']['meses'] == 6
    assert api.get(reverse('api:estatisticas'), {'meses': 99}).json()['periodo']['meses'] == 24


def test_horarios_publicos_anonimo_sem_dados_pessoais(horario_comercial, consulta_futura):
    resposta = APIClient().get(reverse('api:horarios-publicos'))
    assert resposta.status_code == 200
    texto = resposta.content.decode()
    assert 'animal' not in texto and 'proprietario' not in texto and consulta_futura.animal.nome not in texto
    dias = resposta.json()['dias']
    assert dias and len(dias) <= 3
    assert all(len(d['horarios']) <= 8 for d in dias)
