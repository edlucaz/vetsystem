# Plano de melhorias do VETSystem — PI II (para executar com effort menor)

## Contexto

O relatório parcial do Grupo 8 descreve como **já prontos** itens que não existem no código: API REST com DRF, JavaScript consumindo a API, adequação WCAG e testes com Pytest. O professor pediu números concretos (endpoints, testes, tempos, validação com a clínica), menção a nuvem e Git, e análise de dados. O programa precisa ficar **fiel ao DER** (entidades + relacionamentos) **e ao fluxograma swimlane v2** (`/mnt/backup500gb/Lucas/UNIVESP/PI2/Fluxograma/Fluxograma 2/`). Este plano leva o código até lá em fases pequenas, cada uma executável em **uma sessão do Claude Code com effort baixo ou médio**. O código mais delicado já vem escrito aqui.

**Estado verificado em 13/10/2026**
- Django 6.0.3; app único `agendamentos` com 4 models e CRUD completo; `check` e migrações OK. **0 testes, sem DRF, sem API.** O JavaScript se limita ao IMask e à checagem de data passada.
- **Bugs de interface:**
  - `animal_list.html` tem atributos `class="style=..."` quebrados (cabeçalho da tabela com texto branco sem fundo).
  - As classes `ativo-*` não funcionam porque o Tailwind CDN está sem config: botões "Editar" e "+ Adicionar Animal" ficam brancos e sem fundo.
  - O menu some no celular.
  - "Cancelar consulta" **apaga** o registro.
  - O botão "Agendar Consulta" da home leva a uma tela que exige login.
  - O telefone da home está exibido errado: "(19) 99872-86814" deveria ser "(19) 98728-6814".
- **Contraste reprovado (mínimo 4,5:1):** turquesa #31A1A7 com branco 3,09:1; laranja #F26A2E 3,05:1; `text-gray-400` 2,54:1.
- **Configuração:** `STATICFILES_STORAGE` (`settings.py:185`) é ignorado desde o Django 5.1. O Django tem patch de segurança (6.0.9).
- **Segurança:** o repositório GitHub é **PÚBLICO** e o `render.yaml` versiona a senha do superusuário.
- **Produção:** o Postgres gratuito do Render expira em 30 dias e é apagado após mais 14. O banco de março já foi apagado e o site não respondeu.

## Decisões já tomadas
1. **Fidelidade aos modelos** significa mesmas entidades e mesmos relacionamentos. Os nomes dos atributos podem diferir.
   - "verifica" (Consulta N:1 Disponibilidade) vira a **FK real `Consulta.disponibilidade`**, preenchida automaticamente em `save()` a partir do dia da semana.
   - `Animal.idade` passa a ser `data_nascimento` (como no DER); a idade vira um valor calculado.
   - `tipo` e `dia_da_semana` continuam com esses nomes (equivalem a `tipo_atendimento`/`dia_semana`).
   - Os atributos extras do código (`peso`, `queixa`, `duracao_minutos`, `ativo`) ficam e entram no DER v3. A lista do que mudar nos diagramas sai na Fase 8.
2. **Banco de produção:** Neon (Postgres gratuito, sem expiração). O Django continua no Render.
3. **Opcionais incluídos:** análise de dados, aviso ao tutor pelo WhatsApp, agenda semanal e horários livres na página pública.
4. **JavaScript puro** (sem frameworks; Chart.js só nos gráficos), com melhoria progressiva: toda tela continua funcionando sem JS.
5. **Testes** com pytest + pytest-django. **CI** no GitHub Actions rodando em PostgreSQL 16.

---

## Como executar cada fase

Cada fase tem um comando próprio, **`/fase-N`** (em `.claude/skills/fase-N/SKILL.md`). Ele já traz o prompt da fase e **define o effort sozinho** (`effort:` no cabeçalho), então não é preciso rodar `/effort`.

**Como usar:**
1. Abra o Claude Code em `/mnt/backup500gb/Projetos/Web/vetsystem`.
2. Digite `/clear` para começar sem o histórico da fase anterior.
3. Digite `/fase-N`. O Claude executa a fase até o merge.
4. Se ele parar num passo **[VOCÊ]**, faça o que foi pedido e responda com **`/fase-N <sua resposta>`** (ex.: `/fase-6 checklist feito, tudo ok`).
   - Assim a resposta continua no effort da fase. Uma resposta comum, sem o comando, volta ao effort da sessão.
5. Confira o resultado e passe para a próxima fase (volte ao passo 2).

**Passo a passo por etapa:**

| Etapa | Comando | Effort | O que você faz durante a fase |
|---|---|---|---|
| Fase 0 — Preparação | (concluída) | low | Mover o `.deb` para `~/Downloads/`; trocar a senha antiga onde mais tiver sido usada |
| Fase 1 — Neon + Render | `/fase-1` | low | 1.1 criar o banco no Neon; 1.2 configurar o Render (`DATABASE_URL`, senha nova) e publicar; depois `/fase-1 terminei` para o Claude verificar; entrar como `fernanda` |
| Fase 2 — Testes, CI, regras, DER | `/fase-2` | medium | Nada; só conferir o PR |
| Fase 3 — Telas pelo fluxograma | `/fase-3` | medium | Nada; só conferir o PR |
| Fase 4 — API REST + Swagger | `/fase-4` | medium | Nada; só conferir o PR |
| Fase 5 — Acessibilidade | `/fase-5` | medium | Checklist de teclado (Tab/Shift+Tab/Enter/Esc; menu no celular a 375 px) |
| Fase 6 — JavaScript | `/fase-6` | medium | 6.10 checklist manual em `docs/metricas/checklist_manual.md` |
| Fase 6B — Modal tutor/animal + histórico de peso | `/fase-6b` | medium | Nada; só conferir o PR (o teclado do modal entra no checklist do 6.10) |
| Fase 7 — Extras | `/fase-7` | medium | Decidir se roda `popular_demo --forcar` em produção para a apresentação |
| Fase 8 — Métricas e release | `/fase-8` | low | 8.4 validação com a Sra. Fernanda (tarefas cronometradas + SUS); atualizar DER e fluxograma conforme o Apêndice A |

**Prompt usado pelos comandos** (para colar à mão, se preferir, trocando N):

> Leia `docs/PLANO_PI2.md` e o `CLAUDE.md`. Execute **somente a Fase N**, na ordem dos passos, sem acrescentar nada fora do escopo. Quando o plano trouxer código, use-o como está. Passos marcados **[VOCÊ]** são meus: pare e me peça. Ao terminar, rode as verificações da fase, registre falhas de teste e correções em `docs/metricas/registro_testes.md`, marque os checkboxes da fase no plano, faça commit, push e abra o PR. Aguarde o CI ficar verde e faça o merge.

**Fluxo Git de toda fase com código** (atende ao pedido de controle de versão):
```bash
git switch main && git pull
git switch -c fase-N-nome
# ... passos da fase ...
.venv/bin/pytest            # a partir da Fase 2
.venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations --check --dry-run
git add -A && git commit    # mensagens no padrão já usado: feat:, fix:, chore:, test:, docs:
git push -u origin fase-N-nome
gh pr create --fill
gh pr checks --watch        # espera o CI (a partir da Fase 2)
gh pr merge --merge --delete-branch
git switch main && git pull # o Render publica sozinho a main
```

**Regras para quem executa** (erros comuns com effort baixo):
- Nunca rode `makemigrations` interativo. Escreva as migrações fornecidas e confirme com `makemigrations --check --dry-run` ("No changes detected").
- Nos testes, sempre use datetimes com fuso (`em()` em `agendamentos/tests/utils.py`). A fixture `horario_comercial` apaga e recria a Disponibilidade, que é única por dia.
- No JS:
  - Dados vindos da API só entram no DOM com `textContent`, nunca com `innerHTML`.
  - Datas locais sempre com `VetAPI.dataIso()`, nunca com `toISOString()` (que converte para UTC).
- Use só as cores da paleta (Apêndice C).
- Não commite `.env`, `db.sqlite3` nem os relatórios brutos do Lighthouse.
- Se algo não previsto quebrar, pare e explique em vez de improvisar.

| Fase | Entrega | Quem | Effort (automático) | Branch |
|---|---|---|---|---|
| 0 | Preparação: segurança, limpeza, linha de base ("antes") | Claude + [VOCÊ] | low | `fase-0-preparacao` |
| 1 | Nuvem: Neon + Render no ar | [VOCÊ] (Claude verifica) | low | `fase-1-nuvem` (só checkboxes) |
| 2 | Testes + CI + regras de negócio + modelo fiel ao DER | Claude | medium | `fase-2-regras-e-testes` |
| 3 | Telas Django seguindo o fluxograma | Claude | medium | `fase-3-fluxo-telas` |
| 4 | API REST (DRF) + Swagger | Claude | medium | `fase-4-api-rest` |
| 5 | Acessibilidade WCAG 2.1 AA | Claude | medium | `fase-5-acessibilidade` |
| 6 | JavaScript do fluxo de agendamento | Claude | medium | `fase-6-javascript` |
| 6B | Seleção de tutor/animal em modal com abas + histórico de peso | Claude | medium | `fase-6b-selecao-e-peso` |
| 7 | Extras: análise de dados, agenda semanal, home pública, dados demo | Claude | medium | `fase-7-extras` |
| 8 | Métricas finais, documentação, diagramas, release | Claude + [VOCÊ] | low | `fase-8-entrega` |

---

## Fase 0 — Preparação (segurança, limpeza, linha de base)

- [x] **0.1 Plano no repositório.** Copie este arquivo para `docs/PLANO_PI2.md`. É ele que as próximas sessões vão ler.
- [x] **0.2 Marque o fim do PI1:**
  ```bash
  git tag -a v1.0-pi1 3ac86f1 -m "VETSystem — entrega final do PI1"
  git push origin v1.0-pi1
  ```
- [x] **0.3** `git switch -c fase-0-preparacao`. As alterações não commitadas atuais (IMask, data/hora separados, logout por POST) entram neste branch.
- [x] **0.4 Limpeza:**
  - **[VOCÊ]** mova `obs-backgroundremoval-1.1.10-x86_64-linux-gnu.deb` (164 MB, não versionado) para `~/Downloads/`.
  - `git rm agendamentos/urls.py.save files.zip railway.json`
  - `git mv files docs/pi1-fluxogramas`
  - Acrescente ao `.gitignore`:
    ```
    *.deb
    .pytest_cache/
    coverage.xml
    docs/metricas/lighthouse/**/*.report.*
    ```
- [x] **0.5 Segurança do `render.yaml`.** Substitua o arquivo inteiro por:
  ```yaml
  # render.yaml — Deploy do VETSystem no Render (plano gratuito)
  # Banco PostgreSQL: Neon (gratuito, sem expiração). DATABASE_URL e a senha do
  # superusuário são definidas no painel do Render — NUNCA versione senhas.
  services:
    - type: web
      name: vetsystem
      runtime: python
      plan: free
      buildCommand: "pip install -r requirements.txt"
      startCommand: "bash start.sh"
      envVars:
        - key: SECRET_KEY
          generateValue: true
        - key: DEBUG
          value: "False"
        - key: ALLOWED_HOSTS
          value: "vetsystem-gky6.onrender.com"
        - key: DATABASE_URL
          sync: false
        - key: PYTHON_VERSION
          value: "3.12.0"
        - key: DJANGO_SUPERUSER_USERNAME
          value: "fernanda"
        - key: DJANGO_SUPERUSER_EMAIL
          value: "admin@ativamente.vet.br"
        - key: DJANGO_SUPERUSER_PASSWORD
          sync: false
  ```
  **[VOCÊ]** A senha antiga é pública: não a use em mais nada e troque-a onde mais tiver sido usada. A nova senha é definida na Fase 1.
- [x] **0.6 `vetsystem/settings.py`:**
  - Troque "Railway" por "Render" nos comentários (linhas 10, 40, 119, 128). Faça o mesmo em `vetsystem/urls.py:54`.
  - Em `DATABASES` (linha ~129), acrescente `conn_health_checks=True,` depois de `conn_max_age=600,`, com o comentário `# o Neon suspende o banco ocioso; revalida a conexão antes de usar`.
  - Substitua a linha 185 (`STATICFILES_STORAGE = ...`) por:
    ```python
    # STATICFILES_STORAGE foi removido no Django 5.1 — o equivalente atual é STORAGES.
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
    }
    ```
- [x] **0.7 `requirements.txt`** (pins do venv + patch de segurança do Django). Depois rode `.venv/bin/pip install -r requirements.txt`.
  ```
  asgiref==3.11.1
  crispy-tailwind==1.0.3
  dj-database-url==3.1.2
  Django==6.0.9
  django-crispy-forms==2.6
  gunicorn==25.3.0
  pillow==12.1.1
  psycopg2-binary==2.9.11
  python-decouple==3.8
  sqlparse==0.5.5
  whitenoise==6.12.0
  ```
- [x] **0.8 Crie `CLAUDE.md`** na raiz do projeto, seguindo o padrão do `Web/CLAUDE.md`:
  ```markdown
  # CLAUDE.md — VETSystem

  Agendamentos da Clínica ATIVO PET (Django). Projeto Integrador II — UNIVESP.
  Plano do PI II: `docs/PLANO_PI2.md` — execute uma fase por vez e marque os checkboxes.

  ## Comandos (nesta pasta, sempre com o venv)
  - Instalar: `.venv/bin/pip install -r requirements-dev.txt` (produção: `requirements.txt`)
  - Servidor: `.venv/bin/python manage.py runserver`
  - Testes: `.venv/bin/pytest` · cobertura: `.venv/bin/pytest --cov` · um teste: `.venv/bin/pytest agendamentos/tests/test_services.py::test_nome`
  - Verificações: `.venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations --check --dry-run`
  - Expediente padrão: `.venv/bin/python manage.py criar_horarios_padrao`

  ## Arquitetura
  - App `agendamentos/`: models, forms, views (CBVs), templates. DER: Proprietario 1:N Animal 1:N Consulta N:1 Disponibilidade
    ("verifica" = FK `Consulta.disponibilidade`, preenchida em `Consulta.save()` pelo dia da semana).
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
  ```
- [x] **0.9 Linha de base ("antes"), sem mexer em nenhuma tela.**
  1. Crie `scripts/lighthouse.sh` com o conteúdo abaixo e rode `chmod +x scripts/lighthouse.sh`:
     ```bash
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
     ```
  2. Suba o servidor em segundo plano (`.venv/bin/python manage.py runserver 127.0.0.1:8000`), rode `scripts/lighthouse.sh antes` e encerre o servidor depois.
     - Se o `npx`/Chrome falhar: **[VOCÊ]** abra cada tela no Chrome → DevTools → Lighthouse → modo "Desktop" → categoria Acessibilidade, e anote as notas.
  3. Prove a falha do PI1 sem gravar nada. Rode no `manage.py shell` e anote o resultado:
     ```python
     from agendamentos.forms import ConsultaForm
     from agendamentos.models import Animal
     a = Animal.objects.first()
     dados = {'animal': a.pk, 'data_consulta': '2030-01-07', 'hora_consulta': '10:00', 'tipo': 'consulta', 'status': 'agendado'}
     print(ConsultaForm(dados).is_valid())
     # → True: o PI1 não verifica a Disponibilidade nem conflitos de horário
     ```
  4. Crie `docs/metricas/linha_de_base_pi1.md` com:
     - **Testes automatizados:** 0.
     - **Endpoints de API:** 0.
     - **Contraste:** turquesa 3,09:1; laranja 3,05:1; cinza secundário 2,54:1; branco 70% sobre turquesa 2,27:1 (mínimo AA: 4,5:1).
     - **Bugs:** botões e cabeçalhos invisíveis (classes `ativo-*` sem efeito); menu inexistente no celular.
     - **Regra de agendamento:** aceitava datas fora do expediente e conflitos (resultado do passo 3).
     - **Recarregamentos de página para agendar:** tutor já cadastrado = 2 (formulário + lista); tutor novo = 6 (cadastro do tutor, lista, cadastro do animal, lista, consulta, lista).
     - **Lighthouse:** cole o `resumo.md`.
  5. Crie `docs/metricas/registro_testes.md` com o título "Registro de falhas de teste e correções" e uma tabela vazia `| Data | Fase | Teste/erro | Causa | Correção |`.
- [x] **0.10 Verificação:** `check`, `makemigrations --check --dry-run` e `collectstatic --noinput` sem erros. Depois: commit, push e PR. Ainda não há CI, então faça o merge após conferir.
  - Depois do merge, o Render vai tentar publicar e falhar por falta de banco. Isso é esperado até a Fase 1.
- [ ] **0.11 (opcional, confirme antes)** O branch remoto `master` só tem o commit inicial: `git push origin --delete master`.

## Fase 1 — Nuvem: Neon + Render (passos [VOCÊ]; o Claude só verifica)

- [x] **1.1 [VOCÊ] Neon** (neon.tech, entre com o GitHub):
  - Crie o projeto **vetsystem**, região **AWS US West 2 (Oregon)** — a mesma região do Render.
  - Em **Connect**, desligue "Connection pooling" e copie a string `postgresql://…neon.tech/neondb?sslmode=require…`.
  - Se aparecer o erro `channel_binding`, apague `&channel_binding=require` da string.
- [x] **1.2 [VOCÊ] Render → serviço `vetsystem` → Environment:**
  - `DATABASE_URL` = string do Neon.
  - `DJANGO_SUPERUSER_PASSWORD` = **senha nova e forte** (do gerenciador de senhas).
  - Confira `SECRET_KEY`, `ALLOWED_HOSTS` e `DEBUG=False`.
  - Em **Settings**, confirme *Auto-Deploy: On Commit* no branch `main`.
  - **Manual Deploy → Deploy latest commit.**
  - Se houver um Postgres antigo/expirado listado no Render, apague-o.
- [x] **1.3 Se o serviço web não existir mais:** crie um Web Service a partir do repositório (ou New → Blueprint usando o `render.yaml`). Se o domínio mudar, atualize `ALLOWED_HOSTS` (no `render.yaml` e no default do `settings.py`) e o README.
- [x] **1.4 Verificação (Claude):** `curl -s -o /dev/null -w "%{http_code}\n" --max-time 120 https://vetsystem-gky6.onrender.com/login/` deve responder 200. O primeiro acesso demora cerca de 1 min, porque o plano gratuito "dorme" após 15 min.
  - Nos logs do Render deve aparecer "Rodando migrações… Criando superusuário…".
  - **[VOCÊ]** entre como `fernanda` com a senha nova e passe-a à Sra. Fernanda por um canal privado.
- [x] **1.5** Para a apresentação: abra o site 2 minutos antes, por causa do "sono" do plano gratuito.

## Fase 2 — Testes, CI, regras de negócio e modelo fiel ao DER

- [x] **2.1 Dependências de teste.**
  - Crie `requirements-dev.txt`:
    ```
    -r requirements.txt
    pytest==9.1.1
    pytest-django==4.14.0
    pytest-cov==7.1.0
    ```
  - Instale com `.venv/bin/pip install -r requirements-dev.txt`.
- [x] **2.2 Configuração dos testes.**
  - `pytest.ini`:
    ```ini
    [pytest]
    DJANGO_SETTINGS_MODULE = vetsystem.settings_test
    python_files = test_*.py
    testpaths = agendamentos/tests
    addopts = -q
    ```
  - `.coveragerc`:
    ```ini
    [run]
    source = agendamentos
    omit =
        agendamentos/migrations/*
        agendamentos/tests/*

    [report]
    show_missing = True
    ```
  - `vetsystem/settings_test.py`:
    ```python
    """Configurações usadas apenas pelos testes automatizados (pytest)."""
    from .settings import *  # noqa: F401,F403

    # O cliente de testes usa HTTP: nada de redirecionar para HTTPS nem cookies "secure".
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    # Hash de senha rápido — só para acelerar os testes.
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
    ```
- [x] **2.3 Pacote de testes.** Crie `agendamentos/tests/__init__.py` (vazio) e os dois arquivos abaixo.
  - `agendamentos/tests/utils.py`:
    ```python
    """Auxiliares de data dos testes — sempre datetimes com o fuso da clínica."""
    import datetime

    from django.utils import timezone


    def proxima_data(dia_semana, semanas=1):
        """Próxima data estritamente futura do dia da semana pedido (0 = segunda)."""
        hoje = timezone.localdate()
        dias = (dia_semana - hoje.weekday()) % 7 or 7
        return hoje + datetime.timedelta(days=dias + 7 * (semanas - 1))


    def em(data, hora, minuto=0):
        """Datetime 'aware' (America/Sao_Paulo) para a data e hora informadas."""
        return timezone.make_aware(datetime.datetime.combine(data, datetime.time(hora, minuto)))
    ```
  - `agendamentos/tests/conftest.py`:
    ```python
    """Fixtures compartilhadas pelos testes do VETSystem (pytest-django)."""
    import datetime

    import pytest

    from agendamentos.models import Animal, Consulta, Disponibilidade, Proprietario
    from agendamentos.tests.utils import em, proxima_data


    @pytest.fixture
    def usuario(django_user_model):
        return django_user_model.objects.create_user(username='fernanda', password='senha-de-teste-123')


    @pytest.fixture
    def cliente_logado(client, usuario):
        client.force_login(usuario)
        return client


    @pytest.fixture
    def horario_comercial(db):
        """Expediente padrão da ATIVO PET: segunda a sexta, 08:00–19:00."""
        Disponibilidade.objects.all().delete()
        return [Disponibilidade.objects.create(dia_da_semana=dia, hora_inicio=datetime.time(8),
                                               hora_fim=datetime.time(19)) for dia in range(5)]


    @pytest.fixture
    def proprietario(db):
        return Proprietario.objects.create(nome='João Silva', telefone='(19) 99999-9999')


    @pytest.fixture
    def animal(proprietario):
        return Animal.objects.create(nome='Rex', especie='cao', proprietario=proprietario)


    @pytest.fixture
    def segunda():
        return proxima_data(0)


    @pytest.fixture
    def consulta_futura(horario_comercial, animal, segunda):
        return Consulta.objects.create(animal=animal, data_hora=em(segunda, 10), tipo='fisioterapia')
    ```
