"""Freeze current EL identity and Bass progress without accepting private repairs."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-ao.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-an.json'
    assert sha(previous) == '0a201da780476fc5cba91be5b95e8ea9afde89611c1af1822ec957651d1eb819'
    d = json.loads(previous.read_text())
    manifest = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(manifest) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    installed = json.loads(manifest.read_text())
    assert len(installed['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for build in installed['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    d['references'].append(dict(path=previous.relative_to(R).as_posix(),
        sha256=sha(previous), bytes=previous.stat().st_size))
    fz = R / 'build/roster-through-2-2/search/root49-fz-bass-21-flying-fish-a'
    fm = json.loads((fz / 'manifest.json').read_text())
    root = fm['winning_reusable_root']
    assert fm['branch_coldboot_verified'] and root['verified_coldboot']
    assert root['ram_bytes_identical'] == 10240
    assert not root['savestate_loads'] and not root['emulated_writes']
    assert sha(fz / 'winning-inputs.csv') == root['inputs_sha256']
    d['Bass_advanced_branches'][fz.name] = dict(manifest_sha256=sha(fz / 'manifest.json'),
        target=(fz / 'winning-target.lua').read_text().strip(), independent_root=root)
    for tag in ('root49fy-bass-live', 'root49ga-bass-live'):
        f = R / 'build/roster-through-2-2' / (tag + '-9-v0-mmc3')
        m = json.loads((f / 'manifest.json').read_text())
        assert not m['verified_through_2_2'] and not m['full_frame_audit']
        assert sha(f / 'smb-crossover-mmc3.nes') == fm['rom_sha256']
        item = dict(result=m.get('result'), manifest_sha256=sha(f / 'manifest.json'),
            verified_through_2_2=False, full_frame_audit=False)
        for n in ('inputs.csv', 'trace.csv', 'mm-injury-owner.csv', 'pipe-controller.csv'):
            if (f / n).exists():
                item[n] = dict(sha256=sha(f / n), bytes=(f / n).stat().st_size)
        d['route_results'][tag] = item
    cost = V / 'agent49-bill-body-hot-v/cost-review-v9.json'
    d['references'].append(dict(path=cost.relative_to(R).as_posix(), sha256=sha(cost),
        bytes=cost.stat().st_size, scope='Read and numerically checked by root; underlying cost receipts not yet independently rehashed.'))
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    d.update(status='ACTIVE_EL_UNCHANGED_BASS_IN_2_2_PRIVATE_REPAIRS_NOT_ADMITTED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        Bass='FZ independently verifies frame/poll20683, X2899/Y176, all10240RAM. GA ordinary continuation clears2-1, enters2-2 at22332; fatal23909/X1380/Y105 is actual Blooper ID7 slot3 at1368/Y94. Native boxes touch x113; no disjoint-source defect inferred. GB now searches from genuine GA23700 before the middle fish/coral group. All routes unrecorded discovery partials; no full current Bass clear.',
        Bill='V9 remains private. Agent reports 63 native rare scopes/map with exact IRQ composition and65 public-head scopes/map. Four apparent NMI-crossed BG suffixes were misowned weapon Activate calls, now retained observer negatives while the real parents are separately bound. V9 cost review still adds738.654/766.025 ordinary cycles vs EC, six-enemy skips292/162 vs EC202/157. Not performance accepted. Source/layout/capture closure freeze and distinct-cell head successor remain pending.',
        Link_response='Private repair phase active; no installed fix. First LEGACY_COLD placement overflowed actual M5 span; bank9 variant compiles but cannot combine with V9. Agent now uses optional LINK_HEAD_COLD after OBJECT_EX in bank7: reported helper513B fits combined V9 tail660/714, leaving147/201B. Exact fallback flags/live scratch, source Q16/canonical position/cue and both-map native proofs still pending.',
        active_specialists=['Bill V9 exact consumer ownership/capture closure, then head-first cost successor',
            'Link private source-derived Easy positive ceiling-response/cue repair; EL route frozen partial',
            'Rygar EL ordinary adaptation cleared1-4 and enters2-1 at12509; N controller adaptation ongoing'],
        root_live_handles=[dict(handle=64902, tag='root49-gb-bass-22-middle-fish-a',
            scope='Bounded unedited-state discovery from genuine GA23700, mandatory separate cold verifier before adoption')],
        workspace_bytes=used, cap_bytes=55_000_000_000, retain_lossless_captures=True,
        accepted_release=False, goal_complete=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets']['queued_Link_response'] = 350_000_000
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
