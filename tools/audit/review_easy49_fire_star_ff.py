"""Independently pin ordinary EC combat/Star evidence and retain its scope limits."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'specialist-ordinary-fire-combat-ec-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-fire-star-review-ff.json'
    assert not out.exists()
    handoff = H / 'handoff-combat-star-g.json'
    freeze = H / 'handoff-combat-star-g-freeze.json'
    assert sha(handoff) == 'bbe17991a4f287ff4a0fc00d326e4251d4598df940197f8e033cccfc8e609922'
    assert sha(freeze) == '9b23dcd26fff03a05080821a03a7e576a875533045faf8311cac6ad7be29d46f'
    h = json.loads(handoff.read_text())
    refs = {}
    def walk(item):
        if isinstance(item, dict):
            if 'path' in item and 'sha256' in item:
                p = (R / item['path']).resolve()
                assert p.is_relative_to(R) and sha(p) == item['sha256'], p
                if 'bytes' in item:
                    assert p.stat().st_size == item['bytes'], p
                refs[p.relative_to(R).as_posix()] = item['sha256']
            for value in item.values():
                walk(value)
        elif isinstance(item, list):
            for value in item:
                walk(value)
    walk(h)
    walk(json.loads(freeze.read_text()))
    assert len(h['combat_proofs']) == h['combat_case_count'] == 8
    assert h['actual_fireball_defeat_receipts'] == 38
    assert h['all8_have_both_firing_directions_ground_and_air']
    assert h['all8_have_airborne_origin_fireball_enemy_defeat']
    seen = set()
    for p in h['combat_proofs']:
        seen.add((p['character'], p['mode'], p['mapper']))
        assert p['all_window_power_states_fire_tier2']
        contexts = p['emission_context_counts']
        for direction in (1, 2):
            assert contexts.get(f'direction{direction}_state0', 0) > 0
            assert sum(contexts.get(f'direction{direction}_state{s}', 0) for s in (1, 2)) > 0
        assert p['contacts_and_defeats']
    assert seen == {(c, m, k) for c in (0, 8) for m in (0, 1) for k in ('mmc3', 'mmc5')}
    assert len(h['Star_cold_fixed_proofs']) == 2
    for p in h['Star_cold_fixed_proofs']:
        assert p['frames'] == 4300 and p['polls'] == 4299 and p['deaths'] == 0
        assert p['all19_fields_and_Star_timer_frames_exact_vs_original_E']
        assert p['pickup_frame'] == 3009 and p['item_type'] == 2
        timer = p['timer_trace']
        assert len(timer) == 36 and timer[0] == dict(frame=3009, value=35)
        assert timer[-1] == dict(frame=3744, value=0)
        assert all(b['frame'] - a['frame'] == 21 and b['value'] == a['value'] - 1 for a, b in zip(timer, timer[1:]))
        assert p['active_to_zero_updates'] == 735 and p['no_projectiles_at_protected_contacts']
        contacts = p['body_contact_protection_and_Goomba_defeats']
        assert [r['frame'] for r in contacts] == [3256, 3303]
        assert all(r['active_fireballs'] == 0 and r['injury_starts'] == 0 and r['player_engine'] == 8 for r in contacts)
    report = dict(status='PASS_FROZEN_SCOPED_EC_COMBAT_AND_BOTH_MAPPER_STAR_RECEIPTS',
        script_sha256=sha(__file__), handoff_sha256=sha(handoff), freeze_sha256=sha(freeze),
        verified_reference_files=len(refs), references=refs,
        combat_cases=8, actual_fireball_defeat_receipts=38,
        startup_controller_tests=True, all_MMC3_combat_cases_independently_fixed_replayed=False,
        Star_cold_fixed_mappers=2, Star_native_updates=735,
        native_Star_timer_is_qualified_approximation_of_AS_12000ms=True,
        limits=h['limits'], no_new_runtime_defect_claim=True, runtime_changed=False,
        final_integrated_rebind_and_media_pending=True, main_changed=False,
        accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), len(refs))


if __name__ == '__main__':
    main()
