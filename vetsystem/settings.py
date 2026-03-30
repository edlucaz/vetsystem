"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : vetsystem/settings.py
Função  : Configurações globais do projeto Django. Controla banco de dados,
          apps instalados, templates, arquivos estáticos, fuso horário,
          idioma e segurança. Este arquivo é o "painel de controle" do Django.

          Em produção (Railway), as variáveis sensíveis (SECRET_KEY, DATABASE_URL)
          são lidas do ambiente via python-decouple — nunca ficam hardcoded aqui.

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url

# --- Raiz do projeto ---
# BASE_DIR aponta para a pasta raiz do projeto (onde está o manage.py).
# Usamos ele para construir caminhos relativos de forma segura em qualquer SO.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SEGURANÇA
# =============================================================================

# Chave secreta usada pelo Django para criptografia interna (cookies, tokens, etc.).
# NUNCA deve ser exposta publicamente. Em produção, vem da variável de ambiente.
SECRET_KEY = config('SECRET_KEY', default='django-insecure-chave-local-apenas-para-dev')

# Modo de depuração — exibe erros detalhados no navegador.
# DEVE ser False em produção para não expor informações internas.
DEBUG = config('DEBUG', default=True, cast=bool)

# Lista de domínios/IPs autorizados a acessar o sistema.
# Em desenvolvimento: localhost. Em produção: domínio do Railway.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# =============================================================================
# APLICAÇÕES INSTALADAS
# =============================================================================

INSTALLED_APPS = [
    # --- Apps padrão do Django ---
    'django.contrib.admin',        # Painel administrativo em /admin
    'django.contrib.auth',         # Sistema de autenticação (login/logout/usuários)
    'django.contrib.contenttypes', # Framework de tipos de conteúdo (usado internamente)
    'django.contrib.sessions',     # Gerenciamento de sessões de usuário
    'django.contrib.messages',     # Sistema de mensagens flash (ex: "Salvo com sucesso!")
    'django.contrib.staticfiles',  # Gerenciamento de arquivos estáticos (CSS, JS, imagens)

    # --- Apps de terceiros ---
    'crispy_forms',        # Renderiza formulários Django com estilo automático
    'crispy_tailwind',     # Integra o crispy_forms com Tailwind CSS

    # --- App principal do VETSystem ---
    # Contém os models, views e formulários do sistema de agendamento da ATIVO PET
    'agendamentos',
]


# =============================================================================
# MIDDLEWARES
# =============================================================================

# Middlewares são camadas que processam cada requisição/resposta HTTP.
# Executados em ordem, do primeiro ao último na entrada, e inverso na saída.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # Cabeçalhos de segurança HTTP
    'whitenoise.middleware.WhiteNoiseMiddleware',               # Serve arquivos estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',     # Gerencia sessões de usuário
    'django.middleware.common.CommonMiddleware',                # Normaliza URLs (ex: adiciona barra final)
    'django.middleware.csrf.CsrfViewMiddleware',               # Proteção contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Associa usuários às requisições
    'django.contrib.messages.middleware.MessageMiddleware',    # Habilita mensagens flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Proteção contra clickjacking
]


# =============================================================================
# URLs
# =============================================================================

# Arquivo raiz de URLs — ponto de entrada para todas as rotas do sistema.
ROOT_URLCONF = 'vetsystem.urls'


# =============================================================================
# TEMPLATES (HTML)
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Pasta global de templates — onde fica o base.html compartilhado por todo o projeto.
        # Templates específicos de cada app ficam dentro da pasta do próprio app.
        'DIRS': [BASE_DIR / 'templates'],

        # Permite que o Django encontre templates dentro das pastas de cada app instalado.
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Necessário para o admin e login
                'django.contrib.auth.context_processors.auth', # Disponibiliza o usuário logado nos templates
                'django.contrib.messages.context_processors.messages', # Disponibiliza mensagens flash
            ],
        },
    },
]

# Ponto de entrada para servidores WSGI (usado em produção no Railway).
WSGI_APPLICATION = 'vetsystem.wsgi.application'


# =============================================================================
# BANCO DE DADOS
# =============================================================================

# Em desenvolvimento usamos SQLite (arquivo local, sem necessidade de instalar nada).
# Em produção no Railway, DATABASE_URL aponta para PostgreSQL automaticamente.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# =============================================================================
# VALIDAÇÃO DE SENHAS
# =============================================================================

# Regras de segurança para senhas dos usuários administrativos.
AUTH_PASSWORD_VALIDATORS = [
    # Impede senhas muito similares ao nome/email do usuário
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # Exige no mínimo 8 caracteres
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # Impede senhas comuns (ex: "123456", "password")
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # Impede senhas puramente numéricas
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNACIONALIZAÇÃO
# =============================================================================

# Idioma padrão do sistema — afeta o Django Admin e mensagens de erro dos forms.
LANGUAGE_CODE = 'pt-br'

# Fuso horário da ATIVO PET (Limeira/SP = horário de Brasília).
# Garante que datas e horas de agendamento sejam salvas corretamente.
TIME_ZONE = 'America/Sao_Paulo'

# Habilita tradução de textos do Django para o idioma definido acima.
USE_I18N = True

# Usa o fuso horário definido em TIME_ZONE para datas/horas no banco.
USE_TZ = True


# =============================================================================
# ARQUIVOS ESTÁTICOS (CSS, JS, Imagens)
# =============================================================================

# URL pública para acessar arquivos estáticos no navegador.
STATIC_URL = 'static/'

# Pastas onde o Django procura arquivos estáticos durante o desenvolvimento.
# O Tailwind CSS via CDN não precisa de pasta local, mas imagens e CSS customizado ficam aqui.
STATICFILES_DIRS = [BASE_DIR / 'static']

# Pasta de destino do comando 'collectstatic' (usado no deploy em produção).
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =============================================================================
# ARQUIVOS DE MÍDIA (uploads de usuários)
# =============================================================================

# URL pública para acessar arquivos enviados pelos usuários (ex: fotos de animais).
MEDIA_URL = '/media/'

# Pasta local onde os uploads são salvos. Ignorada pelo .gitignore.
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# CHAVE PRIMÁRIA PADRÃO
# =============================================================================

# Tipo de campo usado como chave primária automática nos models que não definem um.
# BigAutoField suporta valores maiores que o AutoField padrão (até 9.2 quintilhões).
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# CONFIGURAÇÃO DO CRISPY FORMS (formulários estilizados)
# =============================================================================

# Define o template pack usado pelo crispy_forms para renderizar os formulários.
# Como usamos Tailwind CSS, configuramos o pack correspondente.
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'


# =============================================================================
# AUTENTICAÇÃO — redirecionamentos
# =============================================================================

# Página para onde o usuário é redirecionado após fazer login com sucesso.
LOGIN_REDIRECT_URL = '/dashboard/'

# Página de login — usada quando uma view protegida exige autenticação.
LOGIN_URL = '/login/'

# Página para onde o usuário é redirecionado após fazer logout.
LOGOUT_REDIRECT_URL = '/login/'


# =============================================================================
# SEGURANÇA EM PRODUÇÃO
# =============================================================================
# Ativado apenas quando DEBUG=False (produção no Render).

if not DEBUG:
    # HTTPS — o Render termina SSL no proxy, então confiamos nos headers dele
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        f'https://{host}' for host in ALLOWED_HOSTS if host not in ('localhost', '127.0.0.1')
    ]
