"""Preserve later route/repair progress without changing the installed ROMs."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-ai.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-ah.json'
    assert sha(previous) == '214c0035cb98976b2ef30b62e1db2e1a56d0c180767f261dab017498b2c509c1'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(checkpoint) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    by = json.loads(checkpoint.read_text())
    assert len(by['source_hashes']) == 440
    assert all(sha(R / n) == h for n, h in by['source_hashes'].items())
    for build in by['builds']:
        assert all(sha(R / x['path']) == x['sha256'] for x in build['artifacts'].values())
    handoff = V / 'specialist-scrooge-by/handoff-m3-a.json'
    assert sha(handoff) == 'dbc2121e79575e652e425fc0b6bba466143510bd0509d61482f3ba3a3616cfda'
    # The handoff is independently pinned even if its companion uses a different filename.
    scrooge_companions = [p for p in handoff.parent.glob('*.json')
                         if sha(p) == 'c669a9f839f10b18bdae3d0da5a689c3086305d9d1b90d8db38033c91f2d75ef']
    assert len(scrooge_companions) == 1
    de = R / 'build/roster-through-2-2/search/root49-de-megaman-14-bars-a'
    manifest = json.loads((de / 'manifest.json').read_text())
    verified = json.loads((de / 'best-coldboot-verified.json').read_text())
    assert manifest['best_coldboot_verified'] and verified['verified']
    assert verified['ram_bytes_identical'] == 10240 and not verified['savestate_loads'] and not verified['emulated_writes']
    assert not json.loads((de / 'result.json').read_text())['won']
    assert sha(de / 'best-inputs.csv') == manifest['best_inputs_sha256']
    target = (de / 'best-target.lua').read_text().strip()
    assert 'x=1346,y=112' in target and 'poll=14378' in target
    refs = [previous, checkpoint, handoff, scrooge_companions[0], R / 'docs/qa/easy-hard-legacy-v49.md']
    refs += [de / n for n in ['manifest.json', 'result.json', 'best-coldboot-verified.json',
                              'best-target.lua', 'best-inputs.csv', 'best-ram.bin', 'best-reusable-root.json']]
    df = R / 'build/roster-through-2-2/search/root49-df-megaman-14-bars-b'
    dm = json.loads((df / 'manifest.json').read_text())
    dv = json.loads((df / 'coldboot-verified.json').read_text())
    assert dm['branch_coldboot_verified'] and dv['verified'] and dv['ram_bytes_identical'] == 10240
    assert not dv['savestate_loads'] and not dv['emulated_writes']
    assert sha(df / 'winning-inputs.csv') == dm['winning_inputs_sha256']
    refs += [df / n for n in ['manifest.json', 'coldboot-verified.json', 'winning-target.lua', 'winning-inputs.csv']]
    dh = R / 'build/roster-through-2-2/root49dh-megaman-live-1-v0-mmc3'
    hr = json.loads((dh / 'result.json').read_text())
    hm = json.loads((dh / 'manifest.json').read_text())
    assert hr['failure'] == 'death' and hr['frames'] == 14848
    assert not hm['full_frame_audit'] and hm['controller_only'] and not hm['memory_or_register_writes']
    refs += [dh / n for n in ['result.json', 'manifest.json', 'mm-slide-events.csv', 'trace.csv', 'inputs.csv']]
    dg = V / 'root49-bill-body-union-dg/report.json'
    assert sha(dg) == '3252ea899aa312e7cf8efefeabed360401d32589f468ddb6997dacc7dcb3ad43'
    gr = json.loads(dg.read_text())
    assert all(x['exact_expected_rom'] and x['exit'] == 0 for x in gr['builds']) and len(gr['builds']) == 4
    assert all(sha(dg.parent / 'source' / n) == h for n, h in gr['source_hashes'].items())
    source_freeze = V / 'agent49-bill-source-body-f/source-freeze-j.json'
    assert sha(source_freeze) == '5d5ab8ab8852c16630cec3e0c619868bae1e89d43776dd839a8dbd101ab36f96'
    refs += [dg, source_freeze]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    report = dict(status='ACTIVE_BY_STABLE_ORDINARY_ROUTES_AND_PRIVATE_SOURCE_REPAIRS_CONTINUE',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        previous_goal_turn_classification='progress', installed_BY_440_sources_and_artifacts_exact=True,
        source_and_runtime_changed_this_progress_packet=False,
        current_full_route_proofs='Mario/Luigi Easy+Hard bothmaps; Scrooge Easy MMC3 fixed20170/20169 sixstages zero deaths, all19fields exact discovery, source/mode guard and81 real dry takeoffs. Unrecorded; no all-arsenal/media claim.',
        MegaMan=dict(current_room='1-4', first_three_stages_cleared=True,
            DE='Bounded search fails its1590 goal but preserves independently cold-verified best14378/X1346/Y112/power0. No runtime defect inferred.',
            DF='Independently cold-verified winner14626/X1590/Y128/power0; all10240RAM exact. Controller stream includes82 Down-bearing polls; actual slide events need the DH passive observer.',
            root_live_handle=54457, tag='root49-di-megaman-14-fireball-a',
            DH='Discovery-fast partial dies14848 at later castle fireball/step. Passive observer proves actual slide pose12 at14496,14561,14592 with normal endings; no full frame audit/recording claim.',
            DI='Bounded search from real DH safe grounded prefix14804 toward2020 before Bowser. Independent cold proof required.'),
        Scrooge='MMC3 proof frozen. MMC5 Q clears1-2/1-3; S independently cold-verifies11583/X1509/Y128. T/U deaths retained. Guarded V confirms body touches Bowser atX159 while pinned strict pogo stopsX158, matching the existing intentionally narrower attack oracle; no missing valid-overlap priority. Continue actual earlier takeoff/wait timing, no source edit.',
        Bill='Both maps final-layout2784 geometry/selection/seam/death/flag cases including1176 actual actor-consumer comparisons pass. Source J441 files frozen; DG privately adds disjoint CG baseline guards and produces exact F crossover ROMs plus exact CG baseline ROMs, all4 builds. Final head/cost/foreign/reset admission pending. Measured selector+162..166 and publication+554..566 cycles prompt a separate exact-math optimization candidate. Two appended7FE5/7FE6 bytes; no main admission.',
        Simon='Passive frozen-attack victory cause proved. Experimental21B hot gate B adds20 ordinary guest cycles and shifts real input phase; retained negative. Rare-only C changes only victory farcall operands, addsPLAYER28/RYU_COLD184, zero ordinary hot cost; actual I-prefix continuation clears castle and enters2-1 at14784, later dies15829. Source attack/shoot timers progress without immediate cancellation; pending release events retained. Native automatic motion during remaining attack and frozen victory projectile pools remain explicit adaptation limits. Native ABI/cycle/component/freeze review pending.',
        active_specialists=['Bill body/source-water epoch/cost and closure finalization',
                            'Simon rare victory/source WATCH lifecycle repair',
                            'Scrooge MMC5 guarded pogo/body contact review and controller continuation'],
        source_repair_admission='All current repair candidates stay private. Stable public local artifacts remain BY. Any successor needs compiled/binary/native checks and new ordinary route validation.',
        remaining='All13 final-runtime routes, every alternate/special/upgrade/weapon, measured lag optimization, final retained lossless captures and complete video/audio review.',
        workspace_bytes=used, cap_bytes=55_000_000_000,
        retain_lossless_captures=True, files_deleted=False,
        references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(out.name, sha(out), used)


if __name__ == '__main__':
    main()