- [x] **2.4 `agendamentos/models.py`:**
  - Acrescente `from urllib.parse import quote` aos imports.
  - Atualize a docstring do módulo: relacionamento "verifica" e `data_nascimento`.
  - **Animal:** troque o campo `idade` (linha ~130) por:
    ```python
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de nascimento',
        help_text='Se não souber a data exata, informe uma aproximada.',
    )
    ```
    e acrescente, depois do `__str__` de Animal:
    ```python
    @property
    def idade(self):
        """Idade em anos completos, calculada a partir de data_nascimento (None se não informada)."""
        if not self.data_nascimento:
            return None
        hoje = timezone.localdate()
        nasc = self.data_nascimento
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

    @property
    def idade_formatada(self):
        """Texto para as telas: '3 anos', '1 ano', '7 meses' ou '—'."""
        if not self.data_nascimento:
            return '—'
        anos = self.idade
        if anos >= 1:
            return '1 ano' if anos == 1 else f'{anos} anos'
        hoje = timezone.localdate()
        nasc = self.data_nascimento
        meses = max((hoje.year - nasc.year) * 12 + hoje.month - nasc.month - (hoje.day < nasc.day), 0)
        return '1 mês' if meses == 1 else f'{meses} meses'
    ```
  - **Consulta:** acrescente, depois de `duracao_minutos` (linha ~251):
    ```python
    # Relacionamento "verifica" do DER (Consulta N:1 Disponibilidade).
    # Preenchido automaticamente em save() com a Disponibilidade do dia da semana.
    disponibilidade = models.ForeignKey(
        'Disponibilidade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='consultas',
        verbose_name='Disponibilidade verificada',
    )
    ```
    e acrescente, depois de `is_futuro`:
    ```python
    def save(self, *args, **kwargs):
        """Liga a consulta à Disponibilidade do seu dia da semana (relacionamento "verifica")."""
        if self.data_hora:
            data_hora = self.data_hora
            if timezone.is_naive(data_hora):
                data_hora = timezone.make_aware(data_hora)
            dia = timezone.localtime(data_hora).weekday()
            self.disponibilidade = Disponibilidade.objects.filter(dia_da_semana=dia).first()
        super().save(*args, **kwargs)

    @property
    def link_whatsapp(self):
        """
        Link wa.me com a mensagem de confirmação para o tutor (fluxograma:
        "Confirmar agendamento — avisa o tutor"). Vazio se o telefone for inválido.
        """
        digitos = ''.join(c for c in self.animal.proprietario.telefone if c.isdigit())
        if len(digitos) in (10, 11):  # DDD + número: acrescenta o código do Brasil
            digitos = '55' + digitos
        if len(digitos) not in (12, 13):
            return ''
        local = timezone.localtime(self.data_hora)
        mensagem = (
            f'Olá, {self.animal.proprietario.nome}! Confirmamos o atendimento de '
            f'{self.animal.nome} ({self.get_tipo_display().lower()}) na ATIVO PET em '
            f'{local:%d/%m/%Y} às {local:%H:%M}. Endereço: Av. Maria Thereza Silveira de '
            f'Barros Camargo, 1525 — Limeira/SP. Qualquer dúvida, é só responder esta mensagem.'
        )
        return f'https://wa.me/{digitos}?text={quote(mensagem)}'
    ```
- [x] **2.5 Migrações escritas à mão** (não use o `makemigrations` interativo).
  - `agendamentos/migrations/0002_consulta_disponibilidade.py`:
    ```python
    """Relacionamento "verifica" do DER: FK Consulta → Disponibilidade, preenchida pelo dia da semana."""
    import django.db.models.deletion
    from django.db import migrations, models
    from django.utils import timezone


    def vincular_disponibilidade(apps, schema_editor):
        Consulta = apps.get_model('agendamentos', 'Consulta')
        Disponibilidade = apps.get_model('agendamentos', 'Disponibilidade')
        por_dia = {d.dia_da_semana: d for d in Disponibilidade.objects.all()}
        for consulta in Consulta.objects.all():
            consulta.disponibilidade = por_dia.get(timezone.localtime(consulta.data_hora).weekday())
            consulta.save(update_fields=['disponibilidade'])


    class Migration(migrations.Migration):
        dependencies = [('agendamentos', '0001_initial')]

        operations = [
            migrations.AddField(
                model_name='consulta',
                name='disponibilidade',
                field=models.ForeignKey(
                    blank=True, editable=False, null=True,
                    on_delete=django.db.models.deletion.SET_NULL, related_name='consultas',
                    to='agendamentos.disponibilidade', verbose_name='Disponibilidade verificada'),
            ),
            migrations.RunPython(vincular_disponibilidade, migrations.RunPython.noop),
        ]
    ```
  - `agendamentos/migrations/0003_animal_data_nascimento.py`:
    ```python
    """DER: Animal guarda data_nascimento (a idade passa a ser calculada)."""
    import datetime

    from django.db import migrations, models


    def idade_para_data_nascimento(apps, schema_editor):
        """Converte a idade (anos) em data aproximada: mesmo dia e mês de hoje."""
        Animal = apps.get_model('agendamentos', 'Animal')
        hoje = datetime.date.today()
        for animal in Animal.objects.exclude(idade__isnull=True):
            ano = hoje.year - animal.idade
            try:
                animal.data_nascimento = hoje.replace(year=ano)
            except ValueError:  # 29/02 em ano não bissexto
                animal.data_nascimento = hoje.replace(year=ano, day=28)
            animal.save(update_fields=['data_nascimento'])


    def data_nascimento_para_idade(apps, schema_editor):
        Animal = apps.get_model('agendamentos', 'Animal')
        hoje = datetime.date.today()
        for animal in Animal.objects.exclude(data_nascimento__isnull=True):
            nasc = animal.data_nascimento
            animal.idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
            animal.save(update_fields=['idade'])


    class Migration(migrations.Migration):
        dependencies = [('agendamentos', '0002_consulta_disponibilidade')]

        operations = [
            migrations.AddField(
                model_name='animal',
                name='data_nascimento',
                field=models.DateField(
                    blank=True, null=True, verbose_name='Data de nascimento',
                    help_text='Se não souber a data exata, informe uma aproximada.'),
            ),
            migrations.RunPython(idade_para_data_nascimento, data_nascimento_para_idade),
            migrations.RemoveField(model_name='animal', name='idade'),
        ]
    ```
  - Rode `migrate` e depois `makemigrations --check --dry-run`, que deve responder "No changes detected".
- [x] **2.6 Crie `agendamentos/services.py`** (cabeçalho no padrão do projeto):
  ```python
  """
  VETSystem — Sistema de Agendamento Veterinário
  ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II

  Arquivo : agendamentos/services.py
  Função  : Regras de negócio do agendamento, usadas pelos formulários (telas
            Django) e pela API REST — uma única fonte de verdade para:
              - "Consultar horários livres" (fluxograma, etapa 3);
              - "Horário disponível?" (fluxograma, decisão 5): data futura +
                Disponibilidade do dia + sem conflito;
              - "Confirmar agendamento" / "Atualizar status" (fluxograma, final).

  Autor   : Lucas Eduardo Rocha (RA 24217901)
  Data    : <data de hoje>
  """

  import datetime

  from django.core.exceptions import ValidationError
  from django.utils import timezone

  from .models import Consulta, Disponibilidade

  INTERVALO_GRADE_MINUTOS = 30   # de quanto em quanto tempo a agenda oferece horários
  DURACAO_PADRAO_MINUTOS = 60    # duração padrão das sessões da ATIVO PET

  NOMES_DIAS = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira',
                'sexta-feira', 'sábado', 'domingo']

  # Transições das ações rápidas (fluxograma: confirmar; realizar atendimento ou
  # registrar ausência). A edição completa da consulta ainda corrige qualquer status.
  TRANSICOES_STATUS = {
      'agendado': {'confirmado', 'realizado', 'cancelado'},
      'confirmado': {'realizado', 'cancelado'},
      'realizado': set(),
      'cancelado': set(),
  }


  def validar_telefone(telefone):
      """Exige ao menos 8 dígitos; devolve o telefone sem espaços nas pontas."""
      telefone = (telefone or '').strip()
      if len([c for c in telefone if c.isdigit()]) < 8:
          raise ValidationError('Telefone inválido. Informe pelo menos 8 dígitos.', code='telefone')
      return telefone


  def validar_data_nascimento(data):
      if data and data > timezone.localdate():
          raise ValidationError('A data de nascimento não pode estar no futuro.', code='nascimento_futuro')
      return data


  def _no_fuso(data, hora):
      """Combina date + time num datetime com o fuso da clínica (America/Sao_Paulo)."""
      return timezone.make_aware(datetime.datetime.combine(data, hora))


  def _intervalo(consulta):
      inicio = timezone.localtime(consulta.data_hora)
      return inicio, inicio + datetime.timedelta(minutes=consulta.duracao_minutos)


  def disponibilidade_do_dia(data):
      """Disponibilidade ATIVA do dia da semana de `data`, ou None se a clínica não atende."""
      return Disponibilidade.objects.filter(dia_da_semana=data.weekday(), ativo=True).first()


  def consultas_que_ocupam(data, ignorar_id=None):
      """Consultas do dia que ocupam a agenda (as canceladas liberam o horário)."""
      consultas = (Consulta.objects.filter(data_hora__date=data)
                   .exclude(status='cancelado').select_related('animal'))
      if ignorar_id:
          consultas = consultas.exclude(pk=ignorar_id)
      return consultas


  def horarios_livres(data, duracao=DURACAO_PADRAO_MINUTOS, ignorar_id=None):
      """
      Fluxograma, etapa 3 — "Consultar horários livres" (Consulta × Disponibilidade).
      Inícios possíveis (datetimes no fuso da clínica), a cada INTERVALO_GRADE_MINUTOS,
      que cabem no expediente, estão no futuro e não se sobrepõem a outra consulta.
      """
      disponibilidade = disponibilidade_do_dia(data)
      if disponibilidade is None:
          return []
      abertura = _no_fuso(data, disponibilidade.hora_inicio)
      fechamento = _no_fuso(data, disponibilidade.hora_fim)
      ocupados = [_intervalo(c) for c in consultas_que_ocupam(data, ignorar_id)]
      agora = timezone.now()
      duracao_td = datetime.timedelta(minutes=duracao)
      passo = datetime.timedelta(minutes=INTERVALO_GRADE_MINUTOS)

      livres = []
      inicio = abertura
      while inicio + duracao_td <= fechamento:
          fim = inicio + duracao_td
          conflita = any(inicio < ocupado_fim and ocupado_inicio < fim
                         for ocupado_inicio, ocupado_fim in ocupados)
          if inicio > agora and not conflita:
              livres.append(inicio)
          inicio += passo
      return livres


  def validar_agendamento(data_hora, duracao=DURACAO_PADRAO_MINUTOS, ignorar_id=None):
      """
      Fluxograma, decisão 5 — "Horário disponível?".
      Lança ValidationError com mensagem para o usuário; se estiver tudo certo,
      devolve a Disponibilidade que "verifica" a consulta (relacionamento do DER).
      """
      if data_hora <= timezone.now():
          raise ValidationError('A data e hora do agendamento devem ser no futuro.', code='passado')

      inicio = timezone.localtime(data_hora)
      fim = inicio + datetime.timedelta(minutes=duracao)
      disponibilidade = disponibilidade_do_dia(inicio.date())
      if disponibilidade is None:
          raise ValidationError(
              f'A clínica não atende neste dia ({NOMES_DIAS[inicio.weekday()]}).', code='dia_fechado')

      abertura = _no_fuso(inicio.date(), disponibilidade.hora_inicio)
      fechamento = _no_fuso(inicio.date(), disponibilidade.hora_fim)
      if inicio < abertura or fim > fechamento:
          raise ValidationError(
              f'Horário fora do expediente: {disponibilidade.hora_inicio:%H:%M} às '
              f'{disponibilidade.hora_fim:%H:%M}.', code='fora_do_expediente')

      for consulta in consultas_que_ocupam(inicio.date(), ignorar_id):
          outro_inicio, outro_fim = _intervalo(consulta)
          if inicio < outro_fim and outro_inicio < fim:
              raise ValidationError(
                  f'Conflito de horário com a consulta de {consulta.animal.nome} '
                  f'às {outro_inicio:%H:%M}.', code='conflito')
      return disponibilidade


  def atualizar_status(consulta, novo_status, observacao=''):
      """Fluxograma — "Confirmar agendamento" e "Atualizar status (realizado/cancelado)"."""
      if novo_status not in TRANSICOES_STATUS.get(consulta.status, set()):
          rotulos = dict(Consulta.STATUS_CHOICES)
          raise ValidationError(
              f'Não é possível mudar de "{rotulos[consulta.status]}" para '
              f'"{rotulos.get(novo_status, novo_status)}".', code='transicao_invalida')
      consulta.status = novo_status
      observacao = (observacao or '').strip()
      if observacao:
          carimbo = timezone.localtime().strftime('%d/%m/%Y %H:%M')
          linha = f'[{carimbo}] {observacao}'
          consulta.observacoes = f'{consulta.observacoes}\n{linha}' if consulta.observacoes else linha
      consulta.save(update_fields=['status', 'observacoes'])
      return consulta
  ```
- [x] **2.7 `agendamentos/forms.py`.** Imports no topo:
  ```python
  import datetime
  from django.utils import timezone
  from .services import DURACAO_PADRAO_MINUTOS, validar_agendamento, validar_data_nascimento, validar_telefone
  ```
  Remova os imports de dentro dos métodos. Depois:
  - `ProprietarioForm.clean_telefone` passa a ser só `return validar_telefone(self.cleaned_data.get('telefone'))`. A docstring curta pode ficar.
  - **AnimalForm:**
    - Em `fields`, troque `'idade'` por `'data_nascimento'`.
    - Widget: `'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})`, removendo o widget de `idade`.
    - No `__init__`: `self.fields['data_nascimento'].widget.attrs['max'] = timezone.localdate().isoformat()`.
    - No Layout, troque `Field('idade')` por `Field('data_nascimento')`.
    - Acrescente:
      ```python
      def clean_data_nascimento(self):
          return validar_data_nascimento(self.cleaned_data.get('data_nascimento'))
      ```
  - **ConsultaForm:** substitua `__init__` e `clean` por:
    ```python
    def __init__(self, *args, **kwargs):
        # animal_pk pode vir da URL (?animal=1) para pré-selecionar o animal
        animal_pk = kwargs.pop('animal_pk', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # Evita uma consulta extra por opção (Animal.__str__ usa o nome do tutor)
        self.fields['animal'].queryset = Animal.objects.select_related('proprietario').order_by('nome')

        if self.instance.pk is None:
            # Fluxograma: "Registrar consulta — status: agendado" — na criação o status não é escolhido
            del self.fields['status']
            self.fields['data_consulta'].widget.attrs['min'] = timezone.localdate().isoformat()
        if animal_pk:
            self.fields['animal'].initial = animal_pk
        if self.instance.pk and self.instance.data_hora:
            dt_local = timezone.localtime(self.instance.data_hora)
            self.fields['data_consulta'].initial = dt_local.date()
            self.fields['hora_consulta'].initial = dt_local.strftime('%H:%M')

    def clean(self):
        """
        Combina data + hora em data_hora e aplica a decisão "Horário disponível?"
        (mesma regra da API) na criação ou quando a data/hora foi alterada.
        """
        cleaned = super().clean()
        data = cleaned.get('data_consulta')
        hora = cleaned.get('hora_consulta')
        if data and hora:
            data_hora = timezone.make_aware(datetime.datetime.combine(data, hora))
            mudou_horario = (self.instance.pk is None
                             or bool({'data_consulta', 'hora_consulta'} & set(self.changed_data)))
            if mudou_horario:
                validar_agendamento(data_hora, self.instance.duracao_minutos or DURACAO_PADRAO_MINUTOS,
                                    ignorar_id=self.instance.pk)
            cleaned['data_hora'] = data_hora
        return cleaned
    ```
    O `save()` continua igual. Atualize a docstring da classe.
- [x] **2.8 Ajustes que dependem dos campos:**
  - `admin.py`: em AnimalAdmin, `list_display` troca `'idade'` por `'data_nascimento'`; em ConsultaAdmin, acrescente `'disponibilidade'`.
  - `animal_detail.html:49`: `<p class="font-semibold">{{ animal.idade_formatada }}</p>`.
  - `proprietario_detail.html:93`: `{% if animal.data_nascimento %}<span>{{ animal.idade_formatada }}</span>{% endif %}`.
  - `consulta_form.html`: envolva o bloco "Status" em `{% if 'status' in form.fields %} … {% endif %}`.
- [x] **2.9 Testes.** Os exemplos abaixo vão completos; escreva os demais pela lista, um teste por linha.
  - `agendamentos/tests/test_services.py`, exemplos completos:
    ```python
    from django.core.exceptions import ValidationError
    from django.utils import timezone
    import pytest

    from agendamentos import services
    from agendamentos.models import Consulta
    from agendamentos.tests.utils import em, proxima_data


    def horas(livres):
        return [f'{h:%H:%M}' for h in livres]


    def test_grade_completa_de_08_as_18(horario_comercial, segunda):
        livres = horas(services.horarios_livres(segunda))
        assert livres[:3] == ['08:00', '08:30', '09:00']
        assert livres[-1] == '18:00'          # sessão de 60 min termina às 19:00
        assert len(livres) == 21


    def test_conflito_remove_horarios_sobrepostos(horario_comercial, animal, segunda):
        Consulta.objects.create(animal=animal, data_hora=em(segunda, 10), tipo='consulta')
        livres = horas(services.horarios_livres(segunda))
        assert {'09:30', '10:00', '10:30'}.isdisjoint(livres)
        assert '09:00' in livres and '11:00' in livres


    def test_hoje_nao_oferece_horarios_passados(horario_comercial, segunda, monkeypatch):
        monkeypatch.setattr(timezone, 'now', lambda: em(segunda, 10, 15))
        assert horas(services.horarios_livres(segunda))[0] == '10:30'


    def test_validar_agendamento_rejeita_conflito(consulta_futura, segunda):
        with pytest.raises(ValidationError, match='Conflito'):
            services.validar_agendamento(em(segunda, 10, 30))
    ```
  - Demais casos de `test_services.py`:
    - sábado → `[]`;
    - dia com `ativo=False` → `[]`;
    - consulta cancelada libera o horário;
    - `ignorar_id` devolve o horário da própria consulta;
    - `validar_agendamento` com data passada (`match='futuro'`);
    - dia fechado (`match='não atende'`);
    - antes da abertura (07:30) → fora do expediente;
    - 18:30 + 60 min → fora do expediente;
    - encostado no fim de outra consulta (11:00, depois de 10:00–11:00) → permitido e devolve a Disponibilidade de segunda;
    - `atualizar_status` agendado→confirmado com observação carimbada;
    - transição inválida realizado→agendado → ValidationError;
    - `validar_telefone('1234')` → erro.
  - `test_models.py`:
    - a consulta criada numa segunda fica com `disponibilidade` igual à de segunda, e `disponibilidade.consultas.count() == 1` (relacionamento "verifica");
    - sem Disponibilidade cadastrada → `disponibilidade is None`;
    - apagar a Disponibilidade deixa a FK nula (SET_NULL);
    - duas Disponibilidades no mesmo dia → `IntegrityError`, usando `with pytest.raises(IntegrityError), transaction.atomic():` para não quebrar a transação do teste;
    - `idade` e `idade_formatada` ('3 anos', '1 ano', '7 meses', '—');
    - `link_whatsapp` começa com `https://wa.me/5519999999999?text=`; com telefone de 8 dígitos → `''`.
  - `test_forms.py`:
    - formulário de criação sem o campo `status`, e a consulta salva fica `agendado`;
    - criação em conflito → inválido, com mensagem de conflito em `non_field_errors`;
    - edição de consulta **passada** mudando só observações → válido (crie a consulta com `data_hora` no passado direto pelo ORM);
    - AnimalForm aceita peso "12,50";
    - AnimalForm recusa nascimento futuro;
    - ProprietarioForm recusa telefone curto.
- [x] **2.10 CI** — crie `.github/workflows/ci.yml`:
  ```yaml
  name: CI

  on:
    push:
      branches: [main]
    pull_request:

  jobs:
    testes:
      name: Testes (PostgreSQL 16)
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:16
          env:
            POSTGRES_USER: vetsystem
            POSTGRES_PASSWORD: vetsystem
            POSTGRES_DB: vetsystem
          ports:
            - 5432:5432
          options: >-
            --health-cmd "pg_isready -U vetsystem"
            --health-interval 10s
            --health-timeout 5s
            --health-retries 5
      env:
        DATABASE_URL: postgres://vetsystem:vetsystem@localhost:5432/vetsystem
        SECRET_KEY: chave-apenas-para-o-ci
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.12'
            cache: pip
            cache-dependency-path: requirements*.txt
        - name: Instalar dependências
          run: pip install -r requirements-dev.txt
        - name: Verificações do Django
          run: |
            python manage.py check
            python manage.py makemigrations --check --dry-run
            python manage.py collectstatic --noinput
        - name: Testes com cobertura
          run: pytest --cov --cov-report=term-missing
  ```
  Não defina `DEBUG` no CI: com `DEBUG=False`, o settings ligaria o redirecionamento para HTTPS.
- [x] **2.11 Verificação:**
  - `.venv/bin/pytest --cov` passa (meta: ≥ 90% em `services.py`).
  - `check`, `makemigrations --check` e `migrate` local OK.
  - Smoke test no `runserver`: agendar duas consultas no mesmo horário mostra o erro de conflito, e a página do animal mostra a idade.
  - PR com CI verde e merge.

## Fase 3 — Telas Django seguindo o fluxograma

