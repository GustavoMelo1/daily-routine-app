CREATE TABLE dias(
id INTEGER PRIMARY KEY,
data TEXT UNIQUE, 
minutos_estudados INTEGER,
frase_do_dia TEXT,
tipo TEXT );

CREATE TABLE tarefas(
id INTEGER PRIMARY KEY,
dia_id INTEGER,
descricao TEXT, 
cumprida INTEGER,
FOREIGN KEY (dia_id) REFERENCES dias(id));

CREATE TABLE conferencias(
id INTEGER PRIMARY KEY,
semana_inicio TEXT,
semana_fim TEXT,
total_minutos_estudados INTEGER,
percentual_tarefas_cumpridas REAL,
streak_Dias INT,
observacoes TEXT);