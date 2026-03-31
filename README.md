# VETSystem — Sistema de Agendamento Veterinário

> Projeto Integrador em Computação I (PJI110) — UNIVESP 2026
> Clínica ATIVO PET — Fisioterapia e Bem-Estar Animal, Limeira/SP

## Sobre o projeto

O VETSystem substitui o controle manual de agendamentos via WhatsApp da clínica ATIVO PET por uma solução web centralizada. A proprietária Sra. Fernanda Guevara pode cadastrar tutores, animais e consultas, gerenciar a agenda diária e configurar os horários de funcionamento da clínica, tudo pelo navegador.

**Sistema em produção:** https://vetsystem-gky6.onrender.com

## Funcionalidades

- Cadastro e busca de proprietários (tutores)
- Cadastro de animais vinculados aos tutores
- Agendamento de consultas com tipo (consulta, fisioterapia, acupuntura) e status
- Dashboard com agenda do dia e próximos 7 dias
- Configuração de horários de funcionamento por dia da semana
- Frontpage pública da ATIVO PET com CTA de agendamento
- Autenticação com login/logout

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Django 6.x |
| Frontend | Tailwind CSS via CDN |
| Formulários | django-crispy-forms + crispy-tailwind |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL (Render) |
| Deploy | Render (plano gratuito) |
| Servidor WSGI | Gunicorn |
| Estáticos | WhiteNoise |

## Estrutura do projeto

```
vetsystem/
├── agendamentos/               # App principal
│   ├── management/commands/    # Comandos customizados (criar_superusuario)
│   ├── migrations/             # Migrações do banco de dados
│   ├── templates/agendamentos/ # Templates HTML do app
│   ├── admin.py                # Configuração do Django Admin
│   ├── forms.py                # Formulários (Proprietario, Animal, Consulta, Disponibilidade)
│   ├── models.py               # Models (Proprietario, Animal, Consulta, Disponibilidade)
│   ├── urls.py                 # Rotas do app
│   └── views.py                # Views (CBVs)
├── templates/                  # Templates globais (base.html, home.html, dashboard.html)
├── static/                     # Arquivos estáticos (CSS, JS, imagens)
├── vetsystem/                  # Configurações do projeto Django
│   ├── settings.py             # Configurações (dev + produção)
│   ├── urls.py                 # Roteador principal
│   └── wsgi.py                 # Ponto de entrada WSGI
├── Procfile                    # Comando de inicialização (Render)
├── railway.json                # Configuração Railway (legado)
├── render.yaml                 # Configuração Render
├── requirements.txt            # Dependências Python
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

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env se necessário (a chave padrão funciona em desenvolvimento)

# 5. Execute as migrações
python manage.py migrate

# 6. Crie o superusuário
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

Acesse em: http://127.0.0.1:8000

## Variáveis de ambiente

| Variável | Descrição | Padrão (dev) |
|----------|-----------|--------------|
| `SECRET_KEY` | Chave secreta Django | chave insegura local |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL do banco de dados | SQLite local |
| `DJANGO_SUPERUSER_USERNAME` | Usuário admin (produção) | `fernanda` |
| `DJANGO_SUPERUSER_EMAIL` | E-mail admin (produção) | — |
| `DJANGO_SUPERUSER_PASSWORD` | Senha admin (produção) | — |

## Deploy (Render)

O projeto está configurado para deploy automático no Render via `render.yaml`.

1. Acesse dashboard.render.com → New → Blueprint
2. Conecte o repositório `edlucaz/vetsystem`
3. O Render cria automaticamente o web service + PostgreSQL gratuito
4. O `start.sh` executa migrações e cria o superusuário automaticamente

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
| `/consultas/` | Lista de consultas | Sim |
| `/disponibilidade/` | Horários de funcionamento | Sim |
| `/admin/` | Painel administrativo Django | Sim (staff) |

## Grupo

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

---

*Disciplina PJI110 — Projeto Integrador em Computação I, UNIVESP 2026.*
