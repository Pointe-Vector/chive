import argparse
import dataclasses
import logging
import pathlib
from typing import IO

from pointevector.chive import common, hashtree


def parser(subparsers: argparse._SubParsersAction):
    parser: argparse.ArgumentParser = subparsers.add_parser("verify")
    parser.set_defaults(func=main)
    parser.add_argument("--manifest", "-m", required=True, type=pathlib.Path)
    parser.add_argument("--reference", "-r", required=True, type=pathlib.Path)


@dataclasses.dataclass(slots=True)
class Args:
    manifest: pathlib.Path
    reference: pathlib.Path


def load_metadata(manifest: pathlib.Path):
    with common.load_manifest(manifest) as conn:
        return conn.execute(
            "SELECT archive_id, copy_id, version FROM metadata;"
        ).fetchone()


def gen_files(manifest: pathlib.Path):
    with common.load_manifest(manifest) as conn:
        for row in conn.execute(
            "SELECT rowid, relative_path, hash_method FROM files ORDER BY relative_path;"
        ):
            with conn.blobopen("files", "hash_value", row["rowid"]) as blob:
                yield row, blob


def gen_hashes(blob: IO[bytes], *, hash_method: hashtree.HashMethod):
    method: hashtree._Method = hash_method.value
    while node_hash := blob.read(method.digest_size):
        yield node_hash


def main(args: Args):
    # Check metadata
    m_metadata = load_metadata(args.manifest)
    r_metadata = load_metadata(args.reference)
    if m_metadata["archive_id"] != r_metadata["archive_id"]:
        raise ValueError
    if m_metadata["copy_id"] == r_metadata["copy_id"]:
        raise ValueError

    # Check file info
    for (m_info, m_blob), (r_info, r_blob) in zip(
        gen_files(args.manifest),
        gen_files(args.reference),
        strict=True,
    ):
        if m_info != r_info:
            raise ValueError

        hash_method = hashtree.load_hash_method(m_info["hash_method"])

        for idx, (m_hash, r_hash) in enumerate(
            zip(
                gen_hashes(m_blob, hash_method=hash_method),
                gen_hashes(r_blob, hash_method=hash_method),
                strict=True,
            )
        ):
            if m_hash != r_hash:
                logging.getLogger().warning(
                    "%s hash #%d -> %s %s", m_info["relative_path"], idx, m_hash, r_hash
                )
