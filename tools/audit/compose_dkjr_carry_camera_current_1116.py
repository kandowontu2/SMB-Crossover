"""Strict leased214+16 DK carry/camera correction over actual6a3; memory only."""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_bowser_life_gain_signed_1116 as Bowser
import plan_dkjr_carry_camera_bc5_1116 as Plan

R = Plan.R
PIN = '6a3ff7c9a60b5ff5906d38f7815f021062006e0817d43e7ed139f47589c4eee2'
REFERENCE = Plan.PIN
GRANT = R/'docs/qa/allocations/dkjr-carry-camera-source-1116.json'
GRANT_SHA = 'cd1c91f433f10eaa357738291c22fdc8544c1a46f43c9e9d1c313e4b90f8b9ef'
PLAN_SHA = '2d7020ed4a3b6cf5529b554a03f9c872ea79298ec5a8e015dd3009f7252657c7'
CANDIDATE = '6d7c3fa958efd42a1fcf5d256f0c5506228d55d344dce9bf7382e577d06272f5'
H = lambda value: sha256(value).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes()) == GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes()) == PLAN_SHA
    q = json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256'] == PIN and q['frozen_reference_parent_SHA256'] == REFERENCE
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k] for k in ('physical_ROM_file_writes_authorized',
                                  'native_Mesen_authorized','Downloads_delivery_authorized'))
    assert q['code']['file_half_open'] == [1951413,1951627]
    assert q['code']['CPU_half_open'] == [Plan.START,Plan.END]
    return q


def reference(parent):
    assert isinstance(parent, bytes) and H(parent) == PIN, 'Exact actual6a3 parent required'
    assert Bowser.CANDIDATE == PIN and Bowser.PIN == REFERENCE
    ref = Bowser.inverse(parent)
    assert H(ref) == REFERENCE
    owned = set()
    for at, old, new in Bowser.spans():
        assert parent[at:at+len(new)] == new and ref[at:at+len(old)] == old
        owned.update(range(at, at+len(new)))
    assert len(owned) == 72
    assert all(a == b or i in owned for i,(a,b) in enumerate(zip(parent,ref,strict=True)))
    return ref


def payload(raw):
    old = Plan.Current.F.Prior.Early.Old
    return b''.join(raw[old.CHR+p*1024:old.CHR+(p+1)*1024] for p in old.PAGES)


def spans(parent):
    q = lease()
    ref = reference(parent)
    _, _, body, _, _, old, new = Plan.measured(ref)
    before, after = old['images']['CARRY'], new['images']['CARRY']
    assert H(before) == q['code']['old_SHA256'] and H(after) == q['code']['new_SHA256']
    assert payload(parent) == body
    updated = body[:Plan.START-0xa000]+after+body[Plan.END-0xa000:]
    assert len(updated) == 11264
    cookie = bytes.fromhex(q['cookie']['new_prefix_hex'])+sha256(updated).digest()[:13]
    old_cookie = bytes.fromhex(q['cookie']['old_hex'])
    at = q['cookie']['file_half_open'][0]
    assert parent[at:at+16] == old_cookie
    return [(q['code']['file_half_open'][0],before,after),(at,old_cookie,cookie)]


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent, bytes) and H(parent) == PIN
    q = lease()
    result = bytearray(parent)
    owned = set()
    rows = spans(parent)
    for at, before, after in rows:
        assert len(before) == len(after) and parent[at:at+len(before)] == before
        assert not owned.intersection(range(at,at+len(before)))
        owned.update(range(at,at+len(before)));result[at:at+len(before)] = after
    result = bytes(result)
    changed = {i for i,(a,b) in enumerate(zip(parent,result,strict=True)) if a != b}
    assert len(owned) == 230 and changed <= owned
    for at, before, after in Bowser.spans():
        assert result[at:at+len(after)] == parent[at:at+len(after)] == after
        assert not owned.intersection(range(at,at+len(after)))
    body = payload(result)
    assert result[534485:534501] == bytes.fromhex('a72801')+sha256(body).digest()[:13]
    assert body[0xb7bb-0xa000:0xb7c1-0xa000] == bytes.fromhex('2010a24ce1a8')
    assert body[0xb779-0xa000:0xb77b-0xa000] == bytes.fromhex('1860')
    if CANDIDATE is not None:assert H(result) == CANDIDATE
    receipt = dict(parent_SHA256=PIN, frozen_reference_SHA256=REFERENCE,
        candidate_SHA256=H(result), grant_SHA256=GRANT_SHA, plan_SHA256=PLAN_SHA,
        owned_bytes=len(owned), changed_bytes=len(changed),
        packet_SHA256=H(body), cookie=result[534485:534501].hex(),
        spans=[dict(file_offset=at,bytes=len(a),old_SHA256=H(a),new_SHA256=H(b)) for at,a,b in rows],
        all_unowned_bytes_exact=True, all72_Bowser_bytes_exact=True,
        source_only=True, CPU_executed=False, ROM_written=False, outputs=0)
    return result, receipt


def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw, bytes) and H(raw) == CANDIDATE
    q = lease()
    parent = bytearray(raw)
    # Old exact code comes from the pinned current plan/reference. Reconstruct
    # the reference with the new DK span restored before the strict Bowser API.
    _, labels = Plan.source_inputs()
    source = Plan.SOURCE_PATH.read_text().replace('\r\n','\n')
    fragment = source[source.index('DkjrNativeCarryEvent:'):source.index('DkjrNativeLifeReset:')]
    labels['DkCarryPendingTransition'] = 0xb7bb
    fragment = Plan.Source.once(fragment,' jsr DkjrFallDistance\n',' jsr DkCarryPendingTransition\n')
    old = Plan.assemble_fragment(fragment,source,labels)['images']['CARRY']
    assert H(old) == q['code']['old_SHA256']
    at = q['code']['file_half_open'][0]
    assert H(raw[at:at+214]) == q['code']['new_SHA256']
    parent[at:at+214] = old
    parent[534485:534501] = bytes.fromhex(q['cookie']['old_hex'])
    parent = bytes(parent)
    assert H(parent) == PIN
    assert proposal(parent)[0] == raw
    return parent


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent', type=Path, required=True)
    args = ap.parse_args()
    parent = args.parent.read_bytes()  # Immutable one-time input snapshot.
    raw, q = proposal(parent)
    if CANDIDATE is not None:assert inverse(raw) == parent
    encoded = json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_CARRY_CAMERA_COMPOSITION '+encoded,flush=True)
    print('DKJR_CARRY_CAMERA_COMPOSITION_SHA256 '+H(encoded.encode()),flush=True)
