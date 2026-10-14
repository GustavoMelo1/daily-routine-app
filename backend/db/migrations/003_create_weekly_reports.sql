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
