"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/models.py
Função  : Define as tabelas do banco de dados do sistema de agendamento.
          Cada classe Python aqui representa uma tabela no banco (SQLite em dev,
          PostgreSQL em produção). O Django ORM cuida de criar e atualizar
          essas tabelas automaticamente via migrações.

          Entidades modeladas:
            - Proprietario  : tutor/dono do animal
            - Animal        : paciente da ATIVO PET
            - Consulta      : agendamento de atendimento
            - Disponibilidade: horários de funcionamento da clínica

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from django.db import models
from django.utils import timezone


# =============================================================================
# MODEL: Proprietario
# =============================================================================

class Proprietario(models.Model):
    """
    Representa o tutor/dono do animal atendido na ATIVO PET.

    Cada Proprietário pode ter vários Animais associados (relação 1:N).
    Os dados de contato são usados pela Sra. Fernanda para confirmar consultas
    e comunicar alterações de agenda.

    Campos:
        nome     -- Nome completo do tutor (obrigatório).
        telefone -- Número de contato principal (obrigatório).
        email    -- E-mail para notificações (opcional).
        cpf      -- CPF para identificação única (opcional no PI).
    """

    nome = models.CharField(
        max_length=200,
        verbose_name='Nome completo',
        help_text='Nome completo do tutor responsável pelo animal.',
    )

    telefone = models.CharField(
        max_length=20,
        verbose_name='Telefone',
        help_text='Número de contato principal. Ex: (19) 99999-9999',
    )

    email = models.EmailField(
        blank=True,  # Campo opcional — nem todos os tutores têm e-mail
        verbose_name='E-mail',
        help_text='E-mail para envio de confirmações (opcional).',
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,  # Campo opcional no escopo do PI
        verbose_name='CPF',
        help_text='CPF no formato 000.000.000-00 (opcional).',
    )

    class Meta:
        verbose_name = 'Proprietário'
        verbose_name_plural = 'Proprietários'
        # Ordena a listagem por nome alfabeticamente por padrão
        ordering = ['nome']

    def __str__(self):
        """Representação textual usada no Django Admin e nos selects dos formulários."""
        return self.nome


# =============================================================================
# MODEL: Animal
# =============================================================================

class Animal(models.Model):
    """
    Representa o animal paciente atendido na ATIVO PET.

    Cada Animal pertence a um Proprietário e pode ter várias Consultas
    ao longo do tempo (relação 1:N com Consulta).

    A ATIVO PET atende principalmente cães e gatos, com opção 'outro'
    para demais espécies (coelhos, aves, etc.).

    Campos:
        nome        -- Nome do animal (obrigatório).
        especie     -- Espécie: cão, gato ou outro (obrigatório).
        raca        -- Raça do animal (opcional).
        idade       -- Idade em anos (opcional).
        peso        -- Peso em kg com duas casas decimais (opcional).
        queixa      -- Motivo principal do atendimento — sintomas relatados (opcional).
        proprietario-- Tutor responsável pelo animal (obrigatório, FK).
    """

    # Opções de espécie disponíveis no formulário de cadastro.
    # Formato: (valor_no_banco, texto_exibido_na_tela)
    ESPECIE_CHOICES = [
        ('cao',   'Cão'),   # Caninos em geral
        ('gato',  'Gato'),  # Felinos em geral
        ('outro', 'Outro'), # Demais espécies atendidas pela clínica
    ]

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome do animal',
    )

    especie = models.CharField(
        max_length=20,
        choices=ESPECIE_CHOICES,
        verbose_name='Espécie',
    )

    raca = models.CharField(
        max_length=100,
        blank=True,  # Opcional — SRD (Sem Raça Definida) é comum
        verbose_name='Raça',
        help_text='Deixe em branco para SRD (Sem Raça Definida).',
    )

    idade = models.PositiveIntegerField(
        null=True,   # Permite valor nulo no banco
        blank=True,  # Permite campo vazio no formulário
        verbose_name='Idade (anos)',
    )

    peso = models.DecimalField(
        max_digits=5,      # Ex: 999.99 — suporta animais de até ~100kg
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Peso (kg)',
        help_text='Peso em quilogramas. Ex: 12.50',
    )

    queixa = models.TextField(
        blank=True,
        verbose_name='Queixa principal',
        help_text='Descreva os sintomas ou motivo do atendimento.',
    )

    # Chave estrangeira — vincula o animal ao seu tutor.
    # CASCADE: se o proprietário for deletado, seus animais também são deletados.
    # related_name='animais' permite acessar os animais de um proprietário
    # via: proprietario.animais.all()
    proprietario = models.ForeignKey(
        Proprietario,
        on_delete=models.CASCADE,
        related_name='animais',
        verbose_name='Proprietário',
    )

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['nome']

    def __str__(self):
        """Ex: 'Rex (Cão) — João Silva'"""
        return f'{self.nome} ({self.get_especie_display()}) — {self.proprietario.nome}'


# =============================================================================
# MODEL: Consulta
# =============================================================================

