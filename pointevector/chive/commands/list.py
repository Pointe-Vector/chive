import argparse
import dataclasses
import logging
import pathlib

from pointevector.chive import common


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("list")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path


def main(args: Args):
    with common.load_manifest(args.manifest) as conn:
        for file in conn.execute(
            "SELECT relative_path, hash_method, HEX(SUBSTR(hash_value, 1, 32)) AS root_hash FROM files ORDER BY relative_path;"
        ).fetchall():
            logging.getLogger().info(file)
