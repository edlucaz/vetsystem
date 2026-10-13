"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II

Arquivo : agendamentos/services.py
Função  : Regras de negócio do agendamento, usadas pelos formulários (telas
          Django) e pela API REST — uma única fonte de verdade para:
            - "Consultar horários livres" (fluxograma, etapa 3);
            - "Horário disponível?" (fluxograma, decisão 5): data futura +
              Disponibilidade do dia + sem conflito;
            - "Confirmar agendamento" / "Atualizar status" (fluxograma, final).

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-10-13
"""

import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Consulta, Disponibilidade

INTERVALO_GRADE_MINUTOS = 30   # de quanto em quanto tempo a agenda oferece horários
DURACAO_PADRAO_MINUTOS = 60    # duração padrão das sessões da ATIVO PET

NOMES_DIAS = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira',
              'sexta-feira', 'sábado', 'domingo']

# Transições das ações rápidas (fluxograma: confirmar; realizar atendimento ou
# registrar ausência). A edição completa da consulta ainda corrige qualquer status.
TRANSICOES_STATUS = {
    'agendado': {'confirmado', 'realizado', 'cancelado'},
    'confirmado': {'realizado', 'cancelado'},
    'realizado': set(),
    'cancelado': set(),
}


def validar_telefone(telefone):
    """Exige ao menos 8 dígitos; devolve o telefone sem espaços nas pontas."""
    telefone = (telefone or '').strip()
    if len([c for c in telefone if c.isdigit()]) < 8:
        raise ValidationError('Telefone inválido. Informe pelo menos 8 dígitos.', code='telefone')
    return telefone


def validar_data_nascimento(data):
    if data and data > timezone.localdate():
        raise ValidationError('A data de nascimento não pode estar no futuro.', code='nascimento_futuro')
    return data


def _no_fuso(data, hora):
    """Combina date + time num datetime com o fuso da clínica (America/Sao_Paulo)."""
    return timezone.make_aware(datetime.datetime.combine(data, hora))


def _intervalo(consulta):
    inicio = timezone.localtime(consulta.data_hora)
    return inicio, inicio + datetime.timedelta(minutes=consulta.duracao_minutos)


def disponibilidade_do_dia(data):
    """Disponibilidade ATIVA do dia da semana de `data`, ou None se a clínica não atende."""
    return Disponibilidade.objects.filter(dia_da_semana=data.weekday(), ativo=True).first()


def consultas_que_ocupam(data, ignorar_id=None):
    """Consultas do dia que ocupam a agenda (as canceladas liberam o horário)."""
    consultas = (Consulta.objects.filter(data_hora__date=data)
                 .exclude(status='cancelado').select_related('animal'))
    if ignorar_id:
        consultas = consultas.exclude(pk=ignorar_id)
    return consultas


def horarios_livres(data, duracao=DURACAO_PADRAO_MINUTOS, ignorar_id=None):
    """
    Fluxograma, etapa 3 — "Consultar horários livres" (Consulta × Disponibilidade).
    Inícios possíveis (datetimes no fuso da clínica), a cada INTERVALO_GRADE_MINUTOS,
    que cabem no expediente, estão no futuro e não se sobrepõem a outra consulta.
    """
    disponibilidade = disponibilidade_do_dia(data)
    if disponibilidade is None:
        return []
    abertura = _no_fuso(data, disponibilidade.hora_inicio)
    fechamento = _no_fuso(data, disponibilidade.hora_fim)
    ocupados = [_intervalo(c) for c in consultas_que_ocupam(data, ignorar_id)]
    agora = timezone.now()
    duracao_td = datetime.timedelta(minutes=duracao)
    passo = datetime.timedelta(minutes=INTERVALO_GRADE_MINUTOS)

    livres = []
    inicio = abertura
    while inicio + duracao_td <= fechamento:
        fim = inicio + duracao_td
        conflita = any(inicio < ocupado_fim and ocupado_inicio < fim
                       for ocupado_inicio, ocupado_fim in ocupados)
        if inicio > agora and not conflita:
            livres.append(inicio)
        inicio += passo
    return livres


def validar_agendamento(data_hora, duracao=DURACAO_PADRAO_MINUTOS, ignorar_id=None):
    """
    Fluxograma, decisão 5 — "Horário disponível?".
    Lança ValidationError com mensagem para o usuário; se estiver tudo certo,
    devolve a Disponibilidade que "verifica" a consulta (relacionamento do DER).
    """
    if data_hora <= timezone.now():
        raise ValidationError('A data e hora do agendamento devem ser no futuro.', code='passado')

    inicio = timezone.localtime(data_hora)
    fim = inicio + datetime.timedelta(minutes=duracao)
    disponibilidade = disponibilidade_do_dia(inicio.date())
    if disponibilidade is None:
        raise ValidationError(
            f'A clínica não atende neste dia ({NOMES_DIAS[inicio.weekday()]}).', code='dia_fechado')

    abertura = _no_fuso(inicio.date(), disponibilidade.hora_inicio)
    fechamento = _no_fuso(inicio.date(), disponibilidade.hora_fim)
    if inicio < abertura or fim > fechamento:
        raise ValidationError(
            f'Horário fora do expediente: {disponibilidade.hora_inicio:%H:%M} às '
            f'{disponibilidade.hora_fim:%H:%M}.', code='fora_do_expediente')

    for consulta in consultas_que_ocupam(inicio.date(), ignorar_id):
        outro_inicio, outro_fim = _intervalo(consulta)
        if inicio < outro_fim and outro_inicio < fim:
            raise ValidationError(
                f'Conflito de horário com a consulta de {consulta.animal.nome} '
                f'às {outro_inicio:%H:%M}.', code='conflito')
    return disponibilidade


def atualizar_status(consulta, novo_status, observacao=''):
    """Fluxograma — "Confirmar agendamento" e "Atualizar status (realizado/cancelado)"."""
    if novo_status not in TRANSICOES_STATUS.get(consulta.status, set()):
        rotulos = dict(Consulta.STATUS_CHOICES)
        raise ValidationError(
            f'Não é possível mudar de "{rotulos[consulta.status]}" para '
            f'"{rotulos.get(novo_status, novo_status)}".', code='transicao_invalida')
    consulta.status = novo_status
    observacao = (observacao or '').strip()
    if observacao:
        carimbo = timezone.localtime().strftime('%d/%m/%Y %H:%M')
        linha = f'[{carimbo}] {observacao}'
        consulta.observacoes = f'{consulta.observacoes}\n{linha}' if consulta.observacoes else linha
    consulta.save(update_fields=['status', 'observacoes'])
    return consulta
