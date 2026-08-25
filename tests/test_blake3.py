from hachimi_tl_vi.blake3_pure import blake3_hex, Blake3


def test_blake3_official_vectors():
    assert blake3_hex(b"") == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    assert blake3_hex(b"abc") == "6437b3ac38465133ffb63b75273a8db548c558465d79db03fd359c6cd5bd9d85"


def test_blake3_streaming_matches_one_shot():
    data = bytes(range(256)) * 20
    one = blake3_hex(data)
    h = Blake3()
    for i in range(0, len(data), 17):
        h.update(data[i:i+17])
    assert h.hexdigest() == one
