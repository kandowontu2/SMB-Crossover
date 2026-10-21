"""Preserve the current runtime and completed Simon route without promoting partial runs."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-am.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-al.json'
    assert sha(previous) == 'ae4412193a331300cab4ffeb28538c8d38e27ee3917388302056a7ee7fc0b512'
    d = json.loads(previous.read_text())
    installed = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(installed) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    main_state = json.loads(installed.read_text())
    assert len(main_state['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for build in main_state['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    pins = {
        previous: sha(previous),
        V / 'root49-simon-full-review-fj.json': '8d33b00a2c87ba2bef1b4c598c18bbc810415c200d1fa9c3e82bc10323d3b627',
        V / 'agent-lsr-victory-repair-c/route-t/freeze.json': '7b15d9a8827235aea25a79079dac20633608c22b571110576a70986c406a0e40',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
        d['references'].append(dict(path=p.relative_to(R).as_posix(), sha256=h, bytes=p.stat().st_size))
    for tag in ('root49fh-bass-live', 'root49fk-bass-live'):
        folder = R / 'build/roster-through-2-2' / f'{tag}-9-v0-mmc3'
        m = json.loads((folder / 'manifest.json').read_text())
        assert not m['verified_through_2_2'] and not m['full_frame_audit']
        assert sha(folder / 'smb-crossover-mmc3.nes') == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
        d['route_results'][tag] = dict(result=m['result'],
            result_sha256=sha(folder / 'result.json'), manifest_sha256=sha(folder / 'manifest.json'),
            inputs_sha256=sha(folder / 'inputs.csv'), trace_sha256=sha(folder / 'trace.csv'),
            verified_through_2_2=False, full_frame_audit=False)
    for tag in ('root49-fg-bass-12-pipes-a', 'root49-fi-bass-13-first-gap-a'):
        folder = R / 'build/roster-through-2-2/search' / tag
        p = folder / 'manifest.json'
        m = json.loads(p.read_text())
        assert m['branch_coldboot_verified']
        root = m['winning_reusable_root']
        assert root['verified_coldboot'] and root['ram_bytes_identical'] == 10240
        assert not root['savestate_loads'] and not root['emulated_writes']
        assert sha(folder / 'winning-inputs.csv') == root['inputs_sha256']
        d['references'].append(dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size))
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    d.update(status='ACTIVE_EL_UNCHANGED_SIMON_C_FIXED_CLEAR_BASS_PLATFORM_ROUTE_AND_BILL_COST_WORK',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        Simon='C/EC full independent fixed replay23853frames/23852polls, six zero-death stages, 2-3entry23829 plus25controls X40to70. All nine audit CSV streams literally repeat discoveryT. RootFJ independently rehashes441source/8artifacts/frozen packet. Historical C scope; final EL/successor/media/allarsenal remain open.',
        Bass='EL FG independent cold branch passes1-2 pipes/foes with natural tier1; FH clears1-2 and enters1-3at11141, then pitfall11385. FI independent cold branch reaches540/160 grounded with tier1. FK continues to12419/X1120/Y241 custom pitfall; no native injury-owner callback receipt. Both adopted branches replay all10240RAM exactly; partial discoveries, no full clear or source-defect claim.',
        Bill='G2/EU remain unshipped due material measured cost. Separate V6 hot-layout successor is private: rare native closures move to bank9 to make room for near body paths. Exact flags, actual mapper selector, new capture scratch lifetimes and NMI safety must be proved before final cost comparison or admission.',
        active_specialists=[
            'Bill private V6 closure/flags/selector correctness and full ordinary/seeded cost comparison',
            'Link new300MB explicit EL ordinary phase; early jump during sword cannot queue source jump, controller retiming only',
            'Pit explicit EL clears five stages; 400MB phase checks water-fish contacts and independent full fixed audit'],
        root_live_handles=[dict(handle=57875, tag='root49-fl-bass-13-middle-a', ROM='immutable EJ=EL',
            scope='ordinary-input search from FK12280; no adoption without independent power-on/all10240RAM proof')],
        workspace_bytes=used, cap_bytes=55_000_000_000, retain_lossless_captures=True,
        accepted_release=False, goal_complete=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets'].update(ordinary_Pit_EL=400_000_000, ordinary_Link_EL=300_000_000)
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
