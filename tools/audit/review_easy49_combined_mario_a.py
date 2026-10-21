"""Freeze the two actual full Mario integration replays of immutable source-c."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
S = V / 'agent-lsr-sophia-feet-implementation-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS = 'frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    out = V / 'root49-combined-mario-a.json'
    assert not out.exists()
    revision = S / 'revision-c.json'
    catalog = json.loads(revision.read_text())['source_sha256']
    for name, digest in catalog.items():
        assert sha(S / 'source-c' / name) == digest, name
    proofs = []
    for mapper in ('mmc3', 'mmc5'):
        current = R / f'build/roster-through-2-2/root49-combined-mario-a-0-v0-{mapper}'
        previous = R / f'build/roster-through-2-2/root49cc-mario-fixed-0-v0-{mapper}'
        manifest = json.loads((current / 'manifest.json').read_text())
        result = json.loads((current / 'result.json').read_text())
        assert manifest['controller_only'] and not manifest['memory_or_register_writes']
        assert manifest['full_frame_audit'] and not manifest['config']['record']
        assert result['cleared'] and result['all_six_stages'] and not result['deaths'] and not result['failure']
        assert result['frames'] == 16991 and result['polls'] == 16990
        assert sha(current / 'inputs.csv') == sha(previous / 'inputs.csv') == manifest['inputs_sha256']
        assert manifest['inputs_sha256'] == '3d8eeb2f97ece9a4f7ff18dac568c83627a5a310f0f9f20218e11ffa5f4c3141'
        before, after = rows(previous / 'trace.csv'), rows(current / 'trace.csv')
        assert len(before) == len(after) == 16991
        differences = [dict(frame=b['frame'], fields={k: [a[k], b[k]] for k in FIELDS if a[k] != b[k]})
                       for a, b in zip(before, after) if any(a[k] != b[k] for k in FIELDS)]
        takeoffs = current / 'ordinary-fresh-grounded-a.csv'
        assert takeoffs.read_bytes() == (previous / takeoffs.name).read_bytes()
        endpoint = [z for z in after if z['world'] == '1' and z['level'] == '2' and z['mode'] == '1' and z['task'] == '3']
        assert len(endpoint) >= 25 and int(endpoint[-1]['x']) > int(endpoint[-25]['x'])
        profile = {}
        for row in rows(current / 'render.csv'):
            key = f"{int(row['world'])+1}-{int(row['level'])+1}"
            item = profile.setdefault(key, dict(audited_frames=0, lag_NMI_frames=0, maximum_sprites_per_scanline=0))
            item['audited_frames'] += 1
            item['lag_NMI_frames'] += int(row['lagNmi']) != 0
            item['maximum_sprites_per_scanline'] = max(item['maximum_sprites_per_scanline'], int(row['maxSprites']))
        log = V / f'smb-crossover-{mapper}-run-root49-combined-mario-a-0-v0-{mapper}.log'
        proofs.append(dict(mapper=mapper, path=current.relative_to(R).as_posix(), result=result,
            rom_sha256=sha(current / f'smb-crossover-{mapper}.nes'),
            input_sha256=manifest['inputs_sha256'],
            compared_fields=FIELDS, differing_frames_vs_historical_CC=differences,
            historical_CC_movement_fields_exact=not differences,
            dry_takeoffs_exact_vs_CC=True, dry_takeoff_count=len(rows(takeoffs)),
            actual_next_stage_control_frames=25, next_stage_control_X=[int(endpoint[-25]['x']), int(endpoint[-1]['x'])],
            hardware_observations=profile,
            files={p.name: sha(p) for p in current.iterdir() if p.is_file()},
            native_log=dict(path=log.relative_to(R).as_posix(), sha256=sha(log))))
    for name, digest in catalog.items():
        assert sha(S / 'source-c' / name) == digest, name
    report = dict(status='PASS_COMBINED_SOURCE_C_MARIO_EASY_THROUGH_2_2_BOTH_MAPPERS',
        script_sha256=sha(__file__), source_revision=dict(path=revision.relative_to(R).as_posix(), sha256=sha(revision)),
        source_files_verified=455, proofs=proofs, root_live_handles=[],
        qualifications=[
            'Actual fixed-controller power-on native replays; no savestate loads or emulated grants.',
            'Full render/CHR/OAM/scroll/APU telemetry is captured. This is not full RAM equivalence or an exhaustive perceptual media review.',
            'Historical CC ordinary route has explicitly classified corner takeoffs; no glitchless claim.',
            'Screenshots of actual2-2 entry and2-3 endpoint visually inspected; no final recording or all-arsenal claim.',
            'The immutable source-c candidate is under independent landing audio review. Results do not automatically transfer to later runtime revisions.',
        ], main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out),
        differing_frames=[len(p['differing_frames_vs_historical_CC']) for p in proofs],
        dry_takeoffs=[p['dry_takeoff_count'] for p in proofs])))


if __name__ == '__main__':
    main()
