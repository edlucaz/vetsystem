"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/management/commands/criar_horarios_padrao.py
Função  : Cadastra o expediente padrão (segunda a sexta, 08:00–19:00) quando
          ainda não há nenhuma Disponibilidade. Idempotente — roda no start.sh.
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-13
"""
import datetime

from django.core.management.base import BaseCommand

from agendamentos.models import Disponibilidade


class Command(BaseCommand):
    help = 'Cadastra o horário padrão da clínica (seg–sex, 08:00–19:00) se nenhum existir.'

    def handle(self, *args, **options):
        if Disponibilidade.objects.exists():
            self.stdout.write(self.style.SUCCESS('Horários já cadastrados — nenhuma ação necessária.'))
            return
        for dia, _nome in Disponibilidade.DIAS_CHOICES:
            Disponibilidade.objects.create(dia_da_semana=dia, hora_inicio=datetime.time(8),
                                           hora_fim=datetime.time(19))
        self.stdout.write(self.style.SUCCESS('Horário padrão cadastrado: segunda a sexta, 08:00–19:00.'))
