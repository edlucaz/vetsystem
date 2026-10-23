# VETSystem — Documentação Técnica

**Versão:** 2.0 (PI II) | **Data:** Outubro 2026 | **Projeto:** PJI110 — UNIVESP

---

## 1. Visão Geral

O VETSystem é um sistema web de agendamento desenvolvido para a clínica **ATIVO PET — Fisioterapia e Bem-Estar Animal** (Limeira/SP). O sistema substitui o controle manual de agendamentos via WhatsApp por uma solução centralizada acessível pelo navegador.

**Problema resolvido:** A proprietária Sra. Fernanda Guevara recebia solicitações de agendamento por WhatsApp, sem histórico organizado, sem visibilidade da agenda e sem controle de cancelamentos.

**Solução entregue:** Aplicação web com cadastro de tutores e animais, agendamento de consultas com ciclo de vida completo (agendado → confirmado → realizado/cancelado), dashboard de agenda diária e configuração de horários de funcionamento.

**URL de produção:** https://vetsystem-gky6.onrender.com

---

## 2. Arquitetura

### 2.1 Stack tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Linguagem | Python | 3.12 |
| Framework web | Django | 6.x |
| API | Django REST Framework + drf-spectacular | 3.18 |
| Frontend | Tailwind CSS (CDN) + JavaScript puro | 3.x |
| Formulários | django-crispy-forms | 2.6 |
| Banco (dev) | SQLite | — |
| Banco (prod) | PostgreSQL (Neon) | — |
| Testes | pytest, pytest-django, pytest-cov | — |
| CI | GitHub Actions (PostgreSQL 16) | — |
| Servidor WSGI | Gunicorn | 21.2 |
| Estáticos (prod) | WhiteNoise | 6.8 |
| Deploy | Render | — |

### 2.2 Padrão MTV (Model-Template-View)

O Django segue o padrão MTV, equivalente ao MVC:

- **Model** (`models.py`) — define as tabelas do banco e as regras de negócio dos dados
- **Template** (`templates/`) — HTML com tags Django para renderização dinâmica
- **View** (`views.py`) — processa requisições HTTP e conecta models aos templates

### 2.3 Estrutura de diretórios

```
vetsystem/
├── agendamentos/               # App principal do sistema
│   ├── api/                    # API REST (DRF): serializers, views, urls (13 rotas, 29 operações)
│   ├── management/commands/    # criar_superusuario, criar_horarios_padrao, popular_demo, medir_desempenho
│   ├── migrations/             # Histórico de alterações no banco
│   ├── templates/agendamentos/ # Templates do app (19 arquivos HTML)
│   ├── tests/                  # Suíte pytest (129 testes)
│   ├── admin.py                # Registro dos models no Django Admin
│   ├── apps.py                 # Configuração do app
│   ├── forms.py                # 4 formulários com validação
│   ├── models.py               # 5 models: Proprietario, Animal, RegistroPeso, Consulta, Disponibilidade
│   ├── services.py             # Regras de negócio (horários livres, validação, status, estatísticas)
│   ├── urls.py                 # 23 rotas do app
│   └── views.py                # 23 CBVs
├── templates/                  # Templates globais compartilhados
│   ├── base.html               # Layout base com navbar e footer
│   ├── dashboard.html          # Dashboard pós-login
│   ├── home.html               # Frontpage pública
│   └── registration/login.html # Tela de login
├── static/                     # CSS, JS e imagens customizadas
├── vetsystem/                  # Pacote de configuração do projeto
│   ├── settings.py             # Configurações (dev + produção via env vars)
│   ├── urls.py                 # Roteador raiz
│   └── wsgi.py                 # Ponto de entrada WSGI (produção)
├── Procfile                    # Comando de start para o Render
├── render.yaml                 # Blueprint de deploy (Render)
├── requirements.txt            # Dependências Python
└── start.sh                    # Script de inicialização em produção
```

