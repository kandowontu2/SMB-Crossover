"""Strict34-byte Metal life repair and data-only portable inverse; RAM only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import plan_metal_life_snapshot_root_1116 as Plan

R = Plan.R
PIN = '7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
CANDIDATE = '00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
OLD_COOKIE = bytes.fromhex('a7232e7f64f1695d30762600e8451a6c')
COOKIE = bytes.fromhex('a7232fc62354dfbde732156cd49e287a')
GRANT = R/'docs/qa/allocations/metal-life-snapshot-source-root-1116.json'
GRANT_SHA = '9142d95037c3fcbb20b5d7243b84a9581774bba99112b9f78c2b1f44e03620c0'
PLAN_SHA = '7db3678ec0dafe77febe1d9e74215fb0b463c10fbf7f795c957de9c5e2b62a6b'
H = lambda value: sha256(value).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes()) == GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes()) == PLAN_SHA
    g = json.loads(GRANT.read_bytes())
    assert (g['parent_SHA256'], g['candidate_SHA256']) == (PIN, CANDIDATE)
    assert g['source_in_memory_composition_and_CPU_authorized']
    assert not any(g[key] for key in ('physical_ROM_file_writes_authorized', 'native_Mesen_authorized', 'Downloads_delivery_authorized'))
    assert g['owned_bytes'] == 34
    return g


def spans():
    g = lease()
    result = tuple((row['file'], bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex']))
                   for row in g['physical_spans'])
    assert result == ((1561533, bytes.fromhex('f039'), bytes.fromhex('1036')),
                      (212991, OLD_COOKIE, COOKIE), (817141, OLD_COOKIE, COOKIE))
    return result


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent, bytes) and H(parent) == PIN
    g = lease()
    fit = Plan.measure(parent)
    assert fit['receipt_SHA256'] == g['detached_plan_receipt_SHA256']
    assert fit['predicted_candidate_SHA256'] == CANDIDATE
    assert fit['proposed_cookie'] == COOKIE.hex() and not fit['proposed_CPU_executed']
    out = bytearray(parent)
    owned = set()
    for at, old, new in spans():
        assert len(old) == len(new) and parent[at:at+len(old)] == old
        assert not owned.intersection(range(at, at+len(old)))
        owned.update(range(at, at+len(old)))
        out[at:at+len(new)] = new
    raw = bytes(out)
    changed = {i for i, (a, b) in enumerate(zip(parent, raw, strict=True)) if a != b}
    assert len(owned) == 34 and changed <= owned and H(raw) == CANDIDATE
    assert all(a == b for i, (a, b) in enumerate(zip(parent, raw, strict=True)) if i not in owned)
    return raw, dict(parent_SHA256=PIN, candidate_SHA256=CANDIDATE, owned_bytes=34,
        changed_bytes=len(changed), code_bytes=2, existing_cookie_views=2,
        all_unowned_current7c0f_bytes_exact=True, old_cookie=OLD_COOKIE.hex(), cookie=COOKIE.hex(),
        only_renderer_life_branch_and_full_resident_cookies=True,
        old_guards_header_player_Fresh_unchanged=True, new_capacity_or_RAM_or_helpers=0,
        grant_SHA256=GRANT_SHA, plan_SHA256=PLAN_SHA,
        provenance='Composition includes installed compiled-menu metadata validation; no proposed candidate CPU in this function',
        proposed_candidate_CPU_executed=False, physical_ROM_written=False, outputs=0)


def inverse(raw):
    assert isinstance(raw, bytes) and H(raw) == CANDIDATE
    out = bytearray(raw)
    for at, old, new in spans():
        assert raw[at:at+len(new)] == new
        out[at:at+len(old)] = old
    parent = bytes(out)
    assert H(parent) == PIN
    return parent


if __name__ == '__main__':
    parent = Plan.Current.ROM.read_bytes()
    raw, report = proposal(parent)
    assert inverse(raw) == parent and proposal(inverse(raw))[0] == raw
    rejected = 0
    for image, func in ((parent, inverse), (raw, proposal), (raw[:-1], inverse), (parent[:-1], proposal)):
        try:
            func(image)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError('Wrong role accepted')
    report.update(strict_inverse_roundtrip=True, wrong_role_or_truncated_rejections=rejected,
                  composer_SHA256=H(Path(__file__).read_bytes()))
    report['receipt_SHA256'] = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
