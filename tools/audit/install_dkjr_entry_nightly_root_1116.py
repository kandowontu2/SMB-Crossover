"""Replace the single Downloads nightly with the tested DK Jr image, no backup."""
import json
from pathlib import Path

import compose_dkjr_forced_entry_current_1116 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/dkjr-entry-delivery-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['Downloads_direct_replacement_authorized'] and g['root_visually_reviewed_both_entry_images']
    assert not g['backups_releases_patches_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    official = Path(g['target'])
    assert official == C.BT.ROM
    before = check(official)
    parent = official.read_bytes()
    assert C.H(parent) == C.Parent.PIN == g['parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    raw, composition = C.current_proposal(parent)
    assert C.H(raw) == C.CANDIDATE == g['tested_candidate_SHA256']
    assert C.Parent.inverse(C.inverse(raw)) == parent
    assert composition['all_unowned_a3fb_bytes_exact']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    assert check(official) == before and official.read_bytes() == parent
    official.write_bytes(raw)
    assert official.read_bytes() == raw and check(official)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == official.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, installed_SHA256=C.H(raw), bytes=len(raw),
        tested_private_candidate_exact=True, private_native_receipt_SHA256=g['private_native_receipt_SHA256'],
        nightly_patch_guard_clear=True, backups=0, releases=0, patch_assets=0, new_output_files=0,
        verification_scope='Installed bytes verified; actual Downloads native repeat still required'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
