"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II

Arquivo : agendamentos/api/views.py
Função  : ViewSets da API REST (CRUD de proprietários, animais, consultas e
          disponibilidades), ação de status da consulta e horários livres
          do dia — etapas do fluxograma swimlane v2.

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-10-13
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django_filters import rest_framework as filtros
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import services
from ..models import Animal, Consulta, Disponibilidade, Proprietario
from .serializers import (AnimalSerializer, AtualizarStatusSerializer, ConsultaSerializer,
                          DisponibilidadeSerializer, HorariosLivresEntradaSerializer,
                          ProprietarioSerializer, RegistroPesoSerializer)


class ProprietarioViewSet(viewsets.ModelViewSet):
    """CRUD de tutores. Busca: ?search=<nome, telefone, CPF ou e-mail>."""
    serializer_class = ProprietarioSerializer
    search_fields = ['nome', 'telefone', 'cpf', 'email']
    ordering_fields = ['nome']

    def get_queryset(self):
        return Proprietario.objects.annotate(total_animais=Count('animais')).order_by('nome')


class AnimalViewSet(viewsets.ModelViewSet):
    """CRUD de animais. Autocomplete (fluxograma, etapa 2): ?search=<nome do animal ou do tutor>."""
    serializer_class = AnimalSerializer
    queryset = Animal.objects.select_related('proprietario').order_by('nome')
    search_fields = ['nome', 'proprietario__nome', 'proprietario__telefone']
    filterset_fields = ['especie', 'proprietario']
    ordering_fields = ['nome']

    @extend_schema(responses=RegistroPesoSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='pesos', url_name='pesos')
    def pesos(self, request, pk=None):
        """Histórico de peso do animal, da pesagem mais recente à mais antiga."""
        return Response(RegistroPesoSerializer(self.get_object().pesos.all(), many=True).data)


class ConsultaFiltro(filtros.FilterSet):
    data = filtros.DateFilter(field_name='data_hora', lookup_expr='date')
    inicio = filtros.DateFilter(field_name='data_hora', lookup_expr='date__gte')
    fim = filtros.DateFilter(field_name='data_hora', lookup_expr='date__lte')

    class Meta:
        model = Consulta
        fields = ['status', 'tipo', 'animal', 'data', 'inicio', 'fim']


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    Agenda. Filtros: ?status= ?tipo= ?animal= ?data=AAAA-MM-DD ?inicio=&fim=.
    Criar = fluxograma "Registrar consulta (status: agendado)".
    """
    serializer_class = ConsultaSerializer
    queryset = Consulta.objects.select_related('animal__proprietario', 'disponibilidade').order_by('data_hora')
    filterset_class = ConsultaFiltro
    search_fields = ['animal__nome', 'animal__proprietario__nome']
    ordering_fields = ['data_hora']

    @extend_schema(request=AtualizarStatusSerializer, responses=ConsultaSerializer)
    @action(detail=True, methods=['post'], url_path='status', url_name='status')
    def atualizar_status(self, request, pk=None):
        """Fluxograma: "Confirmar agendamento" e "Atualizar status (realizado/cancelado)"."""
        consulta = self.get_object()
        entrada = AtualizarStatusSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        try:
            services.atualizar_status(consulta, entrada.validated_data['status'],
                                      entrada.validated_data.get('observacao', ''))
        except DjangoValidationError as erro:
            raise serializers.ValidationError({'status': erro.messages})
        return Response(self.get_serializer(consulta).data)


class DisponibilidadeViewSet(viewsets.ModelViewSet):
    """Horários de funcionamento (um por dia da semana)."""
    serializer_class = DisponibilidadeSerializer
    queryset = Disponibilidade.objects.order_by('dia_da_semana')
    pagination_class = None  # no máximo 5 registros


class HorariosLivresView(APIView):
    """Fluxograma, etapa 3 — GET /api/horarios-livres/?data=AAAA-MM-DD[&duracao=60][&ignorar=<id>]."""

    @extend_schema(parameters=[HorariosLivresEntradaSerializer])
    def get(self, request):
        entrada = HorariosLivresEntradaSerializer(data=request.query_params)
        entrada.is_valid(raise_exception=True)
        data = entrada.validated_data['data']
        duracao = entrada.validated_data['duracao']
        disponibilidade = services.disponibilidade_do_dia(data)
        livres = services.horarios_livres(data, duracao, entrada.validated_data.get('ignorar'))
        return Response({
            'data': data.isoformat(),
            'aberto': disponibilidade is not None,
            'inicio': f'{disponibilidade.hora_inicio:%H:%M}' if disponibilidade else None,
            'fim': f'{disponibilidade.hora_fim:%H:%M}' if disponibilidade else None,
            'duracao': duracao,
            'horarios': [f'{h:%H:%M}' for h in livres],
        })