---

## 3. Modelo de Dados

### 3.1 Diagrama de entidades

```
Proprietario (1) ──────── (N) Animal (1) ──────── (N) Consulta (N) ──── (1) Disponibilidade
                             │                                     "verifica" (FK)
                             └── (N) RegistroPeso
```

### 3.2 Models

#### Proprietario
Representa o tutor/dono do animal atendido.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `id` | BigAutoField (PK) | Auto | Chave primária automática |
| `nome` | CharField(200) | ✓ | Nome completo do tutor |
| `telefone` | CharField(20) | ✓ | Contato principal |
| `email` | EmailField | — | E-mail para confirmações |
| `cpf` | CharField(14) | — | CPF no formato 000.000.000-00 |

#### Animal
Representa o paciente atendido pela ATIVO PET.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `id` | BigAutoField (PK) | Auto | Chave primária automática |
| `nome` | CharField(100) | ✓ | Nome do animal |
| `especie` | CharField (choices) | ✓ | `cao`, `gato` ou `outro` |
| `raca` | CharField(100) | — | Raça (vazio = SRD) |
| `data_nascimento` | DateField | — | Data de nascimento; a idade é calculada (`idade`, `idade_formatada`) |
| `peso` | DecimalField(5,2) | — | Peso atual em kg; ao salvar, grava um `RegistroPeso` (`services.registrar_peso`) |
| `queixa` | TextField | — | Motivo do atendimento |
| `proprietario` | FK → Proprietario | ✓ | Tutor responsável (CASCADE) |

#### RegistroPeso
Histórico de pesagens do animal (um registro por dia).

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `animal` | FK → Animal | ✓ | Animal pesado (CASCADE) |
| `data` | DateField | ✓ | Dia da pesagem (único por animal e dia) |
| `peso` | DecimalField(5,2) | ✓ | Peso em kg |

#### Consulta
Representa um agendamento de atendimento — model central do sistema.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `id` | BigAutoField (PK) | Auto | Chave primária automática |
| `animal` | FK → Animal | ✓ | Animal atendido (CASCADE) |
| `data_hora` | DateTimeField | ✓ | Data e horário do atendimento |
| `tipo` | CharField (choices) | ✓ | `consulta`, `fisioterapia`, `acupuntura` |
| `status` | CharField (choices) | ✓ | `agendado`, `confirmado`, `realizado`, `cancelado` |
| `observacoes` | TextField | — | Anotações da veterinária |
| `duracao_minutos` | PositiveIntegerField | ✓ | Duração estimada (padrão: 60) |
| `disponibilidade` | FK → Disponibilidade | — | Relacionamento "verifica": preenchida em `save()` pelo dia da semana |

#### Disponibilidade
Define os horários de funcionamento da clínica por dia da semana.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `id` | BigAutoField (PK) | Auto | Chave primária automática |
| `dia_da_semana` | IntegerField (choices) | ✓ | 0=Segunda … 4=Sexta (único por dia) |
| `hora_inicio` | TimeField | ✓ | Horário de abertura |
| `hora_fim` | TimeField | ✓ | Horário de encerramento |
| `ativo` | BooleanField | ✓ | False = clínica não atende (feriados) |

---

## 4. Rotas (URLs)

