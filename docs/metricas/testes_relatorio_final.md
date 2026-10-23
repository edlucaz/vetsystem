# Testes — texto para o relatório final (seção de Resultados)

> Pronto para colar. Números conferidos em 23/10/2026 (`pytest --cov`: 129 aprovados, 0 falhas, cobertura 89%).
> Substitui o bloco "32 testes" e amplia o Quadro 1 do relatório parcial.

## Verificação por testes automatizados

A verificação do sistema seguiu a estratégia de testes automatizados em camadas, de modo que cada regra fosse
conferida no nível mais simples possível e, depois, no funcionamento conjunto das partes (DELAMARO; MALDONADO; JINO, 2016; SOMMERVILLE, 2019).
Os testes foram escritos com o **Pytest** e o plugin **pytest-django**, que cria um banco de dados temporário a cada
execução, e a cobertura do código foi medida com o **pytest-cov**. A suíte final reúne **129 testes**, distribuídos
em três tipos (Tabela 4).

**Tabela 4 — Testes automatizados do VETSystem**

| Tipo | Qtd. | O que verifica | Exemplos |
|---|---:|---|---|
| Unidade | 39 | Regras de negócio isoladas: horários livres, expediente, conflitos, transições de status, modelos e formulários | Consulta no mesmo horário de outra é recusada; peso "12,50" com vírgula é aceito |
| Integração | 66 | Telas, rotas da API REST e comandos funcionando com o banco de dados | `POST /api/consultas/` cria a consulta; sem login a API responde 403; cadastro de tutor volta ao agendamento |
| Acessibilidade | 24 | Estrutura exigida pela WCAG 2.1 nas telas: rótulos, títulos, foco, `scope` em tabelas, atributos ARIA | Todo campo tem rótulo; erros ligados ao campo por `aria-describedby` |
| **Total** | **129** | **129 aprovados, 0 falhas** | |

Fonte: elaborado pelos autores (2026).

A cobertura alcançou **89%** do código do sistema, com **99%** no módulo de regras de agendamento (`services.py`),
**96%** nos modelos de dados e **100%** nas rotas da API. Como todas as regras ficam concentradas no módulo
`services.py`, chamado tanto pelos formulários quanto pela API, a alta cobertura desse módulo garante que as duas
formas de agendar obedecem às mesmas verificações.

Os testes também rodam automaticamente por **integração contínua** (GitHub Actions): a cada envio de código ao
repositório, a suíte é executada em um banco **PostgreSQL 16**, o mesmo tipo usado em produção, e uma alteração só
é incorporada à versão principal quando todos os testes passam.

Além dos testes automatizados, o fluxo completo foi conferido no navegador (Chrome controlado pelo Playwright):
busca do tutor pelo teclado, agenda de horários livres, agendamento pela API, conflito de horário aberto em duas
abas e mudança de status no painel.

## Falhas encontradas e correções

Seguindo o ciclo "testar, falhar, corrigir e testar de novo", toda falha foi registrada com causa e correção
(`docs/metricas/registro_testes.md`). O Quadro 1 resume as principais: duas eram defeitos herdados do PI I e as
demais surgiram durante o desenvolvimento do PI II.

**Quadro 1 — Falhas encontradas pelos testes e correções**

| Teste | Falha | Causa | Correção |
|---|---|---|---|
| Edição de consulta passada alterando só observações | Recusada com "a data deve ser no futuro" | O formulário considerava o horário sempre alterado e revalidava a data | Valor inicial do horário passou a ter o mesmo tipo do campo |
| Peso do animal com vírgula ("12,50") | Recusado com "Informe um número" | O campo numérico rejeitava a vírgula antes da conversão | Campo próprio que troca a vírgula por ponto |
| Testes de acessibilidade (23) | Todos falharam na versão do PI I | Faltavam o link "Pular para o conteúdo", rótulos nos filtros, `scope` nas tabelas e a ligação das mensagens de erro aos campos | Novo modelo de página e formulários com esses elementos; 23 de 23 aprovados |
| Teste no navegador da agenda | Botões que deveriam sumir continuavam visíveis | A regra de estilo dos botões anulava o atributo `hidden` | Regra `[hidden] { display: none }` no CSS |
| Peso registrado duas vezes no mesmo dia | Comparação do valor 12,80 falhava | Número decimal do banco comparado com número de ponto flutuante | Comparação com o tipo `Decimal` |

Fonte: elaborado pelos autores (2026).

O resultado mostra que os testes cumpriram dois papéis: **encontraram defeitos** que passariam despercebidos no uso
comum (como os dois herdados do PI I) e **protegeram as mudanças seguintes**, já que cada nova funcionalidade foi
incorporada sem quebrar as anteriores.

---

> Citações já presentes na Fundamentação teórica e na lista de referências do guia (Delamaro, Maldonado e Jino, 2016;
> Sommerville, 2019). Se o relatório já tiver uma "Tabela 4", renumere.
