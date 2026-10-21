"""Durable Pit EL acceptance, Link response issue and qualified Bill/Bass work in progress."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-an.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-am.json'
    assert sha(previous) == 'df80cf44778faf396470f6588eab6a97994251e62a478fddc6c3a7789485656b'
    d = json.loads(previous.read_text())
    installed = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(installed) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    current = json.loads(installed.read_text())
    assert len(current['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in current['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for b in current['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    pins = {
        previous: sha(previous),
        V / 'root49-pit-el-full-ft.json': '51c1d022475603b6c9a507d6f22481143a086e09a1336baf67f194e97a0a3d27',
        V / 'specialist-pit-el-a/phase-index-ab-freeze.json': 'c40b4fd1b9b09877287519543c02fb7c095f35b1e2732169208e10ef016b434c',
        V / 'agent-lsr-link-el-route-a/head-response-scope-handoff.json': 'b570fa099d907fc2772502a8b5b6b2164e67db9e16db7c5710c71be9cda482d5',
        V / 'agent-lsr-link-el-route-a/head-j-passive/freeze.json': '1815f648bb13a63e9c13ac84085bdcc6e965a5c8c6fbd94cc5464059149a35b6',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
        d['references'].append(dict(path=p.relative_to(R).as_posix(), sha256=h, bytes=p.stat().st_size))
    hj = V / 'agent-lsr-link-el-route-a/head-j-passive'
    for n, h in json.loads((hj / 'freeze.json').read_text())['files'].items():
        assert sha(hj / n) == h
    for tag in ('root49fm-bass-live', 'root49fo-bass-live', 'root49fq-bass-live',
                'root49fs-bass-live', 'root49fu-bass-live', 'root49fv-bass-live', 'root49fw-bass-live'):
        f = R / 'build/roster-through-2-2' / f'{tag}-9-v0-mmc3'
        m = json.loads((f / 'manifest.json').read_text())
        assert not m['verified_through_2_2'] and not m['full_frame_audit']
        assert sha(f / 'smb-crossover-mmc3.nes') == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
        item = dict(result=m.get('result'), manifest_sha256=sha(f / 'manifest.json'),
            verified_through_2_2=False, full_frame_audit=False)
        for n in ('inputs.csv', 'trace.csv', 'mm-injury-owner.csv', 'pipe-controller.csv'):
            if (f / n).exists():
                item[n] = dict(sha256=sha(f / n), bytes=(f / n).stat().st_size)
        d['route_results'][tag] = item
    d['Bass_advanced_branches'] = {}
    for tag in ('root49-fl-bass-13-middle-a', 'root49-fn-bass-14-first-bars-a',
                'root49-fp-bass-14-middle-a', 'root49-fr-bass-21-first-stairs-a',
                'root49-fx-bass-21-middle-gap-a'):
        f = R / 'build/roster-through-2-2/search' / tag
        m = json.loads((f / 'manifest.json').read_text())
        assert m['branch_coldboot_verified']
        root = m['winning_reusable_root']
        assert root['verified_coldboot'] and root['ram_bytes_identical'] == 10240
        assert not root['savestate_loads'] and not root['emulated_writes']
        assert sha(f / 'winning-inputs.csv') == root['inputs_sha256']
        d['Bass_advanced_branches'][tag] = dict(manifest_sha256=sha(f / 'manifest.json'),
            target=(f / 'winning-target.lua').read_text().strip(), independent_root=root)
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    d.update(status='ACTIVE_EL_UNCHANGED_PIT_EL_FIXED_CLEAR_LINK_RESPONSE_REPAIR_AND_BILL_COST_PENDING',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        Pit='EL MMC3 X2 full independent fixed24726/24725, sixzero,2-3entry24702+25controlsX40to76;19fields exactW. RootFT rehash781files/441sources/8artifacts.159support receipts include1explicit native landing-then-side-push corner catch, not continuous support/glitchless/source-perfect. M5 AA same-tape negative3442; first19field difference2435, no source defect inferred. No final media/allarsenal claim.',
        Bass='EL FQ clears1-4 and enters2-1at17217; fatal17651 is live kicked GreenKoopa ID0/state84, not a defeated Goomba(ID6). FR cold-verifies17869/X800/Y176. FS/FU wait1798 then timerdeath27184;32px controller probe does not reach pipe1840. FV is bootstrap-only logging syntax negative. FW64px probe records tiles20/21 at+48/+64, passespipe group then pitfall20225/X2250/Y245. FX cold-verifies20285/X2400/Y176. All adopted opaque branches independently match all10240RAM. FY now continues with FWpolicy; no runtime edits.',
        Link_response='Frozen specialist positive contact12019: tile16/cellbottom80 legitimately meets currenttop79.4998/prior82.6665. Separate response gaps: sourcecanonicalPY63/fraction0 vsactual62.4998; source100/120Q00D555 vsnative1/nextAirSync010000; ceiling cue absent. Easy normal15 only demonstrated, not Hard/foreign/cache/crouch/water. No response fix admitted; private350MB repair phase queued after EL route outcome freeze.',
        Bill='G2/EU remain performance-rejected. V9 private443-source layout compiledall4 with OBJECT_EX paired rare closures; third appended selector byte7FF6 itemized. Specialist41984compiled cases/map and205quick cases/map pass exact physical flags/banks with individually bound relocated JumpEngine pointers; no scratch mask. Native rare scopes59/63 exact;4IRQ/NMI-crossed gaps and head/reward/caller-liveness/reset/cost work remain pending. Valid authored warps only; SPACE-world35/code-byte lookup negative retained. No install or cost acceptance.',
        active_specialists=['Bill V9 rare-native/interrupt/liveness/source regressions and final whole-frame costs',
            'Link EL partial1-3 route; separate private source-derived Easy ceiling-response/cue repair next',
            'Pit phase frozen; new300MB Rygar EL ordinary adaptation has cleared1-2, current1-3'],
        root_live_handles=[dict(handle=25142, tag='root49fy-bass-live', ROM='immutable EJ=EL',
            scope='ordinary cold startup continuation from independently verified FX20285; no fullclear yet')],
        workspace_bytes=used, cap_bytes=55_000_000_000, retain_lossless_captures=True,
        accepted_release=False, goal_complete=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets'].update(Bill=5_450_000_000, ordinary_Pit_EL=600_000_000,
        ordinary_Rygar_EL=300_000_000, root_Bass_EL=400_000_000, queued_Link_response=350_000_000)
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
