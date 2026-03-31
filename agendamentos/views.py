"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/views.py
Função  : Views (controladores) do sistema. Cada view processa uma requisição
          HTTP e retorna uma resposta — renderizando um template ou redirecionando.

          Padrão usado: CBVs (Class-Based Views) do Django.
          Todas as views internas exigem login via LoginRequiredMixin.

          Módulos:
            Home / Dashboard     : HomeView, DashboardView
            Proprietário         : List, Detail, Create, Update, Delete
            Animal               : List, Detail, Create, Update, Delete
            Consulta             : List, Detail, Create, Update, Delete
            Disponibilidade      : List, Create, Update, Delete

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-30
"""

from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)

from .models import Proprietario, Animal, Consulta, Disponibilidade
from .forms import ProprietarioForm, AnimalForm, ConsultaForm, DisponibilidadeForm


# =============================================================================
# VIEWS PÚBLICAS
# =============================================================================

class HomeView(TemplateView):
    """
    Frontpage pública da ATIVO PET — acessível sem login.

    Apresenta a clínica, seus serviços e o CTA para agendamento.

    Rota    : GET /
    Template: templates/home.html
    """
    template_name = 'home.html'


# =============================================================================
# DASHBOARD
# =============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Tela inicial pós-login da Sra. Fernanda.

    Exibe totais por status, consultas de hoje e próximos 7 dias.

    Rota    : GET /dashboard/
    Template: templates/dashboard.html
    Contexto:
        hoje               -- Data atual (date)
        total_agendado     -- Contagem de consultas com status 'agendado'
        total_confirmado   -- Contagem de consultas com status 'confirmado'
        total_realizado    -- Contagem de consultas com status 'realizado'
        total_cancelado    -- Contagem de consultas com status 'cancelado'
        consultas_hoje     -- QuerySet de consultas de hoje ordenadas por horário
        proximas_consultas -- QuerySet dos próximos 7 dias (max 10 registros)
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        import datetime

        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        sete_dias = hoje + datetime.timedelta(days=7)

        ctx['total_agendado']   = Consulta.objects.filter(status='agendado').count()
        ctx['total_confirmado'] = Consulta.objects.filter(status='confirmado').count()
        ctx['total_realizado']  = Consulta.objects.filter(status='realizado').count()
        ctx['total_cancelado']  = Consulta.objects.filter(status='cancelado').count()

        # Consultas de hoje — usadas na tabela principal do dashboard
        ctx['consultas_hoje'] = (
            Consulta.objects
            .filter(data_hora__date=hoje)
            .select_related('animal__proprietario')
            .order_by('data_hora')
        )

        # Próximas consultas ativas (agendado ou confirmado) nos próximos 7 dias
        ctx['proximas_consultas'] = (
            Consulta.objects
            .filter(
                data_hora__date__gt=hoje,
                data_hora__date__lte=sete_dias,
                status__in=['agendado', 'confirmado'],
            )
            .select_related('animal__proprietario')
            .order_by('data_hora')[:10]
        )

        ctx['hoje'] = hoje
        return ctx


# =============================================================================
# VIEWS DE PROPRIETÁRIO
# =============================================================================

class ProprietarioListView(LoginRequiredMixin, ListView):
    """
    Lista todos os proprietários com busca por nome ou telefone.

    Rota    : GET /proprietarios/
              GET /proprietarios/?q=João
    Template: agendamentos/proprietario_list.html
    Contexto: proprietarios (paginado, 10/página), query (termo de busca)
    """
    model = Proprietario
    template_name = 'agendamentos/proprietario_list.html'
    context_object_name = 'proprietarios'
    paginate_by = 10

    def get_queryset(self):
        qs = Proprietario.objects.order_by('nome')
        q = self.request.GET.get('q', '').strip()
        if q:
            # icontains = busca case-insensitive (maiúsculas/minúsculas ignoradas)
            qs = qs.filter(nome__icontains=q) | qs.filter(telefone__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ProprietarioDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe dados de um proprietário e todos os seus animais.

    Rota    : GET /proprietarios/<pk>/
    Template: agendamentos/proprietario_detail.html
    Contexto: proprietario, animais
    """
    model = Proprietario
    template_name = 'agendamentos/proprietario_detail.html'
    context_object_name = 'proprietario'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['animais'] = self.object.animais.order_by('nome')
        return ctx


class ProprietarioCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário de cadastro de novo proprietário.

    Rota    : GET/POST /proprietarios/novo/
    Template: agendamentos/proprietario_form.html
    Sucesso : redireciona para a listagem
    """
    model = Proprietario
    form_class = ProprietarioForm
    template_name = 'agendamentos/proprietario_form.html'
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        messages.success(self.request, 'Proprietário cadastrado com sucesso!')
        return super().form_valid(form)


class ProprietarioUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário de edição de proprietário existente.

    Rota    : GET/POST /proprietarios/<pk>/editar/
    Template: agendamentos/proprietario_form.html
    Sucesso : redireciona para a listagem
    """
    model = Proprietario
    form_class = ProprietarioForm
    template_name = 'agendamentos/proprietario_form.html'
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        messages.success(self.request, 'Proprietário atualizado com sucesso!')
        return super().form_valid(form)


class ProprietarioDeleteView(LoginRequiredMixin, DeleteView):
    """
    Confirmação e exclusão de proprietário.

    ATENÇÃO: exclui em cascata todos os animais e consultas vinculados.

    Rota    : GET/POST /proprietarios/<pk>/excluir/
    Template: agendamentos/proprietario_confirm_delete.html
    Sucesso : redireciona para a listagem
    """
    model = Proprietario
    template_name = 'agendamentos/proprietario_confirm_delete.html'
    context_object_name = 'proprietario'
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        messages.success(self.request, 'Proprietário excluído com sucesso.')
        return super().form_valid(form)


# =============================================================================
# VIEWS DE ANIMAL
# =============================================================================

class AnimalListView(LoginRequiredMixin, ListView):
    """
    Lista todos os animais com busca e filtro por espécie.

    Rota    : GET /animais/
              GET /animais/?q=Rex&especie=cao
    Template: agendamentos/animal_list.html
    Contexto: animais, query, especie_selecionada
    """
    model = Animal
    template_name = 'agendamentos/animal_list.html'
    context_object_name = 'animais'
    paginate_by = 10

    def get_queryset(self):
        # select_related evita query extra para buscar o proprietário de cada animal
        qs = Animal.objects.select_related('proprietario').order_by('nome')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(proprietario__nome__icontains=q)
        especie = self.request.GET.get('especie', '').strip()
        if especie:
            qs = qs.filter(especie=especie)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['especie_selecionada'] = self.request.GET.get('especie', '')
        return ctx


class AnimalDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe dados de um animal e seu histórico de consultas.

    Rota    : GET /animais/<pk>/
    Template: agendamentos/animal_detail.html
    Contexto: animal, consultas (do mais recente ao mais antigo)
    """
    model = Animal
    template_name = 'agendamentos/animal_detail.html'
    context_object_name = 'animal'

    def get_queryset(self):
        return Animal.objects.select_related('proprietario')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['consultas'] = self.object.consultas.order_by('-data_hora')
        return ctx


class AnimalCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário de cadastro de novo animal.

    Aceita ?proprietario=<pk> na URL para pré-selecionar o tutor.

    Rota    : GET/POST /animais/novo/
    Template: agendamentos/animal_form.html
    Sucesso : redireciona para a listagem
    """
    model = Animal
    form_class = AnimalForm
    template_name = 'agendamentos/animal_form.html'
    success_url = reverse_lazy('agendamentos:animal-list')

    def get_initial(self):
        initial = super().get_initial()
        pk = self.request.GET.get('proprietario')
        if pk:
            initial['proprietario'] = pk
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Animal cadastrado com sucesso!')
        return super().form_valid(form)


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário de edição de animal existente.

    Rota    : GET/POST /animais/<pk>/editar/
    Template: agendamentos/animal_form.html
    """
    model = Animal
    form_class = AnimalForm
    template_name = 'agendamentos/animal_form.html'
    success_url = reverse_lazy('agendamentos:animal-list')

    def form_valid(self, form):
        messages.success(self.request, 'Animal atualizado com sucesso!')
        return super().form_valid(form)


class AnimalDeleteView(LoginRequiredMixin, DeleteView):
    """
    Confirmação e exclusão de animal.

    ATENÇÃO: exclui em cascata todas as consultas do animal.

    Rota    : GET/POST /animais/<pk>/excluir/
    Template: agendamentos/animal_confirm_delete.html
    """
    model = Animal
    template_name = 'agendamentos/animal_confirm_delete.html'
    context_object_name = 'animal'
    success_url = reverse_lazy('agendamentos:animal-list')

    def form_valid(self, form):
        messages.success(self.request, 'Animal excluído com sucesso.')
        return super().form_valid(form)


# =============================================================================
# VIEWS DE CONSULTA
# =============================================================================

class ConsultaListView(LoginRequiredMixin, ListView):
    """
    Lista todas as consultas com filtros por status e data.

    Rota    : GET /consultas/
              GET /consultas/?status=agendado&data=2026-04-10
    Template: agendamentos/consulta_list.html
    Contexto: consultas, status_choices, status_atual, data_filtro
    """
    model = Consulta
    template_name = 'agendamentos/consulta_list.html'
    context_object_name = 'consultas'
    ordering = ['data_hora']

    def get_queryset(self):
        qs = super().get_queryset().select_related('animal__proprietario')
        status = self.request.GET.get('status')
        data = self.request.GET.get('data')
        if status:
            qs = qs.filter(status=status)
        if data:
            qs = qs.filter(data_hora__date=data)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Consulta.STATUS_CHOICES
        ctx['status_atual']   = self.request.GET.get('status', '')
        ctx['data_filtro']    = self.request.GET.get('data', '')
        return ctx


class ConsultaDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma consulta com animal e proprietário.

    Rota    : GET /consultas/<pk>/
    Template: agendamentos/consulta_detail.html
    """
    model = Consulta
    template_name = 'agendamentos/consulta_detail.html'
    context_object_name = 'consulta'

    def get_queryset(self):
        return super().get_queryset().select_related('animal__proprietario')


class ConsultaCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário de agendamento de nova consulta.

    Aceita ?animal=<pk> na URL para pré-selecionar o animal.

    Rota    : GET/POST /consultas/nova/
    Template: agendamentos/consulta_form.html
    """
    model = Consulta
    form_class = ConsultaForm
    template_name = 'agendamentos/consulta_form.html'
    success_url = reverse_lazy('agendamentos:consulta-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['animal_pk'] = self.request.GET.get('animal')
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Consulta agendada com sucesso!')
        return super().form_valid(form)


class ConsultaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário de edição de consulta existente.

    Rota    : GET/POST /consultas/<pk>/editar/
    Template: agendamentos/consulta_form.html
    """
    model = Consulta
    form_class = ConsultaForm
    template_name = 'agendamentos/consulta_form.html'

    def get_success_url(self):
        return reverse_lazy('agendamentos:consulta-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['animal_pk'] = None
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Consulta atualizada com sucesso!')
        return super().form_valid(form)


class ConsultaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Confirmação e cancelamento de consulta.

    Rota    : GET/POST /consultas/<pk>/cancelar/
    Template: agendamentos/consulta_confirm_delete.html
    """
    model = Consulta
    template_name = 'agendamentos/consulta_confirm_delete.html'
    success_url = reverse_lazy('agendamentos:consulta-list')
    context_object_name = 'consulta'

    def form_valid(self, form):
        messages.success(self.request, 'Consulta cancelada.')
        return super().form_valid(form)


# =============================================================================
# VIEWS DE DISPONIBILIDADE
# =============================================================================
# Gerencia os horários de funcionamento da ATIVO PET por dia da semana.
# Configurados uma única vez pela Sra. Fernanda — usados para validar
# se o horário de um agendamento está dentro do expediente da clínica.

class DisponibilidadeListView(LoginRequiredMixin, ListView):
    """
    Lista os horários de funcionamento configurados para cada dia da semana.

    Rota    : GET /disponibilidade/
    Template: agendamentos/disponibilidade_list.html
    Contexto: disponibilidades (ordenadas por dia_da_semana)
    """
    model = Disponibilidade
    template_name = 'agendamentos/disponibilidade_list.html'
    context_object_name = 'disponibilidades'
    ordering = ['dia_da_semana']


class DisponibilidadeCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário de cadastro de horário de funcionamento.

    Cada dia da semana pode ter apenas um registro (constraint no model).

    Rota    : GET/POST /disponibilidade/novo/
    Template: agendamentos/disponibilidade_form.html
    Sucesso : redireciona para a listagem
    """
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'agendamentos/disponibilidade_form.html'
    success_url = reverse_lazy('agendamentos:disponibilidade-list')

    def form_valid(self, form):
        messages.success(self.request, 'Horário cadastrado com sucesso!')
        return super().form_valid(form)


class DisponibilidadeUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário de edição de horário de funcionamento existente.

    Rota    : GET/POST /disponibilidade/<pk>/editar/
    Template: agendamentos/disponibilidade_form.html
    """
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'agendamentos/disponibilidade_form.html'
    success_url = reverse_lazy('agendamentos:disponibilidade-list')

    def form_valid(self, form):
        messages.success(self.request, 'Horário atualizado com sucesso!')
        return super().form_valid(form)


class DisponibilidadeDeleteView(LoginRequiredMixin, DeleteView):
    """
    Confirmação e exclusão de horário de funcionamento.

    Rota    : GET/POST /disponibilidade/<pk>/excluir/
    Template: agendamentos/disponibilidade_confirm_delete.html
    """
    model = Disponibilidade
    template_name = 'agendamentos/disponibilidade_confirm_delete.html'
    context_object_name = 'disponibilidade'
    success_url = reverse_lazy('agendamentos:disponibilidade-list')

    def form_valid(self, form):
        messages.success(self.request, 'Horário excluído.')
        return super().form_valid(form)
