# Hospedagem pessoal

Esta configuração é para uma pessoa, em um servidor Linux com Docker Compose e
acesso SSH. Não cria contas de usuários e não publica o app na internet.
Primeiro escolha o servidor; os comandos abaixo são executados nele, salvo indicação.

## Como o acesso funciona

O frontend compilado usa `/api`. O Caddy pede usuário e senha antes de entregar
qualquer página ou rota da API. A API não publica a porta 8000 no host.
O único acesso publicado é `127.0.0.1:8080`, alcançado por um túnel SSH.
O navegador pede a senha e pode mantê-la em memória até a sessão ser fechada.

Não troque o endereço por `0.0.0.0` nem abra a porta 8080 no firewall.
HTTP Basic não deve atravessar a internet sem criptografia: aqui o tráfego remoto
passa pelo SSH. Para usar um domínio ou acessar pelo celular sem túnel,
prepare HTTPS e controle de acesso antes de expor o serviço.

## Preparar

Na raiz do projeto, copie `deploy/.env.example` para `deploy/.env`.
Esse arquivo não vai para o Git. O `.env` do backend no teu computador não é
copiado para o servidor nem para as imagens Docker.

Gere um hash de senha, digitando a senha quando solicitado:

```sh
docker run --rm -it caddy:2-alpine caddy hash-password
```

No `deploy/.env`, configure `APP_USER` (somente letras e números),
`APP_PASSWORD_HASH` e a chave do Gemini. Coloque o hash entre aspas simples para
preservar os caracteres `$`. Sem usuário ou hash o Compose recusa a inicialização.
Não publique a saída de `docker compose config`, pois ela pode mostrar segredos.

```sh
chmod 600 deploy/.env
docker compose --env-file deploy/.env config --quiet
docker compose --env-file deploy/.env up -d --build
docker compose --env-file deploy/.env ps
```

O primeiro início cria um banco vazio. Nos próximos, as migrações são aplicadas
antes de iniciar a API, com backup do banco existente. A API usa um processo,
sem `--reload`, e o volume `routine_data` persiste entre recriações dos containers.
Não execute `docker compose down -v`: essa opção remove o volume com os dados.
Reinício automático não é monitoramento: confira `ps` e os logs se ficar indisponível.

## Abrir no teu computador

No PowerShell local, mantenha este comando aberto, substituindo usuário e servidor:

```powershell
ssh -N -L 127.0.0.1:8080:127.0.0.1:8080 usuario@servidor
```

Abra `http://127.0.0.1:8080`. Use o usuário e a senha original do hash,
não a chave do Gemini. Fora do túnel, o servidor não deve responder na porta 8080.

## Levar o banco atual

Pare API, lote e agendamento no Windows antes de copiar o banco atual. Guarde uma
cópia original separada. Transfira a cópia por SCP para o servidor, sem usar Git.
Faça isto antes de usar o app hospedado: substituir um banco que já tem dados
novos exige decidir qual cópia preservar.

Com o serviço parado e o banco de destino ainda vazio:

```sh
docker compose --env-file deploy/.env stop web api
docker compose --env-file deploy/.env cp ./rotina.db api:/data/rotina.db
docker compose --env-file deploy/.env run --rm --no-deps --user root api chown 1000:1000 /data/rotina.db
docker compose --env-file deploy/.env up -d
```

Não mantenha duas instalações recebendo dados: os bancos não são sincronizados.

## Backup e recuperação

Para criar uma cópia consistente, inclusive com a API em uso:

```sh
docker compose --env-file deploy/.env exec api python -m db.backup --output /data/backups
docker compose --env-file deploy/.env cp api:/data/backups ./deploy/backups
```

Copie os backups para fora do servidor por SCP. O volume sozinho não protege
contra perda do servidor. Combine uma rotina diária antes de depender da hospedagem;
este pacote não instala agendamento de backup. Backups e cópias de migração não
têm retenção automática: acompanhe o espaço disponível.

Para recuperar, pare ambos os serviços, preserve o banco atual, escolha uma cópia
que passou em `PRAGMA integrity_check` e siga o procedimento de importação acima,
copiando-a para `/data/rotina.db`. Depois confira dias, tarefas, relatos e notas.
Teste uma recuperação em uma instalação descartável antes de precisar dela.

## Fotos

O agendamento do Windows e a pasta local não são enviados automaticamente.
Ainda não existe upload de foto pelo navegador. Como opção manual, transfira uma
pasta de imagens para o servidor por SCP e execute:

```sh
docker compose --env-file deploy/.env cp ./images api:/tmp/images
docker compose --env-file deploy/.env exec api python -m pipeline.batch --folder /tmp/images --log-file /data/batch.log
```

Isso chama o Gemini. Os arquivos em `/tmp` são temporários; guarde os originais.
O lote usa a API internamente, sem abrir a porta 8000 nem carregar a senha do site.
Não há tarefa agendada no servidor nesta entrega.

## Verificação antes de usar

- Sem credenciais, `/` e `/api/dias?ano=2026&mes=10` devem responder 401.
- Com credenciais, o calendário deve carregar sem chamadas para `localhost:8000`.
- Crie um registro descartável, reinicie os containers e confira a persistência.
- Gere um backup e confira a leitura dele em uma instalação separada.
- Confira que 8000 e 8080 não são acessíveis pelo IP público.
- Teste a comparação de relatos separadamente; hospedagem não corrige erros 503 do Gemini.

A base foi preparada sem Docker disponível no ambiente de desenvolvimento.
Build, autenticação no proxy e persistência precisam passar por essa verificação
no servidor antes de considerar o deploy concluído.

Referências: [autenticação do Caddy](https://caddyserver.com/docs/caddyfile/directives/basic_auth),
[variáveis do Compose](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).