- [x] **3.1 Cancelar vira mudança de status** (fluxograma: "Atualizar status — cancelado"); excluir passa a ser outra ação.
  - Em `views.py`, importe `redirect`, `reverse`, `ValidationError`, `Count`, `Q` e `atualizar_status`, e crie:
    ```python
    class ConsultaCancelarView(LoginRequiredMixin, DetailView):
        """
        Cancela a consulta mudando o status (fluxograma: "Atualizar status — cancelado").
        O registro continua no histórico e na análise de dados.

        Rota    : GET/POST /consultas/<pk>/cancelar/
        Template: agendamentos/consulta_confirm_cancel.html
        """
        model = Consulta
        template_name = 'agendamentos/consulta_confirm_cancel.html'
        context_object_name = 'consulta'

        def post(self, request, *args, **kwargs):
            consulta = self.get_object()
            try:
                atualizar_status(consulta, 'cancelado', 'Cancelada pela clínica.')
                messages.success(request, 'Consulta cancelada. O horário voltou a ficar livre na agenda.')
            except ValidationError as erro:
                messages.error(request, erro.messages[0])
            return redirect('agendamentos:consulta-detail', pk=consulta.pk)
    ```
  - Em `urls.py`:
    - `path('consultas/<int:pk>/cancelar/', views.ConsultaCancelarView.as_view(), name='consulta-cancelar')`;
    - a rota `consulta-delete` passa para `consultas/<int:pk>/excluir/`, com a mensagem `'Consulta excluída.'`.
  - Templates:
    - Crie `consulta_confirm_cancel.html`, copiando `consulta_confirm_delete.html`, com os textos "Cancelar consulta?", "O horário ficará livre de novo e o registro continuará no histórico." e o botão "Sim, cancelar consulta".
    - Em `consulta_confirm_delete.html`, use "Excluir consulta?" e "Apaga o registro definitivamente. Para manter o histórico, prefira Cancelar."
    - Em `consulta_detail.html`, mostre "Cancelar consulta" (→ `consulta-cancelar`) só se o status for agendado ou confirmado, e um link discreto "Excluir registro" (→ `consulta-delete`).
- [x] **3.2 Fluxo encadeado de cadastro** (fluxograma: "Cadastrado? Não → Cadastrar proprietário e animal → Consultar horários livres").
  - Em `ProprietarioCreateView` e `AnimalCreateView`, acrescente:
    ```python
    def get_success_url(self):
        # Fluxograma: depois de "Cadastrar proprietário e animal", volta ao agendamento
        if self.request.GET.get('fluxo') == 'agendamento':
            return f"{reverse('agendamentos:animal-create')}?proprietario={self.object.pk}&fluxo=agendamento"
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['fluxo_agendamento'] = self.request.GET.get('fluxo') == 'agendamento'
        return ctx
    ```
    O exemplo acima é o de Proprietario. Em `AnimalCreateView`, o destino é `f"{reverse('agendamentos:consulta-create')}?animal={self.object.pk}"`.
  - O crispy envia o formulário para a própria URL, com a *query string*, então o `?fluxo=` chega no POST.
  - Em `proprietario_form.html` e `animal_form.html`, mostre um aviso se `fluxo_agendamento`. Por exemplo: "Etapa 1 de 3 — cadastro do tutor. Depois: animal e horário." e "Etapa 2 de 3 — cadastro do animal. Depois: escolha do horário."
  - Em `consulta_form.html`, abaixo do campo Animal: "Tutor ou animal ainda não cadastrado?" com os links `proprietario-create?fluxo=agendamento` ("Cadastrar tutor e animal") e `animal-create?fluxo=agendamento` ("Cadastrar animal de tutor já cadastrado").
- [x] **3.3 Lista de proprietários:**
  - `get_queryset` passa a usar `Proprietario.objects.annotate(total_animais=Count('animais')).order_by('nome')`.
  - A busca usa `Q(nome__icontains=q) | Q(telefone__icontains=q) | Q(email__icontains=q)` (o placeholder já promete e-mail).
  - No template, troque `proprietario.animais.count` por `proprietario.total_animais`.
- [x] **3.4 Expediente padrão.**
  - Crie `agendamentos/management/commands/criar_horarios_padrao.py`:
    ```python
    """
    VETSystem — ATIVO PET | Projeto Integrador UNIVESP 2026 — PI II
    Arquivo : agendamentos/management/commands/criar_horarios_padrao.py
    Função  : Cadastra o expediente padrão (segunda a sexta, 08:00–19:00) quando
              ainda não há nenhuma Disponibilidade. Idempotente — roda no start.sh.
    Autor   : Lucas Eduardo Rocha (RA 24217901) | <data>
    """
    import datetime

    from django.core.management.base import BaseCommand

    from agendamentos.models import Disponibilidade


    class Command(BaseCommand):
        help = 'Cadastra o horário padrão da clínica (seg–sex, 08:00–19:00) se nenhum existir.'

        def handle(self, *args, **options):
            if Disponibilidade.objects.exists():
                self.stdout.write(self.style.SUCCESS('Horários já cadastrados — nenhuma ação necessária.'))
                return
            for dia, _nome in Disponibilidade.DIAS_CHOICES:
                Disponibilidade.objects.create(dia_da_semana=dia, hora_inicio=datetime.time(8),
                                               hora_fim=datetime.time(19))
            self.stdout.write(self.style.SUCCESS('Horário padrão cadastrado: segunda a sexta, 08:00–19:00.'))
    ```
  - No `start.sh`, depois de `criar_superusuario`, acrescente `echo "==> Expediente padrão..."` e `python manage.py criar_horarios_padrao`.
  - Rode o comando no banco local.
- [x] **3.5 Testes** (`test_views.py`, `test_comandos.py`):
  - todas as telas internas redirecionam para `/login/` sem login (parametrize as URLs);
  - a home é pública (200);
  - POST em cancelar → status `cancelado`, e o registro continua existindo;
  - POST em excluir → registro apagado;
  - `proprietario-create?fluxo=agendamento` redireciona para `animal-create?proprietario=<id>&fluxo=agendamento`;
  - `animal-create?fluxo=agendamento` redireciona para `consulta-create?animal=<id>`;
  - criar consulta pela tela → `agendado` e com `disponibilidade` preenchida;
  - criar em conflito → 200 com a mensagem de erro;
  - a lista de proprietários mostra o total de animais e busca por e-mail;
  - `criar_horarios_padrao` rodado duas vezes → 5 registros.
- [x] **3.6 Verificação:** pytest verde, smoke test do fluxo completo no `runserver` e PR com CI verde. Depois do deploy, confira no site que os horários padrão existem.

## Fase 4 — API REST (Django REST Framework)

- [x] **4.1 Dependências.** Acrescente ao `requirements.txt` e reinstale:
  ```
  djangorestframework==3.18.1
  django-filter==26.1
  drf-spectacular==0.30.0
  ```
- [x] **4.2 `settings.py`.** Em `INSTALLED_APPS` (seção "Apps de terceiros"), acrescente `'rest_framework', 'django_filters', 'drf_spectacular',`. No fim do arquivo:
  ```python
  # =============================================================================
  # API REST (Django REST Framework) — PI II
  # =============================================================================
  REST_FRAMEWORK = {
      # Mesma sessão do login do Django (cookies + proteção CSRF)
      'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
      'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
      'DEFAULT_FILTER_BACKENDS': [
          'django_filters.rest_framework.DjangoFilterBackend',
          'rest_framework.filters.SearchFilter',
          'rest_framework.filters.OrderingFilter',
      ],
      'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
      'PAGE_SIZE': 50,
      'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
      'DEFAULT_THROTTLE_RATES': {'anon': '60/min'},   # só no endpoint público
  }

  SPECTACULAR_SETTINGS = {
      'TITLE': 'VETSystem API',
      'DESCRIPTION': 'API REST do VETSystem — agendamentos da Clínica ATIVO PET (Projeto Integrador II — UNIVESP).',
      'VERSION': '2.0.0',
      'SERVE_INCLUDE_SCHEMA': False,
  }
  ```
- [x] **4.3 Pacote `agendamentos/api/`.** Crie `__init__.py` (vazio) e os três arquivos abaixo, com cabeçalho no padrão do projeto.
  - `serializers.py`:
    ```python
    from django.core.exceptions import ValidationError as DjangoValidationError
    from rest_framework import serializers
    from rest_framework.validators import UniqueValidator

    from .. import services
    from ..models import Animal, Consulta, Disponibilidade, Proprietario


    class ProprietarioSerializer(serializers.ModelSerializer):
        total_animais = serializers.IntegerField(read_only=True)

        class Meta:
            model = Proprietario
            fields = ['id', 'nome', 'telefone', 'email', 'cpf', 'total_animais']

        def validate_telefone(self, valor):
            return services.validar_telefone(valor)  # o DRF converte a ValidationError do Django


    class AnimalSerializer(serializers.ModelSerializer):
        especie_display = serializers.CharField(source='get_especie_display', read_only=True)
        idade = serializers.IntegerField(read_only=True)
        proprietario_nome = serializers.CharField(source='proprietario.nome', read_only=True)
        proprietario_telefone = serializers.CharField(source='proprietario.telefone', read_only=True)

        class Meta:
            model = Animal
            fields = ['id', 'nome', 'especie', 'especie_display', 'raca', 'data_nascimento', 'idade',
                      'peso', 'queixa', 'proprietario', 'proprietario_nome', 'proprietario_telefone']

        def validate_data_nascimento(self, valor):
            return services.validar_data_nascimento(valor)


    class ConsultaSerializer(serializers.ModelSerializer):
        animal_nome = serializers.CharField(source='animal.nome', read_only=True)
        proprietario_nome = serializers.CharField(source='animal.proprietario.nome', read_only=True)
        proprietario_telefone = serializers.CharField(source='animal.proprietario.telefone', read_only=True)
        tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
        status_display = serializers.CharField(source='get_status_display', read_only=True)
        disponibilidade_descricao = serializers.StringRelatedField(source='disponibilidade', read_only=True)
        link_whatsapp = serializers.CharField(read_only=True)

        class Meta:
            model = Consulta
            fields = ['id', 'animal', 'animal_nome', 'proprietario_nome', 'proprietario_telefone',
                      'data_hora', 'duracao_minutos', 'tipo', 'tipo_display', 'status', 'status_display',
                      'observacoes', 'disponibilidade', 'disponibilidade_descricao', 'link_whatsapp']
            # Fluxograma: toda consulta nasce "agendado"; o status muda por POST .../status/
            read_only_fields = ['status', 'disponibilidade']
            extra_kwargs = {'duracao_minutos': {'min_value': 15, 'max_value': 240}}

        def validate(self, attrs):
            """Decisão "Horário disponível?" — a mesma regra do formulário (services)."""
            consulta = self.instance
            data_hora = attrs.get('data_hora', consulta.data_hora if consulta else None)
            duracao = attrs.get('duracao_minutos',
                                consulta.duracao_minutos if consulta else services.DURACAO_PADRAO_MINUTOS)
            mudou_horario = (consulta is None or data_hora != consulta.data_hora
                             or duracao != consulta.duracao_minutos)
            if mudou_horario and data_hora:
                try:
                    services.validar_agendamento(data_hora, duracao, ignorar_id=getattr(consulta, 'pk', None))
                except DjangoValidationError as erro:
                    raise serializers.ValidationError({'data_hora': erro.messages})
            return attrs


    class AtualizarStatusSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Consulta.STATUS_CHOICES)
        observacao = serializers.CharField(required=False, allow_blank=True, max_length=300)


    class DisponibilidadeSerializer(serializers.ModelSerializer):
        dia_da_semana_display = serializers.CharField(source='get_dia_da_semana_display', read_only=True)

        class Meta:
            model = Disponibilidade
            fields = ['id', 'dia_da_semana', 'dia_da_semana_display', 'hora_inicio', 'hora_fim', 'ativo']
            extra_kwargs = {'dia_da_semana': {'validators': [UniqueValidator(
                queryset=Disponibilidade.objects.all(),
                message='Já existe um horário cadastrado para este dia da semana.')]}}

        def validate(self, attrs):
            inicio = attrs.get('hora_inicio', getattr(self.instance, 'hora_inicio', None))
            fim = attrs.get('hora_fim', getattr(self.instance, 'hora_fim', None))
            if inicio and fim and fim <= inicio:
                raise serializers.ValidationError(
                    {'hora_fim': 'O horário de encerramento deve ser posterior ao de início.'})
            return attrs


    class HorariosLivresEntradaSerializer(serializers.Serializer):
        data = serializers.DateField()
        duracao = serializers.IntegerField(default=services.DURACAO_PADRAO_MINUTOS, min_value=15, max_value=240)
        ignorar = serializers.IntegerField(required=False)
    ```
  - `views.py`:
    ```python
    from django.core.exceptions import ValidationError as DjangoValidationError
    from django.db.models import Count
    from django_filters import rest_framework as filtros
    from drf_spectacular.utils import extend_schema
    from rest_framework import serializers, viewsets
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.views import APIView

    from .. import services
    from ..models import Animal, Consulta, Disponibilidade, Proprietario
    from .serializers import (AnimalSerializer, AtualizarStatusSerializer, ConsultaSerializer,
                              DisponibilidadeSerializer, HorariosLivresEntradaSerializer,
                              ProprietarioSerializer)


    class ProprietarioViewSet(viewsets.ModelViewSet):
        """CRUD de tutores. Busca: ?search=<nome, telefone, CPF ou e-mail>."""
        serializer_class = ProprietarioSerializer
        search_fields = ['nome', 'telefone', 'cpf', 'email']
        ordering_fields = ['nome']

        def get_queryset(self):
            return Proprietario.objects.annotate(total_animais=Count('animais')).order_by('nome')


    class AnimalViewSet(viewsets.ModelViewSet):
        """CRUD de animais. Autocomplete (fluxograma, etapa 2): ?search=<nome do animal ou do tutor>."""
        serializer_class = AnimalSerializer
        queryset = Animal.objects.select_related('proprietario').order_by('nome')
        search_fields = ['nome', 'proprietario__nome', 'proprietario__telefone']
        filterset_fields = ['especie', 'proprietario']
        ordering_fields = ['nome']


    class ConsultaFiltro(filtros.FilterSet):
        data = filtros.DateFilter(field_name='data_hora', lookup_expr='date')
        inicio = filtros.DateFilter(field_name='data_hora', lookup_expr='date__gte')
        fim = filtros.DateFilter(field_name='data_hora', lookup_expr='date__lte')

        class Meta:
            model = Consulta
            fields = ['status', 'tipo', 'animal', 'data', 'inicio', 'fim']


    class ConsultaViewSet(viewsets.ModelViewSet):
        """
        Agenda. Filtros: ?status= ?tipo= ?animal= ?data=AAAA-MM-DD ?inicio=&fim=.
        Criar = fluxograma "Registrar consulta (status: agendado)".
        """
        serializer_class = ConsultaSerializer
        queryset = Consulta.objects.select_related('animal__proprietario', 'disponibilidade').order_by('data_hora')
        filterset_class = ConsultaFiltro
        search_fields = ['animal__nome', 'animal__proprietario__nome']
        ordering_fields = ['data_hora']

        @extend_schema(request=AtualizarStatusSerializer, responses=ConsultaSerializer)
        @action(detail=True, methods=['post'], url_path='status', url_name='status')
        def atualizar_status(self, request, pk=None):
            """Fluxograma: "Confirmar agendamento" e "Atualizar status (realizado/cancelado)"."""
            consulta = self.get_object()
            entrada = AtualizarStatusSerializer(data=request.data)
            entrada.is_valid(raise_exception=True)
            try:
                services.atualizar_status(consulta, entrada.validated_data['status'],
                                          entrada.validated_data.get('observacao', ''))
            except DjangoValidationError as erro:
                raise serializers.ValidationError({'status': erro.messages})
            return Response(self.get_serializer(consulta).data)


    class DisponibilidadeViewSet(viewsets.ModelViewSet):
        """Horários de funcionamento (um por dia da semana)."""
        serializer_class = DisponibilidadeSerializer
        queryset = Disponibilidade.objects.order_by('dia_da_semana')
        pagination_class = None  # no máximo 5 registros


    class HorariosLivresView(APIView):
        """Fluxograma, etapa 3 — GET /api/horarios-livres/?data=AAAA-MM-DD[&duracao=60][&ignorar=<id>]."""

        @extend_schema(parameters=[HorariosLivresEntradaSerializer])
        def get(self, request):
            entrada = HorariosLivresEntradaSerializer(data=request.query_params)
            entrada.is_valid(raise_exception=True)
            data = entrada.validated_data['data']
            duracao = entrada.validated_data['duracao']
            disponibilidade = services.disponibilidade_do_dia(data)
            livres = services.horarios_livres(data, duracao, entrada.validated_data.get('ignorar'))
            return Response({
                'data': data.isoformat(),
                'aberto': disponibilidade is not None,
                'inicio': f'{disponibilidade.hora_inicio:%H:%M}' if disponibilidade else None,
                'fim': f'{disponibilidade.hora_fim:%H:%M}' if disponibilidade else None,
                'duracao': duracao,
                'horarios': [f'{h:%H:%M}' for h in livres],
            })
    ```
  - `urls.py`:
    ```python
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter

    from . import views

    app_name = 'api'

    roteador = DefaultRouter()
    roteador.register('proprietarios', views.ProprietarioViewSet, basename='proprietario')
    roteador.register('animais', views.AnimalViewSet, basename='animal')
    roteador.register('consultas', views.ConsultaViewSet, basename='consulta')
    roteador.register('disponibilidades', views.DisponibilidadeViewSet, basename='disponibilidade')

    urlpatterns = [
        path('horarios-livres/', views.HorariosLivresView.as_view(), name='horarios-livres'),
        path('', include(roteador.urls)),
    ]
    ```
- [x] **4.4 `vetsystem/urls.py`.** Importe `SpectacularAPIView` e `SpectacularSwaggerView` de `drf_spectacular.views` e acrescente, **antes** de `path('', include('agendamentos.urls'))`:
  ```python
  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
  path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
  path('api/', include('agendamentos.api.urls')),
  ```
  Atualize a docstring com as novas rotas.
- [x] **4.5 Testes** (`test_api.py`).
  - Acrescente ao `conftest.py`:
    ```python
    @pytest.fixture
    def api(usuario):
        from rest_framework.test import APIClient
        cliente = APIClient()
        cliente.force_login(usuario)  # sessão real, como no navegador
        return cliente
    ```
  - Casos (use `reverse('api:consulta-list')` etc. e `format='json'`):
    - sem login → 403;
    - `APIClient(enforce_csrf_checks=True)` logado, POST sem token → 403;
    - lista de proprietários traz `total_animais`;
    - criar proprietário com telefone curto → 400;
    - `/api/animais/?search=João` encontra o Rex pelo nome do tutor;
    - filtro `?proprietario=`;
    - POST de consulta segunda 09:00 → 201, `status == 'agendado'` e `disponibilidade == horario_comercial[0].pk`;
    - conflito → 400 com chave `data_hora`;
    - fora do expediente → 400;
    - data passada → 400;
    - filtros `?data=` e `?inicio=&fim=`;
    - `POST /api/consultas/<id>/status/` com `confirmado` → 200;
    - status `realizado` → `agendado` → 400;
    - `horarios-livres` em segunda → `aberto` true e 21 horários;
    - `horarios-livres` em sábado → `aberto` false e `[]`;
    - `?data=` inválida → 400;
    - Disponibilidade duplicada → 400;
    - `/api/schema/` → 200.
- [x] **4.6 Verificação:**
  - pytest verde e `collectstatic --noinput` OK (estáticos do DRF).
  - Logado no `runserver`, abra `/api/docs/` e `/api/consultas/` (API navegável).
  - Conte as rotas e operações:
    ```bash
    .venv/bin/python manage.py spectacular --format openapi-json --file docs/api-openapi.json
    python3 -c "import json;p=json.load(open('docs/api-openapi.json'))['paths'];print(len(p),'rotas,',sum(1 for v in p.values() for m in v if m in('get','post','put','patch','delete')),'operações')"
    ```
  - PR com CI verde.

## Fase 5 — Acessibilidade (WCAG 2.1 AA)

- [x] **5.1 Crie `static/css/vetsystem.css`:**
  ```css
  /* VETSystem — static/css/vetsystem.css
     Componentes e acessibilidade (WCAG 2.1 AA). Todas as cores com contraste ≥ 4,5:1. */

  /* 2.4.7 Foco visível: anel escuro com halo branco (aparece no fundo claro e no menu turquesa) */
  :focus-visible { outline: 3px solid #1B1B1B !important; outline-offset: 2px !important; box-shadow: 0 0 0 5px #FFFFFF !important; }
  main:focus-visible { outline: none !important; box-shadow: none !important; }

  /* Menu: página atual indicada também sem depender de cor */
  .link-menu { color: #FFFFFF; font-weight: 500; text-underline-offset: 4px; }
  .link-menu:hover, .link-menu[aria-current="page"] { text-decoration: underline; }
  .link-menu[aria-current="page"] { font-weight: 700; }

  /* Selos de status (um só lugar; o JS troca a classe badge-<status>) */
  .badge { display: inline-block; font-size: .75rem; font-weight: 600; padding: .25rem .75rem; border-radius: 9999px; }
  .badge-agendado { background: #DBEAFE; color: #1D4ED8; }
  .badge-confirmado { background: #EAF7F7; color: #1E7579; }
  .badge-realizado { background: #DCFCE7; color: #166534; }
  .badge-cancelado { background: #FEE2E2; color: #B91C1C; }

  /* Botões de ação rápida de status */
  .btn-acao { display: inline-flex; align-items: center; font-size: .75rem; font-weight: 700; padding: .375rem .75rem;
              border-radius: .5rem; border: 1px solid #1E7579; color: #1E7579; background: #FFFFFF; }
  .btn-acao:hover { background: #EAF7F7; }
  .btn-acao-whatsapp { background: #1E7579; color: #FFFFFF; }
  .btn-acao-whatsapp:hover { background: #185F62; }
  .btn-acao-alerta { border-color: #B91C1C; color: #B91C1C; }

  /* Autocomplete (combobox WAI-ARIA) */
  .vs-opcao { padding: .5rem .75rem; cursor: pointer; }
  .vs-opcao:hover, .vs-opcao[aria-selected="true"] { background: #EAF7F7; }
  .vs-opcao[aria-selected="true"] { outline: 2px solid #1E7579; outline-offset: -2px; }

  /* Agenda interativa: dias e horários */
  .vs-nav { padding: .25rem .75rem; border: 1px solid #D1D5DB; border-radius: .5rem; background: #FFFFFF; }
  .vs-nav:disabled { color: #4B5563; background: #F3F4F6; cursor: not-allowed; }
  .vs-dia { padding: .5rem; border: 1px solid #D1D5DB; border-radius: .75rem; background: #FFFFFF; color: #1B1B1B; text-align: center; }
  .vs-dia[aria-pressed="true"] { background: #1E7579; border-color: #1E7579; color: #FFFFFF; }
  .vs-dia:disabled { background: #F3F4F6; color: #4B5563; cursor: not-allowed; }
  .vs-slot { position: relative; display: inline-flex; }
  .vs-slot input { position: absolute; opacity: 0; width: 1px; height: 1px; }
  .vs-slot span { display: inline-block; min-width: 4.5rem; text-align: center; padding: .5rem .75rem; border: 1px solid #1E7579;
                  border-radius: .5rem; color: #1E7579; font-weight: 600; background: #FFFFFF; cursor: pointer; }
  .vs-slot input:checked + span { background: #1E7579; color: #FFFFFF; }
  .vs-slot input:focus-visible + span { outline: 3px solid #1B1B1B; outline-offset: 2px; }

  /* 2.3.3 / conforto: respeita quem pede menos movimento */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important;
                             transition-duration: .01ms !important; scroll-behavior: auto !important; }
  }
  ```
