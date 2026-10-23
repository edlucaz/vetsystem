"""
Testes automatizados de acessibilidade (WCAG 2.1) — verificações estruturais sem
navegador: idioma, link "Pular para o conteúdo", um único <h1>, rótulo em todo
campo, referências ARIA válidas, ids únicos, <th> com scope e <img> com alt.
(Contraste e teclado: Lighthouse/axe e checklist manual.)
"""
from html.parser import HTMLParser

import pytest
from django.urls import reverse

from agendamentos.models import Disponibilidade

CAMPOS = {'input', 'select', 'textarea'}
TIPOS_SEM_ROTULO = {'hidden', 'submit', 'button', 'reset', 'image'}


class _Coletor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elementos = []
        self._labels_abertos = 0

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        atributos['_dentro_de_label'] = self._labels_abertos > 0
        self.elementos.append((tag, atributos))
        if tag == 'label':
            self._labels_abertos += 1

    def handle_startendtag(self, tag, attrs):
        atributos = dict(attrs)
        atributos['_dentro_de_label'] = self._labels_abertos > 0
        self.elementos.append((tag, atributos))

    def handle_endtag(self, tag):
        if tag == 'label' and self._labels_abertos:
            self._labels_abertos -= 1


def problemas_de_acessibilidade(html):
    coletor = _Coletor()
    coletor.feed(html)
    elementos = coletor.elementos
    problemas = []
    ids = [a['id'] for _, a in elementos if a.get('id')]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    if repetidos:
        problemas.append(f'ids repetidos: {repetidos}')
    existentes = set(ids)
    rotulos_for = {a.get('for') for t, a in elementos if t == 'label' and a.get('for')}
    for tag, a in elementos:
        if tag == 'html' and (a.get('lang') or '').lower() != 'pt-br':
            problemas.append('<html> sem lang="pt-br"')
        if tag in CAMPOS and (a.get('type') or '').lower() not in TIPOS_SEM_ROTULO:
            if not (a.get('id') in rotulos_for or a.get('aria-label') or a.get('aria-labelledby')
                    or a['_dentro_de_label']):
                problemas.append(f'campo sem rótulo: <{tag} name="{a.get("name")}" id="{a.get("id")}">')
        for atributo in ('aria-describedby', 'aria-labelledby', 'aria-controls', 'aria-activedescendant'):
            for ref in (a.get(atributo) or '').split():
                if ref not in existentes:
                    problemas.append(f'{atributo}="{ref}" aponta para id inexistente')
        if tag == 'img' and 'alt' not in a:
            problemas.append('<img> sem alt')
        if tag == 'th' and 'scope' not in a:
            problemas.append('<th> sem scope')
    total_h1 = sum(1 for t, _ in elementos if t == 'h1')
    if total_h1 != 1:
        problemas.append(f'esperado 1 <h1>, encontrado {total_h1}')
    if not any(t == 'a' and a.get('href') == '#conteudo' for t, a in elementos):
        problemas.append('falta o link "Pular para o conteúdo"')
    if 'conteudo' not in existentes:
        problemas.append('falta <main id="conteudo">')
    return problemas


PAGINAS_PUBLICAS = ['agendamentos:home', 'login']
PAGINAS_INTERNAS = [
    ('agendamentos:dashboard', None), ('agendamentos:agenda-semanal', None), ('agendamentos:consulta-list', None),
    ('agendamentos:consulta-create', None), ('agendamentos:consulta-detail', 'consulta'),
    ('agendamentos:consulta-update', 'consulta'), ('agendamentos:consulta-cancelar', 'consulta'),
    ('agendamentos:consulta-delete', 'consulta'), ('agendamentos:proprietario-list', None),
    ('agendamentos:proprietario-create', None), ('agendamentos:proprietario-detail', 'proprietario'),
    ('agendamentos:proprietario-update', 'proprietario'), ('agendamentos:proprietario-delete', 'proprietario'),
    ('agendamentos:animal-list', None), ('agendamentos:animal-create', None),
    ('agendamentos:animal-detail', 'animal'), ('agendamentos:animal-update', 'animal'),
    ('agendamentos:animal-delete', 'animal'), ('agendamentos:disponibilidade-list', None),
    ('agendamentos:disponibilidade-create', None), ('agendamentos:disponibilidade-update', 'disponibilidade'),
]


@pytest.mark.parametrize('nome', PAGINAS_PUBLICAS)
def test_paginas_publicas_acessiveis(client, db, nome):
    resposta = client.get(reverse(nome))
    assert resposta.status_code == 200
    assert problemas_de_acessibilidade(resposta.content.decode()) == []


@pytest.mark.parametrize('nome,objeto', PAGINAS_INTERNAS)
def test_paginas_internas_acessiveis(cliente_logado, consulta_futura, nome, objeto):
    alvos = {'consulta': consulta_futura, 'animal': consulta_futura.animal,
             'proprietario': consulta_futura.animal.proprietario,
             'disponibilidade': Disponibilidade.objects.first()}
    url = reverse(nome, args=[alvos[objeto].pk]) if objeto else reverse(nome)
    resposta = cliente_logado.get(url)
    assert resposta.status_code == 200
    assert problemas_de_acessibilidade(resposta.content.decode()) == []


def test_formulario_com_erros_continua_acessivel(cliente_logado):
    resposta = cliente_logado.post(reverse('agendamentos:proprietario-create'), {'nome': '', 'telefone': '12'})
    html = resposta.content.decode()
    assert resposta.status_code == 200 and 'aria-invalid="true"' in html
    assert problemas_de_acessibilidade(html) == []
