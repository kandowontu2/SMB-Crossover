"""Direct no-backup installation after four exact private native Sonic passes."""
import importlib
import json
from pathlib import Path
import compose_sonic_ceiling_complete_1327_1116 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'


def main():
    records = []
    for suffix in ('', 'full-'):
        grant = C.R/f'docs/qa/allocations/sonic-ceiling-{suffix}delivery-root-1116.json'
        g = json.loads(grant.read_bytes())
        assert g['direct_Downloads_replacement_authorized']
        assert not g['backups_patches_releases_authorized']
        assert g['composer_SHA256'] == C.H(Path(C.__file__).read_bytes())
        assert (g['parent_SHA256'], g['candidate_SHA256']) == (C.PIN, C.CANDIDATE)
        records.extend(g['cases'])
    assert len(records) == 4
    assert {(q['kind'], q['form']) for q in records} == {
        ('life', 'sonic'), ('life', 'super'), ('full11', 'sonic'), ('full11', 'super')}
    official = C.ROM
    parent = official.read_bytes()
    guard = check(official)
    assert C.H(parent) == C.PIN and not guard['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    raw, composition = C.proposal(parent)
    assert C.H(raw) == C.CANDIDATE and C.inverse(raw) == parent
    assert composition['all_unowned_bytes_exact']
    assert (composition['owned_bytes'], composition['changed_bytes']) == (94, 91)
    for case in records:
        assert case['private_native_passed'] is True
        assert len(case['private_native_receipt_SHA256']) == 64
        f = importlib.import_module(case['factory_module'])
        assert C.H(Path(f.__file__).read_bytes()) == case['factory_SHA256']
        assert C.H(f.controller(raw, case['form']).encode()) == case['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    assert official.read_bytes() == parent and check(official) == guard
    official.write_bytes(raw)
    assert official.read_bytes() == raw and check(official)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, SHA256=C.CANDIDATE, bytes=len(raw),
        direct_replacement=True, exact_private_tested_candidate=True, private_native_cases=4,
        backups=0, patch_assets=0, releases=0, added_output_files=0,
        actual_Downloads_native_repeat='Required before verified-delivery claim'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