- [x] **5.2 Reescreva `templates/base.html`** com o conteúdo abaixo. **Copie sem alterar** o bloco de máscaras IMask atual (telefone, CPF, peso) para o ponto indicado.
  ```django
  {% load static %}<!DOCTYPE html>
  <html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}VETSystem{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      // Paleta ATIVO PET ajustada para WCAG 2.1 AA (contraste ≥ 4,5:1 com branco).
      tailwind.config = { theme: { extend: { colors: {
        'ativo-turquesa': '#1E7579', 'ativo-roxo': '#4A2C7A', 'ativo-laranja': '#B9471A', 'ativo-fundo': '#F5F6F7'
      } } } };
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/vetsystem.css' %}">
    <style>
      body { font-family: 'Lato', sans-serif; }
      h1, h2, h3 { font-family: 'Montserrat', sans-serif; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/imask/7.6.1/imask.min.js"></script>
    {% block extra_head %}{% endblock %}
  </head>
  <body class="min-h-screen flex flex-col bg-ativo-fundo text-[#1B1B1B]">
    <a href="#conteudo" class="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 bg-white text-ativo-roxo font-bold px-4 py-2 rounded-lg shadow">Pular para o conteúdo</a>

    <header class="bg-ativo-turquesa shadow-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16 gap-3">
          <a href="{% url 'agendamentos:home' %}" class="text-white font-bold text-xl"><span aria-hidden="true">🐾 </span>VETSystem</a>
          {% if user.is_authenticated %}
          <nav aria-label="Navegação principal" class="hidden md:block">{% include 'partials/menu_principal.html' %}</nav>
          {% endif %}
          <div class="flex items-center gap-2">
            {% if user.is_authenticated %}
              <button type="button" id="botao-menu" class="md:hidden text-white font-semibold border border-white rounded-lg px-3 py-1.5" aria-expanded="false" aria-controls="menu-movel">Menu</button>
              <span class="hidden sm:inline text-white text-sm">{{ user.username }}</span>
              <form method="post" action="{% url 'logout' %}" class="inline">
                {% csrf_token %}
                <button type="submit" class="bg-ativo-laranja text-white text-sm font-bold py-1.5 px-4 rounded-lg hover:opacity-90">Sair</button>
              </form>
            {% else %}
              <a href="{% url 'login' %}" class="bg-ativo-laranja text-white text-sm font-bold py-1.5 px-4 rounded-lg hover:opacity-90">Entrar</a>
            {% endif %}
          </div>
        </div>
        {% if user.is_authenticated %}
        <nav id="menu-movel" aria-label="Navegação principal (celular)" class="md:hidden pb-4" hidden>
          {% include 'partials/menu_principal.html' with vertical=True %}
        </nav>
        {% endif %}
      </div>
    </header>

    {% if messages %}
    <div class="max-w-7xl mx-auto px-4 mt-4 w-full" role="status">
      {% for message in messages %}
        <div class="rounded-lg px-4 py-3 mb-2 text-sm {% if message.tags == 'success' %}bg-green-100 text-green-800 border border-green-300{% elif message.tags == 'error' %}bg-red-100 text-red-800 border border-red-300{% else %}bg-blue-100 text-blue-800 border border-blue-300{% endif %}">{{ message }}</div>
      {% endfor %}
    </div>
    {% endif %}
    <div id="anuncios" class="sr-only" role="status" aria-live="polite"></div>

    <main id="conteudo" tabindex="-1" class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {% block content %}{% endblock %}
    </main>

    <footer class="bg-ativo-roxo text-white text-center text-xs py-4 mt-auto">
      VETSystem &copy; 2026 — ATIVO PET Fisioterapia e Bem-Estar Animal, Limeira/SP | Projeto Integrador II — UNIVESP
    </footer>

    <script>
    document.addEventListener('DOMContentLoaded', function () {
      // Menu no celular (WCAG 1.4.10 — todo o conteúdo disponível em telas estreitas)
      var botaoMenu = document.getElementById('botao-menu');
      if (botaoMenu) {
        var menuMovel = document.getElementById('menu-movel');
        botaoMenu.addEventListener('click', function () {
          var abrir = botaoMenu.getAttribute('aria-expanded') !== 'true';
          botaoMenu.setAttribute('aria-expanded', String(abrir));
          menuMovel.hidden = !abrir;
        });
      }
      // <<< COLE AQUI, sem alterações, o bloco IMask atual (telefone, CPF e peso) >>>
    });
    </script>
    {% block extra_js %}{% endblock %}
  </body>
  </html>
  ```
  Crie também `templates/partials/menu_principal.html`:
  ```django
  {% with nome=request.resolver_match.url_name|default:'' %}
  <ul class="{% if vertical %}flex flex-col gap-2 pt-2{% else %}flex items-center gap-6{% endif %}">
    <li><a href="{% url 'agendamentos:dashboard' %}" class="link-menu" {% if nome == 'dashboard' %}aria-current="page"{% endif %}>Dashboard</a></li>
    <li><a href="{% url 'agendamentos:consulta-list' %}" class="link-menu" {% if nome|slice:':8' == 'consulta' %}aria-current="page"{% endif %}>Consultas</a></li>
    <li><a href="{% url 'agendamentos:proprietario-list' %}" class="link-menu" {% if nome|slice:':12' == 'proprietario' %}aria-current="page"{% endif %}>Proprietários</a></li>
    <li><a href="{% url 'agendamentos:animal-list' %}" class="link-menu" {% if nome|slice:':6' == 'animal' %}aria-current="page"{% endif %}>Animais</a></li>
    <li><a href="{% url 'agendamentos:disponibilidade-list' %}" class="link-menu" {% if nome|slice:':15' == 'disponibilidade' %}aria-current="page"{% endif %}>Horários</a></li>
  </ul>
  {% endwith %}
  ```
- [x] **5.3 Conserte os atributos quebrados de `animal_list.html`.** Faça isto **antes** da paleta:
  ```bash
  F=agendamentos/templates/agendamentos/animal_list.html
  sed -i -E \
    -e 's/class="text-2xl font-bold style="color:#4A2C7A""/class="text-2xl font-bold text-ativo-roxo"/' \
    -e 's/class="style="background:#31A1A7" hover:bg-teal-600 /class="bg-ativo-turquesa hover:opacity-90 /' \
    -e 's/class="style="background:#31A1A7" text-white"/class="bg-ativo-turquesa text-white"/' \
    -e 's/class="style="color:#31A1A7" /class="text-ativo-turquesa /g' \
    -e 's/class="style="color:#4A2C7A" /class="text-ativo-roxo /g' \
    -e 's/class="style="color:#F26A2E" /class="text-ativo-laranja /g' "$F"
  grep -c 'class="style=' "$F"   # deve imprimir 0
  ```
- [x] **5.4 Paleta acessível em todos os templates e no `forms.py`:**
  ```bash
  ARQ=$(grep -rlE '#31A1A7|#F26A2E|text-gray-(400|500)|text-red-(400|500|600)|bg-red-500|text-green-600|text-white/(70|80|90)|hover:bg-orange-600' templates agendamentos/templates agendamentos/forms.py)
  sed -i -E -e 's/#31A1A7/#1E7579/gI' -e 's/#F26A2E/#B9471A/gI' -e 's/text-gray-(400|500)/text-gray-600/g' \
    -e 's/text-red-(400|500|600)/text-red-700/g' -e 's/hover:bg-red-600/hover:bg-red-800/g' -e 's/bg-red-500/bg-red-700/g' \
    -e 's/text-green-600/text-green-700/g' -e 's#text-white/(70|80|90)#text-white#g' -e 's/hover:bg-orange-600/hover:bg-orange-800/g' $ARQ
  grep -rnE '#31A1A7|#F26A2E|text-gray-(400|500)|text-red-(400|500|600)|text-green-600' templates agendamentos/templates agendamentos/forms.py || echo "Paleta OK"
  ```
  Ajustes manuais em `home.html`:
  - `#F9A96B` → `#FFD9C2`.
  - Selo "📍 Limeira" e botão "Conheça os serviços": `bg-white/20` → `bg-black/25` e `hover:bg-white/30` → `hover:bg-black/35`.
- [x] **5.5 Selo de status único.**
  - Crie `agendamentos/templates/agendamentos/_badge_status.html`:
    ```django
    <span class="badge badge-{{ consulta.status }}" data-status-badge="{{ consulta.pk }}">{{ consulta.get_status_display }}</span>
    ```
  - Substitua os blocos `{% if consulta.status == 'agendado' %}…{% endif %}` de selo por `{% include 'agendamentos/_badge_status.html' %}` em `dashboard.html` (2×), `consulta_list.html`, `consulta_detail.html` e `animal_detail.html`.
- [x] **5.6 Padrões a aplicar em todos os templates:**
  - **Tabelas:**
    - todo `<th>` ganha `scope="col"`;
    - o `<th>` vazio de ações vira `<th scope="col"><span class="sr-only">Ações</span></th>`;
    - acrescente `<caption class="sr-only">…</caption>` (dashboard, consulta_list, animal_list, disponibilidade_list);
    - em `disponibilidade_list.html`, tire o `flex` do `<td>` e coloque-o num `<div>` interno.
  - **Links ambíguos:**
    - "Ver", "Editar", "Excluir" e "Ver detalhes" ganham contexto oculto, por exemplo `Ver<span class="sr-only"> consulta de {{ consulta.animal.nome }} em {{ consulta.data_hora|date:"d/m H:i" }}</span>`;
    - separadores "|" ganham `aria-hidden="true"`.
  - **Emojis:**
    - os decorativos (🐾 👋 📅 👤 📋 🕐 ⚠️ ⏰ 🐕 🐈 🩺 🦮 🌿 ✅) ficam em `<span aria-hidden="true">`;
    - quando o emoji é o rótulo (📱, ✉️, 📍), acrescente `<span class="sr-only">Telefone: </span>` (ou "E-mail: ", "Endereço: ");
    - tire os emojis das `<option>` de espécie.
  - **Filtros com rótulo:**
    - em `consulta_list`, `<label for="filtro-status">` e `<label for="filtro-data">`, com os `id`s correspondentes nos campos;
    - em `animal_list`, `<label for="busca-animal" class="sr-only">Buscar por nome do animal ou tutor</label>` e `<label for="filtro-especie" class="sr-only">Espécie</label>`;
    - em `proprietario_list`, `<label for="busca-proprietario" class="sr-only">Buscar por nome, telefone ou e-mail</label>`.
  - **Navegação secundária:**
    - breadcrumbs: `<nav aria-label="Trilha de navegação">`, com o item atual em `<span aria-current="page">`;
    - paginação: `<nav aria-label="Paginação">`.
  - **Erros nos templates manuais** (`consulta_form.html`):
    - os erros de cada campo vão dentro de `<div id="{{ form.CAMPO.auto_id }}_error">…</div>`, porque o Django 6 já aponta `aria-describedby` para esse id;
    - acrescente `<p id="{{ form.observacoes.auto_id }}_helptext" class="text-xs text-gray-600 mt-1">{{ form.observacoes.help_text }}</p>`;
    - o bloco de erros gerais recebe `role="alert"`;
    - o asterisco vira `<span class="text-red-700" aria-hidden="true">*</span>`, e o topo do formulário recebe "Campos marcados com * são obrigatórios.".
  - **Login:**
    - a caixa de erro recebe `role="alert"`;
    - inputs com `autocomplete="username"` e `autocomplete="current-password"` (WCAG 1.3.5);
    - o emoji do título fica `aria-hidden`.
  - **Home:**
    - o CTA "Agendar Consulta" passa a usar `href="https://wa.me/5519987286814?text={{ 'Olá! Gostaria de agendar um atendimento para meu pet.'|urlencode }}"` (o filtro `urlencode` codifica espaços e acentos), abrindo em nova aba (é a raia do tutor no fluxograma: solicitar por telefone/WhatsApp);
    - todo `target="_blank"` recebe `rel="noopener"` e `<span class="sr-only"> (abre em nova aba)</span>`;
    - o telefone exibido passa a ser **(19) 98728-6814**.
- [x] **5.7 Override do crispy (os erros passam a ter os ids que o Django referencia):**
  - Crie `templates/tailwind/layout/field_errors.html` e `templates/tailwind/layout/field_errors_block.html`, ambos com:
    ```django
    {% if form_show_errors and field.errors %}
    <div id="{{ field.auto_id }}_error">
      {% for error in field.errors %}<p class="text-red-700 text-xs mt-1"><strong>{{ error }}</strong></p>{% endfor %}
    </div>
    {% endif %}
    ```
  - Copie `.venv/lib/python3.12/site-packages/crispy_tailwind/templates/tailwind/errors.html` para `templates/tailwind/errors.html` e acrescente `role="alert"` à `div` externa.
- [x] **5.8 Testes automatizados de acessibilidade** — crie `agendamentos/tests/test_acessibilidade.py`:
  ```python
  """
  Testes automatizados de acessibilidade (WCAG 2.1) — verificações estruturais sem
  navegador: idioma, link "Pular para o conteúdo", um único <h1>, rótulo em todo
  campo, referências ARIA válidas, ids únicos, <th> com scope e <img> com alt.
  (Contraste e teclado: Lighthouse/axe e checklist manual.)
  """
  from html.parser import HTMLParser

  import pytest
  from django.urls import reverse

  from agendamentos.models import Disponibilidade

  CAMPOS = {'input', 'select', 'textarea'}
  TIPOS_SEM_ROTULO = {'hidden', 'submit', 'button', 'reset', 'image'}


  class _Coletor(HTMLParser):
      def __init__(self):
          super().__init__(convert_charrefs=True)
          self.elementos = []
          self._labels_abertos = 0

      def handle_starttag(self, tag, attrs):
          atributos = dict(attrs)
          atributos['_dentro_de_label'] = self._labels_abertos > 0
          self.elementos.append((tag, atributos))
          if tag == 'label':
              self._labels_abertos += 1

      def handle_startendtag(self, tag, attrs):
          atributos = dict(attrs)
          atributos['_dentro_de_label'] = self._labels_abertos > 0
          self.elementos.append((tag, atributos))

      def handle_endtag(self, tag):
          if tag == 'label' and self._labels_abertos:
              self._labels_abertos -= 1


  def problemas_de_acessibilidade(html):
      coletor = _Coletor()
      coletor.feed(html)
      elementos = coletor.elementos
      problemas = []
      ids = [a['id'] for _, a in elementos if a.get('id')]
      repetidos = sorted({i for i in ids if ids.count(i) > 1})
      if repetidos:
          problemas.append(f'ids repetidos: {repetidos}')
      existentes = set(ids)
      rotulos_for = {a.get('for') for t, a in elementos if t == 'label' and a.get('for')}
      for tag, a in elementos:
          if tag == 'html' and (a.get('lang') or '').lower() != 'pt-br':
              problemas.append('<html> sem lang="pt-br"')
          if tag in CAMPOS and (a.get('type') or '').lower() not in TIPOS_SEM_ROTULO:
              if not (a.get('id') in rotulos_for or a.get('aria-label') or a.get('aria-labelledby')
                      or a['_dentro_de_label']):
                  problemas.append(f'campo sem rótulo: <{tag} name="{a.get("name")}" id="{a.get("id")}">')
          for atributo in ('aria-describedby', 'aria-labelledby', 'aria-controls', 'aria-activedescendant'):
              for ref in (a.get(atributo) or '').split():
                  if ref not in existentes:
                      problemas.append(f'{atributo}="{ref}" aponta para id inexistente')
          if tag == 'img' and 'alt' not in a:
              problemas.append('<img> sem alt')
          if tag == 'th' and 'scope' not in a:
              problemas.append('<th> sem scope')
      total_h1 = sum(1 for t, _ in elementos if t == 'h1')
      if total_h1 != 1:
          problemas.append(f'esperado 1 <h1>, encontrado {total_h1}')
      if not any(t == 'a' and a.get('href') == '#conteudo' for t, a in elementos):
          problemas.append('falta o link "Pular para o conteúdo"')
      if 'conteudo' not in existentes:
          problemas.append('falta <main id="conteudo">')
      return problemas


  PAGINAS_PUBLICAS = ['agendamentos:home', 'login']
  PAGINAS_INTERNAS = [
      ('agendamentos:dashboard', None), ('agendamentos:consulta-list', None),
      ('agendamentos:consulta-create', None), ('agendamentos:consulta-detail', 'consulta'),
      ('agendamentos:consulta-update', 'consulta'), ('agendamentos:consulta-cancelar', 'consulta'),
      ('agendamentos:consulta-delete', 'consulta'), ('agendamentos:proprietario-list', None),
      ('agendamentos:proprietario-create', None), ('agendamentos:proprietario-detail', 'proprietario'),
      ('agendamentos:proprietario-update', 'proprietario'), ('agendamentos:proprietario-delete', 'proprietario'),
      ('agendamentos:animal-list', None), ('agendamentos:animal-create', None),
      ('agendamentos:animal-detail', 'animal'), ('agendamentos:animal-update', 'animal'),
      ('agendamentos:animal-delete', 'animal'), ('agendamentos:disponibilidade-list', None),
      ('agendamentos:disponibilidade-create', None), ('agendamentos:disponibilidade-update', 'disponibilidade'),
  ]


  @pytest.mark.parametrize('nome', PAGINAS_PUBLICAS)
  def test_paginas_publicas_acessiveis(client, db, nome):
      resposta = client.get(reverse(nome))
      assert resposta.status_code == 200
      assert problemas_de_acessibilidade(resposta.content.decode()) == []


  @pytest.mark.parametrize('nome,objeto', PAGINAS_INTERNAS)
  def test_paginas_internas_acessiveis(cliente_logado, consulta_futura, nome, objeto):
      alvos = {'consulta': consulta_futura, 'animal': consulta_futura.animal,
               'proprietario': consulta_futura.animal.proprietario,
               'disponibilidade': Disponibilidade.objects.first()}
      url = reverse(nome, args=[alvos[objeto].pk]) if objeto else reverse(nome)
      resposta = cliente_logado.get(url)
      assert resposta.status_code == 200
      assert problemas_de_acessibilidade(resposta.content.decode()) == []


  def test_formulario_com_erros_continua_acessivel(cliente_logado):
      resposta = cliente_logado.post(reverse('agendamentos:proprietario-create'), {'nome': '', 'telefone': '12'})
      html = resposta.content.decode()
      assert resposta.status_code == 200 and 'aria-invalid="true"' in html
      assert problemas_de_acessibilidade(html) == []
  ```
  Se aparecer um problema, conserte o template, não o teste. Anote cada correção em `registro_testes.md`: isso vira evidência de "falhas encontradas e corrigidas".
- [ ] **5.9 Verificação:** (pytest e CI feitos; checklist de teclado pendente)
  - pytest verde.
  - **[VOCÊ]** checklist de teclado: navegue pelas telas só com Tab, Shift+Tab, Enter e Esc; confira que o foco é sempre visível e que o menu funciona no celular (DevTools, 375 px).
  - Crie `docs/metricas/checklist_manual.md` com o resultado.
  - PR com CI verde.

## Fase 6 — JavaScript do fluxo de agendamento (assíncrono, sem recarregar)

Todos os arquivos ficam em `static/js/`, com cabeçalho em comentário (arquivo, função, etapa do fluxograma, autor).

