import contextlib
import pathlib
import sqlite3

__VERSION__ = "0.1.0"


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@contextlib.contextmanager
def load_manifest(filepath: pathlib.Path):
    with sqlite3.connect(filepath) as conn:
        conn.row_factory = dict_factory
        try:
            yield conn
        finally:
            pass
