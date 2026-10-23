# Roteiro do vídeo — parte técnica (VETSystem, PI II)

Vídeo gerado por `scripts/video/gravar_video.py`: as telas aparecem na ordem do **fluxograma v3**. No painel da direita
ficam a etapa do fluxograma e as entidades/relacionamentos do **DER v3** da cena, com destaque e zoom.
O quadro tracejado "câmera" (canto inferior direito, 680×190 px) é o lugar do seu rosto.

## Como gravar

| Jeito | Comando | Quando usar |
|---|---|---|
| **A — pós-produção** (recomendado) | `.venv/bin/python scripts/video/gravar_video.py` | Gera `video_saida/video_completo.mp4` e `video_saida/cenas/cena_NN.mp4` (1920×1080, sem som). Depois grave rosto e voz com OBS lendo as falas abaixo e junte no editor (Shotcut/Kdenlive/CapCut): webcam por cima do quadro "câmera". |
| **B — ao vivo** | `.venv/bin/python scripts/video/gravar_video.py --ao-vivo` | Abre o Chrome em tela cheia; no OBS, capture a janela + webcam + microfone. Você fala e aperta **Enter** no terminal para cada cena. |

Opções: `--ritmo 1.3` (tudo 30% mais lento, para dar tempo da fala) · `--cenas 4,5` (regravar só algumas) ·
`--sem-camera` (painel sem o quadro da câmera) · `--manter-banco` (não recria os dados).
O banco do vídeo (`video_saida/video.sqlite3`) é recriado a cada execução com os dados de demonstração;
login `fernanda` / `ativopet2026`. Nada disso toca no banco de produção.

Duração da versão automática: cerca de **2min47s**. Com as falas, use `--ritmo 1.3` a `1.6` ou congele quadros no editor.

## Cenas e falas sugeridas

| # | Início | Na tela | Fluxograma | DER |
|---|---|---|---|---|
| 1 | 0:00 | Página pública → "Próximos horários livres" | Início · Solicitar agendamento (6) | Consulta · verifica · Disponibilidade |
| 2 | 0:11 | Login → painel | Realizar login · Autenticar (1) | — |
| 3 | 0:24 | Nova consulta: autocomplete "Th" → janela com abas e filtro | Buscar proprietário · Sugerir (2) | Proprietário · possui · Animal |
| 4 | 0:40 | "Juliana" sem resultado → cadastro do tutor → cadastro do animal | Cadastrado? Não · Cadastrar | Proprietário → possui → Animal |
| 5 | 1:11 | Agenda: escolhe o dia e mostra os horários livres | Consultar horários livres (3) · Agenda interativa (4) | Consulta · verifica · Disponibilidade |
| 6 | 1:19 | Escolhe horário; outra pessoa marca o mesmo; erro de conflito | Selecionar · Horário disponível? **Não** (5) | Consulta · verifica · Disponibilidade |
| 7 | 1:29 | Escolhe outro horário → "Consulta agendada!" | Disponível? **Sim** · Registrar consulta | Animal · realiza · Consulta · verifica · Disponibilidade |
| 8 | 1:39 | "Confirmar e avisar o tutor pelo WhatsApp" → detalhe da consulta | Confirmar (7) · Receber confirmação | Consulta |
| 9 | 1:49 | Painel → Consultas de hoje: "Atendimento realizado" e "Registrar ausência" | Realizar atendimento · Atualizar status | Consulta |
| 10 | 2:02 | Ficha do Paçoca → Editar peso → Histórico de peso | Atualizar peso (8) · Registrar pesagem | Animal · registra · Histórico_peso |
| 11 | 2:20 | Agenda semanal · Análise de dados · Horários de funcionamento · /api/docs | Quadro transversal | Disponibilidade (na tela de horários) |
| 12 | 2:43 | Volta à página inicial | Fim | — |

**1 — Página pública.** "O fluxo começa com o tutor. Na página inicial ele já vê os próximos horários livres da clínica,
calculados pela API a partir das consultas e da tabela de Disponibilidade — o relacionamento *verifica* do DER — e chama
a clínica pelo WhatsApp."

**2 — Login.** "A Sra. Fernanda entra com usuário e senha. A sessão do Django também autentica a API REST, com proteção CSRF,
então as telas usam a API sem um segundo login."

**3 — Busca.** "Para agendar, ela digita o nome do tutor ou do animal e as sugestões chegam pela API enquanto digita.
Quem prefere pode abrir a lista completa, com abas de tutor e animal e filtros. Aqui aparecem Proprietário e Animal,
ligados pelo relacionamento *possui*, um para muitos."

**4 — Cadastro.** "Se o tutor não está cadastrado — a decisão 'Cadastrado? Não' — o cadastro é feito sem sair do agendamento:
primeiro o tutor, depois o animal, que já vem ligado a esse tutor. Ao salvar, o sistema volta direto para a agenda."

**5 — Horários livres.** "A agenda mostra só os horários livres do dia escolhido. Dias fechados aparecem bloqueados,
porque a Disponibilidade define o expediente de cada dia da semana."

**6 — Conflito.** "Se outra pessoa ocupar o mesmo horário antes de salvar, a regra do services.py recusa: o horário
não está mais disponível. A mensagem aparece e a agenda é recarregada — é o 'Não' do losango."

**7 — Registrar.** "Com um horário livre, a consulta é gravada com status *agendado*. No DER: o Animal *realiza* a Consulta,
e a Consulta guarda a chave da Disponibilidade do dia — o relacionamento *verifica*, que no PI II virou chave estrangeira."

**8 — Confirmar.** "Um clique confirma a consulta e abre o WhatsApp do tutor com a mensagem pronta. O status passa
para *confirmado*."

**9 — Atendimento.** "No dia, a lista de consultas de hoje permite registrar o atendimento realizado ou a ausência do tutor,
sem recarregar a página; o status é atualizado pela API."

**10 — Peso.** "Etapa nova do PI II: ao atualizar o peso do animal, o sistema grava uma pesagem no histórico.
No DER é a entidade Histórico de peso, ligada ao Animal pelo relacionamento *registra*, um para muitos."

**11 — Transversal.** "Além do fluxo, o sistema tem a agenda semanal, a análise de dados com indicadores e gráficos,
o cadastro do expediente — a entidade Disponibilidade — e a API documentada em OpenAPI. Por trás de tudo:
acessibilidade WCAG 2.1 AA, 129 testes automatizados, integração contínua e publicação na nuvem com Render e Neon."

**12 — Fim.** "Esse é o fluxo completo do VETSystem, do pedido do tutor ao histórico do animal."

## Ficha técnica (para `Modelo-Ficha_Tecnica_do_video.docx`)
- Captura de tela: Playwright + Google Chrome, 1920×1080, roteiro automatizado (`scripts/video/gravar_video.py`).
- Diagramas: fluxograma v3 e DER v3 (`docs/diagramas/`), gerados por `scripts/diagramas/gerar_v3.py`.
- Câmera e voz: OBS Studio. Edição: [editor usado].
- Dados: fictícios (comando `popular_demo`); nenhum dado real de clientes da clínica.
