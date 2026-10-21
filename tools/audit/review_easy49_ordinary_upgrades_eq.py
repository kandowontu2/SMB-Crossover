"""Independently inventory the bounded natural EC Mario/Luigi handoff."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-ordinary-upgrade-review-eq.json'
    assert not out.exists()
    folder = V / 'specialist-ordinary-upgrades-ec-a'
    handoff = folder / 'handoff-both-h.json'
    freeze = folder / 'handoff-both-h-freeze.json'
    assert sha(handoff) == '9530e4b65453ef0b588e9b8acbb8f37624216aeb7a9e67ced870245de152bdaf'
    assert sha(freeze) == '57e5a300c747299dae66bf231532e92a239991ea792b675d34edfaaa071cbd38'
    h = json.loads(handoff.read_text())
    refs = {}

    def walk(item):
        if isinstance(item, dict):
            if 'path' in item and 'sha256' in item:
                p = (R / item['path']).resolve()
                assert p.is_relative_to(R), p
                assert sha(p) == item['sha256'], p
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
    assert len(h['proofs']) == 8
    observed = set()
    for p in h['proofs']:
        observed.add((p['character'], p['mode'], p['mapper']))
        assert p['frames'] == 2250 and p['polls'] == 2249 and p['deaths'] == 0
        assert p['maximum_observed_active_fireballs'] == 2
        assert p['lower_tier_snapshots_all_projectile_slots_empty']
        assert [r['kind'] for r in p['pickups']] == [0, 1]
        assert all(r['freeze_frames'] == 60 for r in p['pickups'])
        trace = list(csv.DictReader((R / p['canonical_trace']['path']).open(newline='')))
        assert len(trace) == 2250
        live_fire = [r for r in trace if int(r['engine']) == 8 and int(r['power']) == 2]
        assert live_fire and any(int(r['buttons']) & 64 for r in live_fire)
        tape = list(csv.DictReader((R / p['input_tape']['path']).open(newline='')))
        assert len(tape) == 2249 and sha(R / p['input_tape']['path']) == p['tape_sha256']
    assert observed == {(c, m, k) for c in (0, 8) for m in (0, 1) for k in ('mmc3', 'mmc5')}

    ec_path = R / 'build/checkpoints/roster-audit-v49-victory-ec/manifest.json'
    el_path = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(el_path) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    ec, el = (json.loads(p.read_text()) for p in (ec_path, el_path))
    assert set(ec['source_hashes']) == set(el['source_hashes'])
    changes = [n for n, value in el['source_hashes'].items() if ec['source_hashes'][n] != value]
    assert changes == ['src/guest_victory_control.s'], changes
    assert all(sha(R / n) == value for n, value in el['source_hashes'].items())
    for row in el['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in row['artifacts'].values())
    report = dict(status='PASS_FROZEN_BOUNDED_EC_NATURAL_UPGRADE_RECEIPTS',
        script_sha256=sha(__file__), handoff_sha256=sha(handoff), freeze_sha256=sha(freeze),
        checked_reference_files=len(refs), references=refs, cold_replays=8,
        frames_per_replay=2250, polls_per_replay=2249, deaths=0,
        natural_kind0_kind1_pickups=16, contact_to_live_freeze_frames=60,
        actual_hardware_audio_and_render_receipts_pinned=True,
        actual_main_EL_sources_and_artifacts_unchanged=True, source_changes_EC_to_EL=changes,
        qualifications=h['qualification'],
        interpretation='Eight bounded EC natural collection/fire receipts, not eight stage clears or final EL runtime/media admission.',
        runtime_changed=False, emulated_state_changes=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), len(refs))


if __name__ == '__main__':
    main()