- [x] **6.1 `static/js/api.js`:**
  ```js
  /* VETSystem — static/js/api.js — cliente mínimo da API REST (fetch + sessão do Django + CSRF). */
  (function () {
    'use strict';

    function tokenCsrf() {
      var cookie = document.cookie.split('; ').find(function (c) { return c.indexOf('csrftoken=') === 0; });
      if (cookie) return decodeURIComponent(cookie.split('=')[1]);
      var campo = document.querySelector('input[name="csrfmiddlewaretoken"]');
      return campo ? campo.value : '';
    }

    async function requisitar(url, metodo, corpo, opcoes) {
      var cabecalhos = { 'Accept': 'application/json' };
      if (metodo !== 'GET') {
        cabecalhos['Content-Type'] = 'application/json';
        cabecalhos['X-CSRFToken'] = tokenCsrf();
      }
      var resposta = await fetch(url, Object.assign({
        method: metodo, headers: cabecalhos, credentials: 'same-origin',
        body: corpo === undefined ? undefined : JSON.stringify(corpo)
      }, opcoes || {}));
      var dados = null;
      if (resposta.status !== 204) {
        try { dados = await resposta.json(); } catch (e) { dados = null; }
      }
      if (!resposta.ok) {
        var erro = new Error('Erro ' + resposta.status + ' em ' + url);
        erro.status = resposta.status;
        erro.dados = dados;
        throw erro;
      }
      return dados;
    }

    /* Converte o formato de erro do DRF ({campo: [mensagens]}) numa lista de textos. */
    function mensagens(dados) {
      if (!dados) return ['Não foi possível concluir a operação. Tente novamente.'];
      if (typeof dados === 'string') return [dados];
      if (Array.isArray(dados)) return dados.map(String);
      var lista = [];
      Object.keys(dados).forEach(function (campo) {
        var valor = dados[campo];
        (Array.isArray(valor) ? valor : [valor]).forEach(function (m) { lista.push(String(m)); });
      });
      return lista;
    }

    /* Anuncia uma mensagem para leitores de tela (região viva #anuncios, em base.html). */
    function anunciar(texto) {
      var regiao = document.getElementById('anuncios');
      if (!regiao) return;
      regiao.textContent = '';
      window.setTimeout(function () { regiao.textContent = texto; }, 50);
    }

    /* Data LOCAL em AAAA-MM-DD — nunca use toISOString(), que converte para UTC. */
    function dataIso(data) {
      return data.getFullYear() + '-' + String(data.getMonth() + 1).padStart(2, '0') + '-' +
        String(data.getDate()).padStart(2, '0');
    }

    function dataDeIso(texto) {
      var p = texto.split('-').map(Number);
      return new Date(p[0], p[1] - 1, p[2]);
    }

    var DIAS = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado'];

    function dataPorExtenso(data) {  // "terça-feira, 14/10"
      return DIAS[data.getDay()] + ', ' + String(data.getDate()).padStart(2, '0') + '/' +
        String(data.getMonth() + 1).padStart(2, '0');
    }

    window.VetAPI = {
      get: function (url, opcoes) { return requisitar(url, 'GET', undefined, opcoes); },
      post: function (url, corpo, opcoes) { return requisitar(url, 'POST', corpo, opcoes); },
      patch: function (url, corpo) { return requisitar(url, 'PATCH', corpo); },
      mensagens: mensagens, anunciar: anunciar, dataIso: dataIso, dataDeIso: dataDeIso,
      dataPorExtenso: dataPorExtenso,
      DIAS_CURTOS: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    };
  }());
  ```
- [x] **6.2 `static/js/autocomplete.js`** — fluxograma, etapa 2 ("Sugerir proprietário e animal"). Segue o padrão WAI-ARIA 1.2 de combobox com listbox:
  ```js
  /* VETSystem — static/js/autocomplete.js — combobox acessível que busca /api/animais/?search= */
  (function () {
    'use strict';

    function VetAutocomplete(o) {
      this.campo = document.getElementById(o.campoId);
      this.lista = document.getElementById(o.listaId);
      this.status = document.getElementById(o.statusId);
      this.select = document.getElementById(o.selectId);   // <select id_animal> original (reserva sem JS)
      this.url = o.url;
      this.aoFalhar = o.aoFalhar || function () {};
      this.itens = [];
      this.ativo = -1;
      this.temporizador = null;
      this.ultimaBusca = '';
      var self = this;
      this.campo.addEventListener('input', function () {
        self.select.value = '';                             // texto mudou: escolha anterior deixa de valer
        window.clearTimeout(self.temporizador);
        self.temporizador = window.setTimeout(function () { self.buscar(self.campo.value.trim()); }, 250);
      });
      this.campo.addEventListener('keydown', function (e) { self._teclado(e); });
      this.campo.addEventListener('blur', function () { window.setTimeout(function () { self.fechar(); }, 150); });
      this.lista.addEventListener('mousedown', function (e) {
        var opcao = e.target.closest('[role="option"]');
        if (opcao) { e.preventDefault(); self.escolher(Number(opcao.dataset.indice)); }
      });
    }

    VetAutocomplete.prototype.buscar = async function (termo) {
      if (termo.length < 2) { this.fechar(); this._anunciar(''); return; }
      this.ultimaBusca = termo;
      try {
        var dados = await VetAPI.get(this.url + '?search=' + encodeURIComponent(termo) + '&limit=8');
        if (termo !== this.ultimaBusca) return;            // resposta atrasada de uma busca antiga
        this.itens = dados.results || [];
        this._desenhar();
      } catch (erro) {
        this.fechar();
        this._anunciar('Não foi possível buscar agora. Use a lista de animais.');
        this.aoFalhar();
      }
    };

    VetAutocomplete.prototype._desenhar = function () {
      var self = this;
      this.lista.textContent = '';
      this.ativo = -1;
      this.campo.removeAttribute('aria-activedescendant');
      if (!this.itens.length) {
        this.fechar();
        this._anunciar('Nenhum tutor ou animal encontrado. Use "Cadastrar tutor e animal".');
        return;
      }
      this.itens.forEach(function (animal, indice) {
        var li = document.createElement('li');
        li.id = 'sugestao-' + animal.id;
        li.setAttribute('role', 'option');
        li.setAttribute('aria-selected', 'false');
        li.dataset.indice = String(indice);
        li.className = 'vs-opcao';
        var titulo = document.createElement('span');
        titulo.className = 'font-semibold';
        titulo.textContent = animal.nome + ' (' + animal.especie_display + ')';
        var detalhe = document.createElement('span');
        detalhe.className = 'block text-xs text-gray-600';
        detalhe.textContent = 'Tutor: ' + animal.proprietario_nome + ' · ' + animal.proprietario_telefone;
        li.appendChild(titulo);
        li.appendChild(detalhe);
        self.lista.appendChild(li);
      });
      this.lista.hidden = false;
      this.campo.setAttribute('aria-expanded', 'true');
      this._anunciar(this.itens.length + (this.itens.length === 1 ? ' sugestão.' : ' sugestões.') +
        ' Use as setas para escolher e Enter para confirmar.');
    };

    VetAutocomplete.prototype._teclado = function (e) {
      var aberto = !this.lista.hidden;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!aberto && this.itens.length) { this.lista.hidden = false; this.campo.setAttribute('aria-expanded', 'true'); }
        this._mover(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this._mover(-1);
      } else if (e.key === 'Enter' && aberto && this.ativo >= 0) {
        e.preventDefault();
        this.escolher(this.ativo);
      } else if (e.key === 'Escape') {
        if (aberto) { e.preventDefault(); this.fechar(); } else { this.campo.value = ''; this.select.value = ''; }
      }
    };

    VetAutocomplete.prototype._mover = function (passo) {
      if (!this.itens.length || this.lista.hidden) return;
      var opcoes = this.lista.querySelectorAll('[role="option"]');
      if (this.ativo >= 0) opcoes[this.ativo].setAttribute('aria-selected', 'false');
      this.ativo = (this.ativo + passo + this.itens.length) % this.itens.length;
      var atual = opcoes[this.ativo];
      atual.setAttribute('aria-selected', 'true');
      atual.scrollIntoView({ block: 'nearest' });
      this.campo.setAttribute('aria-activedescendant', atual.id);
    };

    VetAutocomplete.prototype.escolher = function (indice) {
      var animal = this.itens[indice];
      if (!animal) return;
      this.select.value = String(animal.id);
      this.campo.value = animal.nome + ' (' + animal.especie_display + ') — ' + animal.proprietario_nome;
      this.fechar();
      this._anunciar('Selecionado: ' + this.campo.value + '.');
    };

    VetAutocomplete.prototype.fechar = function () {
      this.lista.hidden = true;
      this.campo.setAttribute('aria-expanded', 'false');
      this.campo.removeAttribute('aria-activedescendant');
    };

    VetAutocomplete.prototype._anunciar = function (texto) { if (this.status) this.status.textContent = texto; };

    window.VetAutocomplete = VetAutocomplete;
  }());
  ```
- [x] **6.3 `static/js/agenda.js`** — fluxograma, etapas 3 e 4 ("Consultar horários livres" e "Exibir agenda interativa"):
  ```js
  /* VETSystem — static/js/agenda.js — 7 dias por vez + horários livres (rádios) via /api/horarios-livres/ */
  (function () {
    'use strict';
    var SEMANAS_A_FRENTE = 8;

    function formatar(d) { return String(d.getDate()).padStart(2, '0') + '/' + String(d.getMonth() + 1).padStart(2, '0'); }

    function VetAgenda(o) {
      this.dias = document.getElementById(o.diasId);
      this.horarios = document.getElementById(o.horariosId);       // <fieldset>
      this.status = document.getElementById(o.statusId);
      this.titulo = document.getElementById(o.tituloId);
      this.btnAnterior = document.getElementById(o.anteriorId);
      this.btnProximo = document.getElementById(o.proximoId);
      this.campoData = document.getElementById(o.campoDataId);     // id_data_consulta (reserva sem JS)
      this.campoHora = document.getElementById(o.campoHoraId);     // id_hora_consulta
      this.urlHorarios = o.urlHorarios;
      this.urlDisponibilidades = o.urlDisponibilidades;
      this.ignorar = o.ignorarId || '';
      this.diasAbertos = new Set();                                // dias da semana do JS (0 = domingo)
      this.hoje = new Date(); this.hoje.setHours(0, 0, 0, 0);
      this.inicio = new Date(this.hoje);
      this.selecionada = null;
      this.selecionouHorario = false;
      var self = this;
      this.btnAnterior.addEventListener('click', function () { self._mudarSemana(-7); });
      this.btnProximo.addEventListener('click', function () { self._mudarSemana(7); });
    }

    VetAgenda.prototype.iniciar = async function () {
      var self = this;
      try {
        var disponibilidades = await VetAPI.get(this.urlDisponibilidades);
        disponibilidades.forEach(function (d) { if (d.ativo) self.diasAbertos.add((d.dia_da_semana + 1) % 7); });
      } catch (erro) {
        return false;                                              // o formulário volta aos campos de reserva
      }
      var inicial = null;
      if (this.campoData.value) {                                  // edição: começa no dia já marcado
        var marcada = VetAPI.dataDeIso(this.campoData.value);
        if (marcada >= this.hoje) inicial = marcada;
      }
      if (!inicial) inicial = this._proximoDiaAberto(this.hoje);
      if (inicial) this.inicio = new Date(inicial);
      this._desenharDias();
      if (inicial) await this.selecionarDia(VetAPI.dataIso(inicial), this.campoHora.value.slice(0, 5));
      return true;
    };

    VetAgenda.prototype._proximoDiaAberto = function (aPartirDe) {
      for (var i = 0; i < SEMANAS_A_FRENTE * 7; i++) {
        var dia = new Date(aPartirDe); dia.setDate(dia.getDate() + i);
        if (this.diasAbertos.has(dia.getDay())) return dia;
      }
      return null;
    };

    VetAgenda.prototype._mudarSemana = function (deslocamento) {
      var novo = new Date(this.inicio); novo.setDate(novo.getDate() + deslocamento);
      var limite = new Date(this.hoje); limite.setDate(limite.getDate() + (SEMANAS_A_FRENTE - 1) * 7);
      if (novo < this.hoje) novo = new Date(this.hoje);
      if (novo > limite) return;
      this.inicio = novo;
      this._desenharDias();
      this._status('Mostrando ' + this.titulo.textContent + '. Escolha um dia.');
    };

    VetAgenda.prototype._desenharDias = function () {
      var self = this;
      this.dias.textContent = '';
      var fim = new Date(this.inicio); fim.setDate(fim.getDate() + 6);
      this.titulo.textContent = 'dias de ' + formatar(this.inicio) + ' a ' + formatar(fim);
      for (var i = 0; i < 7; i++) {
        var dia = new Date(this.inicio); dia.setDate(dia.getDate() + i);
        var iso = VetAPI.dataIso(dia);
        var aberto = this.diasAbertos.has(dia.getDay());
        var botao = document.createElement('button');
        botao.type = 'button';
        botao.className = 'vs-dia';
        botao.dataset.data = iso;
        botao.setAttribute('aria-pressed', iso === this.selecionada ? 'true' : 'false');
        botao.setAttribute('aria-label', VetAPI.dataPorExtenso(dia) + (aberto ? '' : ' — clínica fechada'));
        [VetAPI.DIAS_CURTOS[dia.getDay()], formatar(dia), aberto ? '' : 'fechado'].forEach(function (texto, n) {
          if (!texto) return;
          var parte = document.createElement('span');
          parte.className = n === 1 ? 'block font-bold' : 'block text-xs';
          parte.textContent = texto;
          botao.appendChild(parte);
        });
        botao.disabled = !aberto;
        botao.addEventListener('click', function (e) { self.selecionarDia(e.currentTarget.dataset.data); });
        this.dias.appendChild(botao);
      }
      this.btnAnterior.disabled = this.inicio <= this.hoje;
      var limite = new Date(this.hoje); limite.setDate(limite.getDate() + (SEMANAS_A_FRENTE - 1) * 7);
      this.btnProximo.disabled = this.inicio >= limite;
    };

    VetAgenda.prototype.selecionarDia = async function (iso, horaMarcada) {
      if (this.selecionouHorario) {                                 // trocou de dia: limpa a escolha anterior
        this.campoData.value = ''; this.campoHora.value = ''; this.selecionouHorario = false;
      }
      this.selecionada = iso;
      this.dias.querySelectorAll('.vs-dia').forEach(function (b) {
        b.setAttribute('aria-pressed', b.dataset.data === iso ? 'true' : 'false');
      });
      var extenso = VetAPI.dataPorExtenso(VetAPI.dataDeIso(iso));
      this.horarios.setAttribute('aria-busy', 'true');
      this.horarios.classList.add('opacity-50');                   // mantém o desenho anterior enquanto carrega
      this._status('Consultando horários livres de ' + extenso + '…');
      try {
        var url = this.urlHorarios + '?data=' + iso + (this.ignorar ? '&ignorar=' + this.ignorar : '');
        var resposta = await VetAPI.get(url);
        if (this.selecionada !== iso) return;                       // o usuário já clicou em outro dia
        this._desenharHorarios(resposta, extenso, horaMarcada);
      } catch (erro) {
        this._status('Não foi possível consultar os horários. Tente novamente.');
      } finally {
        this.horarios.removeAttribute('aria-busy');
        this.horarios.classList.remove('opacity-50');
      }
    };

    VetAgenda.prototype._desenharHorarios = function (resposta, extenso, horaMarcada) {
      var self = this;
      this.horarios.textContent = '';
      var legenda = document.createElement('legend');
      legenda.className = 'text-sm font-semibold text-gray-700 mb-2';
      legenda.textContent = 'Horários livres — ' + extenso +
        (resposta.aberto ? ' (expediente ' + resposta.inicio + ' às ' + resposta.fim + ')' : '');
      this.horarios.appendChild(legenda);
      var horarios = resposta.horarios.slice();
      var mesmoDia = this.campoData.value === resposta.data;
      if (horaMarcada && mesmoDia && horarios.indexOf(horaMarcada) === -1) { horarios.push(horaMarcada); horarios.sort(); }
      if (!horarios.length) {                                       // decisão "Horário disponível? Não"
        this._status(resposta.aberto ? 'Nenhum horário livre em ' + extenso + '. Escolha outro dia.'
                                     : 'A clínica não atende em ' + extenso + '. Escolha outro dia.');
        return;
      }
      var grade = document.createElement('div');
      grade.className = 'flex flex-wrap gap-2';
      horarios.forEach(function (hora) {
        var rotulo = document.createElement('label');
        rotulo.className = 'vs-slot';
        var radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'horario_agenda';
        radio.value = hora;
        radio.checked = mesmoDia && hora === horaMarcada;
        radio.addEventListener('change', function () {
          self.campoData.value = resposta.data;
          self.campoHora.value = hora;
          self.selecionouHorario = true;
          self._status('Horário escolhido: ' + extenso + ' às ' + hora + '.');
        });
        var texto = document.createElement('span');
        texto.textContent = hora;
        rotulo.appendChild(radio);
        rotulo.appendChild(texto);
        grade.appendChild(rotulo);
      });
      this.horarios.appendChild(grade);
      this._status(horarios.length + (horarios.length === 1 ? ' horário livre' : ' horários livres') + ' em ' + extenso + '.');
    };

    VetAgenda.prototype.recarregar = function () {                 // após conflito: "Não" → volta à agenda
      if (!this.selecionada) return;
      this.campoData.value = ''; this.campoHora.value = ''; this.selecionouHorario = false;
      return this.selecionarDia(this.selecionada);
    };

    VetAgenda.prototype._status = function (texto) { this.status.textContent = texto; };

    window.VetAgenda = VetAgenda;
  }());
  ```
- [x] **6.4 `static/js/consulta_form.js`** — liga as peças. Na criação, envia para `POST /api/consultas/` (decisão "Horário disponível?" → "Registrar consulta"); a edição continua com o POST tradicional.
  ```js
  /* VETSystem — static/js/consulta_form.js — agendamento sem recarregar (melhoria progressiva) */
  (function () {
    'use strict';
    var form = document.getElementById('form-consulta');
    if (!form || !window.VetAPI) return;
    var select = document.getElementById('id_animal');
    var blocos = {
      busca: document.getElementById('bloco-busca'), select: document.getElementById('bloco-select-animal'),
      agenda: document.getElementById('bloco-agenda'), dataHora: document.getElementById('bloco-data-hora')
    };
    blocos.busca.hidden = false; blocos.select.hidden = true;
    blocos.agenda.hidden = false; blocos.dataHora.hidden = true;

    new VetAutocomplete({
      campoId: 'campo-busca', listaId: 'lista-sugestoes', statusId: 'status-busca', selectId: 'id_animal',
      url: form.dataset.urlAnimais,
      aoFalhar: function () { blocos.busca.hidden = true; blocos.select.hidden = false; }
    });
    if (select.selectedIndex > 0) document.getElementById('campo-busca').value = select.options[select.selectedIndex].text;

    var agenda = new VetAgenda({
      diasId: 'agenda-dias', horariosId: 'agenda-horarios', statusId: 'agenda-status', tituloId: 'agenda-titulo',
      anteriorId: 'agenda-anterior', proximoId: 'agenda-proximo', campoDataId: 'id_data_consulta',
      campoHoraId: 'id_hora_consulta', urlHorarios: form.dataset.urlHorarios,
      urlDisponibilidades: form.dataset.urlDisponibilidades, ignorarId: form.dataset.consultaId
    });
    agenda.iniciar().then(function (ok) { if (!ok) { blocos.agenda.hidden = true; blocos.dataHora.hidden = false; } });

    if (form.dataset.modo !== 'criar') return;                      // edição: POST do Django, mesma regra

    var botao = document.getElementById('btn-agendar');
    var caixaErros = document.getElementById('mensagens-form');

    function limparErros() {
      caixaErros.hidden = true; caixaErros.textContent = '';
      form.querySelectorAll('[data-erro-campo]').forEach(function (el) { el.textContent = ''; });
      form.querySelectorAll('[aria-invalid="true"]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
    }

    function mostrarErros(dados) {
      var campos = { animal: 'campo-busca', tipo: 'id_tipo', observacoes: 'id_observacoes' };
      var gerais = [];
      Object.keys(dados || {}).forEach(function (campo) {
        var textos = VetAPI.mensagens(dados[campo]);
        var alvo = form.querySelector('[data-erro-campo="' + campo + '"]');
        if (alvo) {
          alvo.textContent = textos.join(' ');
          if (campos[campo]) document.getElementById(campos[campo]).setAttribute('aria-invalid', 'true');
        } else {
          gerais = gerais.concat(textos);
        }
      });
      caixaErros.hidden = false;                                     // mostra antes de escrever: role="alert" anuncia
      caixaErros.textContent = (gerais.length ? gerais : ['Corrija os campos indicados.']).join(' ');
      caixaErros.focus();
    }

    function mostrarSucesso(consulta) {
      var quando = new Date(consulta.data_hora);                     // ISO com fuso → horário local
      document.getElementById('sucesso-resumo').textContent =
        consulta.animal_nome + ' (tutor: ' + consulta.proprietario_nome + ') — ' + consulta.tipo_display + ' — ' +
        VetAPI.dataPorExtenso(quando) + '/' + quando.getFullYear() + ' às ' +
        String(quando.getHours()).padStart(2, '0') + ':' + String(quando.getMinutes()).padStart(2, '0') +
        '. Status: ' + consulta.status_display + '.';
      document.getElementById('sucesso-detalhe').href = form.dataset.urlDetalhe.replace('/0/', '/' + consulta.id + '/');
      var whatsapp = document.getElementById('sucesso-whatsapp');
      whatsapp.hidden = !consulta.link_whatsapp;
      if (consulta.link_whatsapp) {
        whatsapp.href = consulta.link_whatsapp;
        whatsapp.dataset.confirmarConsulta = String(consulta.id);
        whatsapp.dataset.statusAtual = consulta.status;
      }
      form.hidden = true;
      var painel = document.getElementById('painel-sucesso');
      painel.hidden = false;
      painel.focus();
      VetAPI.anunciar('Consulta agendada com sucesso.');
    }

    form.addEventListener('submit', async function (evento) {
      evento.preventDefault();
      limparErros();
      var data = document.getElementById('id_data_consulta').value;
      var hora = document.getElementById('id_hora_consulta').value;
      var tipo = document.getElementById('id_tipo').value;
      var faltando = {};
      if (!select.value) faltando.animal = ['Escolha o tutor/animal nas sugestões.'];
      if (!data || !hora) faltando.data_hora = ['Escolha um dia e um horário livre na agenda.'];
      if (!tipo) faltando.tipo = ['Escolha o tipo de atendimento.'];
      if (Object.keys(faltando).length) { mostrarErros(faltando); return; }

      var textoOriginal = botao.textContent;
      botao.disabled = true;
      botao.textContent = 'Agendando…';
      try {
        mostrarSucesso(await VetAPI.post(form.dataset.urlConsultas, {
          animal: Number(select.value), data_hora: data + 'T' + hora, tipo: tipo,
          observacoes: document.getElementById('id_observacoes').value
        }));
      } catch (erro) {
        if (erro.status === 400) {
          mostrarErros(erro.dados);
          if (erro.dados && erro.dados.data_hora) agenda.recarregar();
        } else if (erro.status === 403) {
          mostrarErros({ geral: ['Sua sessão expirou. Entre novamente para agendar.'] });
        } else {
          mostrarErros({ geral: ['Não foi possível agendar agora. Tente novamente em instantes.'] });
        }
      } finally {
        botao.disabled = false;
        botao.textContent = textoOriginal;
      }
    });
  }());
  ```
