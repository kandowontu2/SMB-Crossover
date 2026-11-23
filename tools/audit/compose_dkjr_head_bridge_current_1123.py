"""Exact3af5 DK Jr. accepted-head bridge; memory-only, no new helpers.

The retained bridge consumes a genuine original jump/ceiling contact without
changing the original response or body. Its three existing code envelopes
and cookie are the complete change domain. This module has no file writer.
"""
from functools import lru_cache
from pathlib import Path
import json

import compose_dkjr_side_epoch_fast_1123 as Fast
import compose_dkjr_head_bridge_1113 as Old

M, H, R = Fast.M, Fast.H, Fast.M.R
PIN = Fast.CANDIDATE
CANDIDATE = '06336f15fae4d24afa8025e972764091def63b6c01d41f206828a5105939661f'
PARENT_PACKET = 'e97491ea6910d1b5d2a8c9ee0cb450da4239770d6ed88b964830dbe66b56f805'
PARENT_COOKIE = bytes.fromhex('a72801e97491ea6910d1b5d2a8c9ee0c')
SOURCE_SHA = '578f7e97b70bc36739cdbeb95750fb6d0a4a3733b106332a1abc56b9ff4e3eb8'
OLD_COMPOSER_SHA = '2c0617ef61f61d858af4f6d5690c528912e5b2aeb1fb84a1c6e79a0a003e75fa'
COOKIE_AT, CHR, PAGES = Old.Base.COOKIE_AT, Old.Base.CHR, Old.Base.PAGES
LAYOUT = dict(Old.LAYOUT)


def payload(raw):
    return Old.payload(raw)


@lru_cache(maxsize=1)
def old_fragments():
    assert H(Old.SOURCE.read_bytes()) == SOURCE_SHA
    assert H(Path(Old.__file__).read_bytes()) == OLD_COMPOSER_SHA
    _, rect, score, definitions = Old.old_source()
    rect = M.assemble('D_ebe3=$aeef\n.segment "OLD"\n'+rect,
                      dict(OLD=LAYOUT['RECT']))
    score = M.assemble(definitions+'DkjrNativeAddScore=$bb37\n.segment "OLD"\n'+score,
                       dict(OLD=LAYOUT['SCORE']))
    assert rect['used'] == dict(OLD=261) and score['used'] == dict(OLD=126)
    return dict(RECT=rect['images']['OLD'], SCORE=score['images']['OLD'],
                HEAD_HOOK=bytes.fromhex('a9048d6bc060'))


@lru_cache(maxsize=1)
def program(parent):
    assert isinstance(parent, bytes) and len(parent) == 2097168 and H(parent) == PIN
    assert H(payload(parent)) == PARENT_PACKET
    assert parent[COOKIE_AT:COOKIE_AT+16] == PARENT_COOKIE
    Fast.inverse(parent)  # Exact current side-gate lineage; no historical extraction.
    old = old_fragments()
    _, _, new = Old.linked(parent)
    assert new['symbols']['NativeAddScore'] == 0xbb37
    assert new['used'] == dict(RECT=261, SCORE=122, HEAD_HOOK=6)
    for name, (pc, size) in LAYOUT.items():
        at = Old.offset(pc)
        assert len(old[name]) == size and payload(parent)[at:at+size] == old[name]
    return new


def chunks(pc, data):
    at, cursor = Old.offset(pc), 0
    while cursor < len(data):
        page, within = divmod(at+cursor, 1024)
        size = min(1024-within, len(data)-cursor)
        yield CHR+PAGES[page]*1024+within, data[cursor:cursor+size]
        cursor += size


def proposal(parent):
    p = program(parent)
    out, owned, spans = bytearray(parent), set(), []
    for name, (pc, size) in LAYOUT.items():
        before = old_fragments()[name]
        after = p['images'][name].ljust(size, b'\xea')
        assert len(after) == size
        for (at, old), (other, new) in zip(chunks(pc, before), chunks(pc, after), strict=True):
            assert at == other and parent[at:at+len(old)] == old
            domain = set(range(at, at+len(old)))
            assert not domain & owned
            owned |= domain
            out[at:at+len(new)] = new
            spans.append(dict(role=name, file=at, bytes=len(new),
                              old_SHA256=H(old), new_SHA256=H(new)))
    body = payload(out)
    cookie = b'\xa7\x28\x01'+bytes.fromhex(H(body))[:13]
    out[COOKIE_AT:COOKIE_AT+16] = cookie
    owned.update(range(COOKIE_AT, COOKIE_AT+16))
    result = bytes(out)
    changed = {i for i, (a, b) in enumerate(zip(parent, result, strict=True)) if a != b}
    assert changed <= owned and len(owned) == 409
    if CANDIDATE is not None:
        assert H(result) == CANDIDATE
    return result, dict(parent_SHA256=PIN, candidate_SHA256=H(result),
        packet_SHA256=H(body), cookie=cookie.hex(), source_SHA256=SOURCE_SHA,
        composer_SHA256=H(Path(__file__).read_bytes()), spans=spans,
        logical_envelopes=LAYOUT, changed_bytes=len(changed), owned_bytes=len(owned),
        used=p['used'], labels=p['symbols'], original_fall_preserved=True,
        all_unowned_bytes_exact=True, helpers_and_body_tables_unchanged=True,
        new_ROM_capacity=0, new_RAM=0, outputs=0, native_qualified=False)


def inverse(candidate):
    assert CANDIDATE is not None and isinstance(candidate, bytes) and H(candidate) == CANDIDATE
    out = bytearray(candidate)
    for name, (pc, _) in LAYOUT.items():
        for at, data in chunks(pc, old_fragments()[name]):
            out[at:at+len(data)] = data
    out[COOKIE_AT:COOKIE_AT+16] = PARENT_COOKIE
    parent = bytes(out)
    assert H(parent) == PIN and proposal(parent)[0] == candidate
    return parent


if __name__ == '__main__':
    _, receipt = proposal(M.ROM.read_bytes())
    print('DK CURRENT HEAD COMPOSITION '+json.dumps(receipt, separators=(',', ':')), flush=True)
