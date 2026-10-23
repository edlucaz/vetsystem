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

from collections import Counter
import datetime

from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Consulta, Disponibilidade, RegistroPeso

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


def registrar_peso(animal, data=None):
    """
    Guarda o peso atual do animal no histórico. Um registro por dia: se o peso for
    corrigido no mesmo dia, o registro do dia é atualizado (não duplica).
    Chamado por Animal.save() quando o peso muda.
    """
    if animal.peso is None:
        return None
    registro, _criado = RegistroPeso.objects.update_or_create(
        animal=animal, data=data or timezone.localdate(), defaults={'peso': animal.peso})
    return registro


def historico_peso(animal):
    """Pesagens do animal, da mais recente à mais antiga, com a variação (kg) em relação à anterior."""
    registros = list(animal.pesos.order_by('data'))
    anterior = None
    for registro in registros:
        registro.variacao = None if anterior is None else registro.peso - anterior
        anterior = registro.peso
    return list(reversed(registros))



def _primeiro_dia_do_periodo(hoje, meses):
    ano, mes = hoje.year, hoje.month - (meses - 1)
    while mes <= 0:
        mes += 12
        ano -= 1
    return datetime.date(ano, mes, 1)


def estatisticas(meses=6):
    """Indicadores do painel de análise de dados (últimos `meses` meses, até hoje)."""
    hoje = timezone.localdate()
    inicio = _primeiro_dia_do_periodo(hoje, meses)
    consultas = Consulta.objects.filter(data_hora__date__range=(inicio, hoje)).order_by()
    total = consultas.count()
    canceladas = consultas.filter(status='cancelado').count()

    por_tipo_bruto = dict(consultas.values_list('tipo').annotate(total=Count('id')))
    por_status_bruto = dict(consultas.values_list('status').annotate(total=Count('id')))
    por_mes_bruto = {m.strftime('%Y-%m'): n for m, n in
                     consultas.annotate(mes=TruncMonth('data_hora')).values_list('mes').annotate(total=Count('id'))}

    por_mes, ano, mes = [], inicio.year, inicio.month
    for _ in range(meses):
        chave = f'{ano:04d}-{mes:02d}'
        por_mes.append({'mes': chave, 'total': por_mes_bruto.get(chave, 0)})
        mes, ano = (1, ano + 1) if mes == 12 else (mes + 1, ano)

    # Ocupação = minutos agendados ÷ minutos de expediente — usa o relacionamento "verifica"
    ocorrencias = Counter((inicio + datetime.timedelta(days=i)).weekday() for i in range((hoje - inicio).days + 1))
    agendados = dict(consultas.exclude(status='cancelado')
                     .values_list('disponibilidade__dia_da_semana').annotate(total=Sum('duracao_minutos')))
    ocupacao = []
    for disp in Disponibilidade.objects.filter(ativo=True).order_by('dia_da_semana'):
        minutos_dia = (disp.hora_fim.hour * 60 + disp.hora_fim.minute) - (disp.hora_inicio.hour * 60 + disp.hora_inicio.minute)
        capacidade = minutos_dia * ocorrencias.get(disp.dia_da_semana, 0)
        usados = agendados.get(disp.dia_da_semana) or 0
        ocupacao.append({'dia': disp.dia_da_semana, 'rotulo': disp.get_dia_da_semana_display(),
                         'minutos_agendados': usados, 'minutos_disponiveis': capacidade,
                         'percentual': round(100 * usados / capacidade, 1) if capacidade else 0.0})
    usados_total = sum(o['minutos_agendados'] for o in ocupacao)
    capacidade_total = sum(o['minutos_disponiveis'] for o in ocupacao)
    return {
        'periodo': {'inicio': inicio.isoformat(), 'fim': hoje.isoformat(), 'meses': meses},
        'total_consultas': total,
        'taxa_cancelamento': round(100 * canceladas / total, 1) if total else 0.0,
        'ocupacao_media': round(100 * usados_total / capacidade_total, 1) if capacidade_total else 0.0,
        'por_tipo': [{'chave': c, 'rotulo': r, 'total': por_tipo_bruto.get(c, 0)} for c, r in Consulta.TIPO_CHOICES],
        'por_status': [{'chave': c, 'rotulo': r, 'total': por_status_bruto.get(c, 0)} for c, r in Consulta.STATUS_CHOICES],
        'por_mes': por_mes,
        'ocupacao_por_dia': ocupacao,
    }