class Consulta(models.Model):
    """
    Representa um agendamento de atendimento na ATIVO PET.

    É o model central do sistema — substitui o controle manual via WhatsApp
    que a Sra. Fernanda realizava antes do VETSystem.

    Ciclo de vida de uma consulta:
        agendado → confirmado → realizado
                 → cancelado (em qualquer etapa)

    A ATIVO PET oferece três tipos de atendimento:
        - Consulta      : avaliação clínica geral
        - Fisioterapia  : sessão de reabilitação física
        - Acupuntura    : sessão de acupuntura veterinária

    Campos:
        animal          -- Animal a ser atendido (FK obrigatória).
        data_hora       -- Data e horário do atendimento (obrigatório).
        tipo            -- Tipo de atendimento (obrigatório).
        status          -- Estado atual do agendamento (padrão: 'agendado').
        observacoes     -- Anotações adicionais da Sra. Fernanda (opcional).
        duracao_minutos -- Duração estimada da sessão em minutos (padrão: 60).
    """

    # --- Choices de status ---
    # Define o ciclo de vida do agendamento. Exibido como select no formulário.
    STATUS_CHOICES = [
        ('agendado',   'Agendado'),    # Solicitado, ainda não confirmado
        ('confirmado', 'Confirmado'),  # Confirmado com o tutor
        ('realizado',  'Realizado'),   # Atendimento concluído
        ('cancelado',  'Cancelado'),   # Cancelado pelo tutor ou pela clínica
    ]

    # --- Choices de tipo de atendimento ---
    # Reflete os serviços oferecidos pela ATIVO PET em Limeira/SP.
    TIPO_CHOICES = [
        ('consulta',     'Consulta'),      # Avaliação clínica geral
        ('fisioterapia', 'Fisioterapia'),  # Reabilitação física animal
        ('acupuntura',   'Acupuntura'),    # Acupuntura veterinária
    ]

    # Chave estrangeira para o animal atendido.
    # related_name='consultas' permite acessar via: animal.consultas.all()
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='consultas',
        verbose_name='Animal',
    )

    data_hora = models.DateTimeField(
        verbose_name='Data e horário',
        help_text='Data e horário do atendimento. Ex: 25/03/2026 14:00',
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de atendimento',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='agendado',  # Todo novo agendamento começa como 'agendado'
        verbose_name='Status',
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre o atendimento (opcional).',
    )

    duracao_minutos = models.PositiveIntegerField(
        default=60,  # Sessões padrão na ATIVO PET têm 60 minutos
        verbose_name='Duração (minutos)',
        help_text='Duração estimada do atendimento em minutos.',
    )

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        # Ordena pelo horário mais próximo primeiro (agenda cronológica)
        ordering = ['data_hora']

    def __str__(self):
        """Ex: '25/03/2026 14:00 — Rex — Fisioterapia [Agendado]'"""
        return (
            f'{self.data_hora.strftime("%d/%m/%Y %H:%M")} — '
            f'{self.animal.nome} — '
            f'{self.get_tipo_display()} '
            f'[{self.get_status_display()}]'
        )

    def is_futuro(self):
        """
        Verifica se o agendamento é para um horário futuro.

        Útil para filtrar a agenda e impedir edição de consultas passadas.

        Retorna:
            bool: True se a consulta ainda não aconteceu, False caso contrário.
        """
        return self.data_hora > timezone.now()


# =============================================================================
# MODEL: Disponibilidade
# =============================================================================

class Disponibilidade(models.Model):
    """
    Define os horários de funcionamento da ATIVO PET por dia da semana.

    Usada pelo sistema para validar se um horário solicitado no formulário
    de agendamento está dentro do período de atendimento da clínica.

    A ATIVO PET funciona de segunda a sexta, das 8h às 19h.
    A Sra. Fernanda pode ajustar esses horários pelo Django Admin conforme necessário.

    Campos:
        dia_da_semana -- Dia da semana (0=Segunda ... 4=Sexta).
        hora_inicio   -- Início do atendimento naquele dia.
        hora_fim      -- Fim do atendimento naquele dia.
        ativo         -- Se False, a clínica não atende naquele dia (ex: feriados).
    """

    # Dias úteis da semana — a ATIVO PET não atende aos fins de semana.
    # Formato: (valor_no_banco, texto_exibido)
    DIAS_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
    ]

    dia_da_semana = models.IntegerField(
        choices=DIAS_CHOICES,
        verbose_name='Dia da semana',
    )

    hora_inicio = models.TimeField(
        verbose_name='Início do atendimento',
        help_text='Horário de abertura da clínica. Ex: 08:00',
    )

    hora_fim = models.TimeField(
        verbose_name='Fim do atendimento',
        help_text='Horário de encerramento da clínica. Ex: 19:00',
    )

    # Permite desativar um dia sem precisar deletar o registro.
    # Útil para feriados ou recesso da clínica.
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Desmarque para indicar que a clínica não atende neste dia.',
    )

    class Meta:
        verbose_name = 'Disponibilidade'
        verbose_name_plural = 'Disponibilidades'
        ordering = ['dia_da_semana', 'hora_inicio']

        # Garante que não existam dois registros para o mesmo dia da semana.
        constraints = [
            models.UniqueConstraint(
                fields=['dia_da_semana'],
                name='unique_dia_da_semana',
            )
        ]

    def __str__(self):
        """Ex: 'Segunda-feira: 08:00 às 19:00 (Ativo)'"""
        status = 'Ativo' if self.ativo else 'Inativo'
        return (
            f'{self.get_dia_da_semana_display()}: '
            f'{self.hora_inicio.strftime("%H:%M")} às '
            f'{self.hora_fim.strftime("%H:%M")} '
            f'({status})'
        )
