SELECT dias.data, dias.frase_do_dia, tarefas.descricao, tarefas.cumprida  FROM dias 
INNER JOIN tarefas ON dias.id = tarefas.dia_id;

SELECT descricao, cumprida FROM tarefas
WHERE cumprida = 0
ORDER BY descricao ASC;

SELECT cumprida, COUNT(*)
FROM tarefas
GROUP BY cumprida;

SELECT SUM(minutos_estudados) FROM dias;

SELECT AVG(minutos_estudados) FROM dias;

SELECT MAX(minutos_estudados), MIN(minutos_estudados) FROM dias; 

SELECT SUM(minutos_estudados) FROM dias 
WHERE data BETWEEN '2026-06-29' AND '2026-07-05';