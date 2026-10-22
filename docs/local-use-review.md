# Revisão para uso pessoal

O aplicativo pode ser usado localmente, mas não foi certificado como livre de
vulnerabilidades. Esta revisão do código não substitui um teste de segurança completo.

## Limites importantes

- Não há autenticação/autorização. Quem conseguir acessar a API pode alterar
  registros e solicitar operações com Gemini. Mantenha o servidor em
  `127.0.0.1`, sem exposição pública ou encaminhamento de portas. CORS não é login.
  O pacote de [hospedagem pessoal](private-deployment.md) adiciona senha no proxy
  e acesso por túnel SSH; a API isoladamente continua sem autenticação.
- Excluir um dia pelo frontend remove tarefas em requisições separadas. Uma
  falha no meio pode deixar uma exclusão parcial. A publicação de imagens, por
  outro lado, é transacional por imagem.
- A quarentena armazena erros, mas ainda não tem fluxo de correção/republicação.
- Renomear/marcar tópicos não tem controle de versão entre abas. Notas e relatos
  possuem proteção de versão; evite editar o mesmo checklist em várias abas.
- O OCR e as comparações reais precisam ser revisados. Datas existentes não são
  sobrescritas; fotos que conflitam podem falhar até revisão manual.
- Somente fotos e relatos enviados explicitamente aos fluxos de IA saem para o
  Gemini. Notas de aprendizado ficam locais. Não envie segredos ou credenciais.
- Backups automáticos acontecem nas migrações, não a cada edição. Faça cópias
  periódicas do banco com a API e o lote parados. Notas podem ser baixadas em `.md`.
- A lista de aprendizado carrega todas as notas. Isso atende uma base pessoal
  pequena; paginação/busca no servidor serão necessárias se ela crescer muito.

## Proteções existentes

SQL parametrizado nos repositórios, validação dos pedidos, chaves estrangeiras,
backup nas migrações, confirmação antes de excluir ramos e renderização Markdown
sem HTML bruto ou imagens externas. Conexões SQLite são individuais por pedido.
Testes automatizados incluem conflitos de versão e preservação de rascunho após erro.

## Verificação manual sugerida

Crie uma área de teste, um subtópico e uma nota; salve e recarregue. Abra a mesma
nota em duas abas, salve em uma e confirme que a outra recebe conflito sem perder
o texto. Baixe a nota antes de descartar o rascunho. Confira também o tema escuro
e a tela pequena. Não houve validação visual de navegador nesta entrega.