| Método | URL | View | Descrição |
|--------|-----|------|-----------|
| GET | `/` | HomeView | Frontpage pública |
| GET | `/login/` | LoginView | Tela de login |
| GET | `/logout/` | LogoutView | Encerra sessão |
| GET | `/dashboard/` | DashboardView | Dashboard interno |
| GET | `/proprietarios/` | ProprietarioListView | Lista de proprietários |
| GET | `/proprietarios/<pk>/` | ProprietarioDetailView | Detalhe do proprietário |
| GET/POST | `/proprietarios/novo/` | ProprietarioCreateView | Cadastro |
| GET/POST | `/proprietarios/<pk>/editar/` | ProprietarioUpdateView | Edição |
| GET/POST | `/proprietarios/<pk>/excluir/` | ProprietarioDeleteView | Exclusão |
| GET | `/animais/` | AnimalListView | Lista de animais |
| GET | `/animais/<pk>/` | AnimalDetailView | Detalhe do animal |
| GET/POST | `/animais/novo/` | AnimalCreateView | Cadastro |
| GET/POST | `/animais/<pk>/editar/` | AnimalUpdateView | Edição |
| GET/POST | `/animais/<pk>/excluir/` | AnimalDeleteView | Exclusão |
| GET | `/consultas/` | ConsultaListView | Lista de consultas |
| GET | `/consultas/agenda/` | AgendaSemanalView | Agenda semanal |
| GET | `/consultas/<pk>/` | ConsultaDetailView | Detalhe da consulta |
| GET/POST | `/consultas/nova/` | ConsultaCreateView | Agendamento |
| GET/POST | `/consultas/<pk>/editar/` | ConsultaUpdateView | Edição |
| GET/POST | `/consultas/<pk>/cancelar/` | ConsultaDeleteView | Cancelamento |
| GET | `/disponibilidade/` | DisponibilidadeListView | Horários de funcionamento |
| GET/POST | `/disponibilidade/novo/` | DisponibilidadeCreateView | Cadastro |
| GET/POST | `/disponibilidade/<pk>/editar/` | DisponibilidadeUpdateView | Edição |
| GET/POST | `/disponibilidade/<pk>/excluir/` | DisponibilidadeDeleteView | Exclusão |
| GET | `/admin/` | Django Admin | Painel administrativo |

### 4.1 API REST (`/api/`)

Autenticação por sessão + CSRF. Documentação interativa em `/api/docs/`; esquema em `docs/api-openapi.json`.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/api/proprietarios/` | Lista (`?search=`) e cria tutores |
| GET/PUT/PATCH/DELETE | `/api/proprietarios/<id>/` | Detalhe, edição e exclusão |
| GET/POST | `/api/animais/` | Lista (`?search=`, `?proprietario=`, `?especie=`) e cria animais |
| GET/PUT/PATCH/DELETE | `/api/animais/<id>/` | Detalhe, edição e exclusão |
| GET | `/api/animais/<id>/pesos/` | Histórico de peso com variação |
| GET/POST | `/api/consultas/` | Lista (filtros) e agenda consultas (valida expediente e conflito) |
| GET/PUT/PATCH/DELETE | `/api/consultas/<id>/` | Detalhe, edição e exclusão |
| POST | `/api/consultas/<id>/status/` | Atualiza o status (confirmar, realizar, ausência) |
| GET/POST | `/api/disponibilidades/` | Expediente por dia da semana |
| GET/PUT/PATCH/DELETE | `/api/disponibilidades/<id>/` | Detalhe, edição e exclusão |
| GET | `/api/horarios-livres/` | Horários livres de uma data |
| GET | `/api/estatisticas/` | Dados do painel de análise |
| GET | `/api/horarios-publicos/` | Horários livres para a home pública |

### 4.2 `services.py`

Única fonte das regras de negócio; formulários, views e API chamam estas funções: `horarios_livres`, `validar_agendamento` ("Horário disponível?"), `atualizar_status`, `registrar_peso`, `historico_peso`, `estatisticas`, `validar_telefone`, `validar_data_nascimento`.

### 4.3 JavaScript (`static/js/`)

JS puro consumindo `/api/`, como melhoria progressiva (as telas funcionam sem JS): `api.js`, `autocomplete.js`, `agenda.js`, `consulta_form.js`, `status.js`, `seletor_cadastro.js`, `agenda_semanal.js`, `dashboard_analise.js`, `horarios_publicos.js`.

### 4.4 Testes

pytest com pytest-django: unitários (models, services, forms), integração (views, API, comandos) e acessibilidade automatizada (`test_acessibilidade.py`). Resultados e cobertura em `docs/metricas/resultados_pi2.md`; falhas e correções em `docs/metricas/registro_testes.md`. O CI roda a suíte em PostgreSQL 16.

### 4.5 Acessibilidade (WCAG 2.1 AA)

Paleta com contraste mínimo 4,5:1 (turquesa #1E7579, laranja #B9471A, texto secundário gray-600), foco visível, link "Pular para o conteúdo", `<main id="conteudo">`, tabelas com `scope`/`caption`, rótulos em todos os filtros e `aria-describedby` nos formulários. Lighthouse ≥ 95 em todas as telas medidas.

---

## 5. Configuração e Deploy

### 5.1 Variáveis de ambiente

| Variável | Descrição | Dev | Prod |
|----------|-----------|-----|------|
| `SECRET_KEY` | Chave criptográfica Django | chave insegura padrão | gerada pelo Render |
| `DEBUG` | Modo debug | `True` | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` | `vetsystem-gky6.onrender.com` |
| `DATABASE_URL` | URL do banco | SQLite local | PostgreSQL Render |
| `DJANGO_SUPERUSER_USERNAME` | Usuário admin | — | `fernanda` |
| `DJANGO_SUPERUSER_EMAIL` | E-mail admin | — | configurado no render.yaml |
| `DJANGO_SUPERUSER_PASSWORD` | Senha admin | — | configurado no render.yaml |

