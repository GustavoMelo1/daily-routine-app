SELECT dias.data, dias.frase_do_dia, tarefas.descricao, tarefas.cumprida  FROM dias 
INNER JOIN tarefas ON dias.id = tarefas.dia_id;

SELECT descricao, cumprida FROM tarefas
WHERE cumprida = 0
ORDER BY descricao ASC;