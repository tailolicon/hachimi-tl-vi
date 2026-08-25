"""Small pure-Python BLAKE3 fallback.

This implements unkeyed hashing and fixed-length/XOF output. It is intentionally
kept internal: when the native ``blake3`` package is installed, the indexer uses
that faster implementation instead.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

IV = [
    0x6A09E667,
    0xBB67AE85,
    0x3C6EF372,
    0xA54FF53A,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
    0x5BE0CD19,
]
MSG_PERMUTATION = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
CHUNK_LEN = 1024
BLOCK_LEN = 64
OUT_LEN = 32
CHUNK_START = 1 << 0
CHUNK_END = 1 << 1
PARENT = 1 << 2
ROOT = 1 << 3
MASK32 = 0xFFFFFFFF


def _rotr32(x: int, n: int) -> int:
    return ((x >> n) | ((x << (32 - n)) & MASK32)) & MASK32


def _g(state: list[int], a: int, b: int, c: int, d: int, mx: int, my: int) -> None:
    state[a] = (state[a] + state[b] + mx) & MASK32
    state[d] = _rotr32(state[d] ^ state[a], 16)
    state[c] = (state[c] + state[d]) & MASK32
    state[b] = _rotr32(state[b] ^ state[c], 12)
    state[a] = (state[a] + state[b] + my) & MASK32
    state[d] = _rotr32(state[d] ^ state[a], 8)
    state[c] = (state[c] + state[d]) & MASK32
    state[b] = _rotr32(state[b] ^ state[c], 7)


def _round(state: list[int], m: list[int]) -> None:
    _g(state, 0, 4, 8, 12, m[0], m[1])
    _g(state, 1, 5, 9, 13, m[2], m[3])
    _g(state, 2, 6, 10, 14, m[4], m[5])
    _g(state, 3, 7, 11, 15, m[6], m[7])
    _g(state, 0, 5, 10, 15, m[8], m[9])
    _g(state, 1, 6, 11, 12, m[10], m[11])
    _g(state, 2, 7, 8, 13, m[12], m[13])
    _g(state, 3, 4, 9, 14, m[14], m[15])


def _permute(m: list[int]) -> list[int]:
    return [m[i] for i in MSG_PERMUTATION]


def _compress(
    cv: list[int], block_words: list[int], counter: int, block_len: int, flags: int
) -> list[int]:
    state = list(cv) + IV[:4] + [
        counter & MASK32,
        (counter >> 32) & MASK32,
        block_len,
        flags,
    ]
    m = list(block_words)
    for round_idx in range(7):
        _round(state, m)
        if round_idx != 6:
            m = _permute(m)
    for i in range(8):
        state[i] ^= state[i + 8]
        state[i + 8] ^= cv[i]
    return [x & MASK32 for x in state]


def _words_from_block(block: bytes) -> list[int]:
    padded = block + b"\0" * (BLOCK_LEN - len(block))
    return list(struct.unpack("<16I", padded))


def _words_to_bytes(words: list[int]) -> bytes:
    return struct.pack("<%dI" % len(words), *words)


@dataclass
class _Output:
    input_cv: list[int]
    block_words: list[int]
    counter: int
    block_len: int
    flags: int

    def chaining_value(self) -> list[int]:
        return _compress(self.input_cv, self.block_words, self.counter, self.block_len, self.flags)[:8]

    def root_output_bytes(self, length: int) -> bytes:
        out = bytearray()
        output_block_counter = 0
        while len(out) < length:
            words = _compress(
                self.input_cv,
                self.block_words,
                output_block_counter,
                self.block_len,
                self.flags | ROOT,
            )
            out.extend(_words_to_bytes(words))
            output_block_counter += 1
        return bytes(out[:length])


class _ChunkState:
    def __init__(self, key_words: list[int], chunk_counter: int, flags: int) -> None:
        self.chaining_value = list(key_words)
        self.chunk_counter = chunk_counter
        self.block = bytearray()
        self.blocks_compressed = 0
        self.flags = flags

    def __len__(self) -> int:
        return BLOCK_LEN * self.blocks_compressed + len(self.block)

    def _start_flag(self) -> int:
        return CHUNK_START if self.blocks_compressed == 0 else 0

    def update(self, data: bytes) -> None:
        view = memoryview(data)
        offset = 0
        while offset < len(view):
            if len(self.block) == BLOCK_LEN:
                words = _words_from_block(bytes(self.block))
                self.chaining_value = _compress(
                    self.chaining_value,
                    words,
                    self.chunk_counter,
                    BLOCK_LEN,
                    self.flags | self._start_flag(),
                )[:8]
                self.blocks_compressed += 1
                self.block.clear()
            take = min(BLOCK_LEN - len(self.block), len(view) - offset)
            self.block.extend(view[offset:offset + take])
            offset += take

    def output(self) -> _Output:
        return _Output(
            input_cv=list(self.chaining_value),
            block_words=_words_from_block(bytes(self.block)),
            counter=self.chunk_counter,
            block_len=len(self.block),
            flags=self.flags | self._start_flag() | CHUNK_END,
        )


def _parent_output(left_cv: list[int], right_cv: list[int], key_words: list[int], flags: int) -> _Output:
    return _Output(
        input_cv=list(key_words),
        block_words=list(left_cv) + list(right_cv),
        counter=0,
        block_len=BLOCK_LEN,
        flags=flags | PARENT,
    )


def _parent_cv(left_cv: list[int], right_cv: list[int], key_words: list[int], flags: int) -> list[int]:
    return _parent_output(left_cv, right_cv, key_words, flags).chaining_value()


class Blake3:
    def __init__(self) -> None:
        self.key_words = list(IV)
        self.flags = 0
        self.chunk_state = _ChunkState(self.key_words, 0, self.flags)
        self.cv_stack: list[list[int]] = []

    def _push_chunk_cv(self, new_cv: list[int], total_chunks: int) -> None:
        while (total_chunks & 1) == 0:
            left = self.cv_stack.pop()
            new_cv = _parent_cv(left, new_cv, self.key_words, self.flags)
            total_chunks >>= 1
        self.cv_stack.append(new_cv)

    def update(self, data: bytes | bytearray | memoryview) -> "Blake3":
        view = memoryview(data)
        offset = 0
        while offset < len(view):
            if len(self.chunk_state) == CHUNK_LEN:
                chunk_cv = self.chunk_state.output().chaining_value()
                total_chunks = self.chunk_state.chunk_counter + 1
                self._push_chunk_cv(chunk_cv, total_chunks)
                self.chunk_state = _ChunkState(self.key_words, total_chunks, self.flags)
            want = CHUNK_LEN - len(self.chunk_state)
            take = min(want, len(view) - offset)
            self.chunk_state.update(view[offset:offset + take].tobytes())
            offset += take
        return self

    def digest(self, length: int = OUT_LEN) -> bytes:
        output = self.chunk_state.output()
        for left_cv in reversed(self.cv_stack):
            output = _parent_output(left_cv, output.chaining_value(), self.key_words, self.flags)
        return output.root_output_bytes(length)

    def hexdigest(self, length: int = OUT_LEN) -> str:
        return self.digest(length).hex()


def blake3_hex(data: bytes) -> str:
    return Blake3().update(data).hexdigest()
