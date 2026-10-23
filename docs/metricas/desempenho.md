# Desempenho (PI II)

Medido em 2026-10-23 com `manage.py medir_desempenho` (30 repetições, cliente de teste do Django, SQLite local, dados do `popular_demo`: 200 consultas passadas e 13 futuras).

| Alvo | Média (ms) | Mediana (ms) | p95 (ms) | Tamanho (KB) |
|---|---|---|---|---|
| `/consultas/nova/` | 5.8 | 5.0 | 5.8 | 20.4 |
| `/consultas/` | 73.4 | 71.4 | 75.8 | 290.0 |
| `/api/horarios-livres/?data=2026-10-26` | 3.4 | 3.3 | 3.5 | 0.2 |
| `/api/animais/?search=a&limit=8` | 4.3 | 3.9 | 5.5 | 2.0 |
| `/api/consultas/?inicio=2026-10-26&fim=2026-11-01` | 5.8 | 5.7 | 6.3 | 1.6 |
| `/api/estatisticas/?meses=6` | 9.8 | 9.7 | 10.1 | 1.2 |
