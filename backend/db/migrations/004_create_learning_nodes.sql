CREATE TABLE learning_nodes (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES learning_nodes(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 160),
    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1))
);
CREATE INDEX learning_nodes_parent ON learning_nodes(parent_id);
