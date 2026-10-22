"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II

Arquivo : agendamentos/api/serializers.py
Função  : Serializers da API REST (Django REST Framework). As validações
          chamam agendamentos/services.py — as mesmas regras dos formulários.

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-10-13
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .. import services
from ..models import Animal, Consulta, Disponibilidade, Proprietario, RegistroPeso


class ProprietarioSerializer(serializers.ModelSerializer):
    total_animais = serializers.IntegerField(read_only=True)

    class Meta:
        model = Proprietario
        fields = ['id', 'nome', 'telefone', 'email', 'cpf', 'total_animais']

    def validate_telefone(self, valor):
        return services.validar_telefone(valor)  # o DRF converte a ValidationError do Django


class AnimalSerializer(serializers.ModelSerializer):
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)
    idade = serializers.IntegerField(read_only=True)
    proprietario_nome = serializers.CharField(source='proprietario.nome', read_only=True)
    proprietario_telefone = serializers.CharField(source='proprietario.telefone', read_only=True)

    class Meta:
        model = Animal
        fields = ['id', 'nome', 'especie', 'especie_display', 'raca', 'data_nascimento', 'idade',
                  'peso', 'queixa', 'proprietario', 'proprietario_nome', 'proprietario_telefone']

    def validate_data_nascimento(self, valor):
        return services.validar_data_nascimento(valor)


class RegistroPesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroPeso
        fields = ['id', 'data', 'peso']


class ConsultaSerializer(serializers.ModelSerializer):
    animal_nome = serializers.CharField(source='animal.nome', read_only=True)
    proprietario_nome = serializers.CharField(source='animal.proprietario.nome', read_only=True)
    proprietario_telefone = serializers.CharField(source='animal.proprietario.telefone', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    disponibilidade_descricao = serializers.StringRelatedField(source='disponibilidade', read_only=True)
    link_whatsapp = serializers.CharField(read_only=True)

    class Meta:
        model = Consulta
        fields = ['id', 'animal', 'animal_nome', 'proprietario_nome', 'proprietario_telefone',
                  'data_hora', 'duracao_minutos', 'tipo', 'tipo_display', 'status', 'status_display',
                  'observacoes', 'disponibilidade', 'disponibilidade_descricao', 'link_whatsapp']
        # Fluxograma: toda consulta nasce "agendado"; o status muda por POST .../status/
        read_only_fields = ['status', 'disponibilidade']
        extra_kwargs = {'duracao_minutos': {'min_value': 15, 'max_value': 240}}

    def validate(self, attrs):
        """Decisão "Horário disponível?" — a mesma regra do formulário (services)."""
        consulta = self.instance
        data_hora = attrs.get('data_hora', consulta.data_hora if consulta else None)
        duracao = attrs.get('duracao_minutos',
                            consulta.duracao_minutos if consulta else services.DURACAO_PADRAO_MINUTOS)
        mudou_horario = (consulta is None or data_hora != consulta.data_hora
                         or duracao != consulta.duracao_minutos)
        if mudou_horario and data_hora:
            try:
                services.validar_agendamento(data_hora, duracao, ignorar_id=getattr(consulta, 'pk', None))
            except DjangoValidationError as erro:
                raise serializers.ValidationError({'data_hora': erro.messages})
        return attrs


class AtualizarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Consulta.STATUS_CHOICES)
    observacao = serializers.CharField(required=False, allow_blank=True, max_length=300)


class DisponibilidadeSerializer(serializers.ModelSerializer):
    dia_da_semana_display = serializers.CharField(source='get_dia_da_semana_display', read_only=True)

    class Meta:
        model = Disponibilidade
        fields = ['id', 'dia_da_semana', 'dia_da_semana_display', 'hora_inicio', 'hora_fim', 'ativo']
        extra_kwargs = {'dia_da_semana': {'validators': [UniqueValidator(
            queryset=Disponibilidade.objects.all(),
            message='Já existe um horário cadastrado para este dia da semana.')]}}

    def validate(self, attrs):
        inicio = attrs.get('hora_inicio', getattr(self.instance, 'hora_inicio', None))
        fim = attrs.get('hora_fim', getattr(self.instance, 'hora_fim', None))
        if inicio and fim and fim <= inicio:
            raise serializers.ValidationError(
                {'hora_fim': 'O horário de encerramento deve ser posterior ao de início.'})
        return attrs


class HorariosLivresEntradaSerializer(serializers.Serializer):
    data = serializers.DateField()
    duracao = serializers.IntegerField(default=services.DURACAO_PADRAO_MINUTOS, min_value=15, max_value=240)
    ignorar = serializers.IntegerField(required=False)
