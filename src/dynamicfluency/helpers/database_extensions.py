from __future__ import annotations

import sqlite3


def connect_to_database(database_file: str) -> sqlite3.Cursor:
    """Connects to the specifed sqlite3 database with a row-based cursor."""
    database = sqlite3.connect(database_file)
    database.row_factory = sqlite3.Row
    return database.cursor()
