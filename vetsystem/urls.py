"""
VETSystem — Sistema de Agendamento Veterinário
ATIVO PET | Projeto Integrador UNIVESP 2026 — PJI110

Arquivo : vetsystem/urls.py
Função  : Roteador principal do projeto. Conecta as URLs raiz do Django
          com as URLs de cada app instalado.

          Estrutura de rotas:
            /admin/          → Painel administrativo do Django
            /                → App agendamentos (rotas públicas e autenticadas)
            /login/          → Página de login (Django Auth embutido)
            /logout/         → Logout (Django Auth embutido)
            /api/            → API REST (Django REST Framework) — PI II
            /api/schema/     → Esquema OpenAPI 3 (drf-spectacular)
            /api/docs/       → Documentação interativa da API (Swagger UI)

Autor   : Lucas Eduardo Rocha (RA 24217901)
Data    : 2026-03-11
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [

    # --- Painel administrativo do Django ---
    # Acessível em /admin/ — usado pela Sra. Fernanda e pela equipe de dev
    path('admin/', admin.site.urls),

    # --- Autenticação (Django Auth embutido) ---
    # Login: exibe o formulário de login e processa a autenticação
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    # Logout: encerra a sessão e redireciona conforme LOGOUT_REDIRECT_URL no settings
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # --- API REST (PI II) e sua documentação OpenAPI/Swagger ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('agendamentos.api.urls')),

    # --- App de agendamentos ---
    # Inclui todas as URLs definidas em agendamentos/urls.py
    # O prefixo vazio '' significa que as rotas do app ficam na raiz do site
    # Ex: /proprietarios/, /animais/, /agendamentos/
    path('', include('agendamentos.urls')),

]

# --- Arquivos de mídia em desenvolvimento ---
# Em produção, o servidor web (nginx/Render) serve os arquivos de mídia.
# Em desenvolvimento, o Django serve diretamente via esta configuração.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