### 5.2 Script de inicialização (start.sh)

Em produção, o Render executa `start.sh` a cada deploy:

```bash
python manage.py migrate --noinput        # Aplica migrações pendentes
python manage.py criar_superusuario       # Cria admin (se não existir)
python manage.py collectstatic --noinput  # Coleta arquivos estáticos
gunicorn vetsystem.wsgi --bind 0.0.0.0:$PORT
```

### 5.3 Configurações de produção (settings.py)

Quando `DEBUG=False`, o settings ativa automaticamente:
- `SECURE_PROXY_SSL_HEADER` — confia nos headers HTTPS do proxy do Render
- `SECURE_SSL_REDIRECT` — redireciona HTTP → HTTPS
- `SESSION_COOKIE_SECURE` — cookie de sessão apenas em HTTPS
- `CSRF_COOKIE_SECURE` — cookie CSRF apenas em HTTPS
- `CSRF_TRUSTED_ORIGINS` — domínios autorizados para requisições POST

### 5.4 Instalação local

```bash
git clone https://github.com/edlucaz/vetsystem.git
cd vetsystem
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 6. Manual do Usuário

### 6.1 Primeiro acesso

1. Acesse https://vetsystem-gky6.onrender.com
2. Clique em **Entrar** (canto superior direito) ou no botão **Agendar Consulta**
3. Digite o usuário `fernanda` e a senha fornecida
4. Após o login, você é redirecionado para o **Dashboard**

> O serviço está no plano gratuito do Render. Se a página demorar ~30 segundos para carregar na primeira vez, é normal — o servidor "acorda" após inatividade.

### 6.2 Dashboard

A tela inicial mostra:
- **Cards de totais** — quantidade de consultas por status (agendadas, confirmadas, realizadas, canceladas)
- **Consultas de hoje** — tabela com todos os atendimentos do dia atual, ordenados por horário
- **Próximos 7 dias** — consultas agendadas ou confirmadas para a semana
- **Atalhos rápidos** — botões para as ações mais comuns

### 6.3 Cadastrar um proprietário (tutor)

1. Clique em **Proprietários** na barra de navegação
2. Clique em **+ Novo Proprietário**
3. Preencha nome e telefone (obrigatórios), e-mail e CPF (opcionais)
4. Clique em **Salvar**

Para buscar um proprietário existente, use o campo de busca na listagem — aceita nome ou telefone.

### 6.4 Cadastrar um animal

1. Clique em **Animais** na barra de navegação
2. Clique em **+ Novo Animal**
3. Preencha nome, espécie, raça (opcional), idade e peso (opcionais), queixa principal e selecione o proprietário
4. Clique em **Salvar**

**Dica:** Na página de detalhe de um proprietário, há um botão direto para cadastrar um animal já vinculado a ele.

### 6.5 Agendar uma consulta

1. Clique em **Consultas** na barra de navegação
2. Clique em **+ Nova Consulta**
3. Selecione o animal, data/hora, tipo de atendimento e status inicial
4. Adicione observações se necessário
5. Clique em **Agendar consulta**

**Regra:** Não é permitido agendar consultas em datas passadas. O sistema exibe uma mensagem de erro se a data selecionada já passou.

### 6.6 Atualizar o status de uma consulta

1. Na lista de consultas, clique em **Ver** na consulta desejada
2. Clique em **Editar Consulta**
3. Altere o campo **Status** para o novo estado
4. Clique em **Salvar alterações**

**Ciclo de vida:** `Agendado → Confirmado → Realizado` (ou `Cancelado` em qualquer etapa)

### 6.7 Configurar horários de funcionamento

1. Clique em **Horários** na barra de navegação
2. Clique em **+ Novo Horário**
3. Selecione o dia da semana, horário de início e fim
4. Deixe **Ativo** marcado (desmarque para feriados)
5. Clique em **Salvar horário**

**Atenção:** Cada dia da semana pode ter apenas um horário cadastrado. Para alterar, use o botão **Editar** na listagem.

### 6.8 Painel Administrativo (Django Admin)

Acesse `/admin/` para gerenciar usuários do sistema, alterar senhas e acessar dados diretamente pelas tabelas. Recomendado apenas para a equipe de desenvolvimento.

---

## 7. Decisões de Projeto

| Decisão | Justificativa |
|---------|--------------|
| Django em vez de Flask | CBVs e ORM reduzem código repetitivo; Admin embutido é entregável imediato |
| Tailwind via CDN | Evita build step (Node.js) — simplifica o ambiente de desenvolvimento e o deploy |
| Cores inline com `style=""` | Tailwind CDN não processa classes customizadas (`bg-ativo-turquesa`) — inline é mais seguro |
| SQLite em dev, PostgreSQL em prod | SQLite é zero-config para desenvolvimento; PostgreSQL é mais robusto para produção |
| Render em vez de Railway | Plano gratuito permanente do Render vs. trial de 30 dias do Railway |
| Neon em vez do banco do Render | O PostgreSQL gratuito do Render expira; o Neon mantém os dados e é acessado só por `DATABASE_URL` |
| JavaScript puro, sem framework | Sem build step; poucos scripts pequenos; a API é consumida com `fetch` |
| Melhoria progressiva | Todas as telas funcionam sem JS; o JS só acelera (agenda, autocomplete, status) |
| Regras em `services.py` | Formulários e API compartilham a mesma validação, sem duplicar regras |
| WhiteNoise para estáticos | Serve arquivos estáticos sem precisar de CDN ou nginx separado |
| `criar_superusuario` command | O Render não oferece Shell no plano gratuito — comando garante admin sem interação manual |

---

## 8. Trabalhos Futuros

- Envio automático de notificação por WhatsApp/e-mail (hoje o aviso é manual, pelo botão "Confirmar e avisar tutor")
- Histórico de alterações de status por consulta
- Suporte a múltiplas veterinárias/profissionais
- Exportação de relatórios (PDF/CSV) além do painel de análise
- Gráfico de evolução do peso na tela do animal
- Autoagendamento pelo tutor, com confirmação da clínica

---

*Projeto Integrador em Computação I (PJI110) — UNIVESP 2026*
*ATIVO PET — Fisioterapia e Bem-Estar Animal, Limeira/SP*
