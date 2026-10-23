# CLAUDE.md — VETSystem

Agendamentos da Clínica ATIVO PET (Django). Projeto Integrador II — UNIVESP.
Plano do PI II: `docs/PLANO_PI2.md` — execute uma fase por vez (`/fase-N`, effort já definido) e marque os checkboxes.

## Comandos (nesta pasta, sempre com o venv)
- Instalar: `.venv/bin/pip install -r requirements-dev.txt` (produção: `requirements.txt`)
- Servidor: `.venv/bin/python manage.py runserver`
- Testes: `.venv/bin/pytest` · cobertura: `.venv/bin/pytest --cov` · um teste: `.venv/bin/pytest agendamentos/tests/test_services.py::test_nome`
- Verificações: `.venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations --check --dry-run`
- Expediente padrão: `.venv/bin/python manage.py criar_horarios_padrao`
- Checklist teclado/375 px no Chrome: `.venv/bin/python scripts/checklist_automatico.py` · vídeo da parte técnica: `scripts/video/ROTEIRO.md`
- Dados demo: `.venv/bin/python manage.py popular_demo` · desempenho: `.venv/bin/python manage.py medir_desempenho` · Lighthouse: `scripts/lighthouse.sh antes|depois`

## Arquitetura
- App `agendamentos/`: models, forms, views (CBVs), templates. DER: Proprietario 1:N Animal 1:N Consulta N:1 Disponibilidade
  ("verifica" = FK `Consulta.disponibilidade`, preenchida em `Consulta.save()` pelo dia da semana);
  Animal 1:N RegistroPeso (histórico, gravado por `Animal.save()` via `services.registrar_peso`).
- `agendamentos/services.py` é a ÚNICA fonte das regras (horários livres, "Horário disponível?", status, estatísticas);
  formulários e API chamam essas funções — não duplique regras.
- `agendamentos/api/`: Django REST Framework, autenticação por sessão + CSRF, documentação em `/api/docs/`.
- `static/js/`: JavaScript puro consumindo `/api/`; melhoria progressiva (as telas funcionam sem JS).
- Produção: Render (web, `start.sh`) + Neon (PostgreSQL via `DATABASE_URL`); deploy automático a cada merge na `main`;
  CI em `.github/workflows/ci.yml`.

## Convenções
- Português em nomes e comentários; docstring de cabeçalho em cada arquivo (Arquivo/Função/Autor/Data), como nos existentes.
- Paleta acessível: turquesa #1E7579, roxo #4A2C7A, laranja #B9471A, fundo #F5F6F7, texto secundário `text-gray-600`
  (classes `ativo-*` do Tailwind). Gráficos: #6848A1.
- Dados da API entram no DOM só com `textContent`; datas locais com `VetAPI.dataIso()` (nunca `toISOString()`).
- Testes: datetimes com fuso (`agendamentos/tests/utils.py`); fixture `horario_comercial` recria a Disponibilidade.
- Git: branch `fase-N-nome` → PR → CI verde → merge.
