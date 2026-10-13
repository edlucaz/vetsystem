"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/forms.py
Função  : Define os formulários de cadastro e edição de Proprietário e Animal.
          Usa o django-crispy-forms para renderizar os campos automaticamente
          com estilo Tailwind CSS, sem precisar escrever HTML manualmente.

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

import datetime
from decimal import Decimal, InvalidOperation

from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import Proprietario, Animal, Consulta, Disponibilidade
from .services import DURACAO_PADRAO_MINUTOS, validar_agendamento, validar_data_nascimento, validar_telefone


class ProprietarioForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de Proprietário (tutor do animal).

    Usado nas views ProprietarioCreateView e ProprietarioUpdateView.
    O crispy_forms cuida da renderização com Tailwind CSS automaticamente.
    """

    class Meta:
        # Model que este formulário representa
        model = Proprietario

        # Campos exibidos no formulário — cpf é opcional mas incluído para identificação
        fields = ['nome', 'telefone', 'email', 'cpf']

        # Textos de ajuda exibidos abaixo de cada campo
        help_texts = {
            'telefone': 'Ex: (19) 99999-9999',
            'cpf': 'Formato: 000.000.000-00 (opcional)',
            'email': 'Opcional — usado para confirmações de agendamento.',
        }

        # Placeholder exibido dentro de cada campo vazio
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do tutor'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(19) 99999-9999'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@exemplo.com'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e configura o crispy_forms helper.

        O FormHelper define como o formulário é renderizado no template —
        posição dos campos, botão de submit e classes CSS do Tailwind.
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'  # Envia os dados via POST (padrão seguro)

        # Layout define a ordem e agrupamento visual dos campos
        self.helper.layout = Layout(
            Field('nome', css_class='w-full'),
            Field('telefone', css_class='w-full'),
            Field('email', css_class='w-full'),
            Field('cpf', css_class='w-full'),
            # Botão de submit com cores da identidade visual da ATIVO PET
            Div(
                Submit(
                    'submit', 'Salvar',
                    css_class='bg-[#B9471A] hover:bg-orange-800 text-white font-bold py-2 px-6 rounded'
                ),
                css_class='mt-4'
            )
        )

    def clean_telefone(self):
        """
        Validação customizada do campo telefone.

        Remove espaços extras e garante que o número tenha pelo menos 8 dígitos,
        evitando cadastros com telefones inválidos ou incompletos.

        Retorna:
            str: Telefone limpo e validado.

        Lança:
            ValidationError: Se o telefone tiver menos de 8 dígitos numéricos.
        """
        return validar_telefone(self.cleaned_data.get('telefone'))


class PesoField(forms.DecimalField):
    """DecimalField que aceita vírgula como separador decimal (padrão BR): '12,50'."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
        return super().to_python(value)


class AnimalForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de Animal (paciente da ATIVO PET).

    Usado nas views AnimalCreateView e AnimalUpdateView.
    O campo 'proprietario' exibe um select com todos os tutores cadastrados,
    permitindo vincular o animal ao seu dono.
    """

    class Meta:
        model = Animal
        fields = ['nome', 'especie', 'raca', 'data_nascimento', 'peso', 'queixa', 'proprietario']
        # Sem isso o DecimalField recusa '12,50' antes de clean_peso rodar
        field_classes = {'peso': PesoField}

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do animal'}),
            'raca': forms.TextInput(attrs={'placeholder': 'Ex: Golden Retriever (deixe vazio para SRD)'}),
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            # TextInput + inputmode="decimal" → compatível com IMask (type=number conflita com máscaras)
            'peso': forms.TextInput(attrs={
                'placeholder': 'Ex: 12,50',
                'inputmode': 'decimal',
            }),
            'queixa': forms.Textarea(attrs={
                'placeholder': 'Descreva os sintomas ou motivo do atendimento...',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário de Animal com crispy_forms helper.

        O select de proprietário é ordenado por nome para facilitar
        a busca visual pela Sra. Fernanda durante o atendimento.
        """
        super().__init__(*args, **kwargs)

        # Ordena o select de proprietários por nome alfabeticamente
        self.fields['proprietario'].queryset = Proprietario.objects.order_by('nome')
        self.fields['proprietario'].empty_label = '— Selecione o tutor —'
        self.fields['data_nascimento'].widget.attrs['max'] = timezone.localdate().isoformat()

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            # Linha com nome e espécie lado a lado
            Div(
                Div(Field('nome'), css_class='w-full md:w-1/2 pr-2'),
                Div(Field('especie'), css_class='w-full md:w-1/2 pl-2'),
                css_class='flex flex-wrap'
            ),
            # Linha com raça, data de nascimento e peso
            Div(
                Div(Field('raca'), css_class='w-full md:w-1/2 pr-2'),
                Div(Field('data_nascimento'), css_class='w-full md:w-1/4 px-2'),
                Div(Field('peso'), css_class='w-full md:w-1/4 pl-2'),
                css_class='flex flex-wrap'
            ),
            Field('queixa'),
            Field('proprietario'),
            Div(
                Submit(
                    'submit', 'Salvar',
                    css_class='bg-[#B9471A] hover:bg-orange-800 text-white font-bold py-2 px-6 rounded'
                ),
                css_class='mt-4'
            )
        )

    def clean_data_nascimento(self):
        return validar_data_nascimento(self.cleaned_data.get('data_nascimento'))

    def clean_peso(self):
        """
        Aceita vírgula como separador decimal (padrão BR) e converte para ponto.
        Exemplo: '12,50' → Decimal('12.50')

        O campo usa TextInput para compatibilidade com IMask.
        """
        valor = self.cleaned_data.get('peso')
        if valor in (None, ''):
            return None
        # Converte vírgula para ponto antes de passar ao Decimal
        valor_str = str(valor).replace(',', '.').strip()
        try:
            resultado = Decimal(valor_str)
            if resultado < 0:
                raise forms.ValidationError('O peso não pode ser negativo.')
            return resultado
        except InvalidOperation:
            raise forms.ValidationError('Informe um peso válido. Ex: 12,50')


