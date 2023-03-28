import argparse
import dataclasses
import pathlib
import sqlite3

from pointevector.chive import common


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("init")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)
    parser.add_argument("--id", "-i", required=True, type=int)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path
    id: int


def main(args: Args):
    with common.load_manifest(args.manifest) as conn:
        conn.execute("CREATE TABLE metadata(id INTEGER PRIMARY KEY, version TEXT);")
        conn.execute(
            "CREATE TABLE files(relative_path TEXT UNIQUE, hash_method INTEGER, hash_value BLOB);"
        )
        conn.execute(
            "INSERT INTO metadata(id, version)VALUES (?,?);",
            (
                args.id,
                common.__VERSION__,
            ),
        )
        conn.execute(
            "CREATE TABLE faults(relative_path TEXT UNIQUE, calculated_hash_value BLOB);"
        )
        conn.commit()
