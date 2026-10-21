"""Snapshot current GQ identity and bounded in-flight roster work."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-ap.json'
    assert not out.exists()
    references = {
        'build/verification/root-current49-progress-ao.json': '84f291dbedead5eeac533d46121cadac3601863c7aaa8ee7ee891149291d1e1d',
        'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json': 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f',
        'build/verification/root49-gq-routes-gu.json': '59b207456809248b58d698125d23b0037659b09fa8473cba28e596ffbac9cf7f',
        'build/verification/root49-el-bass-full-gn.json': 'ccb65684aeb66266f2adb256e2d2f9c2badf4f2acb31b396b3bf94bee8fb0f93',
        'build/verification/root49-el-bass-support-gt.json': 'cb5d350c1bcccc376f48819ade8ce6bf0de14574dc9ad0e74525c350c863684c',
        'build/verification/root49-el-bass-water-profile-gj.json': 'd01fc54b1c2ff0a599fe3352c77fe9924df7e25a94797bfadee0743cf08d7e0d',
        'build/verification/root49-bill-v9-review-gf.json': '444dd03827c8bc25b3d7fd3e17d989043286f7df7b084d32f66b62edec9138a0',
        'build/verification/root49-bill-v9-cost-gh.json': '9254ff54e4ea6cf558052a443f85b723596452345e397890656dbcbd02887eb9',
        'build/verification/agent49-bill-body-hot-w/source-only-freeze-w6.json': 'f80d8921b7501685750895e1e9d2b082882a01ccb98ed02f9f259dedd7889df9',
        'build/verification/specialist-gq-pit-rygar-transfer-a/phase-index-b-freeze.json': '1b9766ad7315bfe291d57aa44d17285d5251b89b86139a8aad7e88b715d5dc98',
        'build/verification/agent-lsr-link-gq-route-a/source-envelope-prose-correction.json': 'b7fb8ae5438bdf4887923b03d4087c1919b2f36d9a30751611a1ad8170bd3e6f',
    }
    for n, value in references.items():
        assert sha(R / n) == value, n
    manifest = json.loads((R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json').read_text())
    assert len(manifest['source_hashes']) == 442
    assert all(sha(R / n) == h for n, h in manifest['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for build in manifest['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 60_000_000_000
    routes = json.loads((V / 'root49-gq-routes-gu.json').read_text())['routes']
    d = dict(status='ACTIVE_GQ_THREE_CURRENT_MMC3_ROUTES_PRIVATE_BILL_PENDING',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        script_sha256=sha(__file__), accepted_release=False, goal_complete=False,
        current_checkpoint='GQ', current_sources442_and_artifacts8_exact=True,
        GQ='EL plus five-file scoped Easy Link normal-jump ceiling response. No Bill successor in main. Both mapper builds byte-exact native-tested private C. GR completed the packaging-only archive path issue.',
        current_MMC3_Easy_routes=routes,
        Link='Current GQ ordinary route C clears1-3 and reaches first castle at14534. Firebar injury at15034 is a genuine native contact; continuation routing remains active, no full current clear.',
        Bill='Private W6 immutable444-source runtime only. Four1780-frame ordinary controls complete with no deaths; exact physical-frame trajectory differs with changed lag timing. Final actual-shot liveness review/freeze is pending. Retained no-shot input-component negative corrected separately. V9 independently reviewed correctness/cost but remains performance-rejected.',
        Bill_cost_qualification='Agent-scoped W6 ordinary overhead versus EC is347.691 M3/377.062 M5 cycles; six-enemy skipped counts246/157 versus EC202/157 and V9292/162. No universal speedup or admission claim.',
        future_union='Must contextually preserve GQ five-file Link repair and EL/D victory helper; whole W6 overlay copying would overwrite them. Union has not been built/tested.',
        Bass_EL='GN independent26689/26688 six-stage zero-death route; GT238 actual accepted launches reclassified. GM MMC5 same-tape pit negative retained. GJ water CPU profiles are overlapping inclusive scopes, not an optimization.',
        historical_coverage='AO and its reference chain retain original scopes: Mario/Luigi Easy+Hard both maps, Scrooge Easy both maps; EC MegaMan and Simon full MMC3 routes; natural Mario/Luigi upgrades, combat and qualified Star checks. None is promoted to current GQ without an actual transfer.',
        active_specialists={
            '/root/link_simon_ryu': 'Current GQ Link ordinary route through2-2; actual castle firebar navigation.',
            '/root/samus_contra_s2': 'Private W6 final fire-liveness and ordinary-control review, then freeze.',
            '/root/mario_luigi_scrooge_s2': 'GQ Pit/Rygar/Bass phase frozen and root-reviewed; newly assigned Samus ordinary current-GQ route, historical candidate inventory first.'},
        root_live_handles=[],
        remaining=['Every character/alternate through2-2 on final integrated runtime and intended mapper/mode scopes.',
            'Every special/weapon/upgrade, remaining source fidelity gaps and actual lag optimizations.',
            'Final retained lossless recordings and frame/audio review.'],
        workspace_bytes=used, cap_bytes=60_000_000_000, retain_lossless_captures=True,
        phase_budgets=dict(Bill_W=5_800_000_000, Link_GQ_route=450_000_000,
            Samus_GQ_route=400_000_000, frozen_GQ_transfer=200_000_000,
            frozen_Rygar_EL=500_000_000, frozen_Pit_EL=600_000_000,
            frozen_Link_response=350_000_000, root_Bass_EL=700_000_000),
        runtime_changes_this_snapshot=False, files_deleted=False,
        references=[dict(path=n, sha256=h, bytes=(R / n).stat().st_size) for n, h in references.items()],
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
