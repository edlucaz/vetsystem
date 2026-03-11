"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/urls.py
Função  : Define as rotas (URLs) do app de agendamentos.
          Cada URL é mapeada para uma view específica.

          Convenção de nomes das rotas:
            home                 → /
            proprietario-list    → /proprietarios/
            proprietario-detail  → /proprietarios/<pk>/
            proprietario-create  → /proprietarios/novo/
            proprietario-update  → /proprietarios/<pk>/editar/
            proprietario-delete  → /proprietarios/<pk>/excluir/
            (mesma convenção para animal-)

          Os nomes das rotas são usados nos templates com {% url 'nome-da-rota' %}
          e nas views com reverse_lazy('nome-da-rota'), evitando URLs hardcoded.

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from django.urls import path
from . import views

# Label do app — permite referenciar as URLs com namespace: agendamentos:proprietario-list
app_name = 'agendamentos'

urlpatterns = [

    # =========================================================================
    # URL DA FRONTPAGE
    # =========================================================================

    # Página inicial pública da ATIVO PET — landing page institucional
    # Acessível sem login em: /
    path(
        '',
        views.HomeView.as_view(),
        name='home'
    ),


    # =========================================================================
    # URLS DE PROPRIETÁRIO
    # =========================================================================

    # Lista todos os proprietários com busca
    # Ex: /proprietarios/ ou /proprietarios/?q=João
    path(
        'proprietarios/',
        views.ProprietarioListView.as_view(),
        name='proprietario-list'
    ),

    # Detalhe de um proprietário específico com seus animais
    # Ex: /proprietarios/1/
    path(
        'proprietarios/<int:pk>/',
        views.ProprietarioDetailView.as_view(),
        name='proprietario-detail'
    ),

    # Formulário de cadastro de novo proprietário
    # Ex: /proprietarios/novo/
    path(
        'proprietarios/novo/',
        views.ProprietarioCreateView.as_view(),
        name='proprietario-create'
    ),

    # Formulário de edição de proprietário existente
    # Ex: /proprietarios/1/editar/
    path(
        'proprietarios/<int:pk>/editar/',
        views.ProprietarioUpdateView.as_view(),
        name='proprietario-update'
    ),

    # Página de confirmação e exclusão de proprietário
    # Ex: /proprietarios/1/excluir/
    path(
        'proprietarios/<int:pk>/excluir/',
        views.ProprietarioDeleteView.as_view(),
        name='proprietario-delete'
    ),


    # =========================================================================
    # URLS DE ANIMAL
    # =========================================================================

    # Lista todos os animais com busca e filtro por espécie
    # Ex: /animais/ ou /animais/?q=Rex ou /animais/?especie=cao
    path(
        'animais/',
        views.AnimalListView.as_view(),
        name='animal-list'
    ),

    # Detalhe de um animal com histórico de consultas
    # Ex: /animais/1/
    path(
        'animais/<int:pk>/',
        views.AnimalDetailView.as_view(),
        name='animal-detail'
    ),

    # Formulário de cadastro de novo animal
    # Ex: /animais/novo/ ou /animais/novo/?proprietario=1
    path(
        'animais/novo/',
        views.AnimalCreateView.as_view(),
        name='animal-create'
    ),

    # Formulário de edição de animal existente
    # Ex: /animais/1/editar/
    path(
        'animais/<int:pk>/editar/',
        views.AnimalUpdateView.as_view(),
        name='animal-update'
    ),

    # Página de confirmação e exclusão de animal
    # Ex: /animais/1/excluir/
    path(
        'animais/<int:pk>/excluir/',
        views.AnimalDeleteView.as_view(),
        name='animal-delete'
    ),

]