- [x] **6.5 `static/js/status.js`** — fluxograma: "Confirmar agendamento (avisa o tutor)" e "Realizar atendimento ou registrar ausência → Atualizar status":
  ```js
  /* VETSystem — static/js/status.js — ações rápidas de status via POST /api/consultas/<id>/status/ */
  (function () {
    'use strict';
    if (!window.VetAPI) return;
    var base = document.body.dataset.urlApiConsultas;               // "/api/consultas/"
    var TRANSICOES = { agendado: ['confirmado', 'realizado', 'cancelado'], confirmado: ['realizado', 'cancelado'],
                       realizado: [], cancelado: [] };

    function atualizarTela(consulta) {
      document.querySelectorAll('[data-status-badge="' + consulta.id + '"]').forEach(function (selo) {
        selo.className = 'badge badge-' + consulta.status;
        selo.textContent = consulta.status_display;
      });
      document.querySelectorAll('[data-acoes-consulta="' + consulta.id + '"]').forEach(function (grupo) {
        var permitidos = TRANSICOES[consulta.status] || [];
        if (!permitidos.length) { grupo.hidden = true; return; }
        grupo.querySelectorAll('[data-acao-status]').forEach(function (b) {
          b.hidden = permitidos.indexOf(b.dataset.acaoStatus) === -1;
        });
        grupo.querySelectorAll('[data-confirmar-consulta]').forEach(function (a) { a.dataset.statusAtual = consulta.status; });
      });
    }

    function mudarStatus(id, status, observacao, opcoes) {
      return VetAPI.post(base + id + '/status/', { status: status, observacao: observacao || '' }, opcoes)
        .then(function (consulta) {
          atualizarTela(consulta);
          VetAPI.anunciar('Status atualizado para ' + consulta.status_display + '.');
          return consulta;
        })
        .catch(function (erro) {
          var texto = VetAPI.mensagens(erro.dados).join(' ');
          document.querySelectorAll('[data-erro-acoes="' + id + '"]').forEach(function (p) { p.textContent = texto; });
          VetAPI.anunciar(texto);
        });
    }

    document.addEventListener('click', function (evento) {
      var botao = evento.target.closest('[data-acao-status]');
      if (botao) {
        botao.disabled = true;
        mudarStatus(botao.dataset.consultaId, botao.dataset.acaoStatus, botao.dataset.observacao)
          .finally(function () { botao.disabled = false; });
        return;
      }
      var link = evento.target.closest('[data-confirmar-consulta]');
      if (link && link.dataset.statusAtual === 'agendado') {
        // Não cancela o clique: o WhatsApp abre em nova aba e a confirmação segue em paralelo.
        mudarStatus(link.dataset.confirmarConsulta, 'confirmado', 'Tutor avisado pelo WhatsApp.', { keepalive: true });
      }
    });
  }());
  ```
- [x] **6.6 Reescreva `consulta_form.html`.** Mantenha cabeçalho, breadcrumb, título e a legenda de obrigatórios da Fase 5. **Apague o `<script>` antigo de validação.** Estrutura:
  - `{% load static %}`.
  - `<div id="mensagens-form" role="alert" tabindex="-1" class="bg-red-50 border border-red-300 text-red-700 text-sm rounded-lg px-4 py-3 mb-6" {% if not form.non_field_errors %}hidden{% endif %}>` com os `non_field_errors`.
  - `<form method="post" novalidate id="form-consulta" …>` com os atributos:
    - `data-modo="{% if object %}editar{% else %}criar{% endif %}"`
    - `data-consulta-id="{{ object.pk|default:'' }}"`
    - `data-url-consultas="{% url 'api:consulta-list' %}"`
    - `data-url-animais="{% url 'api:animal-list' %}"`
    - `data-url-horarios="{% url 'api:horarios-livres' %}"`
    - `data-url-disponibilidades="{% url 'api:disponibilidade-list' %}"`
    - `data-url-detalhe="{% url 'agendamentos:consulta-detail' 0 %}"`
  - **Bloco 1, só com JS** (`<div id="bloco-busca" class="mb-2 relative" hidden>`):
    - `<label for="campo-busca">Tutor ou animal <span class="text-red-700" aria-hidden="true">*</span></label>`;
    - `<input id="campo-busca" type="text" role="combobox" autocomplete="off" aria-autocomplete="list" aria-expanded="false" aria-controls="lista-sugestoes" aria-describedby="ajuda-busca erro-animal" aria-required="true" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">`;
    - `<p id="ajuda-busca" class="text-xs text-gray-600 mt-1">Digite ao menos 2 letras do nome do tutor ou do animal; use as setas e Enter para escolher.</p>`;
    - `<ul id="lista-sugestoes" role="listbox" aria-label="Sugestões de animal e tutor" hidden class="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-72 overflow-auto"></ul>`;
    - `<p id="status-busca" class="sr-only" role="status" aria-live="polite"></p>`;
    - `<p id="erro-animal" data-erro-campo="animal" class="text-red-700 text-xs mt-1"></p>`.
  - **Bloco de reserva sem JS** (`<div id="bloco-select-animal">`): o label e o `{{ form.animal }}` atuais, mais `<div id="{{ form.animal.auto_id }}_error">`.
  - Os links do fluxo encadeado (Fase 3.2).
  - **Bloco 2, só com JS** (`<fieldset id="bloco-agenda" class="mb-6" hidden>`):
    - `<legend>Data e horário <span class="text-red-700" aria-hidden="true">*</span></legend>`;
    - uma linha com `<button type="button" id="agenda-anterior" class="vs-nav"><span aria-hidden="true">←</span><span class="sr-only">Semana anterior</span></button>`, `<p id="agenda-titulo" class="text-sm font-semibold"></p>` e o botão `agenda-proximo` simétrico ("Próxima semana", →);
    - `<div id="agenda-dias" role="group" aria-label="Escolha o dia" class="grid grid-cols-4 sm:grid-cols-7 gap-2 mb-4"></div>`;
    - `<fieldset id="agenda-horarios" class="min-h-[3rem]"></fieldset>`;
    - `<p id="agenda-status" class="text-sm text-gray-700 mt-2" role="status" aria-live="polite"></p>`;
    - `<p id="erro-agenda" data-erro-campo="data_hora" class="text-red-700 text-xs mt-1"></p>`.
  - **Bloco de reserva** `<div id="bloco-data-hora">`: os campos data e hora atuais, com as `div`s `_error`.
  - Tipo, status (só se `'status' in form.fields`) e observações. Cada um com `<p data-erro-campo="tipo|observacoes" class="text-red-700 text-xs mt-1">`, além das `div`s `_error` do Django e do `_helptext` de observações.
  - Botão `#btn-agendar` com `class="bg-ativo-turquesa text-white font-bold py-3 px-8 rounded-xl hover:opacity-90"` e link "Cancelar".
  - **Fora do `<form>`:** `<section id="painel-sucesso" hidden tabindex="-1" aria-labelledby="titulo-sucesso" class="bg-white rounded-2xl shadow-sm p-8">`, contendo:
    - `<h2 id="titulo-sucesso" class="text-xl font-bold text-ativo-roxo mb-2">Consulta agendada!</h2>`;
    - `<p id="sucesso-resumo" class="text-gray-700 mb-6"></p>`;
    - os links `<a id="sucesso-whatsapp" class="btn-acao btn-acao-whatsapp" target="_blank" rel="noopener" hidden>Confirmar e avisar o tutor pelo WhatsApp<span class="sr-only"> (abre em nova aba)</span></a>`, `<a id="sucesso-detalhe" class="btn-acao">Ver consulta</a>` e `<a href="{% url 'agendamentos:consulta-create' %}" class="btn-acao">Agendar outra consulta</a>`.
  - `{% block extra_js %}` com `autocomplete.js`, `agenda.js` e `consulta_form.js`, nessa ordem (via `{% static %}`).
- [x] **6.7 Ações rápidas de status.** Crie `agendamentos/templates/agendamentos/_acoes_status.html`:
  ```django
  {# Fluxograma: "Confirmar agendamento" e "Realizar atendimento ou registrar ausência → Atualizar status" #}
  {% if consulta.status == 'agendado' or consulta.status == 'confirmado' %}
  <div class="flex flex-wrap items-center gap-2" data-acoes-consulta="{{ consulta.pk }}">
    {% if consulta.link_whatsapp %}
      <a href="{{ consulta.link_whatsapp }}" target="_blank" rel="noopener" class="btn-acao btn-acao-whatsapp"
         data-confirmar-consulta="{{ consulta.pk }}" data-status-atual="{{ consulta.status }}">{% if consulta.status == 'agendado' %}Confirmar e avisar tutor{% else %}Avisar tutor{% endif %}<span class="sr-only"> de {{ consulta.animal.nome }} pelo WhatsApp (abre em nova aba)</span></a>
    {% elif consulta.status == 'agendado' %}
      <button type="button" class="btn-acao" data-acao-status="confirmado" data-consulta-id="{{ consulta.pk }}">Confirmar<span class="sr-only"> consulta de {{ consulta.animal.nome }}</span></button>
    {% endif %}
    <button type="button" class="btn-acao" data-acao-status="realizado" data-consulta-id="{{ consulta.pk }}">Atendimento realizado<span class="sr-only"> — {{ consulta.animal.nome }}</span></button>
    <button type="button" class="btn-acao btn-acao-alerta" data-acao-status="cancelado" data-observacao="Ausência do tutor registrada." data-consulta-id="{{ consulta.pk }}">Registrar ausência<span class="sr-only"> — {{ consulta.animal.nome }}</span></button>
    <p class="w-full text-red-700 text-xs" data-erro-acoes="{{ consulta.pk }}"></p>
  </div>
  {% endif %}
  ```
  Use o include em:
  - `consulta_detail.html`, na coluna de ações;
  - `dashboard.html`, numa nova coluna `<th scope="col">Ações</th>` da tabela "Consultas de hoje".
- [x] **6.8 `base.html`:**
  - No `<body>`, acrescente `data-url-api-consultas="{% url 'api:consulta-list' %}"`.
  - Antes de `{% block extra_js %}`, acrescente:
    ```django
    <script src="{% static 'js/api.js' %}"></script>
    {% if user.is_authenticated %}<script src="{% static 'js/status.js' %}"></script>{% endif %}
    ```
- [x] **6.9 Testes:**
  - os testes de acessibilidade continuam verdes (combobox rotulado e `aria-controls` válido);
  - `consulta-create` contém `data-url-horarios` e o `<select id="id_animal">` de reserva;
  - o dashboard mostra `data-acoes-consulta` para a consulta de hoje (crie uma consulta para hoje às 23:00 pelo ORM).
- [ ] **6.10 [VOCÊ] Checklist manual.** (pendente — adiado para o fim do PI II, junto com o 5.9) Anote em `docs/metricas/checklist_manual.md`:
  1. Agendar só com o teclado: autocomplete, setas, Enter, Tab até a agenda, setas nos horários e Enter.
  2. Forçar um conflito: abra duas abas e agende o mesmo horário. A segunda mostra o erro e recarrega a agenda.
  3. Desativar o JavaScript (DevTools → Disable JavaScript) e agendar pelo formulário de reserva.
  4. Confirmar pelo WhatsApp: abre a conversa e o selo vira "Confirmado".
  5. "Atendimento realizado" e "Registrar ausência" no dashboard.
  6. (Opcional) Leitor de tela Orca (Linux) ou NVDA (Windows) no agendamento.
  7. (Fase 6B) Abrir "Procurar na lista de tutores e animais", trocar de aba com as setas, filtrar, escolher com Enter; Esc fecha e o foco volta ao botão.
- [x] **6.11** PR com CI verde.

## Fase 6B — Seleção de tutor/animal em modal e histórico de peso

Pedido do grupo em 13/10/2026, para rodar **antes da Fase 7**: os dados demo (7.5), as métricas (8.1) e a validação (8.4) já contam com estas funções.

**O que entra:**
- **Filtro de tutores e animais já cadastrados.** No agendamento, o botão "Procurar na lista de tutores e animais" abre um modal (`<dialog>`) com duas abas:
  - **Tutor:** filtra os tutores (nome, telefone, CPF ou e-mail) e, ao escolher um, lista os animais dele.
  - **Animal:** filtra os animais (nome do animal ou do tutor, mais a espécie).
  - Escolher um animal preenche o campo do agendamento e fecha o modal.
  - A busca rápida (combobox da Fase 6) continua igual. O modal é a alternativa para quem prefere navegar pela lista.
- **Histórico de peso.** Toda vez que o peso muda no cadastro do animal (tela, API ou admin), a pesagem é guardada em `RegistroPeso`. O peso de `Animal.peso` continua sendo o **peso atual**. A tela do animal mostra a tabela de pesagens com a variação.
  - **Regra:** um registro por dia. Corrigir o peso duas vezes no mesmo dia atualiza o registro do dia em vez de criar outro.

Arquivos: `models.py`, `services.py`, `views.py`, `admin.py`, `forms.py`, `api/serializers.py`, `api/views.py`, migração `0004`, `animal_detail.html`, `consulta_form.html`, `static/js/seletor_cadastro.js`, `static/js/autocomplete.js`, `static/js/consulta_form.js`, `static/css/vetsystem.css` e testes.

- [x] **6B.1 Modelo `RegistroPeso`** (DER: nova entidade HISTÓRICO_PESO, Animal 1:N).
  - Em `models.py`, depois de `Animal`:
    ```python
    # =============================================================================
    # MODEL: RegistroPeso
    # =============================================================================

    class RegistroPeso(models.Model):
        """
        Histórico de peso do Animal (relação 1:N). Gravado por Animal.save() sempre que
        o peso muda — vale para a tela, a API e o admin (regra em services.registrar_peso).
        Um registro por dia: corrigir o peso no mesmo dia atualiza o registro do dia.
        """
        animal = models.ForeignKey(
            Animal,
            on_delete=models.CASCADE,
            related_name='pesos',
            verbose_name='Animal',
        )
        peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Peso (kg)')
        data = models.DateField(default=timezone.localdate, verbose_name='Data da pesagem')

        class Meta:
            verbose_name = 'Registro de peso'
            verbose_name_plural = 'Histórico de peso'
            ordering = ['-data']
            constraints = [models.UniqueConstraint(fields=['animal', 'data'], name='peso_unico_por_dia')]

        def __str__(self):
            return f'{self.animal.nome}: {self.peso} kg em {self.data:%d/%m/%Y}'
    ```
  - Em `Animal`, acrescente o `save()`:
    ```python
    def save(self, *args, **kwargs):
        """Salva o animal; se o peso mudou, guarda a pesagem no histórico (RegistroPeso)."""
        from . import services  # import local: services importa models
        peso_anterior = (Animal.objects.filter(pk=self.pk).values_list('peso', flat=True).first()
                         if self.pk else None)
        super().save(*args, **kwargs)
        if self.peso is not None and self.peso != peso_anterior:
            services.registrar_peso(self)
    ```
  - Atualize a docstring de cabeçalho de `models.py` (entidades e relacionamentos: `Animal 1:N RegistroPeso`) e a docstring de `Animal` (`peso` = peso atual; o histórico fica em `animal.pesos`).
  - Crie `agendamentos/migrations/0004_registropeso.py`. Ela já leva para o histórico o peso atual de quem tem peso:
    ```python
    """Histórico de peso do animal (RegistroPeso, Animal 1:N) + carga inicial com o peso atual."""
    import django.db.models.deletion
    import django.utils.timezone
    from django.db import migrations, models


    def peso_atual_para_historico(apps, schema_editor):
        Animal = apps.get_model('agendamentos', 'Animal')
        RegistroPeso = apps.get_model('agendamentos', 'RegistroPeso')
        hoje = django.utils.timezone.localdate()
        RegistroPeso.objects.bulk_create(
            RegistroPeso(animal_id=animal.pk, peso=animal.peso, data=hoje)
            for animal in Animal.objects.exclude(peso__isnull=True))


    class Migration(migrations.Migration):
        dependencies = [('agendamentos', '0003_animal_data_nascimento')]

        operations = [
            migrations.CreateModel(
                name='RegistroPeso',
                fields=[
                    ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                    ('peso', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Peso (kg)')),
                    ('data', models.DateField(default=django.utils.timezone.localdate, verbose_name='Data da pesagem')),
                    ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pesos',
                                                 to='agendamentos.animal', verbose_name='Animal')),
                ],
                options={
                    'verbose_name': 'Registro de peso',
                    'verbose_name_plural': 'Histórico de peso',
                    'ordering': ['-data'],
                    'constraints': [models.UniqueConstraint(fields=('animal', 'data'), name='peso_unico_por_dia')],
                },
            ),
            migrations.RunPython(peso_atual_para_historico, migrations.RunPython.noop),
        ]
    ```
    Confira com `makemigrations --check --dry-run`, que deve dizer "No changes detected". Se acusar diferença, ajuste a migração ao model; não gere outra.
- [x] **6B.2 Regras em `services.py`.** Importe `RegistroPeso` junto de `Consulta` e `Disponibilidade` e acrescente:
  ```python
  def registrar_peso(animal, data=None):
      """
      Guarda o peso atual do animal no histórico. Um registro por dia: se o peso for
      corrigido no mesmo dia, o registro do dia é atualizado (não duplica).
      Chamado por Animal.save() quando o peso muda.
      """
      if animal.peso is None:
          return None
      registro, _criado = RegistroPeso.objects.update_or_create(
          animal=animal, data=data or timezone.localdate(), defaults={'peso': animal.peso})
      return registro


  def historico_peso(animal):
      """Pesagens do animal, da mais recente à mais antiga, com a variação (kg) em relação à anterior."""
      registros = list(animal.pesos.order_by('data'))
      anterior = None
      for registro in registros:
          registro.variacao = None if anterior is None else registro.peso - anterior
          anterior = registro.peso
      return list(reversed(registros))
  ```
  Apagar o peso (deixar o campo vazio) não cria registro e não apaga o histórico.
- [x] **6B.3 Telas do histórico de peso.**
  - `AnimalDetailView.get_context_data`: `ctx['historico_peso'] = historico_peso(self.object)` (importe de `.services`). Atualize a docstring (Contexto).
  - `animal_detail.html`:
    - no card, abaixo do peso: `{% if historico_peso %}<span class="block text-xs text-gray-600">pesado em {{ historico_peso.0.data|date:"d/m/Y" }}</span>{% endif %}`;
    - entre o card e o histórico de consultas:
    ```html
    <!-- ===== HISTÓRICO DE PESO (Fase 6B) ===== -->
    <section aria-labelledby="titulo-peso" class="mb-8">
      <h2 id="titulo-peso" class="text-lg font-bold text-ativo-roxo mb-4">Histórico de peso ({{ historico_peso|length }})</h2>
      {% if historico_peso %}
      <div class="bg-white rounded-xl shadow overflow-x-auto">
        <table class="w-full text-sm">
          <caption class="sr-only">Pesagens de {{ animal.nome }}, da mais recente à mais antiga</caption>
          <thead class="bg-ativo-fundo text-left">
            <tr>
              <th scope="col" class="px-4 py-2">Data</th>
              <th scope="col" class="px-4 py-2">Peso</th>
              <th scope="col" class="px-4 py-2">Variação</th>
            </tr>
          </thead>
          <tbody>
            {% for registro in historico_peso %}
            <tr class="border-t border-gray-100">
              <th scope="row" class="px-4 py-2 font-medium text-left">{{ registro.data|date:"d/m/Y" }}</th>
              <td class="px-4 py-2">{{ registro.peso }} kg</td>
              <td class="px-4 py-2">{% if registro.variacao is None %}primeira pesagem{% elif registro.variacao > 0 %}+{{ registro.variacao }} kg{% elif registro.variacao < 0 %}{{ registro.variacao }} kg{% else %}sem alteração{% endif %}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      {% else %}
      <p class="text-sm text-gray-600 bg-white rounded-xl shadow p-4">Nenhuma pesagem registrada. Informe o peso em "Editar".</p>
      {% endif %}
    </section>
    ```
  - `AnimalForm.__init__`: na edição (`self.instance.pk`), troque o `help_text` do peso por "Peso de hoje, em kg. Ao alterar, o valor anterior continua no histórico do animal."
  - `admin.py`: `RegistroPesoInline(admin.TabularInline)` com `model = RegistroPeso`, `extra = 0` e `fields = ('data', 'peso')`; em `AnimalAdmin`, `inlines = [RegistroPesoInline]`.
- [x] **6B.4 API do histórico de peso.**
  - Em `serializers.py`:
    ```python
    class RegistroPesoSerializer(serializers.ModelSerializer):
        class Meta:
            model = RegistroPeso
            fields = ['id', 'data', 'peso']
    ```
  - Em `AnimalViewSet` (importe `RegistroPesoSerializer`):
    ```python
    @extend_schema(responses=RegistroPesoSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='pesos', url_name='pesos')
    def pesos(self, request, pk=None):
        """Histórico de peso do animal, da pesagem mais recente à mais antiga."""
        return Response(RegistroPesoSerializer(self.get_object().pesos.all(), many=True).data)
    ```
  - `PATCH /api/animais/<id>/` com `peso` novo grava o histórico sozinho, pelo `Animal.save()`. Não duplique a regra na API.
  - Atualize a docstring de `api/urls.py` (rota `/api/animais/<id>/pesos/`).
