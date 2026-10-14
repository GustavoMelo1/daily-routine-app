# Evolução semanal — M10

Você prepara o relato fora do app, por exemplo pedindo a uma IA que revise seus
repositórios e gere um Markdown. O app não acessa GitHub nem cria relatos a partir
de commits. Ele guarda esses textos para você consultar e comparar semanas.

## Usar

1. Abra **Evolução → Importar relato** e selecione um `.md` UTF-8.
2. Confira título, texto e data. Nomes como `04-10-2026.md` e `2026-10-04.md`
   sugerem a data automaticamente; outros nomes exigem preenchimento manual.
3. Salve. Há um relato por data de referência, sem obrigar segunda-feira/domingo.
4. Importe outra semana, selecione um relato anterior e clique em
   **Gerar comparação com IA**. O padrão é o relato anterior mais próximo.

Importar, editar e ler relatos não chama Gemini. Gerar a comparação envia os dois
textos ao Google e pode ter custo. Remova segredos antes de importar/comparar.
A configuração usa `GEMINI_API_KEY` e `GEMINI_COMPARISON_MODEL` no backend;
a chave nunca vai para o frontend. O modelo padrão acompanha o OCR existente
(`gemini-3.6-flash`); altere a variável se sua conta usar outro modelo compatível
com saída estruturada. [Referência do SDK](https://github.com/googleapis/python-genai).

A resposta apresenta avanços documentados, práticas consolidadas e pendências,
com trechos dos relatos. As citações são verificadas contra os textos antes de salvar.
Isso não comprova domínio técnico nem elimina erros de interpretação: confira
as evidências. Ausência de um tema no texto anterior não prova falta de conhecimento.
Não há nota de produtividade, ranking ou pontuação por commits.

Comparações são reutilizadas para o mesmo par de versões. Editar um relato invalida
as comparações que o usam; excluir remove o relato e essas comparações. O texto
original é armazenado sem reescrita automática. Edições são versionadas para evitar
sobrescrita de uma aba desatualizada, mas não há histórico recuperável de versões.

## Contrato da API

| Método e rota | Uso |
| --- | --- |
| `GET /weekly-reports` | Lista por data decrescente, sem conteúdo completo |
| `POST /weekly-reports` | Cria: `report_date`, `title`, `filename`, `content` |
| `GET /weekly-reports/{id}` | Texto completo, versão e metadados |
| `PUT /weekly-reports/{id}` | Mesmos campos mais `version`; conflito retorna 409 |
| `DELETE /weekly-reports/{id}` | Exclui relato e comparações; 204 |
| `GET /weekly-reports/{id}/comparison?previous_report_id=...` | Comparação salva ou `null`; não chama IA |
| `POST /weekly-reports/{id}/compare` | `{ "previous_report_id": 1 }`, ou `{}` para seleção automática |

Sem relato anterior: 422. Data duplicada: 409. Geração indisponível/inválida: 502,
sem apagar os relatos. Conteúdo: até 100 mil caracteres; upload no frontend: até
400 KB. HTML bruto e imagens externas não são executados/carregados na prévia.
Não há escrita do nome enviado no sistema de arquivos: o texto é armazenado no SQLite.

A geração não mantém uma transação SQLite aberta durante a chamada externa.
Se um relato mudar enquanto a IA responde, a comparação não é salva. Um bloqueio
local impede gerações simultâneas no mesmo processo; use um único worker neste app
local. Autenticação, filas distribuídas e publicação na internet não fazem parte
deste marco. A API atual deve permanecer restrita ao computador do usuário.

## Verificação

Backend: CRUD, validação, conflitos de versão/data, cache, invalidação, referências
e falhas do provedor com SQLite temporário. Frontend: leitura de arquivo, segurança
de Markdown, edição, geração explícita e erro com nova tentativa.
Os testes não chamam Gemini. A qualidade da comparação real depende dos relatos
e do modelo configurado, e precisa de revisão humana.
