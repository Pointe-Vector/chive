import argparse
import dataclasses
import mmap
import pathlib


from pointevector.chive import common, hashtree


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("check")
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
        row = conn.execute(
            "SELECT rowid, hash_method FROM files WHERE relative_path = ?",
            (relative_path.as_posix(),),
        ).fetchone()
        with conn.blobopen("files", "hash_value", row["rowid"]) as blob:
            hash_method = hashtree.load_hash_method(row["hash_method"])
            method: hashtree._Method = hash_method.value
            n_bytes = method.n_complete(args.file.stat().st_size) * method.digest_size
            if len(blob) != n_bytes:  # Quit early if hash tree will be different size
                raise ValueError
            with mmap.mmap(-1, n_bytes) as m:
                hashtree.hash_file(args.file, memory=m, hash_method=hash_method)
                for source, reference in zip(blob.read(), m):
                    if source.to_bytes(byteorder="little") != reference:
                        raise ValueError
