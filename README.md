# VETSystem — Sistema de Agendamento Veterinário

> Projeto Integrador em Computação I (PJI110) e II (PJI240) — UNIVESP 2026
> Clínica ATIVO PET — Fisioterapia e Bem-Estar Animal, Limeira/SP

## Sobre o projeto

O VETSystem substitui o controle manual de agendamentos via WhatsApp da clínica ATIVO PET por uma solução web centralizada. A proprietária Sra. Fernanda Guevara pode cadastrar tutores, animais e consultas, gerenciar a agenda diária e configurar os horários de funcionamento da clínica, tudo pelo navegador.

O sistema foi desenvolvido em duas etapas:

| Etapa | Disciplina | O que entregou | Marco no Git |
|---|---|---|---|
| **PI I** — 1º semestre/2026 | PJI110 | Primeira versão em Django: CRUD de tutores, animais, consultas e horários de funcionamento, dashboard e deploy no Render | tag [`v1.0-pi1`](https://github.com/edlucaz/vetsystem/tree/v1.0-pi1) |
| **PI II** — 2º semestre/2026 | PJI240 | Evolução: regras de negócio, testes automatizados e CI, API REST, acessibilidade WCAG 2.1 AA, JavaScript assíncrono e banco na nuvem (Neon) | branch `main` (PRs #1–#8) |

**Sistema em produção:** https://vetsystem-gky6.onrender.com

## Funcionalidades

### PI I — primeira versão

- Cadastro e busca de proprietários (tutores)
- Cadastro de animais vinculados aos tutores
- Agendamento de consultas com tipo (consulta, fisioterapia, acupuntura) e status
- Dashboard com agenda do dia e próximos 7 dias
- Configuração de horários de funcionamento por dia da semana
- Frontpage pública da ATIVO PET com CTA de agendamento
- Autenticação com login/logout

### PI II — evolução

- **Regras de agendamento:** a consulta só é aceita dentro do expediente cadastrado e sem conflito com outro horário. As regras ficam num único módulo (`agendamentos/services.py`), usado pelos formulários e pela API.
- **Modelo fiel ao DER:** Proprietário 1:N Animal 1:N Consulta N:1 Disponibilidade. A consulta é ligada ao expediente do dia, e a idade do animal é calculada a partir da data de nascimento.
- **Telas seguindo o fluxograma:** cancelar uma consulta muda o status em vez de apagar o registro, e o atendimento pode ser marcado como realizado direto no dashboard.
- **API REST** (Django REST Framework) com documentação interativa Swagger em `/api/docs/`.
- **JavaScript puro e assíncrono:** busca de tutor/animal, agenda de horários livres e agendamento sem recarregar a página. As telas continuam funcionando sem JS (melhoria progressiva).
- **Acessibilidade WCAG 2.1 AA:** paleta com contraste ≥ 4,5:1, link "Pular para o conteúdo", rótulos em todos os campos, tabelas com `scope`/`caption`, erros associados aos campos e menu responsivo no celular.
- **Testes automatizados** com pytest e **integração contínua** no GitHub Actions (PostgreSQL 16).
- **Banco na nuvem:** PostgreSQL no Neon (gratuito e sem expiração). A aplicação continua no Render.

O andamento fase a fase está em [`docs/PLANO_PI2.md`](docs/PLANO_PI2.md).

## Stack

| Camada | PI I | PI II |
|--------|------|-------|
| Backend | Python 3.12 + Django 6.x | Django 6.0.9 (patch de segurança) |
| API | — | Django REST Framework + drf-spectacular (OpenAPI 3 / Swagger) |
| Frontend | Tailwind CSS via CDN | + CSS próprio com paleta acessível e JavaScript puro (Fetch API) |
| Formulários | django-crispy-forms + crispy-tailwind | (mantido) |
| Banco (dev) | SQLite | (mantido) |
| Banco (prod) | PostgreSQL (Render) | PostgreSQL (Neon) |
| Deploy | Render (plano gratuito) | Render, com deploy automático a cada merge na `main` |
| Servidor WSGI | Gunicorn | (mantido) |
| Estáticos | WhiteNoise | (mantido) |
| Testes / CI | — | pytest + pytest-django + pytest-cov; GitHub Actions |

## Estrutura do projeto

```
vetsystem/
├── agendamentos/               # App principal
│   ├── api/                    # API REST — serializers, viewsets e rotas (PI II)
│   ├── management/commands/    # criar_superusuario, criar_horarios_padrao
│   ├── migrations/             # Migrações do banco de dados
│   ├── templates/agendamentos/ # Templates HTML do app
│   ├── tests/                  # Testes automatizados com pytest (PI II)
│   ├── admin.py                # Configuração do Django Admin
│   ├── forms.py                # Formulários (Proprietario, Animal, Consulta, Disponibilidade)
│   ├── models.py               # Models (Proprietario, Animal, Consulta, Disponibilidade)
│   ├── services.py             # Regras de negócio: horários livres, conflitos, status (PI II)
│   ├── urls.py                 # Rotas do app
│   └── views.py                # Views (CBVs)
├── docs/
│   ├── PLANO_PI2.md            # Plano de melhorias do PI II, por fase
│   ├── documentacao_tecnica.md # Documentação técnica
│   ├── api-openapi.json        # Esquema OpenAPI exportado
│   ├── metricas/               # Linha de base do PI I, Lighthouse, registro de testes
│   └── pi1-fluxogramas/        # Fluxogramas entregues no PI I
├── scripts/lighthouse.sh       # Mede acessibilidade/boas práticas das telas
├── static/                     # CSS e JavaScript (api.js, agenda.js, autocomplete.js…)
├── templates/                  # Templates globais (base.html, home.html, dashboard.html)
├── vetsystem/                  # Configurações do projeto Django (settings, urls, wsgi)
├── .github/workflows/ci.yml    # Integração contínua (PI II)
├── Procfile                    # Comando de inicialização
├── render.yaml                 # Configuração Render
├── requirements.txt            # Dependências de produção
├── requirements-dev.txt        # + dependências de teste
└── start.sh                    # Script de inicialização em produção
```

## Instalação local

```bash
# 1. Clone o repositório
git clone https://github.com/edlucaz/vetsystem.git
cd vetsystem

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências (requirements.txt basta se não for rodar os testes)
pip install -r requirements-dev.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env se necessário (a chave padrão funciona em desenvolvimento)

# 5. Execute as migrações
python manage.py migrate

# 6. Crie o superusuário
python manage.py createsuperuser

# 7. Cadastre o expediente padrão (sem ele, nenhuma consulta é aceita)
python manage.py criar_horarios_padrao

# 8. Inicie o servidor
python manage.py runserver
```

Acesse em: http://127.0.0.1:8000

## Testes

```bash
pytest              # todos os testes
pytest --cov        # com cobertura
python manage.py check && python manage.py makemigrations --check --dry-run
```

O CI (`.github/workflows/ci.yml`) roda as mesmas verificações em PostgreSQL 16 a cada push e pull request.

## Variáveis de ambiente

| Variável | Descrição | Padrão (dev) |
|----------|-----------|--------------|
| `SECRET_KEY` | Chave secreta Django | chave insegura local |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL do banco de dados (em produção, a do Neon) | SQLite local |
| `DJANGO_SUPERUSER_USERNAME` | Usuário admin (produção) | `fernanda` |
| `DJANGO_SUPERUSER_EMAIL` | E-mail admin (produção) | — |
| `DJANGO_SUPERUSER_PASSWORD` | Senha admin (produção) | — |

## Deploy (Render + Neon)

O web service é configurado pelo `render.yaml`. O banco fica no Neon, porque o PostgreSQL gratuito do Render expira em 30 dias.

1. Crie um banco PostgreSQL no Neon e copie a connection string.
2. Em dashboard.render.com → New → Blueprint, conecte o repositório `edlucaz/vetsystem`.
3. No painel do Render, defina `DATABASE_URL` (Neon) e `DJANGO_SUPERUSER_PASSWORD`. Senhas nunca são versionadas.
4. O `start.sh` executa as migrações e cria o superusuário automaticamente.
5. A partir daí, cada merge na `main` é publicado sozinho.

**URL de produção:** https://vetsystem-gky6.onrender.com
**Credenciais padrão:** usuário `fernanda` / senha definida em `DJANGO_SUPERUSER_PASSWORD`

## URLs do sistema

| URL | Descrição | Requer login |
|-----|-----------|:---:|
| `/` | Frontpage pública ATIVO PET | Não |
| `/login/` | Página de login | Não |
| `/dashboard/` | Dashboard com agenda do dia | Sim |
| `/proprietarios/` | Lista de proprietários | Sim |
| `/animais/` | Lista de animais | Sim |
| `/consultas/` | Lista de consultas (filtros por status e data) | Sim |
| `/consultas/<id>/cancelar/` | Cancela a consulta (muda o status, mantém o histórico) — PI II | Sim |
| `/disponibilidade/` | Horários de funcionamento | Sim |
| `/api/` | API REST — PI II | Sim |
| `/api/docs/` | Documentação interativa da API (Swagger) — PI II | Sim |
| `/admin/` | Painel administrativo Django | Sim (staff) |

## API REST (PI II)

Autenticação por sessão do Django + CSRF. Documentação completa em `/api/docs/` e em [`docs/api-openapi.json`](docs/api-openapi.json).

| Endpoint | Função |
|---|---|
| `/api/proprietarios/` | CRUD de tutores |
| `/api/animais/` | CRUD de animais |
| `/api/consultas/` | CRUD de consultas, com as mesmas regras de agendamento dos formulários |
| `/api/consultas/<id>/status/` | Atualiza o status (realizado, cancelado…) |
| `/api/disponibilidades/` | Horários de funcionamento |
| `/api/horarios-livres/` | Horários livres de um dia |

## Resultados do PI II até agora

| Indicador | PI I (linha de base) | PI II |
|---|---|---|
| Testes automatizados | 0 | 105 |
| Endpoints de API | 0 | 10 rotas / 26 operações |
| Contraste das cores principais | 3,05–3,09:1 (reprovado) | ≥ 4,5:1 (WCAG AA) |
| Regra de expediente e conflito | não verificava | verificada no formulário e na API |
| Recarregamentos para agendar (tutor já cadastrado) | 2 | 0 (agendamento via API) |

Detalhes em [`docs/metricas/`](docs/metricas/).

## Grupo

### PI I — PJI110

| Nome | RA |
|------|----|
| Alison Ferreira Cabral | 2213917 |
| Denize Aparecida Graciano | 24203934 |
| Eder de Paula Evangelista | 23201277 |
| Lucas Eduardo Rocha | 24217901 |
| Miúcha Carvalho Cicaroni | 23212531 |
| Reginaldo Aparecido Matioli | 1501071 |
| Samuel de Souza Rodrigues | 23219876 |
| Yuri Liston | 24203775 |

**Orientador:** Prof. Eduardo Maurício Moreno Pinto — UNIVESP

### PI II — PJI240 (Grupo 8)

| Nome | RA |
|------|----|
| Daniel Geremias Pinheiro de Jesus | 24223170 |
| Denize Aparecida Graciano | 24203934 |
| Lucas Alves da Silva | 24219708 |
| Lucas Eduardo Rocha | 24217901 |
| Maria Benedita Pinheiro | 24223179 |
| Miúcha Carvalho Cicaroni | 23212531 |
| Yuri Liston | 24203775 |

**Orientador:** Thiago Vinicius Ribeiro Soeira — UNIVESP

---

*Disciplinas PJI110 — Projeto Integrador em Computação I e PJI240 — Projeto Integrador em Computação II, UNIVESP 2026.*
