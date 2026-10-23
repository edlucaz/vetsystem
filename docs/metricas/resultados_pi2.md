# VETSystem 2.0 — Resultados do PI II

Medido em 2026-10-23. Linha de base do PI1: `linha_de_base_pi1.md`.

## Acessibilidade (Lighthouse, desktop) — antes × depois

| Tela | Acessibilidade antes | Acessibilidade depois | Boas práticas (antes → depois) |
|---|---|---|---|
| `/` | 91 | **96** | 96 → 96 |
| `/login/` | 92 | **100** | 96 → 96 |
| `/dashboard/` | 91 | **100** | 96 → 96 |
| `/consultas/` | 74 | **100** | 96 → 96 |
| `/consultas/nova/` | 91 | **96** | 96 → 96 |
| `/animais/` | 84 | **100** | 96 → 96 |
| `/proprietarios/` | 92 | **100** | 96 → 96 |
| `/disponibilidade/` | 91 | **100** | 96 → 96 |
| `/consultas/agenda/` (nova no PI II) | — | **100** | — → 96 |

Relatórios: `docs/metricas/lighthouse/antes/` e `depois/`. Todas as telas ≥ 95 (meta da verificação final).

## Contraste (Apêndice C do plano)

| Uso | Antes | Depois |
|---|---|---|
| Turquesa (menu, botões, links) | #31A1A7 — 3,09:1 | #1E7579 — 5,42:1 |
| Laranja (Sair/Entrar/CTA) | #F26A2E — 3,05:1 | #B9471A — 5,28:1 |
| Texto secundário | gray-400 2,54:1 / gray-500 4,47:1 | gray-600 — 6,98:1 |
| Vermelho (excluir/erros) | red-400 2,77:1 / red-500 3,76:1 | red-700 — 6,47:1 |
| Verde (realizado) | green-600 3,30:1 | green-700 5,02:1 |
| Usuário no menu | 2,27:1 | 5,42:1 |
| Destaque do hero | 1,61:1 | 4,12:1 (texto grande) |
| Série dos gráficos | — | #6848A1 — 6,93:1 |

## Testes

- `pytest --cov`: **129 testes, 129 aprovados**, 0 falhas; cobertura total **89%** (meta ≥ 85%).
- Histórico do CI (PostgreSQL 16): https://github.com/edlucaz/vetsystem/actions/workflows/ci.yml

| Arquivo | Cobertura |
|---|---|
| `admin.py` | 100% |
| `api/serializers.py` | 91% |
| `api/urls.py` | 100% |
| `api/views.py` | 100% |
| `forms.py` | 91% |
| `models.py` | 96% |
| `services.py` | 99% |
| `urls.py` | 100% |
| `views.py` | 91% |
| `management/commands/criar_horarios_padrao.py` | 100% |
| `management/commands/popular_demo.py` | 97% |
| `management/commands/criar_superusuario.py` | 0% (script de deploy) |
| `management/commands/medir_desempenho.py` | 0% (ferramenta de medição) |

## Endpoints

Schema final em `docs/api-openapi.json`: **13 rotas e 29 operações**, documentadas em `/api/docs/`.

## Desempenho

Tabela completa em `desempenho.md` (30 repetições, SQLite local, dados demo).

| Alvo | Média (ms) | p95 (ms) | KB |
|---|---|---|---|
| `/consultas/nova/` | 5,8 | 5,8 | 20,4 |
| `/consultas/` | 73,4 | 75,8 | 290,0 |
| `/api/horarios-livres/` | 3,4 | 3,5 | 0,2 |
| `/api/animais/?search=a&limit=8` | 4,3 | 5,5 | 2,0 |
| `/api/consultas/` (semana) | 5,8 | 6,3 | 1,6 |
| `/api/estatisticas/?meses=6` | 9,8 | 10,1 | 1,2 |

Produção (Render + Neon), `/api/horarios-publicos/`, 20 requisições após acordar o site: **média 468 ms · mediana 316 ms**. A 1ª requisição levou ~57 s (plano gratuito do Render hiberna).

## Recarregamentos para agendar

| Fluxo | PI1 | PI II |
|---|---|---|
| Tutor existente | 2 | **1** |
| Tutor novo | 6 | **3** (o envio final não recarrega) |

## Conflitos e expediente

Antes (PI1) o sistema aceitava consultas sobrepostas e fora do expediente; agora são bloqueados por `services.validar_agendamento`. Testes que provam:
- `test_forms.py::test_criacao_em_conflito_e_invalida`
- `test_services.py::test_validar_agendamento_rejeita_conflito`
- `test_services.py::test_conflito_remove_horarios_sobrepostos`
- `test_views.py::test_criar_consulta_em_conflito_mostra_erro`
- `test_api.py::test_criar_consulta_em_conflito_retorna_400`
- `test_api.py::test_criar_consulta_fora_do_expediente_retorna_400`

## Falhas registradas

Todas as falhas de teste e correções estão em `registro_testes.md` (Fases 2, 5, 6 e 6B).

## Validação com a clínica

Pendente: `validacao_clinica.md` (tempos e nota SUS com a Sra. Fernanda).
