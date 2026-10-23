"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/management/commands/medir_desempenho.py
Função  : Mede o tempo de resposta (média, mediana, p95) e o tamanho das telas e
          endpoints principais com o cliente de teste do Django, logado como o
          1º superusuário. Imprime uma tabela Markdown. Rode com os dados demo.
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
import datetime
import statistics
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.utils import timezone


class Command(BaseCommand):
    help = 'Mede tempo de resposta e tamanho das telas e endpoints principais (tabela Markdown).'

    def add_arguments(self, parser):
        parser.add_argument('--repeticoes', type=int, default=30)

    def handle(self, *args, **options):
        repeticoes = max(1, options['repeticoes'])
        usuario = get_user_model().objects.filter(is_superuser=True).order_by('pk').first()
        if usuario is None:
            raise CommandError('Crie um superusuário antes de medir.')
        cliente = Client(HTTP_HOST='localhost')
        cliente.force_login(usuario)

        hoje = timezone.localdate()
        segunda = hoje + datetime.timedelta(days=(7 - hoje.weekday()) % 7 or 7)
        domingo = segunda + datetime.timedelta(days=6)
        alvos = [
            '/consultas/nova/',
            '/consultas/',
            f'/api/horarios-livres/?data={segunda.isoformat()}',
            '/api/animais/?search=a&limit=8',
            f'/api/consultas/?inicio={segunda.isoformat()}&fim={domingo.isoformat()}',
            '/api/estatisticas/?meses=6',
        ]

        linhas = ['| Alvo | Média (ms) | Mediana (ms) | p95 (ms) | Tamanho (KB) |', '|---|---|---|---|---|']
        for alvo in alvos:
            tempos, tamanho = [], 0
            for _ in range(repeticoes):
                inicio = time.perf_counter()
                resposta = cliente.get(alvo)
                tempos.append((time.perf_counter() - inicio) * 1000)
                if resposta.status_code != 200:
                    raise CommandError(f'{alvo} respondeu {resposta.status_code}.')
                tamanho = len(resposta.content)
            tempos.sort()
            p95 = tempos[min(len(tempos) - 1, int(round(0.95 * len(tempos))) - 1)]
            linhas.append(f'| `{alvo}` | {statistics.mean(tempos):.1f} | '
                          f'{statistics.median(tempos):.1f} | {p95:.1f} | {tamanho / 1024:.1f} |')
        self.stdout.write('\n'.join(linhas))
