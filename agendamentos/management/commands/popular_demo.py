"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
Arquivo : agendamentos/management/commands/popular_demo.py
Função  : Dados de demonstração (apresentação e gráficos da análise de dados):
          8 tutores, 12 animais com histórico de peso, consultas dos últimos 180
          dias e dos próximos 14 dias úteis. Sorteio fixo (random.Random(2026)).
          --apagar remove só os tutores @demo.vetsystem.local (cascade).
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-10-23
"""
import datetime
import random
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from agendamentos import services
from agendamentos.models import Animal, Consulta, Proprietario, RegistroPeso

DOMINIO_DEMO = '@demo.vetsystem.local'

TUTORES = ['Ana Souza', 'Bruno Lima', 'Carla Mendes', 'Diego Rocha',
           'Elisa Prado', 'Fábio Costa', 'Gabriela Nunes', 'Heitor Alves']
ANIMAIS = [('Thor', 'cao', 'Labrador', 30), ('Mel', 'cao', 'Poodle', 7), ('Nina', 'gato', 'Siamês', 4),
           ('Bob', 'cao', 'Beagle', 12), ('Luna', 'gato', 'SRD', 5), ('Max', 'cao', 'Pastor Alemão', 35),
           ('Pipoca', 'outro', 'Coelho', 2), ('Fred', 'cao', 'Dachshund', 9), ('Lola', 'gato', 'Persa', 4),
           ('Zeus', 'cao', 'Golden Retriever', 32), ('Amora', 'cao', 'Shih-tzu', 6), ('Tom', 'gato', 'SRD', 5)]


def _sortear(aleatorio, pesos):
    return aleatorio.choices(list(pesos), weights=list(pesos.values()))[0]


class Command(BaseCommand):
    help = 'Cria dados de demonstração (tutores @demo.vetsystem.local); --apagar remove.'

    def add_arguments(self, parser):
        parser.add_argument('--forcar', action='store_true', help='Permite rodar com DEBUG=False (produção).')
        parser.add_argument('--apagar', action='store_true', help='Remove só os dados de demonstração.')

    def handle(self, *args, **options):
        if options['apagar']:
            self.stdout.write(self.style.SUCCESS(f'Dados de demonstração removidos: {self._apagar()} tutores.'))
            return
        if not settings.DEBUG and not options['forcar']:
            raise CommandError('DEBUG=False: use --forcar para criar dados de demonstração neste ambiente.')

        call_command('criar_horarios_padrao', stdout=self.stdout)
        with transaction.atomic():
            self._apagar()  # rodar de novo não duplica
            resumo = self._criar()
        self.stdout.write(self.style.SUCCESS(
            'Dados de demonstração criados: {tutores} tutores, {animais} animais, {pesos} pesagens, '
            '{passadas} consultas passadas e {futuras} futuras.'.format(**resumo)))

    def _apagar(self):
        tutores = Proprietario.objects.filter(email__endswith=DOMINIO_DEMO)
        total = tutores.count()
        tutores.delete()
        return total

    def _criar(self):
        aleatorio = random.Random(2026)
        hoje = timezone.localdate()

        tutores = [Proprietario.objects.create(
            nome=nome, telefone=f'(19) 9{aleatorio.randint(8000, 9999)}-{aleatorio.randint(1000, 9999)}',
            email=nome.split()[0].lower().replace('á', 'a') + DOMINIO_DEMO) for nome in TUTORES]

        animais, pesos = [], 0
        for i, (nome, especie, raca, peso_base) in enumerate(ANIMAIS):
            peso = Decimal(str(round(peso_base * aleatorio.uniform(0.9, 1.1), 2)))
            animal = Animal.objects.create(
                nome=nome, especie=especie, raca=raca, peso=peso, proprietario=tutores[i % len(tutores)],
                data_nascimento=hoje - datetime.timedelta(days=aleatorio.randint(365, 365 * 12)))
            animais.append(animal)
            pesos += 1  # a pesagem de hoje nasce pelo Animal.save()
            # Fase 6B: de 3 a 5 pesagens mensais nos últimos 180 dias (±5% do peso atual)
            for mes in range(1, aleatorio.randint(3, 5) + 1):
                variacao = Decimal(str(round(aleatorio.uniform(-0.05, 0.05), 4)))
                RegistroPeso.objects.update_or_create(
                    animal=animal, data=hoje - datetime.timedelta(days=30 * mes),
                    defaults={'peso': (peso * (1 + variacao)).quantize(Decimal('0.01'))})
                pesos += 1

        tipos = {'fisioterapia': 50, 'consulta': 30, 'acupuntura': 20}
        passadas = 0
        for d in range(180, 0, -1):
            data = hoje - datetime.timedelta(days=d)
            if data.weekday() >= 5:
                continue
            for hora in aleatorio.sample(range(8, 19), aleatorio.randint(0, 3)):
                Consulta.objects.create(
                    animal=aleatorio.choice(animais), data_hora=self._em(data, hora),
                    tipo=_sortear(aleatorio, tipos),
                    status=_sortear(aleatorio, {'realizado': 85, 'cancelado': 15}), observacoes='[demo]')
                passadas += 1

        futuras, data, dias_uteis = 0, hoje, 0
        while dias_uteis < 14:
            data += datetime.timedelta(days=1)
            if data.weekday() >= 5:
                continue
            dias_uteis += 1
            for hora in aleatorio.sample(range(8, 19), aleatorio.randint(0, 2)):
                data_hora = self._em(data, hora)
                try:
                    services.validar_agendamento(data_hora)  # não atropela a agenda real
                except ValidationError:
                    continue
                Consulta.objects.create(
                    animal=aleatorio.choice(animais), data_hora=data_hora, tipo=_sortear(aleatorio, tipos),
                    status=aleatorio.choice(['agendado', 'confirmado']), observacoes='[demo]')
                futuras += 1

        return {'tutores': len(tutores), 'animais': len(animais), 'pesos': pesos,
                'passadas': passadas, 'futuras': futuras}

    @staticmethod
    def _em(data, hora):
        return timezone.make_aware(datetime.datetime.combine(data, datetime.time(hora)))
