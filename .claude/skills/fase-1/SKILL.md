---
name: fase-1
description: Fase 1 do docs/PLANO_PI2.md — guia os passos [VOCÊ] do Neon e do Render e verifica o site no ar.
argument-hint: "[sua resposta, ao retomar depois de um passo [VOCÊ]]"
effort: low
disable-model-invocation: true
---
Leia `docs/PLANO_PI2.md`, seção **Fase 1**. Os passos 1.1 a 1.3 são meus ([VOCÊ]): mostre-os de forma resumida e pare até eu dizer que terminei. Não peça nem exiba senhas ou a string de conexão do banco.

Quando eu disser que terminei, rode a verificação do passo 1.4 (o `curl` deve responder 200; o primeiro acesso pode levar ~1 min). Se não responder 200, pare e me diga o que conferir nos logs do Render. Se responder, lembre-me do login como `fernanda` (1.4) e do passo 1.5, e marque os checkboxes da Fase 1 no plano num branch `fase-1-nuvem` → commit, push, PR, merge (ainda não há CI antes da Fase 2).

$ARGUMENTS
