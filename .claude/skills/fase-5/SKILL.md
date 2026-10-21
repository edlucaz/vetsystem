---
name: fase-5
description: Executa a Fase 5 do docs/PLANO_PI2.md — acessibilidade WCAG 2.1 AA.
argument-hint: "[sua resposta, ao retomar depois de um passo [VOCÊ]]"
effort: medium
disable-model-invocation: true
---
Leia `docs/PLANO_PI2.md` e o `CLAUDE.md`. Execute **somente a Fase 5**, na ordem dos passos, sem acrescentar nada fora do escopo. Quando o plano trouxer código, use-o como está. Passos marcados **[VOCÊ]** são meus: pare e me peça. Ao terminar, rode as verificações da fase, registre falhas de teste e correções em `docs/metricas/registro_testes.md`, marque os checkboxes da fase no plano, faça commit, push e abra o PR. Aguarde o CI ficar verde e faça o merge.

Se houver texto depois desta linha, é a minha resposta a um passo [VOCÊ]: **não recomece a fase**. Confira o branch `fase-5-*` e o `git status` e continue de onde parou.

$ARGUMENTS

## Contexto (economia de tokens)

- Ao fechar cada etapa, grave o progresso no documento do plano (ou no registro da tarefa) e peça ao
  Lucas numa linha: `/compact foco: <próxima etapa>`. Sessão acima de ~150k tokens custa caro mesmo com cache.
- Não releia arquivo, imagem ou diff já vistos; para retomar, leia o progresso gravado e o registro
  "Onde parei" que aparece no início da sessão.
