"""
VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026
Arquivo : agendamentos/management/commands/criar_superusuario.py
Função  : Comando Django customizado que cria o superusuário em produção
          a partir de variáveis de ambiente, sem interação manual.
          Usado no start.sh para deploy no Render (plano free sem Shell).
Autor   : Lucas Eduardo Rocha (RA 24217901) | 2026-03-30
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Cria superusuário a partir de variáveis de ambiente (produção)'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@ativamente.vet.br')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_PASSWORD não definida — superusuário não criado.'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(
                f'Superusuário "{username}" já existe — nenhuma ação necessária.'
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superusuário "{username}" criado com sucesso.'
        ))
