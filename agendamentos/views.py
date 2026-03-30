"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : agendamentos/views.py
Função  : Define as views (controladores) do sistema. Cada view é responsável
          por processar uma requisição HTTP e retornar uma resposta — seja
          renderizando um template HTML ou redirecionando para outra página.

          Usamos CBVs (Class-Based Views) do Django para evitar código repetitivo.
          O Django já fornece classes prontas para listagem, criação, edição e
          exclusão — só precisamos configurar model, form e template.

          Views implementadas:
            Proprietário: List, Detail, Create, Update, Delete
            Animal:       List, Detail, Create, Update, Delete

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)

from .models import Proprietario, Animal, Consulta
from .forms import ProprietarioForm, AnimalForm, ConsultaForm


# =============================================================================
# MIXIN DE AUTENTICAÇÃO
# =============================================================================

# LoginRequiredMixin garante que apenas usuários autenticados acessem as views.
# Se um usuário não logado tentar acessar, é redirecionado para /login/.
# Todas as views do sistema herdam este mixin por segurança.


# =============================================================================
# VIEWS DE PROPRIETÁRIO
# =============================================================================

class ProprietarioListView(LoginRequiredMixin, ListView):
    """
    Exibe a lista de todos os proprietários (tutores) cadastrados.

    Rota: GET /proprietarios/
    Template: agendamentos/proprietario_list.html

    Contexto disponível no template:
        object_list -- QuerySet com todos os proprietários ordenados por nome.
        page_obj    -- Objeto de paginação (10 por página).
    """

    model = Proprietario
    template_name = 'agendamentos/proprietario_list.html'
    context_object_name = 'proprietarios'  # Nome da variável no template
    paginate_by = 10  # Exibe 10 proprietários por página

    def get_queryset(self):
        """
        Retorna a lista de proprietários, com suporte a busca por nome ou telefone.

        Se o parâmetro 'q' estiver na URL (ex: /proprietarios/?q=João),
        filtra os resultados pelo nome ou telefone do proprietário.
        """
        queryset = Proprietario.objects.order_by('nome')

        # Captura o termo de busca da URL (?q=termo)
        query = self.request.GET.get('q', '').strip()
        if query:
            # Filtra por nome OU telefone — case insensitive (icontains)
            queryset = queryset.filter(nome__icontains=query) | \
                       queryset.filter(telefone__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        """Adiciona o termo de busca ao contexto para manter o valor no campo de pesquisa."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ProprietarioDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um proprietário específico e seus animais vinculados.

    Rota: GET /proprietarios/<pk>/
    Template: agendamentos/proprietario_detail.html

    Contexto disponível no template:
        proprietario -- Objeto do proprietário.
        animais      -- Todos os animais vinculados a este proprietário.
    """

    model = Proprietario
    template_name = 'agendamentos/proprietario_detail.html'
    context_object_name = 'proprietario'

    def get_context_data(self, **kwargs):
        """Inclui os animais do proprietário no contexto do template."""
        context = super().get_context_data(**kwargs)
        # Busca todos os animais deste proprietário via related_name definido no model
        context['animais'] = self.object.animais.order_by('nome')
        return context


class ProprietarioCreateView(LoginRequiredMixin, CreateView):
    """
    Exibe o formulário e processa o cadastro de um novo proprietário.

    Fluxo:
        GET  -- Exibe o formulário em branco.
        POST -- Valida e salva o novo proprietário. Redireciona para a listagem.

    Rota: GET/POST /proprietarios/novo/
    Template: agendamentos/proprietario_form.html
    """

    model = Proprietario
    form_class = ProprietarioForm
    template_name = 'agendamentos/proprietario_form.html'

    # Para onde redirecionar após salvar com sucesso
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso após salvar o proprietário."""
        messages.success(self.request, 'Proprietário cadastrado com sucesso!')
        return super().form_valid(form)


class ProprietarioUpdateView(LoginRequiredMixin, UpdateView):
    """
    Exibe o formulário preenchido e processa a edição de um proprietário.

    Fluxo:
        GET  -- Exibe o formulário com os dados atuais do proprietário.
        POST -- Valida e atualiza os dados. Redireciona para o detalhe.

    Rota: GET/POST /proprietarios/<pk>/editar/
    Template: agendamentos/proprietario_form.html (mesmo template do Create)
    """

    model = Proprietario
    form_class = ProprietarioForm
    template_name = 'agendamentos/proprietario_form.html'
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso após atualizar o proprietário."""
        messages.success(self.request, 'Proprietário atualizado com sucesso!')
        return super().form_valid(form)


class ProprietarioDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exibe a página de confirmação e processa a exclusão de um proprietário.

    ATENÇÃO: A exclusão é em cascata — todos os animais e consultas vinculados
    a este proprietário também serão deletados (definido no model via CASCADE).

    Fluxo:
        GET  -- Exibe a página de confirmação de exclusão.
        POST -- Exclui o proprietário e redireciona para a listagem.

    Rota: GET/POST /proprietarios/<pk>/excluir/
    Template: agendamentos/proprietario_confirm_delete.html
    """

    model = Proprietario
    template_name = 'agendamentos/proprietario_confirm_delete.html'
    context_object_name = 'proprietario'
    success_url = reverse_lazy('agendamentos:proprietario-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso após excluir o proprietário."""
        messages.success(self.request, 'Proprietário excluído com sucesso.')
        return super().form_valid(form)


# =============================================================================
# VIEWS DE ANIMAL
# =============================================================================

class AnimalListView(LoginRequiredMixin, ListView):
    """
    Exibe a lista de todos os animais cadastrados, com busca e filtro por espécie.

    Rota: GET /animais/
    Template: agendamentos/animal_list.html

    Parâmetros de URL aceitos:
        q        -- Termo de busca por nome do animal ou do proprietário.
        especie  -- Filtro por espécie: 'cao', 'gato' ou 'outro'.
    """

    model = Animal
    template_name = 'agendamentos/animal_list.html'
    context_object_name = 'animais'
    paginate_by = 10

    def get_queryset(self):
        """
        Retorna animais filtrados por termo de busca e/ou espécie.

        select_related('proprietario') otimiza a query buscando o proprietário
        junto com o animal em uma única consulta ao banco (evita o problema N+1).
        """
        # select_related evita múltiplas queries ao banco para buscar o proprietário
        queryset = Animal.objects.select_related('proprietario').order_by('nome')

        # Filtra por nome do animal ou nome do proprietário
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(nome__icontains=query) | \
                       queryset.filter(proprietario__nome__icontains=query)

        # Filtra por espécie se o parâmetro estiver presente na URL
        especie = self.request.GET.get('especie', '').strip()
        if especie:
            queryset = queryset.filter(especie=especie)

        return queryset

    def get_context_data(self, **kwargs):
        """Adiciona os filtros ativos ao contexto para manter os valores nos campos."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['especie_selecionada'] = self.request.GET.get('especie', '')
        return context


class AnimalDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de um animal específico e seu histórico de consultas.

    Rota: GET /animais/<pk>/
    Template: agendamentos/animal_detail.html

    Contexto disponível no template:
        animal    -- Objeto do animal com seu proprietário.
        consultas -- Histórico de consultas do animal, do mais recente ao mais antigo.
    """

    model = Animal
    template_name = 'agendamentos/animal_detail.html'
    context_object_name = 'animal'

    def get_queryset(self):
        """Inclui o proprietário na query para evitar query extra no template."""
        return Animal.objects.select_related('proprietario')

    def get_context_data(self, **kwargs):
        """Inclui o histórico de consultas do animal no contexto."""
        context = super().get_context_data(**kwargs)
        # Ordena do mais recente para o mais antigo — mais útil para a Sra. Fernanda
        context['consultas'] = self.object.consultas.order_by('-data_hora')
        return context


class AnimalCreateView(LoginRequiredMixin, CreateView):
    """
    Exibe o formulário e processa o cadastro de um novo animal.

    Rota: GET/POST /animais/novo/
    Template: agendamentos/animal_form.html

    Suporta pré-seleção de proprietário via parâmetro de URL:
        /animais/novo/?proprietario=<pk>
    Útil quando o usuário clica em "Adicionar animal" na página do proprietário.
    """

    model = Animal
    form_class = AnimalForm
    template_name = 'agendamentos/animal_form.html'
    success_url = reverse_lazy('agendamentos:animal-list')

    def get_initial(self):
        """
        Pré-preenche o campo de proprietário se o parâmetro estiver na URL.

        Permite que o fluxo: 'Ver proprietário → Adicionar animal' já venha
        com o tutor correto selecionado no formulário.
        """
        initial = super().get_initial()
        proprietario_pk = self.request.GET.get('proprietario')
        if proprietario_pk:
            initial['proprietario'] = proprietario_pk
        return initial

    def form_valid(self, form):
        """Exibe mensagem de sucesso após cadastrar o animal."""
        messages.success(self.request, 'Animal cadastrado com sucesso!')
        return super().form_valid(form)


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    """
    Exibe o formulário preenchido e processa a edição de um animal.

    Rota: GET/POST /animais/<pk>/editar/
    Template: agendamentos/animal_form.html
    """

    model = Animal
    form_class = AnimalForm
    template_name = 'agendamentos/animal_form.html'
    success_url = reverse_lazy('agendamentos:animal-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso após atualizar o animal."""
        messages.success(self.request, 'Animal atualizado com sucesso!')
        return super().form_valid(form)


class AnimalDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exibe a confirmação e processa a exclusão de um animal.

    ATENÇÃO: Todas as consultas vinculadas ao animal também serão deletadas (CASCADE).

    Rota: GET/POST /animais/<pk>/excluir/
    Template: agendamentos/animal_confirm_delete.html
    """

    model = Animal
    template_name = 'agendamentos/animal_confirm_delete.html'
    context_object_name = 'animal'
    success_url = reverse_lazy('agendamentos:animal-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso após excluir o animal."""
        messages.success(self.request, 'Animal excluído com sucesso.')
        return super().form_valid(form)


# =============================================================================
# VIEW: Home (frontpage pública)
# =============================================================================
# Importação necessária — adicionar ao topo do views.py junto com os outros imports
# from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    View da frontpage pública da ATIVO PET.

    Página inicial do sistema — acessível sem login.
    Apresenta a clínica, seus serviços e o CTA para agendamento.

    Rota: GET /
    Template: templates/home.html
    """
    template_name = 'home.html'
# =============================================================================
# VETSystem — views de Consulta
# Adicionar ao final de agendamentos/views.py
# =============================================================================
# Adicione 'Consulta' ao import do models no topo:
#   from .models import Proprietario, Animal, Consulta, Consulta
# Adicione 'ConsultaForm' ao import do forms no topo:
#   from .forms import ProprietarioForm, AnimalForm, ConsultaForm, ConsultaForm
# =============================================================================


class ConsultaListView(LoginRequiredMixin, ListView):
    """
    Lista todas as consultas com filtros opcionais por status e data.

    GET /consultas/
    GET /consultas/?status=agendado
    GET /consultas/?data=2026-04-10

    Template: agendamentos/consulta_list.html
    Context: object_list, status_choices, status_atual, data_filtro
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
        ctx['status_atual'] = self.request.GET.get('status', '')
        ctx['data_filtro'] = self.request.GET.get('data', '')
        return ctx


class ConsultaDetailView(LoginRequiredMixin, DetailView):
    """
    Exibe os detalhes de uma consulta específica.

    GET /consultas/<pk>/
    Template: agendamentos/consulta_detail.html
    Context: object (Consulta com animal e proprietário)
    """
    model = Consulta
    template_name = 'agendamentos/consulta_detail.html'
    context_object_name = 'consulta'

    def get_queryset(self):
        # Carrega animal e proprietário em uma única query (evita N+1)
        return super().get_queryset().select_related('animal__proprietario')


class ConsultaCreateView(LoginRequiredMixin, CreateView):
    """
    Formulário de criação de nova consulta (agendamento).

    GET  /consultas/nova/           → exibe formulário vazio
    GET  /consultas/nova/?animal=1  → pré-seleciona animal
    POST /consultas/nova/           → salva e redireciona para o detalhe

    Template: agendamentos/consulta_form.html
    """
    model = Consulta
    form_class = ConsultaForm
    template_name = 'agendamentos/consulta_form.html'
    success_url = reverse_lazy('agendamentos:consulta-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Repassa o animal_pk da querystring para o form pré-selecionar
        kwargs['animal_pk'] = self.request.GET.get('animal')
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Consulta agendada com sucesso!')
        return super().form_valid(form)


class ConsultaUpdateView(LoginRequiredMixin, UpdateView):
    """
    Formulário de edição de consulta existente.

    GET  /consultas/<pk>/editar/ → formulário preenchido
    POST /consultas/<pk>/editar/ → salva e redireciona para o detalhe

    Template: agendamentos/consulta_form.html (mesmo do create)
    """
    model = Consulta
    form_class = ConsultaForm
    template_name = 'agendamentos/consulta_form.html'

    def get_success_url(self):
        return reverse_lazy('agendamentos:consulta-detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['animal_pk'] = None  # já vem preenchido do objeto
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Consulta atualizada com sucesso!')
        return super().form_valid(form)


class ConsultaDeleteView(LoginRequiredMixin, DeleteView):
    """
    Página de confirmação de cancelamento/exclusão de consulta.

    GET  /consultas/<pk>/cancelar/ → tela de confirmação
    POST /consultas/<pk>/cancelar/ → exclui e redireciona para lista

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
# VIEW: Dashboard interno
# =============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard interno — tela inicial pós-login da Sra. Fernanda.

    Exibe:
      - Totais de consultas por status (agendado, confirmado, realizado, cancelado)
      - Consultas agendadas para hoje
      - Próximas consultas dos próximos 7 dias (excluindo hoje)

    Rota: GET /dashboard/
    Template: templates/dashboard.html
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        import datetime

        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        sete_dias = hoje + datetime.timedelta(days=7)

        # Totais por status — usados nos cards de resumo
        ctx['total_agendado']   = Consulta.objects.filter(status='agendado').count()
        ctx['total_confirmado'] = Consulta.objects.filter(status='confirmado').count()
        ctx['total_realizado']  = Consulta.objects.filter(status='realizado').count()
        ctx['total_cancelado']  = Consulta.objects.filter(status='cancelado').count()

        # Consultas de hoje ordenadas por horário
        ctx['consultas_hoje'] = (
            Consulta.objects
            .filter(data_hora__date=hoje)
            .select_related('animal__proprietario')
            .order_by('data_hora')
        )

        # Próximas consultas: amanhã até 7 dias, só ativas (agendado ou confirmado)
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
