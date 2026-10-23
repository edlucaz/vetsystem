"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II

Arquivo : agendamentos/api/urls.py
Função  : Rotas da API REST (namespace 'api'), incluídas em /api/:
            /api/proprietarios/, /api/animais/ (+ /api/animais/<id>/pesos/),
            /api/consultas/ (+ /api/consultas/<id>/status/),
            /api/disponibilidades/, /api/horarios-livres/,
            /api/estatisticas/ e /api/horarios-publicos/ (Fase 7).

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-10-13
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

roteador = DefaultRouter()
roteador.register('proprietarios', views.ProprietarioViewSet, basename='proprietario')
roteador.register('animais', views.AnimalViewSet, basename='animal')
roteador.register('consultas', views.ConsultaViewSet, basename='consulta')
roteador.register('disponibilidades', views.DisponibilidadeViewSet, basename='disponibilidade')

urlpatterns = [
    path('horarios-livres/', views.HorariosLivresView.as_view(), name='horarios-livres'),
    path('estatisticas/', views.EstatisticasView.as_view(), name='estatisticas'),
    path('horarios-publicos/', views.HorariosPublicosView.as_view(), name='horarios-publicos'),
    path('', include(roteador.urls)),
]
