# Atualizações do DER e do fluxograma para o relatório final

O que o código faz × o que o grupo muda nos diagramas (versão final).

> **v3 gerada (2026-10-23):** `der_v3.svg/png` e `fluxograma_v3.svg/png` nesta pasta, criados por
> `scripts/diagramas/gerar_v3.py` com todos os ajustes abaixo aplicados. Os elementos têm ids
> (`der-*`, `flx-*`) usados pelo roteiro de vídeo (`scripts/video/`).

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