class ConsultaForm(forms.ModelForm):
    """
    Formulário de agendamento/edição de Consulta.

    O campo data_hora do model é composto por dois campos separados:
      data_consulta  → DateField  (type="date")
      hora_consulta  → TimeField  (type="time")

    Essa separação melhora a UX e permite bloquear datas passadas
    diretamente no browser via atributo min= e validação JS em tempo real.

    O clean() combina os dois em data_hora (datetime aware, fuso SP) e aplica
    a decisão "Horário disponível?" do fluxograma (services.validar_agendamento:
    data futura, expediente do dia e sem conflito) na criação ou quando a
    data/hora muda — editar só as observações de uma consulta passada continua
    permitido. Na criação o campo status não aparece: a consulta nasce 'agendado'.
    """

    # --- Campos extras (não existem no Model) ---
    data_consulta = forms.DateField(
        label='Data',
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',   # type="date" exige YYYY-MM-DD; pt-br usaria dd/mm/YYYY sem isso
            attrs={
                'type': 'date',
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579]'
                ),
            },
        ),
    )
    hora_consulta = forms.TimeField(
        label='Horário',
        required=True,
        widget=forms.TimeInput(
            format='%H:%M',      # garante HH:MM mesmo com localização ativa
            attrs={
                'type': 'time',
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579]'
                ),
            },
        ),
    )

    class Meta:
        model = Consulta
        # data_hora é omitido aqui — será preenchido pelo clean()
        fields = ['animal', 'tipo', 'status', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579]'
                ),
                'placeholder': 'Observações adicionais (opcional)...',
            }),
            'animal': forms.Select(attrs={
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579] bg-white'
                ),
            }),
            'tipo': forms.Select(attrs={
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579] bg-white'
                ),
            }),
            'status': forms.Select(attrs={
                'class': (
                    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
                    'focus:outline-none focus:ring-2 focus:ring-[#1E7579] bg-white'
                ),
            }),
        }

    def __init__(self, *args, **kwargs):
        # animal_pk pode vir da URL (?animal=1) para pré-selecionar o animal
        animal_pk = kwargs.pop('animal_pk', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # Evita uma consulta extra por opção (Animal.__str__ usa o nome do tutor)
        self.fields['animal'].queryset = Animal.objects.select_related('proprietario').order_by('nome')

        if self.instance.pk is None:
            # Fluxograma: "Registrar consulta — status: agendado" — na criação o status não é escolhido
            del self.fields['status']
            self.fields['data_consulta'].widget.attrs['min'] = timezone.localdate().isoformat()
        if animal_pk:
            self.fields['animal'].initial = animal_pk
        if self.instance.pk and self.instance.data_hora:
            dt_local = timezone.localtime(self.instance.data_hora)
            self.fields['data_consulta'].initial = dt_local.date()
            # time (não str): TimeField.has_changed compara com time e acusaria mudança sempre
            self.fields['hora_consulta'].initial = dt_local.time().replace(second=0, microsecond=0)

    def clean(self):
        """
        Combina data + hora em data_hora e aplica a decisão "Horário disponível?"
        (mesma regra da API) na criação ou quando a data/hora foi alterada.
        """
        cleaned = super().clean()
        data = cleaned.get('data_consulta')
        hora = cleaned.get('hora_consulta')
        if data and hora:
            data_hora = timezone.make_aware(datetime.datetime.combine(data, hora))
            mudou_horario = (self.instance.pk is None
                             or bool({'data_consulta', 'hora_consulta'} & set(self.changed_data)))
            if mudou_horario:
                validar_agendamento(data_hora, self.instance.duracao_minutos or DURACAO_PADRAO_MINUTOS,
                                    ignorar_id=self.instance.pk)
            cleaned['data_hora'] = data_hora
        return cleaned

    def save(self, commit=True):
        """Grava data_hora composto a partir dos campos separados."""
        instance = super().save(commit=False)
        instance.data_hora = self.cleaned_data.get('data_hora')
        if commit:
            instance.save()
        return instance


# =============================================================================
# FORM: Disponibilidade
# =============================================================================

class DisponibilidadeForm(forms.ModelForm):
    """
    Formulário de cadastro/edição dos horários de funcionamento da ATIVO PET.

    A Sra. Fernanda configura quais dias e horários a clínica atende.
    O ConsultaForm usa esses dados para validar se o horário escolhido
    está dentro do expediente da clínica.

    Validação: hora_fim deve ser posterior a hora_inicio.
    """

    class Meta:
        model = Disponibilidade
        fields = ['dia_da_semana', 'hora_inicio', 'hora_fim', 'ativo']
        widgets = {
            # type="time" exibe o seletor de horário nativo do browser
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim':    forms.TimeInput(attrs={'type': 'time'}),
        }
        help_texts = {
            'ativo': 'Desmarque para indicar que a clínica não atende neste dia (ex: feriado).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        """Garante que hora_fim seja posterior a hora_inicio."""
        cleaned = super().clean()
        inicio = cleaned.get('hora_inicio')
        fim    = cleaned.get('hora_fim')
        if inicio and fim and fim <= inicio:
            raise forms.ValidationError(
                'O horário de encerramento deve ser posterior ao de início.'
            )
        return cleaned
