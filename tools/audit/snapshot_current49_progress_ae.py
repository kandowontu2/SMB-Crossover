"""Preserve measured Pit optimization while other source repairs remain active."""
from pathlib import Path
import datetime, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root-current49-progress-ae.json'
    assert not output.exists()
    previous = V / 'root-current49-progress-ad.json'
    assert sha(previous) == 'd9c10d814e401588f231f5e7ad203162bff56c4b2ee1ee1c0aca8c30ccf12fde'
    checkpoint = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
    assert sha(checkpoint) == '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / name) == digest for name, digest in published['source_hashes'].items())
    for build in published['builds']:
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            item = build['artifacts'][ext]
            assert sha(R / item['path']) == item['sha256']
    pins = {
        'root49-easy-pit-empty-be/freeze-bi.json': '2442526554d3ac401a542d77998c5569681eb6929bbb6c0ea992a96159833078',
        'root49-easy-pit-empty-be/report.json': 'bb45ec3ead04515ad6eb56a8164ca39590d0f2ec72e29f64f69a67f4da6e55bd',
        'root49-easy-pit-empty-be/native/checks-bf/report.json': '2f38cba3582b585f0d94d59208d89d91e1fe3d5a185e24d5302848d3564d5ff0',
        'root49-easy-pit-empty-be/ordinary-pit-profile-bg/report.json': 'cfd6556ea20c0f588b2cd4c86567eff8aea20b3fa6c0ee88686c8566ae3c1495',
        'root49-easy-pit-empty-be/native/checks-bh/report.json': '76ec3577e658fbd58ddfdd8975ea1ff549fb0f899f5c0dc6f454de7bf4cc5825',
        'root49-easy-advanced-union-ap/ordinary-pit-profile-bd/report.json': 'b07de012432e63daa207d3258e7698f2f0d2e804af2728927c1946d38f2a9ba7',
        'agent-lsr-ap-ryu-transfer-a/actual-review.json': '30af02a893599c55f5057964bfb55578c47fdb56aa74e87f56789fb151ec46f2',
    }
    for name, expected in pins.items():
        assert sha(V / name) == expected, name
    frozen = json.loads((V / 'root49-easy-pit-empty-be/freeze-bi.json').read_text())
    assert all(sha(R / item['path']) == item['sha256'] for item in frozen['files'])
    for name in ['root49-easy-whip-phase-y', 'root49-easy-bro-union-ab', 'root49-easy-ryu-union-ai',
                 'root49-easy-advanced-union-ap', 'root49-easy-pit-empty-be']:
        folder = V / name
        document = json.loads((folder / 'report.json').read_text())
        assert all(sha(folder / 'source' / path) == digest for path, digest in document['source_hashes'].items())
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    refs = [previous, checkpoint, R / 'docs/qa/easy-hard-legacy-v49.md'] + [V / name for name in pins]
    report = dict(
        status='ACTIVE_PIT_OPTIMIZATION_FROZEN_BI_H_AND_RYU_SOURCE_FIXES_UNFINISHED',
        previous_goal_turn_classification='progress',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        published_U_source_and_artifacts_exact=True, published_source_files=len(published['source_hashes']),
        private_Y_AB_AI_AP_BE_source_unchanged=True,
        root_progress=dict(
            BD='Three actual ordinary3000-frame hardware-guarded profiles identify repeated generic terrain work; Y instrumentation is trace-exact.',
            BE='18B GUEST source candidate routes selectedPit26..28 to existing distinct-cell path; old RAM/CHR/header/audio/config preserved.',
            BF='5520 paired seeded native cases/map with zero checked observable differences; bothmodes/tiers/facings/page/Yseams/reward/multicell order.',
            BG='Same3000frame inputstream: attackmean4309→3305M3/4287→3261M5, local lagflags219→185/180→107. Timing changes later world state; no whole-game percentage guarantee.',
            BH='All20 foreign-weapon/bomb groups pass including222 Samus bombs/map and6controller-created/map.',
            BI='Immutable one-file overlay and117 hashed references. Solid-contact path can cost555 extra cycles; scratch/full-RAM/independent source-parity and final-route claims excluded.'),
        ordinary_routes='Mario AP Easy bothmaps full proof remains valid. PitY and RyuO full proofs remain valid; AP fixed transfers fail and are retained. Final stable integration routes still required.',
        Bill_H='Cold bank25 relocation/art/fairness/pool stages are private. E Easy cross-bank near-return defect retained; F local return and bothmode closure controls underway. Birth-contact and sourceexpiry closure remains required, including old240-age qualification.',
        Ryu='Actual ordinary newAP descendant reproduces head/corner source response at9760 with realJumpUsed1 and unchangedX/qVX; laterfall9787 retained.501B prototype37eachmapper passed; separate510B D successor fixes stale ground/head receipt lifecycle, inherited O/native controls still underway. No completed new route claim.',
        Mario_Hard='K route clearsfirst3stages; castle controller alignment/landing discovery continues. Frozen Easy handoff untouched.',
        allocation=dict(bank25_tail_total=3431, RYU_COLD_reserved=512, old_LEGACY_COLD_free59_reserved_for_H=True,
                        root_Pit_GUEST_bytes=18, Ryu_retained_phase_cap_bytes=1_500_000_000,
                        Bill_retained_phase_cap_bytes=3_500_000_000, Mario_route_phase_cap_bytes=3_000_000_000),
        live_root_handles=[], active_specialists=['BillH completion', 'RyuD source repair and regressions', 'MarioHard ordinary controls'],
        references=[dict(path=path.relative_to(R).as_posix(), sha256=sha(path), bytes=path.stat().st_size) for path in refs],
        workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True,
        files_deleted=False, accepted_release=False, goal_complete=False,
        next='Finish/source-freeze H and Ryu, merge with frozen Pit BI on actual shared layout and repeat required native checks. Then stable all13 ordinary routes/alternates/upgrades/modes/maps, remaining lag work and final full recordings. No narrowed success definition.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(output.name, sha(output), used, flush=True)


if __name__ == '__main__':
    main()
