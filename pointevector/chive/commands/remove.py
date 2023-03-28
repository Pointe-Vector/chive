import argparse
import dataclasses
import pathlib

from pointevector.chive import common


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("remove")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)
    parser.add_argument("--file", "-f", required=True, type=pathlib.Path)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path
    file: pathlib.Path


def main(args: Args):
    relative_path = args.file.absolute().relative_to(args.manifest.absolute().parent)
    with common.load_manifest(args.manifest) as conn:
        conn.execute(
            "DELETE FROM files WHERE relative_path=?", (relative_path.as_posix(),)
        )
        conn.commit()
