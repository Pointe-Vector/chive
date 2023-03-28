import dataclasses
import enum
import logging
import hashlib
import math
import pathlib
from typing import Callable, IO, Union
import zlib


logger = logging.getLogger()


@dataclasses.dataclass(frozen=True, slots=True)
class _Method:
    method_id: int
    digest_size: int
    chunk_size: int
    fanout: int
    hash_fnc: Callable[[IO[bytes]], bytes]

    def n_chunks(self, n_bytes: int):
        return math.ceil(n_bytes / self.chunk_size)

    def n_levels(self, n_bytes: int):
        _n_chunks = self.n_chunks(n_bytes)

        return math.ceil(math.log(_n_chunks, self.fanout))

    def n_perfect(self, n_bytes: int):
        _n_levels = self.n_levels(n_bytes)

        # Calculate the number of nodes in a perfect _FANOUT_-ary tree
        return (int(self.fanout ** (_n_levels + 1)) - 1) // (self.fanout - 1)

    def n_complete(self, n_bytes: int):
        _n_chunks = self.n_chunks(n_bytes)
        _n_levels = self.n_levels(n_bytes)
        _n_perfect = self.n_perfect(n_bytes)

        # Calculate the total number of check value bytes in the tree
        _n_complete = _n_perfect - int(self.fanout**_n_levels) + _n_chunks
        return _n_perfect if _n_complete == 0 else _n_complete


class HashMethod(enum.Enum):
    SHA2_1MB_3WAY = _Method(
        method_id=0,
        digest_size=32,
        chunk_size=0x10_0000,
        fanout=3,
        hash_fnc=lambda d: hashlib.sha256(d).digest(),
    )


def load_hash_method(id: int) -> HashMethod:
    for hash_method in HashMethod:
        method: _Method = hash_method.value
        if id == method.method_id:
            return hash_method

    raise ValueError


def hash_file(
    filepath: pathlib.Path,
    *,
    memory: IO[bytes],
    hash_method: Union[HashMethod, None],
):
    if hash_method is None:
        hash_method = HashMethod.SHA2_1MB_3WAY

    n_bytes = filepath.stat().st_size
    method: _Method = hash_method.value

    def read_chunks():
        with filepath.open("rb") as f:
            while chunk := f.read(method.chunk_size):
                yield chunk

    # Add nodes for data check values
    data_start_idx = method.n_complete(n_bytes) - method.n_chunks(n_bytes)
    for chunk_idx, chunk in enumerate(read_chunks()):
        to_check = bytearray(b"\x00")
        to_check.extend(chunk)
        start_byte = method.digest_size * (data_start_idx + chunk_idx)
        logger.debug(
            "Data hash %d @ node %d", chunk_idx, start_byte // method.digest_size
        )
        memory[start_byte : (start_byte + method.digest_size)] = method.hash_fnc(
            to_check
        )

    max_level_node = [method.n_complete(n_bytes) - 1]
    for _ in range(method.n_levels(n_bytes)):
        max_level_node.insert(0, math.floor((max_level_node[0] - 1) / method.fanout))

    # Recursive post-order traversal to fill in rest of tree
    # Note: Unused nodes in a level are copies of the last within the level
    def _post_order_traversal_(index: int = 0, level: int = 0):
        start_byte = method.digest_size * index

        # Unused nodes
        if index > max_level_node[level]:
            max_start_byte = method.digest_size * max_level_node[level]
            to_copy = memory[max_start_byte : (max_start_byte + method.digest_size)]
            if start_byte < method.digest_size * method.n_complete(n_bytes):
                memory[start_byte : (start_byte + method.digest_size)] = to_copy
            return to_copy

        # Leaf nodes
        if index >= data_start_idx:
            return memory[start_byte : (start_byte + method.digest_size)]

        # Combine from children and check
        to_check = bytearray(b"\x01")
        for child in range(method.fanout):
            to_check.extend(
                _post_order_traversal_(index * method.fanout + child + 1, level + 1)
            )
        check_value = method.hash_fnc(to_check)
        memory[start_byte : (start_byte + method.digest_size)] = check_value
        return check_value

    _post_order_traversal_()
