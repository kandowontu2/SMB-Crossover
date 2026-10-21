"""Durable active-goal handoff after rollback and isolated Link WATCH admission."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-aj.json'
    assert not out.exists()
    manifest = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(manifest) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    d = json.loads(manifest.read_text())
    assert len(d['source_hashes']) == 441 and all(sha(R / n) == h for n, h in d['source_hashes'].items())
    for row in d['builds']:
        assert all(sha(R / x['path']) == x['sha256'] for x in row['artifacts'].values())
    assert not (R / 'src/bill_source_body.s').exists()
    pins = {
        manifest: sha(manifest),
        V / 'root-current49-progress-ai.json': '49555b0437511565a901078949dfbc093b596f0f0f8f29ecd6c4ab69e9221962',
        R / 'build/checkpoints/roster-audit-v49-body-victory-du/manifest.json': 'd518efb726559ac120ec4517a73e045e674ec9219a0317884efb8be2ddeeb477',
        R / 'build/checkpoints/roster-audit-v49-victory-ec/manifest.json': '1618a568e0d14e8681efd0dbfc84d68bec1636bfb34703e3c5b9eddea73759d1',
        V / 'root49-body-victory-union-dq/report.json': '40b361bb28db5f1e923c8079d1256bddfd622714ddd46ec44f9110f3039536a7',
        V / 'root49-union-admission-dv.json': 'df27f68df706f7b3a3fed7bb916a4b6e610152e2b201875830a456a2b8863ed7',
        V / 'root49-victory-review-do.json': 'c859e1e53ce3bc3b443228ae5210b314727c8a7406419bb954f86c8df11a0568',
        V / 'root49-union-native-dr.json': '2a5410c864e02aae2a0670b7e77462a670c5209fa805b94a7185b9e9c6495abb',
        V / 'agent49-bill-source-body-f/freeze-o.json': 'c0ee2a77e4bc72442588cc7618b96ce256d3f5aac725e9662c8e1cdef0d16049',
        V / 'agent49-bill-body-dq-rebind-r/freeze-r.json': 'e7d9338d3f8eb7ca3d452a4445d79a8ebc5c533a5e9469dcd64aad88d4ae7126',
        V / 'agent49-du-bill-route-a/incident-freeze-f.json': '5248dd822c9871781bd51e3db0417271a0dcefb86065e3adf8f01c0a44747b3f',
        V / 'agent-lsr-victory-repair-d/implementation-freeze.json': '101980b5961adf0d69b9f46dc74cd068b2a5619e681b36a96fd6c7edd845baed',
        V / 'agent-lsr-victory-repair-ej-checks-a/freeze.json': '92e80a61805cecdb4981b3b12429a219df5d66a251ce5e997f8aadce3a85078a',
        V / 'root49-link-watch-ej/report.json': 'f4a24deaafce07dfad43c720196518156186109ba9e83bcd3d83e8243a5e0caf',
        V / 'root49-du-megaman-injury-dz.json': '9e33736084ec3d9c035d7ffc8f7c1ba687762b9c6cce09aabf61ab3b9f200a54',
        V / 'specialist-scrooge-by/complete-route-index-a.json': '397ed7cfedf479f4934e9f8cd37232a4f227f143033370437fc5f62c7761049d',
        V / 'specialist-mario-luigi-scrooge-coverage-ec-a/coverage.json': '03b4c337a254c90659c6fc0048c24842730fc7bc4147c5616b1c3cd0a821a801',
    }
    refs = []
    for p, h in pins.items():
        assert sha(p) == h, p
        refs.append(dict(path=p.relative_to(R).as_posix(), sha256=h, bytes=p.stat().st_size))
    # These mutable-goal route outputs are already terminal and remain scoped
    # to their exact recorded ROM. Fresh EN is terminal; EO is still running.
    route_results = {}
    for tag in ('root49dn-megaman-live', 'root49ds-megaman-union', 'root49dw-megaman-union',
                'root49dx-megaman-injury', 'root49ea-megaman-union', 'root49eg-megaman-victory',
                'root49eh-megaman-victory', 'root49ei-megaman-victory', 'root49ek-megaman-spring',
                'root49en-megaman-pole'):
        folder = R / 'build/roster-through-2-2' / (tag + '-1-v0-mmc3')
        p = folder / 'result.json'
        route_results[tag] = dict(result=json.loads(p.read_text()), result_sha256=sha(p),
                                  inputs_sha256=sha(folder / 'inputs.csv'), trace_sha256=sha(folder / 'trace.csv'),
                                  actual_ROM_sha256=sha(folder / 'smb-crossover-mmc3.nes'))
    assert route_results['root49en-megaman-pole']['result']['stage_entries']['1-1'] == 20885
    for tag in ('root49-dm-megaman-14-bowser-a', 'root49-dp-megaman-21-pipe-a',
                'root49-dt-megaman-union-12-pipe-a', 'root49-dy-megaman-union-12-pipe-b'):
        folder = R / 'build/roster-through-2-2/search' / tag
        m = json.loads((folder / 'manifest.json').read_text())
        assert m['branch_coldboot_verified']
        assert sha(folder / 'winning-inputs.csv') == m['winning_inputs_sha256']
        refs.append(dict(path=(folder / 'manifest.json').relative_to(R).as_posix(),
                         sha256=sha(folder / 'manifest.json'), bytes=(folder / 'manifest.json').stat().st_size))
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    report = dict(status='ACTIVE_EL_WORKING_BILL_REGRESSION_REVERTED_PRIVATE_SOURCE_AXIS_FIX_CONTINUES',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        previous_goal_turn_classification='progress', installed_EL_441_sources_and_artifacts_exact=True,
        accepted_release=False, goal_complete=False, files_deleted='Only our exact backed-up added main Bill source removed during rollback; no captures/evidence deleted.',
        source_runtime_change='Installed DU after seeded source tests, then ordinary testing proved a real head-side consumer regression. EC reverted all Bill hunks while keeping C. EL adds only actual-EJ-tested Link task2 helper.',
        EL='Castle-stall repair and normal EasyLink task2 animation;616 native cases plus1000 strict compiled ABI,4 builds. Foreign/Hard rare+42cycles, native/ordinary0. Rejected Bill F/N remains absent.',
        Bill='Frozen real pipe/source-axis incident overrides seeded cell-only admission. G2 consumer correction private on DQ: first real Right+A clears pipe; first G1 native matrix retained24 vine-field failures. G2M3 all5192 consumer/hardware cases pass, M5 running;9978 inherited fixtures, ordinary activation/break/reset, closure/cost and finalEL union remain pending.',
        historical_routes='BY Mario/Luigi Easy+Hard bothmaps, plus Scrooge Easy bothmaps. ScroogeM3=20170/20169,M5=20412/20411,sixzero and2-3 controls; current-build replays and final recordings still required.',
        coverage='Frozen fifteen-feature Mario/Luigi/Scrooge inventory preserves historical native passes and exact tier-transition limits. New300MB bounded natural upgrade phase uses explicit EC, full event/frame audit, no state grants.',
        MegaMan='EC EN clears five stages and enters2-2 at20885; allsix entered is not fullclear. Ordinary controller omitted water jumpAge initialization and cut A after6polls; EO corrects input hold only. SourceC and EL are distinct recorded identities; finalEL fixed replay/media still required.',
        root_live_handles=[dict(handle=1990, tag='root49eo-megaman-water', ROM='explicit frozen EC',
                                scope='controller-only discovery-fast; no frame/media final acceptance')],
        active_specialists=['Private Bill G2 source consumer/hardware/cost and old fixtures',
                            'Simon explicit C spring continuation; EL/EJ acceptance frozen',
                            'Bounded ordinary natural Mario/Luigi upgrade gaps on frozen EC'],
        limits='EL Link animation only PlayerVictoryWalk task2; bridge tasks0/1/3/4, full WATCH projectiles, hurt/special-form parity remain open. Native integer-enemy/terrain/firebar geometry qualifications retained.',
        remaining='All13 final-runtime full routes through2-2;every special/alternate/upgrade;actual lag optimization;retained final lossless recordings and video/audio review.',
        workspace_bytes=used, cap_bytes=55_000_000_000, retain_lossless_captures=True,
        phase_budgets=dict(Bill=4_800_000_000, Simon_repair=800_000_000, Scrooge_BY=800_000_000, ordinary_Mario_upgrades=300_000_000),
        route_results=route_results, references=refs,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), used)


if __name__ == '__main__':
    main()
