"""Install only the native-tested full Jay status/size repair, no backup."""
from pathlib import Path
import json
import compose_jay_status_size_publication_00bb_1116 as C
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check

OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/jay-status-delivery-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['direct_Downloads_replacement_authorized'] and not g['backups_patches_releases_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    official = C.Plan.ROM
    before = official.read_bytes()
    guard = check(official)
    assert C.H(before) == C.PIN == g['parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == before
    raw, report = C.proposal(before)
    assert C.H(raw) == C.CANDIDATE == g['candidate_SHA256'] and C.inverse(raw) == before
    assert (report['owned_bytes'], report['changed_bytes']) == (116, 72)
    assert report['all_unowned_00bb_and34Metal_bytes_exact']
    assert all(case['private_native_receipt_SHA256'] for case in g['cases'])
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    assert official.read_bytes() == before and check(official) == guard
    official.write_bytes(raw)
    assert official.read_bytes() == raw and check(official)['ROM_sha256'] == C.CANDIDATE
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    print('RESULT '+json.dumps(dict(installed=True, SHA256=C.CANDIDATE, bytes=len(raw),
        exact_tested_candidate=True, direct_replacement=True, backups=0, patch_assets=0,
        releases=0, output_files_added=0, actual_Downloads_native_repeat='Required before verified-delivery claim'),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
