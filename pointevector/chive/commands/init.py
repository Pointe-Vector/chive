import argparse
import dataclasses
import pathlib
from typing import Union
import uuid

from pointevector.chive import common


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("init")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)
    parser.add_argument("--archive-id", "-a", type=str, default=None)
    parser.add_argument("--copy-id", "-c", type=str, default=None)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path
    archive_id: Union[int, None]
    copy_id: Union[int, None]


def main(args: Args):
    with common.load_manifest(args.manifest) as conn:
        conn.execute("CREATE TABLE metadata(id INTEGER PRIMARY KEY, version TEXT);")
        conn.execute(
            "CREATE TABLE files(relative_path TEXT UNIQUE, hash_method INTEGER, hash_value BLOB);"
        )
        conn.execute(
            "INSERT INTO metadata(archive_id, copy_id, version) VALUES (?,?,?);",
            (
                args.archive_id or uuid.uuid4().int,
                args.copy_id or uuid.uuid4().int,
                common.__VERSION__,
            ),
        )
        conn.execute(
            "CREATE TABLE faults(relative_path TEXT UNIQUE, calculated_hash_value BLOB);"
        )
        conn.commit()
