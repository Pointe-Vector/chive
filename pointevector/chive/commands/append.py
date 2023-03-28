import argparse
import dataclasses
import pathlib

from pointevector.chive import common, hashtree


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("append")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)
    parser.add_argument("--file", "-f", required=True, type=pathlib.Path)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path
    file: pathlib.Path


def main(args: Args):
    method = hashtree.HashMethod.SHA2_1MB_3WAY

    relative_path = args.file.absolute().relative_to(args.manifest.absolute().parent)
    n_bytes = args.file.stat().st_size
    blob_size = method.value.n_complete(n_bytes) * method.value.digest_size

    with common.load_manifest(args.manifest) as conn:
        cursor = conn.execute(
            "INSERT INTO files(relative_path, hash_method, hash_value) VALUES (?,?,ZEROBLOB(?));",
            (
                relative_path.as_posix(),
                method.value.method_id,
                blob_size,
            ),
        )
        with conn.blobopen("files", "hash_value", cursor.lastrowid) as blob:
            hashtree.hash_file(
                args.file,
                memory=blob,
                hash_method=method,
            )
        conn.commit()
