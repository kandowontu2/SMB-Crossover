"""Strict root-leased selected-player Star palette; owningacee, memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_battletoads_carry_current_1115 as Carry
import compose_bub_native_palette_current_1115 as Palette
import plan_bub_star_palette_174fa_1115 as Plan

R, ROM, B, W, N = Palette.R, Palette.ROM, Palette.B, Palette.W, Palette.N
PIN = 'aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe'
CANDIDATE = 'e9d65013d9521f7dd7be2702b946375d31bb52d913d4ba60be45ef4cfa85a171'
GRANT = R/'docs/qa/allocations/bub-selected-star-palette-ace-source-1115.json'
GRANT_SHA = '3d8797d9c702cd51cc762c5d8469cee5740834122c128647e6cfa6cccfc11c15'
DEPENDENCIES = ((Carry,'6b87663ae0de5a1bb8b58ab73fa5313dcc8b80def75b09102fd2b66669fd604d'),
    (Palette,'1b3e655bb5d44a0230d690d6dcc7ebd70959e5200fc661ece80f0758f95f58e6'),
    (Plan,'d931fb0138ec961615fbec4b727d7eff9b2b1e1db2d00631ba9d386eb5b5243f'))
FILE, COOKIE = 1499208, 536570
OLD = bytes.fromhex('b906c14c41b4b902c148ad00c3d00c684829034903d0046829fc606860'+'ff'*27)
NEW = bytes.fromhex('b906c14c41b4b902c148ad9c07f0169829f0d011ad00c329fed00a684d870529fc4d870560ad00c3d00c684829034903d0046829fc606860')
OLD_COOKIE = bytes.fromhex('a72702972671056c12e3e4be9b97af56')
H = lambda v: sha256(v).hexdigest()
code, cookie = Palette.code, Palette.cookie


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes()) == GRANT_SHA
    for module, pin in DEPENDENCIES:
        assert H(Path(module.__file__).read_bytes()) == pin
    q = json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256'] == PIN and q['owned_bytes'] == 72
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    row = q['mapper_envelope']
    assert (row['file'],row['bytes'],bytes.fromhex(row['before']),bytes.fromhex(row['after'])) == (FILE,56,OLD,NEW)
    assert q['cookie_envelope']['file'] == COOKIE
    assert bytes.fromhex(q['cookie_envelope']['before']) == OLD_COOKIE
    assert Plan.measured_bytes(0x79c,0x587)[0] == NEW
    return q


@lru_cache(maxsize=1)
def reference(parent):
    lease(); assert isinstance(parent,bytes) and H(parent) == PIN
    raw174 = Carry.inverse(parent)
    assert H(raw174) == Palette.CANDIDATE
    return raw174


@lru_cache(maxsize=1)
def proposal(parent):
    lease(); reference(parent)
    assert parent[FILE:FILE+56] == OLD and parent[COOKIE:COOKIE+16] == OLD_COOKIE
    out = bytearray(parent); out[FILE:FILE+56] = NEW
    out[COOKIE:COOKIE+16] = cookie(out); out = bytes(out)
    owned = set(range(FILE,FILE+56)) | set(range(COOKIE,COOKIE+16))
    changed = {i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a != b}
    assert len(owned) == 72 and changed <= owned
    assert code(out)[0x1470:0x153a] == b'\xff'*202
    if CANDIDATE is not None: assert H(out) == CANDIDATE
    return out, dict(parent_SHA256=PIN,candidate_SHA256=H(out),grant_SHA256=GRANT_SHA,
        owned_bytes=72,changed_bytes=len(changed),mapper_SHA256=H(NEW),cookie=out[COOKIE:COOKIE+16].hex(),
        all_unowned_acee_bytes_exact=True,all714_carry_changes_preserved=True,
        no_new_RAM_CHR_PRG_carrier_or_OAM=True,source_only=True,output_files=0)


@lru_cache(maxsize=1)
def inverse(raw):
    lease(); assert CANDIDATE is not None and isinstance(raw,bytes) and H(raw) == CANDIDATE
    assert raw[FILE:FILE+56] == NEW and raw[COOKIE:COOKIE+16] == cookie(raw)
    parent = bytearray(raw); parent[FILE:FILE+56] = OLD; parent[COOKIE:COOKIE+16] = OLD_COOKIE
    parent = bytes(parent); assert H(parent) == PIN
    assert proposal(parent)[0] == raw
    return parent


def load_current():
    raw = ROM.read_bytes(); assert H(raw) == PIN,'Expected exact officialacee'
    return raw


if __name__ == '__main__':
    parent = load_current(); raw,q = proposal(parent)
    assert inverse(raw) == parent
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
