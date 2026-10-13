#!/usr/bin/env bash
# VETSystem — mede Acessibilidade e Boas Práticas (Lighthouse) nas telas principais.
# Uso: scripts/lighthouse.sh <rotulo>  (com o servidor rodando em http://127.0.0.1:8000)
set -euo pipefail
cd "$(dirname "$0")/.."
ROTULO="${1:-medicao}"; SAIDA="docs/metricas/lighthouse/$ROTULO"; mkdir -p "$SAIDA"
SESSAO=$(.venv/bin/python manage.py shell --no-imports -c "
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
u = get_user_model().objects.filter(is_superuser=True).first()
s = SessionStore(); s[SESSION_KEY] = str(u.pk)
s[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
s[HASH_SESSION_KEY] = u.get_session_auth_hash(); s.create(); print(s.session_key)
" | tail -n 1)
ROTAS=(/ /login/ /dashboard/ /consultas/ /consultas/nova/ /animais/ /proprietarios/ /disponibilidade/ ${ROTAS_EXTRAS:-})
printf "| Tela | Acessibilidade | Boas práticas |\n|---|---|---|\n" > "$SAIDA/resumo.md"
for ROTA in "${ROTAS[@]}"; do
  NOME=$(echo "$ROTA" | sed 's#^/##; s#/$##; s#/#-#g'); NOME=${NOME:-home}
  npx --yes lighthouse "http://127.0.0.1:8000$ROTA" --only-categories=accessibility,best-practices \
    --preset=desktop --quiet --chrome-flags="--headless=new" \
    --extra-headers="{\"Cookie\":\"sessionid=$SESSAO\"}" \
    --output=json --output=html --output-path="$SAIDA/$NOME"
  node -e "const c=require('./$SAIDA/$NOME.report.json').categories;console.log('| $ROTA | '+Math.round(c.accessibility.score*100)+' | '+Math.round(c['best-practices'].score*100)+' |')" >> "$SAIDA/resumo.md"
done
cat "$SAIDA/resumo.md"
