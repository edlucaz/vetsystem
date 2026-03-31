"""
VETSystem — agendamentos/urls.py  (v2 — com Consultas)
Autor: Lucas Eduardo Rocha (RA 24217901) | 2026-03-11
"""
from django.urls import path
from . import views

app_name = 'agendamentos'

urlpatterns = [

    # =========================================================================
    # FRONTPAGE E DASHBOARD
    # =========================================================================
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # =========================================================================
    # PROPRIETÁRIO
    # =========================================================================
    path('proprietarios/', views.ProprietarioListView.as_view(), name='proprietario-list'),
    path('proprietarios/<int:pk>/', views.ProprietarioDetailView.as_view(), name='proprietario-detail'),
    path('proprietarios/novo/', views.ProprietarioCreateView.as_view(), name='proprietario-create'),
    path('proprietarios/<int:pk>/editar/', views.ProprietarioUpdateView.as_view(), name='proprietario-update'),
    path('proprietarios/<int:pk>/excluir/', views.ProprietarioDeleteView.as_view(), name='proprietario-delete'),

    # =========================================================================
    # ANIMAL
    # =========================================================================
    path('animais/', views.AnimalListView.as_view(), name='animal-list'),
    path('animais/<int:pk>/', views.AnimalDetailView.as_view(), name='animal-detail'),
    path('animais/novo/', views.AnimalCreateView.as_view(), name='animal-create'),
    path('animais/<int:pk>/editar/', views.AnimalUpdateView.as_view(), name='animal-update'),
    path('animais/<int:pk>/excluir/', views.AnimalDeleteView.as_view(), name='animal-delete'),

    # =========================================================================
    # CONSULTA
    # =========================================================================
    # Lista com filtros: /consultas/?status=agendado&data=2026-04-10
    path('consultas/', views.ConsultaListView.as_view(), name='consulta-list'),
    # Detalhe com dados do animal e proprietário
    path('consultas/<int:pk>/', views.ConsultaDetailView.as_view(), name='consulta-detail'),
    # Agendamento: /consultas/nova/ ou /consultas/nova/?animal=1
    path('consultas/nova/', views.ConsultaCreateView.as_view(), name='consulta-create'),
    # Edição de consulta existente
    path('consultas/<int:pk>/editar/', views.ConsultaUpdateView.as_view(), name='consulta-update'),
    # Cancelamento com confirmação
    path('consultas/<int:pk>/cancelar/', views.ConsultaDeleteView.as_view(), name='consulta-delete'),

    # =========================================================================
    # DISPONIBILIDADE — horários de funcionamento da clínica
    # =========================================================================
    path('disponibilidade/', views.DisponibilidadeListView.as_view(), name='disponibilidade-list'),
    path('disponibilidade/novo/', views.DisponibilidadeCreateView.as_view(), name='disponibilidade-create'),
    path('disponibilidade/<int:pk>/editar/', views.DisponibilidadeUpdateView.as_view(), name='disponibilidade-update'),
    path('disponibilidade/<int:pk>/excluir/', views.DisponibilidadeDeleteView.as_view(), name='disponibilidade-delete'),
]
