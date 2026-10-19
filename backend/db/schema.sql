CREATE TABLE learning_nodes (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES learning_nodes(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1))
);
CREATE INDEX learning_nodes_parent ON learning_nodes(parent_id);

CREATE TABLE weekly_reports (
    id INTEGER PRIMARY KEY,
    report_date TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE weekly_comparisons (
    id INTEGER PRIMARY KEY,
    previous_report_id INTEGER NOT NULL REFERENCES weekly_reports(id) ON DELETE CASCADE,
    current_report_id INTEGER NOT NULL REFERENCES weekly_reports(id) ON DELETE CASCADE,
    previous_version INTEGER NOT NULL,
    current_version INTEGER NOT NULL,
    result_json TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(previous_report_id, current_report_id, previous_version, current_version)
);

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

CREATE TABLE image_imports (
    id INTEGER PRIMARY KEY,
    image_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attempt_token TEXT,
    extracted_payload TEXT,
    publication_digest TEXT
);
