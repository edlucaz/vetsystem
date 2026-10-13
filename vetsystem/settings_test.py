"""Configurações usadas apenas pelos testes automatizados (pytest)."""
from .settings import *  # noqa: F401,F403

# O cliente de testes usa HTTP: nada de redirecionar para HTTPS nem cookies "secure".
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# Hash de senha rápido — só para acelerar os testes.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
