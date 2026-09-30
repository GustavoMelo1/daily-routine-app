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

## Sessão seguinte — base SQLite

Bloco de aproximadamente uma hora, conforme informado pelo usuário.

### Feito

- Confirmada a opção por uma tabela no banco da aplicação, controlada pelo
  backend, em vez de um histórico JSON ou banco separado da pipeline.
- Criada a migração `001_create_image_imports.sql` e adicionada a mesma
  tabela ao `schema.sql`, usado na criação de bancos novos.
- Testados status inicial, rejeição de hash duplicado e de status inválido.
- Criada `find_image_import_by_hash` no repositório, com testes de hash
  inexistente e de recuperação do registro correspondente entre dois registros.
- Suíte completa verificada: 44 testes passaram, com um aviso de depreciação
  do `google-genai`.

A migração ainda não foi aplicada ao banco real. Os testes usaram bancos
temporários. Não há novas rotas nem integração do controle com o lote.

### Próxima sessão

Criar a função de inserção de importações e seus testes; depois definir as
transições de estado e a integração pelo backend. Planejar a aplicação da
migração com backup e verificação de preservação dos dados existentes.

Manter o cálculo de hash. O leitor JSON e seus testes ainda existem, mas
não estão ligados ao lote; removê-los quando a substituição estiver pronta.

Definir quando uma imagem pode ser marcada como concluída, incluindo
publicação parcial e dias já existentes: ausência de exceção, sozinha,
não comprova que todas as tarefas foram gravadas. Não alterar o banco real
nem reprocessar fotos pelo Gemini durante os testes.

Continuar em blocos pequenos, explicando o fluxo antes de acrescentar código.
