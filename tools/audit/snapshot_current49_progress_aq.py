"""Freeze current GQ identity, private integration state and new Sophia evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-aq.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-ap.json'
    assert sha(previous) == '4cb287239f664f223d8fff621c37ed85b45b90256463ed478fc121ef023ead9a'
    d = json.loads(previous.read_text())
    manifest = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    assert sha(manifest) == 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f'
    gq = json.loads(manifest.read_text())
    assert len(gq['source_hashes']) == 442 and all(sha(R / n) == h for n, h in gq['source_hashes'].items())
    for build in gq['builds']:
        assert all(sha(R / p['path']) == p['sha256'] for p in build['artifacts'].values())
    assert not (R / 'src/bill_source_body.s').exists()
    refs = {
        'build/verification/root-current49-progress-ap.json': sha(previous),
        'build/verification/agent49-bill-body-hot-w/freeze-final-w6.json': '1df55ea3bc787439a35fbbeb5b4c7018fc80f7ff746f805339ac60c10f210c1d',
        'build/verification/root49-bill-w6-review-gz.json': '6c69386dcbf5604eb3a888881d144bdb4801a8c4899bd62f1a4c2009ea0a8b62',
        'build/verification/root49-link-firebar-lead-hf.json': 'b685944f556f278457a1e9d233e3bd1acf1d7df2e21ba55dc5fd6a1b69a6ecba',
        'build/verification/root49-sophia-body-lead-hj.json': '91ac217f1aa65777d5914fdc3874e2d1c3e1ebdcefde5c99fde6ee6f758a364e',
        'build/roster-through-2-2/search/root49-gy-sophia-13-upper-pillar-a/manifest.json': '0d331b87f4b04a38d7d2328f06a614d1d206eced85abb9f5433d134077b81647',
        'build/roster-through-2-2/search/root49-he-sophia-13-platforms-a/manifest.json': 'ee381fffd3c1e0d1f96e9f1bf5a746eb9f91d2f5bf698e1b90b0d5ec3fcb8973',
    }
    for n, value in refs.items():
        assert sha(R / n) == value, n
    branches = {}
    for name, basename in [('root49-gy-sophia-13-upper-pillar-a', 'best'), ('root49-he-sophia-13-platforms-a', 'winning')]:
        folder = P / 'search' / name
        m = json.loads((folder / 'manifest.json').read_text())
        root = m[basename + '_reusable_root']
        assert root['verified_coldboot'] and root['ram_bytes_identical'] == 10240
        assert not root['savestate_loads'] and not root['emulated_writes']
        assert sha(folder / (basename + '-inputs.csv')) == root['inputs_sha256']
        branches[name] = root
    routes = {}
    for tag in ('root49gv-sophia-live', 'root49gw-sophia-live', 'root49gx-sophia-live',
        'root49ha-sophia-live', 'root49hb-sophia-live', 'root49hc-sophia-live', 'root49hd-sophia-live',
        'root49hg-sophia-live', 'root49hh-sophia-firebar', 'root49hi-sophia-body'):
        folder = P / (tag + '-11-v0-mmc3')
        m = json.loads((folder / 'manifest.json').read_text())
        assert not m['verified_through_2_2']
        routes[tag] = dict(result=m.get('result'), manifest_sha256=sha(folder / 'manifest.json'),
            inputs_sha256=sha(folder / 'inputs.csv'), full_frame_audit=m['full_frame_audit'])
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R);assert used < 60_000_000_000
    d.update(status='ACTIVE_GQ_PRIVATE_BILL_LINK_FIREBAR_UNION_AND_SOPHIA_SOURCE_BODY_WORK',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        previous_goal_turn_classification='progress', current_sources442_and_artifacts8_exact=True,
        Bill='W6 frozen and root GZ rehashes444source/eight artifacts/192native receipts/four ordinary traces. Private GQ+W6 union C compiles with old baselines/audio/DPCM/RAM/SMC/CHR/header guards. Later D is a retained input-flags negative for rare VineAnchor; restore input P before cold core is pending combined H build. No private union is installed.',
        future_union='W6 and GQ conflict in old spring tail. Rare death112 moves into LEVEL FF tail; H adds96/85 resident +184cold. Further rare pickup/climb/anchor relocation is being proved, preserving both behavior layers and all audio PCs. Final actual union native/ABI/NMI/cost controls remain required.',
        Link='GQ route clears1-3/castleentry14534 then actual disjoint second-bar failure15299. Root HF independently verifies source/current-body discrepancy and full9CSV replay. Private H both maps/baselines compile, no RAM, native/ABI checks pending. Full source firebar birth/rotation/anchor parity remains qualified.',
        Sophia=dict(scope='Current GQ MMC3 Easy, normal variant, outlinesOff; no final recording/full2-2 clear.',
            ordinary_routes=routes, adopted_cold_branches=branches,
            reached='Clears1-1 and1-2, HE farbank1660/Y80 at9381, HG clears1-3 and castleentry10652.',
            next_defect='Castle fatal11129 is repeated HH/HI, all21 trace/input fields literal HG, all9 audit streams literal HH/HI. HJ binds flat normal19x15.5source body versus14x24native, full10240RAM preChgSDir, authoredground144/PY112 and all six emitted bar parts. Source-shaped body and actual consumers need correction before routing onward.',
            next_action='Implement exact source normal flat fractional body/consumer rules in a new private phase. Keep wall/ceiling/vine/head/side source requirements explicit; do not replace correction with another controller wait.',
            qualifications='Source/native firebar full phase/anchor and pixel-positive parity unproved; sourceFrame CSV is rawRgBillBurst, actual Sophia form bound separately. Existing native integer enemy-proxy geometry is not full Flash bitmap equivalence.'),
        active_specialists={
            '/root/samus_contra_s2': 'Private combined GQ+W6+H layout and rare-wrapper ABI/interrupt/cost closure; frozen parents untouched.',
            '/root/link_simon_ryu': 'Private Link H disjoint firebar gate proof and combined placement coordination; source phase fidelity qualified.',
            '/root/mario_luigi_scrooge_s2': 'Current Samus GQ ordinary route; natural Morph/bomb corridor established,1-2finish-room rule corrected; platform geometry verified, no source defect established.'},
        root_live_handles=[], workspace_bytes=used, cap_bytes=60_000_000_000,
        runtime_changes_this_snapshot=False, accepted_release=False, goal_complete=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets'].update(root_Sophia_GQ=500_000_000, private_Bill_union=400_000_000, private_Link_firebar=350_000_000)
    d['references'] += [dict(path=n, sha256=value, bytes=(R / n).stat().st_size) for n, value in refs.items()]
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