- [x] **6B.5 Modal de seleção — HTML** (`consulta_form.html`).
  - Em `ConsultaCreateView` e `ConsultaUpdateView`, `get_context_data` acrescenta `ctx['especies'] = Animal.ESPECIE_CHOICES`.
  - No `<form id="form-consulta">`, acrescente `data-url-proprietarios="{% url 'api:proprietario-list' %}"` e `data-url-novo-animal="{% url 'agendamentos:animal-create' %}?fluxo=agendamento"`.
  - No `bloco-busca`, logo depois de `ajuda-busca`:
    ```html
    <button type="button" id="abrir-seletor" class="btn-acao mt-2" aria-haspopup="dialog" hidden>Procurar na lista de tutores e animais</button>
    ```
  - Depois do `</form>` e do `painel-sucesso`, ainda dentro de `<div class="max-w-2xl">`:
    ```html
    <!-- ===== SELETOR EM MODAL (Fase 6B): abas Tutor / Animal ===== -->
    <dialog id="seletor-cadastro" aria-labelledby="seletor-titulo" class="vs-dialogo">
      <div class="p-6">
        <div class="flex items-center justify-between gap-4 mb-4">
          <h2 id="seletor-titulo" class="text-lg font-bold text-ativo-roxo">Selecionar tutor e animal</h2>
          <button type="button" class="vs-nav" data-fechar-dialogo><span aria-hidden="true">✕</span><span class="sr-only">Fechar</span></button>
        </div>

        <div role="tablist" aria-label="Procurar por" class="flex gap-2 border-b border-gray-200 mb-4">
          <button type="button" role="tab" id="aba-tutor" aria-controls="painel-tutor" aria-selected="true" class="vs-aba">Tutor</button>
          <button type="button" role="tab" id="aba-animal" aria-controls="painel-animal" aria-selected="false" tabindex="-1" class="vs-aba">Animal</button>
        </div>

        <!-- Aba Tutor: filtra tutores; ao escolher, lista os animais dele -->
        <div role="tabpanel" id="painel-tutor" aria-labelledby="aba-tutor">
          <label for="filtro-tutor" class="block text-sm font-semibold text-gray-700 mb-1">Nome, telefone, CPF ou e-mail do tutor</label>
          <input id="filtro-tutor" type="search" autocomplete="off" aria-describedby="status-tutor"
                 class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <p id="status-tutor" role="status" class="text-xs text-gray-600 mt-1"></p>
          <ul id="lista-tutores" aria-label="Tutores encontrados" class="mt-2 max-h-60 overflow-auto"></ul>
          <div id="animais-do-tutor" class="mt-4 border-t border-gray-100 pt-4" hidden>
            <h3 id="titulo-animais-tutor" tabindex="-1" class="text-sm font-bold text-ativo-roxo mb-2"></h3>
            <ul id="lista-animais-tutor" aria-labelledby="titulo-animais-tutor" class="max-h-48 overflow-auto"></ul>
            <a id="link-novo-animal" href="{% url 'agendamentos:animal-create' %}?fluxo=agendamento"
               class="inline-block mt-2 text-sm font-semibold hover:underline" style="color:#1E7579;">Cadastrar outro animal para este tutor</a>
          </div>
        </div>

        <!-- Aba Animal: filtra por nome (do animal ou do tutor) e espécie -->
        <div role="tabpanel" id="painel-animal" aria-labelledby="aba-animal" hidden>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="sm:col-span-2">
              <label for="filtro-animal" class="block text-sm font-semibold text-gray-700 mb-1">Nome do animal ou do tutor</label>
              <input id="filtro-animal" type="search" autocomplete="off" aria-describedby="status-animal"
                     class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            </div>
            <div>
              <label for="filtro-especie" class="block text-sm font-semibold text-gray-700 mb-1">Espécie</label>
              <select id="filtro-especie" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Todas</option>
                {% for valor, rotulo in especies %}<option value="{{ valor }}">{{ rotulo }}</option>{% endfor %}
              </select>
            </div>
          </div>
          <p id="status-animal" role="status" class="text-xs text-gray-600 mt-1"></p>
          <ul id="lista-animais" aria-label="Animais encontrados" class="mt-2 max-h-72 overflow-auto"></ul>
        </div>
      </div>
    </dialog>
    ```
  - No `extra_js`, inclua `{% static 'js/seletor_cadastro.js' %}` **antes** de `consulta_form.js`.
  - Sem JavaScript, o botão continua `hidden` e o `<dialog>` nunca abre: o formulário de reserva da Fase 6 segue igual.
- [x] **6B.6 CSS** (`static/css/vetsystem.css`, depois do bloco do autocomplete):
  ```css
  /* Seletor de tutor/animal (Fase 6B): <dialog> modal com abas WAI-ARIA */
  .vs-dialogo { width: min(42rem, calc(100vw - 2rem)); max-height: calc(100vh - 4rem); padding: 0; border: 0;
                border-radius: 1rem; box-shadow: 0 20px 40px rgba(0, 0, 0, .25); }
  .vs-dialogo::backdrop { background: rgba(27, 27, 27, .55); }
  .vs-aba { padding: .5rem 1rem; font-weight: 600; color: #4B5563; border-bottom: 3px solid transparent; margin-bottom: -1px; }
  .vs-aba[aria-selected="true"] { color: #1E7579; border-bottom-color: #1E7579; }
  .vs-item { display: block; width: 100%; text-align: left; padding: .5rem .75rem; border-radius: .5rem; }
  .vs-item:hover { background: #EAF7F7; }
  ```
  `#4B5563` dá 7,56:1 e `#1E7579` dá 5,42:1 sobre o branco. A aba ativa também se distingue pela borda, não só pela cor.
- [x] **6B.7 `static/js/seletor_cadastro.js`** (cabeçalho padrão; fluxograma: etapa 2 — "Sugerir proprietário e animal"):
  ```js
  (function () {
    'use strict';

    function textoAnimal(animal) {
      var partes = ['Tutor: ' + animal.proprietario_nome];
      if (animal.raca) partes.push(animal.raca);
      if (animal.peso) partes.push(String(animal.peso).replace('.', ',') + ' kg');
      return partes.join(' · ');
    }

    function resumo(dados, singular, plural) {
      var total = dados.count, mostrados = dados.results.length;
      if (!total) return 'Nenhum ' + singular + ' encontrado.';
      var texto = total + ' ' + (total === 1 ? singular + ' encontrado' : plural + ' encontrados') + '.';
      if (mostrados < total) texto += ' Mostrando os ' + mostrados + ' primeiros; refine o filtro.';
      return texto;
    }

    /* Item de lista = botão (Tab/Enter/Espaço funcionam sem código extra). Dados da API só via textContent. */
    function item(titulo, detalhe, aoClicar) {
      var li = document.createElement('li');
      var botao = document.createElement('button');
      botao.type = 'button';
      botao.className = 'vs-item';
      var t = document.createElement('span');
      t.className = 'font-semibold';
      t.textContent = titulo;
      var d = document.createElement('span');
      d.className = 'block text-xs text-gray-600';
      d.textContent = detalhe;
      botao.appendChild(t);
      botao.appendChild(d);
      botao.addEventListener('click', aoClicar);
      li.appendChild(botao);
      return li;
    }

    function VetSeletor(o) {
      this.dialogo = document.getElementById(o.dialogoId);
      this.abridor = document.getElementById(o.abridorId);
      this.urlTutores = o.urlTutores;
      this.urlAnimais = o.urlAnimais;
      this.urlNovoAnimal = o.urlNovoAnimal;   // animal-create?fluxo=agendamento
      this.aoEscolher = o.aoEscolher;
      this.versoes = {};
      this.temporizadores = {};
      if (!this.dialogo || typeof this.dialogo.showModal !== 'function') return;   // sem <dialog>: fica só a busca rápida
      this.abas = Array.prototype.slice.call(this.dialogo.querySelectorAll('[role="tab"]'));
      var self = this;
      this.abridor.hidden = false;
      this.abridor.addEventListener('click', function () { self.abrir(); });
      this.dialogo.querySelectorAll('[data-fechar-dialogo]').forEach(function (b) {
        b.addEventListener('click', function () { self.dialogo.close(); });
      });
      this.dialogo.addEventListener('click', function (e) { if (e.target === self.dialogo) self.dialogo.close(); });  // clique no fundo
      this.dialogo.addEventListener('close', function () { self.abridor.focus(); });   // Esc também cai aqui
      this.abas.forEach(function (aba) {
        aba.addEventListener('click', function () { self.mostrarAba(aba); });
        aba.addEventListener('keydown', function (e) { self._tecladoAbas(e, aba); });
      });
      this._aoDigitar('filtro-tutor', function () { self.buscarTutores(); });
      this._aoDigitar('filtro-animal', function () { self.buscarAnimais(); });
      document.getElementById('filtro-especie').addEventListener('change', function () { self.buscarAnimais(); });
    }

    VetSeletor.prototype._aoDigitar = function (id, buscar) {
      var self = this;
      document.getElementById(id).addEventListener('input', function () {
        window.clearTimeout(self.temporizadores[id]);
        self.temporizadores[id] = window.setTimeout(buscar, 250);
      });
    };

    VetSeletor.prototype.abrir = function () {
      this.dialogo.showModal();
      this.mostrarAba(this.abas[0]);
      document.getElementById('filtro-tutor').focus();
    };

    /* Abas WAI-ARIA com ativação automática: setas, Home e End trocam de aba. */
    VetSeletor.prototype.mostrarAba = function (escolhida) {
      this.abas.forEach(function (aba) {
        var ativa = aba === escolhida;
        aba.setAttribute('aria-selected', String(ativa));
        aba.tabIndex = ativa ? 0 : -1;
        document.getElementById(aba.getAttribute('aria-controls')).hidden = !ativa;
      });
      if (escolhida.id === 'aba-tutor') this.buscarTutores(); else this.buscarAnimais();
    };

    VetSeletor.prototype._tecladoAbas = function (e, aba) {
      var i = this.abas.indexOf(aba), n = this.abas.length, destino = null;
      if (e.key === 'ArrowRight') destino = this.abas[(i + 1) % n];
      else if (e.key === 'ArrowLeft') destino = this.abas[(i - 1 + n) % n];
      else if (e.key === 'Home') destino = this.abas[0];
      else if (e.key === 'End') destino = this.abas[n - 1];
      if (!destino) return;
      e.preventDefault();
      this.mostrarAba(destino);
      destino.focus();
    };

    /* GET com controle de versão: uma resposta atrasada não sobrescreve a busca mais nova. */
    VetSeletor.prototype._buscar = async function (chave, url, statusId) {
      var versao = (this.versoes[chave] || 0) + 1;
      this.versoes[chave] = versao;
      var status = document.getElementById(statusId);
      status.textContent = 'Buscando…';
      try {
        var dados = await VetAPI.get(url);
        return versao === this.versoes[chave] ? dados : null;
      } catch (erro) {
        if (versao === this.versoes[chave]) status.textContent = 'Não foi possível buscar agora. Tente novamente.';
        return null;
      }
    };

    VetSeletor.prototype.buscarTutores = async function () {
      var termo = document.getElementById('filtro-tutor').value.trim();
      document.getElementById('animais-do-tutor').hidden = true;
      var dados = await this._buscar('tutor',
        this.urlTutores + '?search=' + encodeURIComponent(termo) + '&limit=20', 'status-tutor');
      if (!dados) return;
      var self = this, lista = document.getElementById('lista-tutores');
      lista.textContent = '';
      dados.results.forEach(function (tutor) {
        var animais = tutor.total_animais + (tutor.total_animais === 1 ? ' animal' : ' animais');
        lista.appendChild(item(tutor.nome, tutor.telefone + ' · ' + animais,
          function () { self.mostrarAnimaisDoTutor(tutor); }));
      });
      document.getElementById('status-tutor').textContent = resumo(dados, 'tutor', 'tutores');
    };

    VetSeletor.prototype.mostrarAnimaisDoTutor = async function (tutor) {
      var dados = await this._buscar('tutor', this.urlAnimais + '?proprietario=' + tutor.id + '&limit=50', 'status-tutor');
      if (!dados) return;
      var self = this, lista = document.getElementById('lista-animais-tutor');
      var titulo = document.getElementById('titulo-animais-tutor');
      lista.textContent = '';
      dados.results.forEach(function (animal) {
        lista.appendChild(item(animal.nome + ' (' + animal.especie_display + ')', textoAnimal(animal),
          function () { self.escolher(animal); }));
      });
      titulo.textContent = 'Animais de ' + tutor.nome + ' (' + dados.count + ')';
      document.getElementById('link-novo-animal').href = this.urlNovoAnimal + '&proprietario=' + tutor.id;
      document.getElementById('status-tutor').textContent =
        dados.count ? 'Escolha o animal.' : 'Este tutor ainda não tem animal cadastrado.';
      document.getElementById('animais-do-tutor').hidden = false;
      titulo.focus();
    };

    VetSeletor.prototype.buscarAnimais = async function () {
      var termo = document.getElementById('filtro-animal').value.trim();
      var especie = document.getElementById('filtro-especie').value;
      var url = this.urlAnimais + '?search=' + encodeURIComponent(termo) + '&limit=20' +
        (especie ? '&especie=' + encodeURIComponent(especie) : '');
      var dados = await this._buscar('animal', url, 'status-animal');
      if (!dados) return;
      var self = this, lista = document.getElementById('lista-animais');
      lista.textContent = '';
      dados.results.forEach(function (animal) {
        lista.appendChild(item(animal.nome + ' (' + animal.especie_display + ')', textoAnimal(animal),
          function () { self.escolher(animal); }));
      });
      document.getElementById('status-animal').textContent = resumo(dados, 'animal', 'animais');
    };

    VetSeletor.prototype.escolher = function (animal) {
      this.dialogo.close();        // fecha antes: com o modal aberto, o resto da página fica inerte
      this.aoEscolher(animal);
    };

    window.VetSeletor = VetSeletor;
  }());
  ```
- [x] **6B.8 Ligar o modal ao formulário.**
  - `autocomplete.js`: separe a parte final de `escolher` num método público, usado também pelo modal:
    ```js
    VetAutocomplete.prototype.escolher = function (indice) {
      var animal = this.itens[indice];
      if (animal) this.selecionar(animal);
    };

    /* Também usado pelo seletor em modal (seletor_cadastro.js). */
    VetAutocomplete.prototype.selecionar = function (animal) {
      this.select.value = String(animal.id);
      this.campo.value = animal.nome + ' (' + animal.especie_display + ') — ' + animal.proprietario_nome;
      this.campo.removeAttribute('aria-invalid');
      this.fechar();
      this._anunciar('Selecionado: ' + this.campo.value + '.');
    };
    ```
  - `consulta_form.js`: guarde a instância (`var busca = new VetAutocomplete({...});`) e, logo depois:
    ```js
    if (window.VetSeletor) {
      new VetSeletor({
        dialogoId: 'seletor-cadastro', abridorId: 'abrir-seletor',
        urlTutores: form.dataset.urlProprietarios, urlAnimais: form.dataset.urlAnimais,
        urlNovoAnimal: form.dataset.urlNovoAnimal,
        aoEscolher: function (animal) { busca.selecionar(animal); }
      });
    }
    ```
  - Atualize o comentário de cabeçalho de `consulta_form.html`: a etapa 2 agora tem busca rápida **ou** lista em modal.
- [x] **6B.9 Testes** (`test_models.py`, `test_services.py`, `test_views.py`, `test_api.py`):
  - criar animal com peso → 1 registro com a data de hoje; criar sem peso → 0;
  - mudar o peso no mesmo dia → continua 1 registro, com o valor novo;
  - mudar o peso em outro dia (mova o 1º registro para ontem com `animal.pesos.update(data=hoje - timedelta(days=1))`) → 2 registros;
  - salvar o animal sem mudar o peso (ex.: só o nome) → nenhum registro novo;
  - `historico_peso`: 3 pesagens (10,00 → 10,50 → 10,20) → ordem do mais recente, variações `-0.30`, `0.50` e `None`;
  - POST em `animal-update` com peso novo → registro criado; `animal-detail` mostra "Histórico de peso" e "primeira pesagem";
  - API: `GET /api/animais/<id>/pesos/` → 200 com a lista; `PATCH /api/animais/<id>/` com peso novo → histórico atualizado; sem login → 403;
  - `consulta-create` contém `id="seletor-cadastro"`, `role="tablist"`, `data-url-proprietarios` e uma `<option value="gato">`;
  - os testes de acessibilidade continuam verdes (rótulos dos filtros, `aria-controls` das abas e ids únicos);
  - API: `/api/proprietarios/?search=Silva` e `/api/animais/?especie=cao&search=Rex` (os filtros usados pelo modal).
- [x] **6B.10 Documentação desta fase.**
  - `CLAUDE.md`, na linha do DER: acrescente "Animal 1:N RegistroPeso (histórico, gravado por `Animal.save()` via `services.registrar_peso`)".
  - O passo do modal no checklist manual já está no item **6.10** (passo 7).
  - Registre falhas e correções em `docs/metricas/registro_testes.md`.
- [x] **6B.11 Verificação:**
  - pytest verde, `check` e `makemigrations --check --dry-run` sem mudanças;
  - no `runserver`:
    - agende escolhendo o animal pela aba **Tutor** e depois pela aba **Animal**, com filtro de espécie;
    - edite o peso de um animal duas vezes e confira a tabela na tela do animal;
  - PR com CI verde e merge. O deploy roda a migração `0004` no Render (o `start.sh` já faz `migrate`).

## Fase 7 — Extras (análise de dados, agenda semanal, home pública, dados demo)

- [ ] **7.1 Análise de dados — regra.** Acrescente ao `services.py`. Imports novos: `from collections import Counter`, `from django.db.models import Count, Sum` e `from django.db.models.functions import TruncMonth`.
  ```python
  def _primeiro_dia_do_periodo(hoje, meses):
      ano, mes = hoje.year, hoje.month - (meses - 1)
      while mes <= 0:
          mes += 12
          ano -= 1
      return datetime.date(ano, mes, 1)


  def estatisticas(meses=6):
      """Indicadores do painel de análise de dados (últimos `meses` meses, até hoje)."""
      hoje = timezone.localdate()
      inicio = _primeiro_dia_do_periodo(hoje, meses)
      consultas = Consulta.objects.filter(data_hora__date__range=(inicio, hoje)).order_by()
      total = consultas.count()
      canceladas = consultas.filter(status='cancelado').count()

      por_tipo_bruto = dict(consultas.values_list('tipo').annotate(total=Count('id')))
      por_status_bruto = dict(consultas.values_list('status').annotate(total=Count('id')))
      por_mes_bruto = {m.strftime('%Y-%m'): n for m, n in
                       consultas.annotate(mes=TruncMonth('data_hora')).values_list('mes').annotate(total=Count('id'))}

      por_mes, ano, mes = [], inicio.year, inicio.month
      for _ in range(meses):
          chave = f'{ano:04d}-{mes:02d}'
          por_mes.append({'mes': chave, 'total': por_mes_bruto.get(chave, 0)})
          mes, ano = (1, ano + 1) if mes == 12 else (mes + 1, ano)

      # Ocupação = minutos agendados ÷ minutos de expediente — usa o relacionamento "verifica"
      ocorrencias = Counter((inicio + datetime.timedelta(days=i)).weekday() for i in range((hoje - inicio).days + 1))
      agendados = dict(consultas.exclude(status='cancelado')
                       .values_list('disponibilidade__dia_da_semana').annotate(total=Sum('duracao_minutos')))
      ocupacao = []
      for disp in Disponibilidade.objects.filter(ativo=True).order_by('dia_da_semana'):
          minutos_dia = (disp.hora_fim.hour * 60 + disp.hora_fim.minute) - (disp.hora_inicio.hour * 60 + disp.hora_inicio.minute)
          capacidade = minutos_dia * ocorrencias.get(disp.dia_da_semana, 0)
          usados = agendados.get(disp.dia_da_semana) or 0
          ocupacao.append({'dia': disp.dia_da_semana, 'rotulo': disp.get_dia_da_semana_display(),
                           'minutos_agendados': usados, 'minutos_disponiveis': capacidade,
                           'percentual': round(100 * usados / capacidade, 1) if capacidade else 0.0})
      usados_total = sum(o['minutos_agendados'] for o in ocupacao)
      capacidade_total = sum(o['minutos_disponiveis'] for o in ocupacao)
      return {
          'periodo': {'inicio': inicio.isoformat(), 'fim': hoje.isoformat(), 'meses': meses},
          'total_consultas': total,
          'taxa_cancelamento': round(100 * canceladas / total, 1) if total else 0.0,
          'ocupacao_media': round(100 * usados_total / capacidade_total, 1) if capacidade_total else 0.0,
          'por_tipo': [{'chave': c, 'rotulo': r, 'total': por_tipo_bruto.get(c, 0)} for c, r in Consulta.TIPO_CHOICES],
          'por_status': [{'chave': c, 'rotulo': r, 'total': por_status_bruto.get(c, 0)} for c, r in Consulta.STATUS_CHOICES],
          'por_mes': por_mes,
          'ocupacao_por_dia': ocupacao,
      }
  ```
  Na API, crie `EstatisticasView(APIView)` em `GET /api/estatisticas/?meses=N` (nome `estatisticas`). Ela lê `meses` com `int()`, usa 6 quando inválido, limita entre 1 e 24 e devolve `Response(services.estatisticas(meses))`.
