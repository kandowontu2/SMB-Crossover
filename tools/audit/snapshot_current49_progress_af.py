"""Preserve foreign-route isolation and the independently found lifetime gap."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-af.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-ae.json'
    assert sha(previous) == '30123c4a02a8ecada9ad1ea9baba1be1708aa658e9f98840d4aa991c28262855'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    for build in published['builds']:
        assert all(sha(R / item['path']) == item['sha256'] for item in build['artifacts'].values())
    pins = {
        'root49-easy-pit-empty-be/freeze-bi.json': '2442526554d3ac401a542d77998c5569681eb6929bbb6c0ea992a96159833078',
        'root49-easy-pit-empty-be/ordinary-scrooge-bj/report.json': '8352fead73931c5db0465f85ff9a21890910f8542d85e75a6e40a779644755f2',
        'root49-easy-pit-empty-be/ordinary-scrooge-control-bk/report.json': '041178b13730ffd71ef8a2202b91e5545714f96828d3a705679d9ee2eca7f853',
        'root49-easy-pit-empty-be/ordinary-scrooge-review-bl/report.json': 'a4bda946e6a19e07b326153ab50139c72c36d902130742dff9e95a50f8466510',
        'root49-bill-lifetime-review-bm/report.json': '7d33bef84b41851d3bd9d22c8b8c1109dc6fdf775163d73ae1d96d8d14a41e74',
    }
    for name, digest in pins.items():
        assert sha(V / name) == digest
    frozen = json.loads((V / 'root49-easy-pit-empty-be/freeze-bi.json').read_text())
    assert all(sha(R / x['path']) == x['sha256'] for x in frozen['files'])
    for name in ['root49-easy-whip-phase-y', 'root49-easy-bro-union-ab', 'root49-easy-ryu-union-ai',
                 'root49-easy-advanced-union-ap', 'root49-easy-pit-empty-be']:
        path = V / name
        frozen_source = json.loads((path / 'report.json').read_text())['source_hashes']
        assert all(sha(path / 'source' / n) == h for n, h in frozen_source.items())
    bl = json.loads((V / 'root49-easy-pit-empty-be/ordinary-scrooge-review-bl/report.json').read_text())
    assert bl['status'] == 'PASS_SCROOGE_AP_BE_ORDINARY_NEGATIVE_ISOLATION'
    assert len(bl['rows']) == 4 and all(x['passed'] for x in bl['rows'] + bl['comparisons'])
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / n for n in pins]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='ACTIVE_SCROOGE_ISOLATION_PROVED_RYU_E_FREEZING_BILL_LONG_LIFETIME_UNFINISHED',
                  previous_goal_turn_classification='progress', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  script_sha256=sha(__file__), published_U_source_and_artifacts_exact=True,
                  published_source_files=len(published['source_hashes']), private_Y_AB_AI_AP_BE_source_unchanged=True,
                  root_progress=dict(
                      BJ='Old S2 Scrooge streams fail on BE at6767M3/13987M5; originals retained.',
                      BK='Same actual controls on AP produce identical endpoints and19 movement/controller fields; classifier marker false because emu.log is absent from captured console.',
                      BL='Four explicit650-frame cold identity receipts are trace-exact against complete native negatives. Scrooge12/Easy0/shadowsOff1 observed412. All seven other native CSVs exact; scroll values/order/physicalframe exact,2780/7740subscanline timings differ. No fullclear/media claim.',
                      BM='Independent original-source review rejects speed-only384 lifetime premise: platform transport is outside vxMax. No demonstrated age384 gameplay failure claimed.'),
                  Bill_H='Both-mode primary/art/pool/confirmed-hit/birth and fractional/cached-expiry components are private.4096 exact source orbit rows proposed from finite stage extent; measured C000 padding can hold data. Old384 theorem rejected and retained. Native extent, placement, interrupt-safe bank restore, final native/source guards/profile and freeze remain required.',
                  Ryu='Simplified E497B removes side-bypass/receipt/reset entirely, no new RAM/SAMUS/OBJECT change.168candidate+452inherited cases pass. Actual9760 source response preservesX/qVX; later9787fall retained. OldAP42 baseline has15setup failures/map, not92 clean source disagreements. E freeze pending.',
                  Mario_Hard='Controller-only K route now clears first4stages, enters2-1at10554; Bowser/flame/alignment branches independently cold verified. Later2-1fall retained; continuation discovery ongoing.',
                  ordinary_routes='MarioAP Easy bothmaps remains full. LuigiAB/PitY/RyuO/S2Scrooge proofs remain tied to their frozen ROMs. Current AP/BE transfers are not final combined source clears. All13 modes/maps/alternates/upgrades/final media remain incomplete.',
                  allocation=dict(bank25_tail_total=3431, RYU_COLD_reserved=512, Ryu_E_current_bytes=497,
                                  root_Pit_GUEST_bytes=18, Bill_retained_phase_cap_bytes=4_500_000_000,
                                  Ryu_retained_phase_cap_bytes=1_500_000_000, Mario_route_phase_cap_bytes=3_000_000_000),
                  references=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                  live_root_handles=[], active_specialists=['BillH exact long-lifetime closure', 'RyuE freeze', 'MarioHard2-1 ordinary controls'],
                  workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True,
                  files_deleted=False, accepted_release=False, goal_complete=False,
                  next='Finish/freeze H and E, integrate both with frozen BI on actual shared layout, rebind and run required native checks. Continue stable all13 ordinary routes, every alternate/upgrade, measured lag work and final lossless recordings. No narrowed success definition.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
