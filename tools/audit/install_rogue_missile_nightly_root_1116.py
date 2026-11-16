"""Direct no-backup install of the exact native-qualified Rogue operand fix."""
from pathlib import Path
import json
import compose_rogue_missile_9826_1116 as C
import replay_rogue_missile_cb95_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'


def main():
    g = json.loads((C.R/'docs/qa/allocations/rogue-missile-cb95-delivery-root-1116.json').read_bytes())
    assert g['direct_Downloads_replacement_authorized'] and not g['backups_patches_releases_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    assert (g['parent_SHA256'], g['candidate_SHA256']) == (C.PARENT, C.CANDIDATE)
    assert len(g['cases']) == 2 and {r['kind'] for r in g['cases']} == {'missile', 'full'}
    parent = C.ROM.read_bytes()
    guard = check(C.ROM)
    assert C.H(parent) == C.PARENT and not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert target.read_bytes() == parent
    raw, q = C.proposal(parent)
    assert C.inverse(raw) == parent and q['all_unowned_bytes_exact']
    assert q['protected'] == ['Mini20', 'Sonic94'] and (q['owned_bytes'], q['changed_bytes']) == (2, 1)
    for case in g['cases']:
        assert case['private_native_passed'] is True and len(case['private_native_receipt_SHA256']) == 64
        assert C.H(F.controller(raw, case['kind']).encode()) == case['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    assert C.ROM.read_bytes() == parent and check(C.ROM) == guard
    C.ROM.write_bytes(raw)
    assert C.ROM.read_bytes() == raw and check(C.ROM)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, SHA256=C.CANDIDATE, bytes=len(raw),
        exact_private_tested_candidate=True, direct_replacement=True, Mini20_Sonic94_preserved=True,
        backups=0, patch_assets=0, releases=0, added_output_files=0,
        actual_Downloads_native_repeat='Required before verified-delivery claim'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
