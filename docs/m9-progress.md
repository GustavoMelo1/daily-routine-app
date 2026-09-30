# M9 — Ponto de retomada

## Sessão de 30/09/2026

Bloco de estudo: 30 minutos, conforme registro solicitado pelo usuário
(não é uma medição automática de tempo).

### Feito

- Cálculo do hash SHA-256 pelo conteúdo da imagem em `pipeline/tracking.py`.
- Leitura inicial de histórico JSON, retornando conjunto vazio quando o
  arquivo não existe e rejeitando estruturas que não sejam listas de textos.
- Quatro testes com arquivos temporários reais, sem mocks: mesmo conteúdo,
  conteúdo alterado, histórico ausente e leitura de histórico existente.
- Escopo do refactor M11 registrado em `m11-refactor.md`.

### Ainda não implementado

- Gravação do histórico e integração com o lote.
- Ignorar imagens já concluídas e controlar novas tentativas.
- Logs em arquivo e agendamento.

### Próxima sessão

Foi proposta a troca da persistência JSON por SQLite; confirmar essa escolha
com o usuário antes de implementar. Manter o cálculo de hash e seus testes.
O leitor JSON atual é uma etapa inicial, não um controle de processamento
já conectado ao lote.

Definir quando uma imagem pode ser marcada como concluída, incluindo
publicação parcial e dias já existentes: ausência de exceção, sozinha,
não comprova que todas as tarefas foram gravadas. Não alterar o banco real
nem reprocessar fotos pelo Gemini durante os testes.

Continuar em blocos pequenos, explicando o fluxo antes de acrescentar código.
