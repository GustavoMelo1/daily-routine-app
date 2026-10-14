# Importação de imagens — M9

## Instalação

Na pasta `backend`, configure `.env`, instale as dependências e execute:

```powershell
python db/migrate.py
python -m uvicorn app.main:app --reload
```

O migrador cria um banco novo ou atualiza o existente em uma transação.
Antes de alterar um arquivo existente, cria um backup SQLite consistente ao lado
dele (`rotina.db.<data UTC>.backup`). Migrações aplicadas têm checksum registrado;
não edite migrações antigas. Pare processos que escrevem no banco antes de migrar.
Para restaurar, pare a API e o agendador, preserve o banco atual e copie o backup
para o caminho configurado em `DB_URL`. O backup inclui os dados anteriores à migração.

Coloque imagens diretamente em `backend/images/` e rode:

```powershell
python -m pipeline.batch
python -m pipeline.batch --folder "C:\caminho\fotos"
```

O lote consulta `/image-imports/health` antes de gastar com OCR. Imagens concluídas
são ignoradas pelo conteúdo SHA-256, mesmo se o nome mudar. Imagens alteradas têm
novo hash. O arquivo não deve ser editado enquanto estiver sendo processado.

## Falhas e retomada

```text
pending -> processing -> completed
                |
                v
              failed -> pending
```

- Cada início recebe um token; uma tentativa antiga não pode publicar pela nova.
- Dias, tarefas, quarentena e conclusão da imagem são confirmados juntos.
  Um conflito faz rollback de toda a publicação daquela imagem.
- O payload validado fica salvo antes da publicação. Se a API falhar depois,
  o próximo lote reaproveita esse payload sem repetir OCR.
- Falha antes de salvar o payload pode exigir outra chamada ao Gemini.
- Uma resposta perdida após o commit é reconciliada consultando o status.
- Tentativas `processing` há menos de uma hora são ignoradas como ocupadas.
  Após uma hora sem atualização, podem ser retomadas pelo próximo lote.
- Uma foto diferente com uma data já existente gera conflito: não apaga nem
  sobrescreve registros. Revise os dados; não exclua um dia real só para forçar a importação.
- Alterar a imagem gera outro hash. O lote não substitui o checkpoint de um hash
  existente; revisão manual de quarentena segue fora do M9.

Logs: `backend/logs/batch.log`, até 2 MB por arquivo com três rotações.
Falhas em uma imagem não impedem as seguintes. Saída `1` indica falha; `0` indica
nenhuma falha, podendo incluir imagens ignoradas/concluídas/ocupadas. Não significa
que todos os arquivos foram publicados naquela execução.

## Agendamento no Windows

Na pasta `backend`, usando o Python que tem as dependências:

```powershell
.\scripts\install_schedule.ps1 -PythonPath (Get-Command python).Source -Time '20:00'
Get-ScheduledTaskInfo -TaskName DailyRoutineImageImport
```

A tarefa usa o usuário atual, sem senha ou privilégios administrativos, diariamente
às 20h. O computador precisa estar ligado e a sessão conectada; uma execução
perdida pode iniciar quando o Windows estiver disponível. Não há execuções
simultâneas e o limite é de 55 minutos. Isso não é um serviço de produção.

O script usa a API local na porta 8000. Se ela não estiver rodando, inicia uma API
temporária e encerra somente esse processo ao terminar. Não encerra servidores
que você abriu. Uma API existente incompatível precisa ser reiniciada após migrar.
Use `API_BASE_URL=http://localhost:8000` para essa configuração.

A instalação não executa OCR imediatamente. Execuções agendadas enviam novas fotos
ao Gemini e podem consumir sua cota. Confira a pasta antes do horário agendado.
Uploads temporários feitos pelo OCR são removidos ao terminar, quando o serviço permite.

```powershell
Disable-ScheduledTask -TaskName DailyRoutineImageImport
Enable-ScheduledTask -TaskName DailyRoutineImageImport
```

Problemas ao iniciar a API ficam em `logs/api-scheduler-error.log`; falhas do
agendador, em `logs/scheduler-error.log`. Os logs podem conter dados de erro dos
registros: não publique a pasta. O arquivo `.env` e os backups também são locais.
