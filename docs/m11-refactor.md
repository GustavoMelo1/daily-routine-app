# M11 — Refactor planejado

Pedido registrado em 30/09/2026. Este documento descreve trabalho futuro,
não funcionalidades já implementadas. Continuar o M9 antes deste bloco.

## Objetivo

Revisar a organização do projeto inteiro para facilitar manutenção,
crescimento e entendimento pelo autor. A pipeline é uma prioridade:
a distribuição atual dos arquivos está difícil de acompanhar.

## Escopo a revisar

- Mapear responsabilidades e dependências antes de propor a árvore de pastas.
- Apresentar a estrutura proposta e explicar cada pasta antes de mover arquivos.
- Avaliar quais módulos devem ser agrupados, separados ou unificados por
  responsabilidade. Não juntar tudo em um arquivo nem criar camadas apenas
  para dar aparência de organização.
- Padronizar nomes em inglês: funções, variáveis, módulos e, com migração
  planejada, tabelas, colunas e contratos da API e do frontend.
- Preservar os dados existentes; testar migrações em uma cópia antes de
  qualquer alteração no banco utilizado pelo usuário.
- Simplificar os testes da pipeline, reduzir preparação repetida e explicar
  o cenário, a execução e as verificações de cada teste.
- Manter mocks onde ajudam a isolar dependências externas e complementar
  com testes de integração; não trocar ferramentas só por aparência.
- Revisar código sem uso, duplicação, configuração, imports e documentação.

## Forma de trabalho

- Ensinar durante a refatoração: o usuário precisa conseguir entender e
  manter o resultado, não apenas copiar os trechos.
- Definir uma lista fechada de mudanças e critérios de conclusão antes de
  começar, evitando um refactor interminável.
- Fazer alterações pequenas, verificadas por testes, preservando o
  comportamento; separar correções de bugs de mudanças de organização.
- Commits em inglês, com prefixos convencionais sem escopo, como
  `refactor:` e `test:`. Não commitar automaticamente sem solicitação.

## Critérios de conclusão propostos

- Responsabilidades e pontos de entrada claros e documentados.
- Testes relevantes passando, sem chamadas pagas ao Gemini na suíte padrão.
- Compatibilidade entre pipeline, API, banco e frontend verificada.
- Migrações verificadas sem perda dos dados existentes.
- README e instruções de execução alinhados à estrutura final.
- O usuário consegue explicar o fluxo e localizar onde fazer uma mudança.
