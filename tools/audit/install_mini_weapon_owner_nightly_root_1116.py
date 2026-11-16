"""Install exact native-tested Mini20 over Sonic a2, direct with no backup."""
from pathlib import Path
import importlib
import json
import compose_mini_weapon_owner_a2_1116 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'


def main():
    grant = C.R/'docs/qa/allocations/mini-weapon-owner-a2-delivery-root-1116.json'
    g = json.loads(grant.read_bytes())
    assert g['direct_Downloads_replacement_authorized']
    assert not g['backups_patches_releases_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert (g['parent_SHA256'], g['candidate_SHA256']) == (C.PARENT, C.CANDIDATE)
    assert len(g['cases']) == 2 and {q['kind'] for q in g['cases']} == {'flower', 'full11'}
    before = C.ROM.read_bytes()
    guard = check(C.ROM)
    assert C.H(before) == C.PARENT and not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert target.read_bytes() == before
    raw, proof = C.proposal(before)
    assert C.inverse(raw) == before and proof['all_unowned_bytes_exact'] and proof['Sonic94_preserved']
    assert (proof['owned_bytes'], proof['changed_bytes']) == (20, 20)
    for case in g['cases']:
        assert case['private_native_passed'] is True and len(case['private_native_receipt_SHA256']) == 64
        f = importlib.import_module(case['factory_module'])
        assert C.H(Path(f.__file__).read_bytes()) == case['factory_SHA256']
        assert C.H(f.controller(raw, case['kind']).encode()) == case['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    assert C.ROM.read_bytes() == before and check(C.ROM) == guard
    C.ROM.write_bytes(raw)
    assert C.ROM.read_bytes() == raw and check(C.ROM)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, SHA256=C.CANDIDATE, bytes=len(raw),
        exact_tested_candidate=True, direct_replacement=True, backups=0, patch_assets=0,
        releases=0, output_files_added=0, Sonic94_preserved=True,
        actual_Downloads_native_repeat='Required before verified-delivery claim'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
