# Checklist manual de acessibilidade e usabilidade

> **Como foi conferido.** Os itens marcados "automático" foram executados no Chrome por `scripts/checklist_automatico.py`
> (`.venv/bin/python scripts/checklist_automatico.py`, banco SQLite próprio com os dados de demonstração): o script aperta
> as teclas e confere o resultado na página. Itens que dependem de julgamento humano (leitor de tela, clareza das mensagens)
> continuam para conferir à mão. No relatório, descrever como "verificação automatizada no navegador", não como teste com usuário.

## Fase 5 — Teclado e celular (WCAG 2.1 AA)

Data: 23/10/2026 (automático) · Responsável: Lucas Eduardo Rocha · Navegador: Google Chrome via Playwright (`scripts/checklist_automatico.py`)

Navegação só com Tab, Shift+Tab, Enter e Esc; menu no celular com DevTools a 375 px.

| # | Verificação | Resultado |
|---|---|---|
| 1 | O 1º Tab mostra "Pular para o conteúdo"; Enter leva o foco ao conteúdo principal | ✅ automático |
| 2 | O foco é sempre visível (anel escuro com halo branco), inclusive no menu turquesa | ✅ automático (inclui o novo anel no campo de data) |
| 3 | A ordem do Tab segue a ordem visual (menu → conteúdo → rodapé) em todas as telas | ✅ automático (nenhum `tabindex` positivo) |
| 4 | Shift+Tab volta na ordem inversa, sem armadilhas de foco | ✅ automático |
| 5 | Formulários (tutor, animal, consulta, horário) preenchidos e enviados só pelo teclado | ◐ parcial: envio e erros pelo teclado (automático); preencher um cadastro inteiro — conferir à mão |
| 6 | Com erro de validação, a mensagem aparece e é lida junto do campo | ✅ automático (`aria-invalid` + `aria-describedby`); leitura em voz — conferir com leitor de tela |
| 7 | Filtros e busca (consultas, animais, proprietários) operáveis pelo teclado | ⏳ conferir à mão (o Tab alcança todos os filtros — automático) |
| 8 | Celular (375 px): o botão "Menu" abre/fecha o menu (`aria-expanded` muda) e todos os links ficam acessíveis | ✅ automático |
| 9 | Celular (375 px): sem rolagem horizontal nas telas principais | ✅ automático (8 telas) |
| 10 | Logout ("Sair") acionável pelo teclado | ✅ automático |

Problemas encontrados (corrigidos em 23/10/2026, branch `fase-8-entrega-final`):
- **375 px — rolagem horizontal** no painel, em Consultas e em Horários: os textos `sr-only` dos botões, por serem `position: absolute`,
  escapavam da caixa da tabela. Correção: caixas das tabelas com `overflow-x-auto relative` (a tabela rola dentro da caixa) e o
  indicador "atendimento mais procurado" com fonte menor no celular.
- **Foco invisível no filtro de data** (Consultas): o campo de data recebe o foco num subcampo interno, que não ativa `:focus-visible`.
  Correção: `input[type="date"]:focus` e o ícone de calendário com o mesmo anel de foco.

## Fase 6 — JavaScript do agendamento

Data: 23/10/2026 (automático) · Responsável: Lucas Eduardo Rocha · Navegador: Google Chrome via Playwright (`scripts/checklist_automatico.py`)

| # | Verificação | Resultado |
|---|---|---|
| 1 | Agendar só com o teclado: autocomplete, setas, Enter, Tab até a agenda, setas nos horários e Enter | ✅ automático |
| 2 | Conflito: duas abas agendando o mesmo horário — a segunda mostra o erro e recarrega a agenda | ✅ automático |
| 3 | JavaScript desativado (DevTools → Disable JavaScript): agendar pelo formulário de reserva | ✅ automático |
| 4 | Confirmar pelo WhatsApp: abre a conversa e o selo vira "Confirmado" | ✅ automático |
| 5 | "Atendimento realizado" e "Registrar ausência" no dashboard | ✅ automático |
| 6 | (Opcional) Leitor de tela Orca (Linux) ou NVDA (Windows) no agendamento | ⏳ pendente (precisa de pessoa com leitor de tela) |

Problemas encontrados: nenhum nos itens automáticos (o script falha com a mensagem da tela se algo quebrar).

