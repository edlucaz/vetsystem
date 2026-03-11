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

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import Proprietario, Animal


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
                    css_class='bg-[#F26A2E] hover:bg-orange-600 text-white font-bold py-2 px-6 rounded'
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
        telefone = self.cleaned_data.get('telefone', '').strip()

        # Conta apenas os dígitos (ignora parênteses, traços e espaços)
        digitos = ''.join(filter(str.isdigit, telefone))

        if len(digitos) < 8:
            raise forms.ValidationError(
                'Telefone inválido. Informe pelo menos 8 dígitos.'
            )

        return telefone


class AnimalForm(forms.ModelForm):
    """
    Formulário de cadastro e edição de Animal (paciente da ATIVO PET).

    Usado nas views AnimalCreateView e AnimalUpdateView.
    O campo 'proprietario' exibe um select com todos os tutores cadastrados,
    permitindo vincular o animal ao seu dono.
    """

    class Meta:
        model = Animal
        fields = ['nome', 'especie', 'raca', 'idade', 'peso', 'queixa', 'proprietario']

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do animal'}),
            'raca': forms.TextInput(attrs={'placeholder': 'Ex: Golden Retriever (deixe vazio para SRD)'}),
            'idade': forms.NumberInput(attrs={'placeholder': 'Idade em anos', 'min': 0}),
            'peso': forms.NumberInput(attrs={'placeholder': 'Ex: 12.50', 'step': '0.01', 'min': 0}),
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

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            # Linha com nome e espécie lado a lado
            Div(
                Div(Field('nome'), css_class='w-full md:w-1/2 pr-2'),
                Div(Field('especie'), css_class='w-full md:w-1/2 pl-2'),
                css_class='flex flex-wrap'
            ),
            # Linha com raça, idade e peso
            Div(
                Div(Field('raca'), css_class='w-full md:w-1/2 pr-2'),
                Div(Field('idade'), css_class='w-full md:w-1/4 px-2'),
                Div(Field('peso'), css_class='w-full md:w-1/4 pl-2'),
                css_class='flex flex-wrap'
            ),
            Field('queixa'),
            Field('proprietario'),
            Div(
                Submit(
                    'submit', 'Salvar',
                    css_class='bg-[#F26A2E] hover:bg-orange-600 text-white font-bold py-2 px-6 rounded'
                ),
                css_class='mt-4'
            )
        )