- [ ] **7.2 Análise de dados — painel** em `dashboard.html`, depois das tabelas. Segue as regras da skill de dataviz:
  - **Forma:**
    - indicadores (cards) para os números-chave;
    - colunas para "consultas por mês";
    - barras horizontais para "por tipo";
    - barras de progresso em HTML para "ocupação por dia".
    - Não há gráfico por status, porque os cards de status já existem.
  - **Cor:** série única `#6848A1`, validada pelo validador da skill (banda de luminosidade, croma ≥ 0,10, contraste 6,9:1 no branco). Trilha da ocupação: `#EAE4FA`. Grade: `#E5E7EB` (hairline sólida). Textos de eixo: `#4B5563`. Rótulos: `#1B1B1B`, nunca na cor da série.
  - **Marcas:** barras com no máximo 24 px, ponta arredondada de 4 px e base reta; valor só na ponta; sem legenda (série única: o título já diz o que é).
  - **Acessibilidade:**
    - cada `<canvas role="img">` recebe um `aria-label` gerado com os valores;
    - cada gráfico tem um `<details><summary>Ver dados em tabela</summary><table>` gêmeo (cabeçalhos `scope="col"`; nas linhas, `<th scope="row">`);
    - o tooltip é só um complemento;
    - respeita `prefers-reduced-motion`.
  - **Filtro:** um único `<label for="periodo-analise">Período</label><select id="periodo-analise">` (3, 6 ou 12 meses; padrão 6) acima de tudo. Ao recarregar, o desenho anterior fica com `opacity-50`, sem esqueleto.
  - **Estrutura:**
    - `<section id="analise-dados" aria-labelledby="titulo-analise" data-url="{% url 'api:estatisticas' %}">` com `<h2 id="titulo-analise">Análise de dados</h2>`;
    - o filtro e `<p id="analise-erro" class="text-red-700" hidden>`;
    - 4 cards (`kpi-total`, `kpi-cancelamento`, `kpi-ocupacao`, `kpi-tipo`), com texto "—" até carregar;
    - `<figure>` "Consultas por mês", com `<div class="relative h-64"><canvas id="grafico-mes" role="img" data-titulo="Gráfico de colunas — consultas por mês" aria-label="Carregando"></canvas></div>` e tabela `tabela-mes`;
    - `<figure>` "Consultas por tipo de atendimento" (`grafico-tipo`, `tabela-tipo`);
    - `<figure>` "Ocupação da agenda por dia da semana", com `<ul id="lista-ocupacao">` e a nota "Ocupação = minutos agendados ÷ minutos de expediente (Disponibilidade) no período".
  - **Scripts no `extra_js`:**
    - `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`;
    - `static/js/dashboard_analise.js`, cujo núcleo é:
    ```js
    var COR_SERIE = '#6848A1', COR_HOVER = '#563A8C', COR_GRADE = '#E5E7EB', COR_EIXO = '#4B5563', COR_ROTULO = '#1B1B1B';
    var semAnimacao = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var rotuloNaPonta = { id: 'rotuloNaPonta', afterDatasetsDraw: function (g) {
      var ctx = g.ctx, horizontal = g.options.indexAxis === 'y';
      ctx.save(); ctx.fillStyle = COR_ROTULO; ctx.font = '600 12px Lato, sans-serif';
      g.getDatasetMeta(0).data.forEach(function (barra, i) {
        var v = g.data.datasets[0].data[i]; if (!v) return;
        if (horizontal) { ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(String(v), barra.x + 6, barra.y); }
        else { ctx.textAlign = 'center'; ctx.textBaseline = 'bottom'; ctx.fillText(String(v), barra.x, barra.y - 4); }
      }); ctx.restore(); } };
    function desenharBarras(id, rotulos, valores, horizontal) {   // guarde as instâncias e chame .destroy() antes de redesenhar
      var eixoValor = { beginAtZero: true, grid: { color: COR_GRADE }, border: { display: false }, ticks: { color: COR_EIXO, precision: 0 } };
      var eixoCat = { grid: { display: false }, border: { color: COR_GRADE }, ticks: { color: COR_EIXO } };
      var canvas = document.getElementById(id);
      var grafico = new Chart(canvas, { type: 'bar',
        data: { labels: rotulos, datasets: [{ data: valores, backgroundColor: COR_SERIE, hoverBackgroundColor: COR_HOVER,
                maxBarThickness: 24, borderRadius: 4, borderSkipped: 'start' }] },
        options: { indexAxis: horizontal ? 'y' : 'x', responsive: true, maintainAspectRatio: false,
          animation: semAnimacao ? false : { duration: 300 },
          layout: { padding: { top: horizontal ? 0 : 20, right: horizontal ? 36 : 0 } },
          plugins: { legend: { display: false }, tooltip: { displayColors: false } },
          scales: horizontal ? { x: eixoValor, y: eixoCat } : { x: eixoCat, y: eixoValor } },
        plugins: [rotuloNaPonta] });
      canvas.setAttribute('aria-label', canvas.dataset.titulo + ': ' + rotulos.map(function (r, i) { return r + ' ' + valores[i]; }).join('; ') + '.');
      return grafico;
    }
    ```
  - **Resto do arquivo:**
    - rótulos de mês "mai/26" (`['jan','fev',…,'dez']`);
    - cards preenchidos com `textContent` (números com `toLocaleString('pt-BR')` e "%");
    - tabelas preenchidas com `createElement`/`textContent`;
    - ocupação: cada `<li>` com texto visível ("Segunda-feira — 42% (7 h de 17 h)") e a barra decorativa `aria-hidden="true"`;
    - estado vazio: "Ainda não há consultas no período selecionado.";
    - ao terminar, `VetAPI.anunciar('Análise atualizada: N consultas no período.')`.
- [ ] **7.3 Agenda semanal:**
  - `AgendaSemanalView(LoginRequiredMixin, TemplateView)`, rota `consultas/agenda/` (nome `agenda-semanal`), template `agenda_semanal.html`, mais o link "Agenda" no `partials/menu_principal.html` (`aria-current` quando `nome == 'agenda-semanal'`).
  - `static/js/agenda_semanal.js`:
    - estado `segunda` (segunda-feira da semana atual);
    - botões "Semana anterior", "Hoje" e "Próxima semana";
    - `<h2 id="titulo-semana" aria-live="polite">Semana de dd/mm a dd/mm/aaaa</h2>`;
    - busca `/api/consultas/?inicio=<seg>&fim=<dom>&limit=200` e `/api/disponibilidades/`;
    - desenha uma `<section aria-labelledby>` por dia (sábado e domingo só se houver consulta ou expediente), com `<h3>` "Seg 13/10 · 08:00–19:00" (ou "Fechado") e `<ul>` de consultas;
    - cada item é um link para o detalhe ("09:00 · Rex (João) · Fisioterapia") com o selo `badge-<status>`;
    - dia vazio mostra "Sem consultas";
    - enquanto carrega, mantém o desenho anterior com `opacity-50` e anuncia "N consultas na semana".
- [ ] **7.4 Horários livres na página pública** (raia do Tutor):
  - `HorariosPublicosView(APIView)` em `GET /api/horarios-publicos/` (nome `horarios-publicos`), com `permission_classes = [AllowAny]`, `authentication_classes = []` e `throttle_classes = [AnonRateThrottle]`. Ela percorre os próximos 14 dias com `services.horarios_livres(data)`, guarda até 3 dias com horário (até 8 horários cada) e devolve `{'dias': [{'data': 'AAAA-MM-DD', 'horarios': ['09:00', …]}]}`, sem dados pessoais.
  - `home.html`: `<section id="horarios" aria-labelledby="titulo-horarios" data-url="{% url 'api:horarios-publicos' %}" data-whatsapp="5519987286814">` com o título "Próximos horários livres". O conteúdo de reserva, sem JS, é "Consulte os horários pelo WhatsApp (19) 98728-6814".
  - `static/js/horarios_publicos.js`:
    - por dia, um `<h3>` "terça-feira, 14/10" e uma lista de links `https://wa.me/5519987286814?text=` + `encodeURIComponent('Olá! Gostaria de agendar um atendimento em 14/10 às 09:00 para meu pet.')`;
    - cada link com texto "09:00" + `<span class="sr-only"> — pedir este horário pelo WhatsApp (abre em nova aba)</span>`, `target="_blank"` e `rel="noopener"`.
  - No hero, acrescente o link "Ver horários livres" → `#horarios`.
- [ ] **7.5 Comando `popular_demo`** (para a apresentação e os gráficos):
  - Recusa rodar com `DEBUG=False`, a menos que receba `--forcar`.
  - Chama `criar_horarios_padrao` antes.
  - Usa `random.Random(2026)`.
  - Cria 8 tutores (e-mail `@demo.vetsystem.local`) e 12 animais com `data_nascimento` e `peso`.
  - (Fase 6B) Para cada animal, cria de 3 a 5 `RegistroPeso` mensais nos últimos 180 dias, variando até ±5% do peso atual (o de hoje já nasce pelo `Animal.save()`).
  - Nos dias úteis dos últimos 180 dias, cria de 0 a 3 consultas em horas distintas entre 8 e 18. Status: realizado 85%, cancelado 15%. Tipos: fisioterapia 50%, consulta 30%, acupuntura 20%. Observação `[demo]`.
  - Nos próximos 14 dias úteis, cria de 0 a 2 consultas, agendado ou confirmado.
  - `--apagar` remove só os tutores `@demo.vetsystem.local` (o cascade leva animais e consultas).
  - Imprime o resumo.
- [ ] **7.6 Testes:**
  - `estatisticas`:
    - 3 consultas em segundas-feiras passadas (`proxima_data(0) - timedelta(days=14)` e `- 21`): 2 de fisioterapia realizadas e 1 consulta cancelada;
    - o resultado deve ter total 3, `taxa_cancelamento` 33.3, `por_tipo` com fisioterapia 2 e `ocupacao_por_dia[0]['minutos_agendados'] == 120`.
  - `/api/estatisticas/`: exige login e devolve 200.
  - `/api/horarios-publicos/`: anônimo → 200, sem chaves de animal ou tutor, e `dias` não vazio com `horario_comercial`.
  - Home contém `id="horarios"` e `wa.me`.
  - Agenda semanal: 200 e entra na lista de páginas do teste de acessibilidade.
  - `popular_demo --forcar` cria dados e `--apagar` remove.
- [ ] **7.7 Verificação:**
  - pytest verde.
  - No `runserver`: `popular_demo` local, depois dashboard, agenda semanal e home.
  - **[VOCÊ]** decida se roda `popular_demo --forcar` em produção para a apresentação. Se rodar, apague com `--apagar` antes de a clínica usar de verdade.
  - PR com CI verde.

## Fase 8 — Métricas finais, documentação, diagramas e release

- [ ] **8.1 Comando `medir_desempenho`** (`agendamentos/management/commands/medir_desempenho.py`):
  - Usa `django.test.Client(HTTP_HOST='localhost')`, `force_login` no 1º superusuário e `--repeticoes` (padrão 30).
  - Mede `time.perf_counter()` e imprime uma tabela Markdown: média, mediana, p95 e tamanho em KB.
  - Alvos:
    - `/consultas/nova/` e `/consultas/` (HTML completo, modelo do PI1);
    - `/api/horarios-livres/?data=<próxima segunda>`;
    - `/api/animais/?search=a&limit=8`;
    - `/api/consultas/?inicio=<seg>&fim=<dom>`;
    - `/api/estatisticas/?meses=6`.
  - Se algum alvo não responder 200, levanta `CommandError`.
  - Rode com os dados demo e salve a saída em `docs/metricas/desempenho.md`.
  - Em produção, depois de "acordar" o site, meça também o endpoint público:
    ```bash
    for i in $(seq 20); do curl -s -o /dev/null -w "%{time_total}\n" https://vetsystem-gky6.onrender.com/api/horarios-publicos/; done \
      | python3 -c "import sys,statistics as s;t=[float(x)*1000 for x in sys.stdin];print(f'média {s.mean(t):.0f} ms · mediana {s.median(t):.0f} ms')"
    ```
- [ ] **8.2 Lighthouse "depois":** `ROTAS_EXTRAS="/consultas/agenda/" scripts/lighthouse.sh depois`, com o servidor local rodando.
- [ ] **8.3 Números finais.** Gere `docs/metricas/resultados_pi2.md` com:
  - Lighthouse antes × depois, por tela;
  - contraste antes × depois (Apêndice C);
  - testes (`pytest --cov`: total, aprovados e cobertura por arquivo) e o link para o histórico do CI;
  - endpoints (contagem do schema, Fase 4.6; salve o schema final em `docs/api-openapi.json`);
  - desempenho (8.1);
  - recarregamentos para agendar: tutor existente 2 → 1; tutor novo 6 → 3 (o envio final não recarrega);
  - conflitos e expediente: antes aceitos, agora bloqueados (testes que provam);
  - falhas registradas em `registro_testes.md`.
- [ ] **8.4 [VOCÊ] Validação com a Sra. Fernanda.** O Claude cria o modelo `docs/metricas/validacao_clinica.md`.
  - **Tarefas cronometradas:**
    1. agendar para tutor já cadastrado;
    2. cadastrar tutor e animal novos e agendar;
    3. confirmar e avisar pelo WhatsApp;
    4. registrar atendimento e ausência;
    5. ler a análise de dados;
    6. achar um animal pela lista com filtros (modal, aba Tutor ou Animal) e agendar;
    7. atualizar o peso de um animal e conferir o histórico.
  - **Anotar:** tempo, número de cliques, erros e comentários.
  - **SUS** (escala de 1 a 5):
    1. Eu gostaria de usar este sistema com frequência.
    2. Achei o sistema desnecessariamente complexo.
    3. Achei o sistema fácil de usar.
    4. Precisaria de ajuda de uma pessoa técnica para usar o sistema.
    5. As funções do sistema estão bem integradas.
    6. O sistema tem muita inconsistência.
    7. As pessoas aprenderiam a usar este sistema rapidamente.
    8. Achei o sistema atrapalhado de usar.
    9. Eu me senti confiante ao usar o sistema.
    10. Precisei aprender várias coisas antes de usar o sistema.
  - **Nota SUS:** some (resposta − 1) nos itens ímpares e (5 − resposta) nos pares, e multiplique por 2,5.
- [ ] **8.5 Documentação:**
  - **README:** PI II, funcionalidades novas, stack (DRF, Neon, pytest, GitHub Actions), link `/api/docs/`, como rodar os testes e o selo `![CI](https://github.com/edlucaz/vetsystem/actions/workflows/ci.yml/badge.svg)`.
  - **`docs/documentacao_tecnica.md`:** models (FK "verifica", `data_nascimento` e `RegistroPeso`), tabela de endpoints, `services.py`, testes, acessibilidade, decisões de projeto (Neon × Render DB, JS puro, melhoria progressiva) e "Trabalhos futuros" sem os itens já feitos.
  - **`CLAUDE.md`:** atualize se algo mudou.
  - **Opcional:** em `/mnt/backup500gb/Projetos/Web/CLAUDE.md`, acrescente à linha do `vetsystem/` "PI II; tem CLAUDE.md próprio".
- [ ] **8.6 `docs/diagramas/atualizacoes_relatorio_final.md`.** Copie o Apêndice A, que é o que **você** muda no DER e no fluxograma para a versão final.
- [ ] **8.7 Release:**
  ```bash
  git tag -a v2.0-pi2 -m "VETSystem 2.0 — Projeto Integrador II"
  git push origin v2.0-pi2
  gh release create v2.0-pi2 --title "VETSystem 2.0 — PI II" --notes-file docs/metricas/resultados_pi2.md
  ```

---

## Apêndice A — Fidelidade aos modelos (o que o código faz × o que atualizar nos diagramas)

**DER**

| Elemento do DER (v2) | No código | Ação no DER v3 (você) |
|---|---|---|
| PROPRIETÁRIO (id, nome, cpf, telefone, email) | `Proprietario` | nenhuma |
| ANIMAL (id, nome, especie, raca, data_nascimento, id_proprietario FK) | `Animal` com `data_nascimento` (idade calculada) | acrescentar `peso` (peso atual) e `queixa` |
| — (não existe no v2) | **`RegistroPeso`** (id, data, peso, FK animal; um por dia), Fase 6B | **nova entidade HISTÓRICO_PESO** (id, data, peso, id_animal FK) e relacionamento **"registra" Animal 1:N Histórico de peso**; legenda "Novo no PI2" |
| CONSULTA (id, data_hora, tipo_atendimento, status, observacoes, id_animal FK) | `Consulta` (`tipo` = tipo_atendimento) | acrescentar `duracao_minutos` e **`id_disponibilidade (FK)`** |
| DISPONIBILIDADE (id, dia_semana, hora_inicio, hora_fim) | `Disponibilidade` (`dia_da_semana` = dia_semana) | acrescentar `ativo` |
| possui (Proprietário 1:N Animal) | FK `Animal.proprietario` | nenhuma |
| realiza (Animal 1:N Consulta) | FK `Consulta.animal` | nenhuma |
| verifica (Consulta N:1 Disponibilidade), "sem FK" | **FK `Consulta.disponibilidade`**, preenchida pelo dia da semana; usada na validação e na ocupação | linha contínua; tirar a nota "sem FK"; legenda "Novo no PI2: FK + endpoint de horários livres" |

**Fluxograma swimlane (v2)**

| Etapa | No código | Ajuste no fluxograma v3 (você) |
|---|---|---|
| Solicitar agendamento (Tutor) | home: CTA e horários livres pelo WhatsApp | "telefone, WhatsApp ou presencial (vê horários livres no site)" |
| Realizar login / ① Autenticar | login do Django; API com sessão + CSRF | nenhum |
| Buscar proprietário / ② Sugerir proprietário e animal | combobox + `GET /api/animais/?search=`; ou modal com abas Tutor/Animal e filtros (`/api/proprietarios/?search=`, `/api/animais/?proprietario=&especie=`), Fase 6B | "Sugerir proprietário e animal (busca rápida ou lista com filtros)" |
| Cadastrado? Não → Cadastrar proprietário e animal | fluxo `?fluxo=agendamento` que volta ao agendamento | opcional: "(volta direto ao agendamento)" |
| ③ Consultar horários livres | `GET /api/horarios-livres/` (Consulta × Disponibilidade) | nenhum |
| ④ Exibir agenda interativa / Selecionar horário | `agenda.js` (dias + horários) | nenhum |
| ⑤ Horário disponível? (data + Disponibilidade + sem conflito); Não → ④ | `services.validar_agendamento` no formulário e na API; conflito recarrega a agenda | nenhum |
| Registrar consulta (status: agendado) | `POST /api/consultas/` | nenhum |
| Confirmar agendamento (avisa o tutor) → Receber confirmação | botão "Confirmar e avisar tutor" (status confirmado + WhatsApp) | "status: confirmado · aviso pelo WhatsApp" |
| Realizar atendimento ou registrar ausência → Atualizar status | botões "Atendimento realizado" / "Registrar ausência" (`POST …/status/`) | "cancelado (ausência)" |
| (novo) Atualizar peso do animal | editar o animal grava a pesagem em `RegistroPeso`; histórico na tela do animal e em `GET /api/animais/<id>/pesos/` (Fase 6B) | opcional: "Atualizar peso (histórico)" junto de "Realizar atendimento" |
| Transversal | WCAG 2.1 AA, testes, deploy automático, branches + PR | acrescentar "análise de dados" e "nuvem: Render + Neon" |

## Apêndice B — Pedido técnico do professor × evidência gerada

| Pedido | Evidência | Fase |
|---|---|---|
| Citar a nuvem | Render (web) + Neon (Postgres), URL pública, deploy automático | 1 |
| Citar Git/GitHub | branches por fase, PRs, CI, tags `v1.0-pi1`/`v2.0-pi2`, release | 0–8 |
| PostgreSQL continua? | Neon em produção; CI testa em PostgreSQL 16 | 1, 2 |
| Quais endpoints? | 12 rotas e ~30 operações em `/api/docs/` e `docs/api-openapi.json`, mais `/api/animais/<id>/pesos/` (Fase 6B) | 4, 6B, 8 |
| O que a Disponibilidade permite? | FK "verifica", validação de expediente/conflito, horários livres, ocupação | 2, 4, 7 |
| Horários em tempo real | `/api/horarios-livres/` + agenda em JS | 4, 6 |
| Análise de dados (opcional) | `/api/estatisticas/` + painel acessível | 7 |
| Quantos testes, resultados, falhas | pytest (~80 testes), cobertura, CI, `registro_testes.md` | 2–8 |
| Métricas (tempo, endpoints) | `medir_desempenho`, Lighthouse antes/depois, recarregamentos | 0, 8 |
| Alterações visuais da WCAG | paleta 3,09 → 5,42:1, foco visível, menu no celular, testes a11y | 5 |
| JavaScript no front-end | `api.js`, `autocomplete.js`, `agenda.js`, `status.js`, `seletor_cadastro.js` (modal com abas), gráficos | 6, 6B, 7 |
| Acompanhamento do paciente | histórico de peso com variação (`RegistroPeso`), na tela e na API | 6B |
| Tipos de teste | unitário (services/models), integração (views/API), acessibilidade automatizada, manual (teclado/leitor), usabilidade (SUS) | 2–8 |
| Validação com a clínica | roteiro + SUS + tempos | 8 |
| Próximos passos | "Trabalhos futuros" da documentação | 8 |

## Apêndice C — Paleta e contrastes (WCAG 1.4.3 / 1.4.11)

| Uso | Antes | Depois |
|---|---|---|
| Turquesa (menu, botões, links) | #31A1A7 — 3,09:1 | **#1E7579 — 5,42:1** (4,94:1 sobre #EAF7F7) |
| Laranja (Sair/Entrar/CTA) | #F26A2E — 3,05:1 | **#B9471A — 5,28:1** |
| Texto secundário | gray-400 2,54:1 / gray-500 4,47:1 no fundo | **gray-600 — 6,98:1** |
| Vermelho (excluir/erros) | red-400 2,77:1 / red-500 3,76:1 | **red-700 — 6,47:1** |
| Verde (realizado) | green-600 3,30:1 | **green-700 5,02:1** / selo green-800 6,49:1 |
| Usuário no menu | branco 70% sobre turquesa 2,27:1 | **branco sobre #1E7579 — 5,42:1** |
| Destaque do hero | #F9A96B sobre turquesa 1,61:1 | **#FFD9C2 — 4,12:1 (texto grande, mín. 3:1)** |
| Foco | inexistente na maioria dos elementos | anel #1B1B1B + halo branco (3,18:1 sobre o menu; 17:1 sobre o branco) |
| Série dos gráficos | — | **#6848A1 — 6,93:1**, aprovada no validador da skill de dataviz |

## Verificação de ponta a ponta (ao fim da Fase 8)
1. `.venv/bin/pytest --cov` passa localmente e no CI (PostgreSQL 16), com cobertura ≥ 85% em `agendamentos/`.
2. `check`, `makemigrations --check --dry-run` e `collectstatic` sem erros.
3. Produção: login → agendar para um tutor existente sem recarregar → conflito bloqueado → confirmar pelo WhatsApp → "Atendimento realizado" no dashboard → análise de dados atualiza → `/api/docs/` lista os endpoints.
4. Lighthouse "depois" ≥ 95 em Acessibilidade nas telas medidas; checklist manual de teclado concluído.
5. Os documentos de `docs/metricas/` e `docs/diagramas/` estão preenchidos e prontos para o relatório final.
