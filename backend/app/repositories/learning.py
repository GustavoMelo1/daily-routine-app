def list_nodes(connection):
    return [dict(id=row[0], parent_id=row[1], title=row[2], completed=bool(row[3]), notes=row[4], notes_version=row[5])
            for row in connection.execute('SELECT id,parent_id,title,completed,notes,notes_version FROM learning_nodes ORDER BY id')]


def update_notes(connection, node_id, notes, version):
    return connection.execute(
        'UPDATE learning_nodes SET notes=?,notes_version=notes_version+1 WHERE id=? AND notes_version=?',
        (notes, node_id, version),
    ).rowcount


def find_node(connection, node_id):
    return connection.execute('SELECT id,parent_id FROM learning_nodes WHERE id=?', (node_id,)).fetchone()


def insert_node(connection, title, parent_id):
    return connection.execute('INSERT INTO learning_nodes(title,parent_id) VALUES (?,?)', (title, parent_id)).lastrowid


def update_node(connection, node_id, title, completed):
    return connection.execute('UPDATE learning_nodes SET title=?,completed=? WHERE id=?', (title, int(completed), node_id)).rowcount


def delete_node(connection, node_id):
    return connection.execute('DELETE FROM learning_nodes WHERE id=?', (node_id,)).rowcount
