from __future__ import annotations

from sqlite3 import Connection, Cursor, Row


def get_row_cursor(connection: Connection) -> Cursor:
    """Configures the connection to a row-based factory, and then returns the cursor
    Modifies the connection in place.
    """
    connection.row_factory = Row
    return connection.cursor()
