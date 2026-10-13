"""Auxiliares de data dos testes — sempre datetimes com o fuso da clínica."""
import datetime

from django.utils import timezone


def proxima_data(dia_semana, semanas=1):
    """Próxima data estritamente futura do dia da semana pedido (0 = segunda)."""
    hoje = timezone.localdate()
    dias = (dia_semana - hoje.weekday()) % 7 or 7
    return hoje + datetime.timedelta(days=dias + 7 * (semanas - 1))


def em(data, hora, minuto=0):
    """Datetime 'aware' (America/Sao_Paulo) para a data e hora informadas."""
    return timezone.make_aware(datetime.datetime.combine(data, datetime.time(hora, minuto)))
