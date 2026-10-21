"""Independently freeze four full current-C Mario/Luigi ordinary replays."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-current-c-transfers-a'
FIELDS = 'frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()
SHA = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    out = D / 'full-route-review-a.json'
    assert not out.exists()
    checkpoint = R / 'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert SHA(checkpoint) == '7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305'
    cp = json.loads(checkpoint.read_text())
    for n, h in cp['source_hashes'].items():
        assert SHA(R / n) == h, n
    catalog = json.loads((V / 'root49-combined-working-c/source-catalog.json').read_text())
    for n, h in catalog.items():
        assert SHA(V / 'root49-combined-working-c/source' / n) == h
    proofs = []
    for character, expected_frames, expected_entry in [(0, 16991, 16967), (8, 17412, 17388)]:
        for mapper in ('mmc3', 'mmc5'):
            p = R / f'build/roster-through-2-2/root49-current-c-{"mario" if character == 0 else "luigi"}-fixed-a-{character}-v0-{mapper}'
            parent = R / 'build/roster-through-2-2' / (f'root49-combined-mario-a-0-v0-{mapper}' if character == 0 else
                       f'specialist-bq-luigi-easy-fixed-{"c" if mapper == "mmc3" else "d"}-8-v0-{mapper}')
            m = json.loads((p / 'manifest.json').read_text())
            result = json.loads((p / 'result.json').read_text())
            assert m['controller_only'] and not m['memory_or_register_writes'] and m['full_frame_audit']
            assert m['verified_through_2_2'] and not m['config']['record'] and m['config']['character'] == character
            assert m['config']['mapper'] == mapper and m['config']['variant'] == 0
            assert result == m['result'] and result['cleared'] and result['all_six_stages']
            assert not result['deaths'] and result['failure'] is None
            assert result['frames'] == expected_frames and result['stage_entries']['1-2'] == expected_entry
            rom = p / f'smb-crossover-{mapper}.nes'
            assert SHA(rom) == m['rom_sha256'] == SHA(V / f'root49-combined-working-c/source/build/{rom.name}')
            assert SHA(p / 'inputs.csv') == SHA(parent / 'inputs.csv') == m['inputs_sha256'] == m['replay_sha256']
            assert SHA(p / 'harness.lua') == m['harness_sha256']
            assert SHA(p / 'audit.lua') == m['audit_sha256']
            assert SHA(p / 'policy.lua') == m['policy_sha256']
            before, after = rows(parent / 'trace.csv'), rows(p / 'trace.csv')
            assert len(before) == len(after) == expected_frames
            assert all(all(a[k] == b[k] for k in FIELDS) for a, b in zip(before, after))
            endpoint = [z for z in after if z['world'] == '1' and z['level'] == '2' and z['mode'] == '1' and z['task'] == '3']
            assert len(endpoint) >= 25 and int(endpoint[-1]['x']) > int(endpoint[-25]['x'])
            identity = None
            if character == 8:
                identity = json.loads((p / 'current-c-identity.json').read_text())
                assert identity == dict(character=8, behavior=0, marioVariant=1, billVariant=0, outlinesOff=1)
            else:
                guard = V / 'specialist-mario-easy-hard-source-a/routes-k/mario-easy-guard.lua'
                assert "r('CrossoverBehaviorVersion')==0" in guard.read_text()
                assert "r('SelectedCharacter')==0" in guard.read_text()
                assert 'ORDINARY MARIO title verified: mode=0 selected=0' in (V / f'smb-crossover-{mapper}-run-root49-current-c-mario-fixed-a-0-v0-{mapper}.log').read_text()
            stomp = json.loads((p / 'stomp-summary.json').read_text())
            assert stomp['failure'] is None and stomp['illegal_guest_events'] == stomp['resident_opcode_mismatches'] == 0
            assert stomp['behavior_version'] == 0
            profile = {}
            for z in rows(p / 'render.csv'):
                key = f"{int(z['world']) + 1}-{int(z['level']) + 1}"
                t = profile.setdefault(key, dict(audited_frames=0, lag_NMI_frames=0, max_sprites_per_scanline=0))
                t['audited_frames'] += 1
                t['lag_NMI_frames'] += int(z['lagNmi']) != 0
                t['max_sprites_per_scanline'] = max(t['max_sprites_per_scanline'], int(z['maxSprites']))
                assert int(z['behaviorVersion']) == 0
            if character == 0:
                assert (p / 'ordinary-fresh-grounded-a.csv').read_bytes() == (parent / 'ordinary-fresh-grounded-a.csv').read_bytes()
            proofs.append(dict(character=character, mapper=mapper, output=p.relative_to(R).as_posix(), result=result,
                               identity=identity, input_sha256=m['inputs_sha256'], ROM_sha256=m['rom_sha256'],
                               parent=parent.relative_to(R).as_posix(), compared_fields=FIELDS,
                               exact_compared_rows=len(after), endpoint_trace_rows=len(endpoint),
                               endpoint_control_X=[int(endpoint[-25]['x']), int(endpoint[-1]['x'])],
                               hardware_observations=profile, stomp=stomp,
                               files={q.name: dict(bytes=q.stat().st_size, sha256=SHA(q)) for q in p.iterdir() if q.is_file()}))
    report = dict(status='PASS_CURRENT_C_MARIO_LUIGI_4_FULL_FIXED_REPLAYS', script_sha256=SHA(__file__),
                  checkpoint_sha256=SHA(checkpoint), source_files_rehashed=len(catalog), proofs=proofs,
                  qualifications=['All six stages, zero-death ordinary controller replays on each mapper; no state or memory grants.',
                                  'All19 movement/controller fields exact to the pinned historical proofs, not whole-RAM or waveform identity.',
                                  'Actual2-3 entry and endpoint screenshots inspected. Full physical audit captured; no exhaustive perceptual frame-by-frame claim.',
                                  'No final recordings or exhaustive character weapon/upgrade coverage are claimed. Historical corner takeoffs remain classified.'],
                  main_changed=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], proofs=len(proofs), sha256=SHA(out))))


if __name__ == '__main__':
    main()
