CREATE TABLE dias(
id INTEGER PRIMARY KEY,
data TEXT UNIQUE, 
minutos_estudados INTEGER,
frase_do_dia TEXT,
autor_frase TEXT,
tipo TEXT );

CREATE TABLE tarefas(
id INTEGER PRIMARY KEY,
dia_id INTEGER,
descricao TEXT, 
cumprida INTEGER,
FOREIGN KEY (dia_id) REFERENCES dias(id)
);

CREATE TABLE conferencias(
id INTEGER PRIMARY KEY,
semana_inicio TEXT,
semana_fim TEXT,
total_minutos_estudados INTEGER,
percentual_tarefas_cumpridas REAL,
streak_Dias INT,
observacoes TEXT);

CREATE TABLE metas_semanais(
id INTEGER PRIMARY KEY,
semana_inicio TEXT,
semana_fim TEXT,
descricao TEXT,
cumprida INTEGER);

CREATE TABLE erros_quarentena(
id INTEGER PRIMARY KEY,
data TEXT UNIQUE, 
minutos_estudados INTEGER,
frase_do_dia TEXT,
autor_frase TEXT,
tipo TEXT,
status TEXT DEFAULT 'pendente',
motivo_erro TEXT
);

CREATE TABLE tarefas_quarentena(
id INTEGER PRIMARY KEY,
erro_quarentena_id INTEGER,
descricao TEXT, 
cumprida INTEGER,
status TEXT DEFAULT 'pendente',
motivo_erro TEXT,
FOREIGN KEY (erro_quarentena_id) REFERENCES erros_quarentena(id)
);

