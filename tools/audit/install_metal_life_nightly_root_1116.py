"""Directly replace one nightly with tested00bb, without any backup file."""
from pathlib import Path
import json

import compose_metal_life_snapshot_root_1116 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/metal-life-delivery-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['Downloads_direct_replacement_authorized'] and not g['backups_releases_patches_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    official = Path(g['target'])
    assert official == C.Plan.Current.ROM
    parent = official.read_bytes()
    before = check(official)
    assert C.H(parent) == C.PIN == g['parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    raw, composition = C.proposal(parent)
    assert C.H(raw) == C.CANDIDATE == g['tested_candidate_SHA256'] and C.inverse(raw) == parent
    assert (composition['owned_bytes'], composition['changed_bytes']) == (34, 30)
    assert composition['all_unowned_current7c0f_bytes_exact']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    assert official.read_bytes() == parent and check(official) == before
    official.write_bytes(raw)
    assert official.read_bytes() == raw and check(official)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, SHA256=C.H(raw), bytes=len(raw),
        exact_tested_private_bytes=True, patch_guard_clear=True, backups=0, releases=0, patch_assets=0,
        new_output_files=0, actual_Downloads_native_repeat='Still required before verified-delivery claim'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
