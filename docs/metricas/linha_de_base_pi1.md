# Linha de base do PI1 ("antes")

Medida em 13/10/2026 na tag `v1.0-pi1` + alterações pendentes (IMask, data/hora separados, logout por POST), sem mexer em nenhuma tela.

- **Testes automatizados:** 0.
- **Endpoints de API:** 0.
- **Contraste:** turquesa 3,09:1; laranja 3,05:1; cinza secundário 2,54:1; branco 70% sobre turquesa 2,27:1 (mínimo AA: 4,5:1).
- **Bugs:** botões e cabeçalhos invisíveis (classes `ativo-*` sem efeito); menu inexistente no celular.
- **Regra de agendamento:** aceitava datas fora do expediente e conflitos. No `manage.py shell`,
  `ConsultaForm({'animal': a.pk, 'data_consulta': '2030-01-07', 'hora_consulta': '10:00', 'tipo': 'consulta', 'status': 'agendado'}).is_valid()`
  retornou **`True`**: o PI1 não verifica a Disponibilidade nem conflitos de horário.
- **Recarregamentos de página para agendar:** tutor já cadastrado = 2 (formulário + lista); tutor novo = 6 (cadastro do tutor, lista, cadastro do animal, lista, consulta, lista).

## Lighthouse (desktop, `scripts/lighthouse.sh antes`)

| Tela | Acessibilidade | Boas práticas |
|---|---|---|
| / | 91 | 96 |
| /login/ | 92 | 96 |
| /dashboard/ | 91 | 96 |
| /consultas/ | 74 | 96 |
| /consultas/nova/ | 91 | 96 |
| /animais/ | 84 | 96 |
| /proprietarios/ | 92 | 96 |
| /disponibilidade/ | 91 | 96 |
