"""Index existing complete audited routes so later retargets reuse real tapes."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
P = R / 'build/roster-through-2-2'
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-full-route-inventory-fb.json'
    assert not out.exists()
    valid, excluded, errors = [], Counter(), []
    for path in P.glob('*/manifest.json'):
        try:
            m = json.loads(path.read_text())
            result, cfg = m.get('result') or {}, m.get('config') or {}
            if not (m.get('verified_through_2_2') and m.get('full_frame_audit') and
                    result.get('cleared') and result.get('deaths') == 0):
                excluded['not_complete_audited_zero_death'] += 1
                continue
            entries = result.get('stage_entries', {})
            if not all(k in entries for k in ('0-0', '0-1', '0-2', '0-3', '1-0', '1-1', '1-2')):
                excluded['missing_stage_entry'] += 1
                continue
            character, mapper = cfg.get('character'), cfg.get('mapper')
            if character not in range(13) or mapper not in ('mmc3', 'mmc5'):
                excluded['not_roster_config'] += 1
                continue
            folder = path.parent
            tape = folder / 'inputs.csv'
            rom = folder / f'smb-crossover-{mapper}.nes'
            assert sha(tape) == m['inputs_sha256'] and sha(rom) == m['rom_sha256']
            behavior = None
            render = folder / 'render.csv'
            if render.exists():
                with render.open(newline='') as stream:
                    first = next(csv.DictReader(stream), {})
                if 'behaviorVersion' in first:
                    behavior = int(first['behaviorVersion'])
            valid.append(dict(output=folder.relative_to(R).as_posix(),
                character=character, variant=cfg.get('variant'), mapper=mapper,
                first_rendered_behavior=behavior,
                behavior_scope='First audited frame only; this inventory does not independently assert mode invariance.',
                frames=result['frames'], polls=result['polls'], stage_entries=entries,
                next_stage_frames_including_entry=result['frames'] - entries['1-2'] + 1,
                ROM_sha256=m['rom_sha256'], input_sha256=m['inputs_sha256'],
                manifest_sha256=sha(path), trace_sha256=sha(folder / 'trace.csv'),
                recorded=bool(cfg.get('record')), recording_verified=bool(m.get('recording_verified')),
                mtime_ns=path.stat().st_mtime_ns))
        except (KeyError, OSError, ValueError, AssertionError) as exc:
            errors.append(dict(path=path.relative_to(R).as_posix(), error=repr(exc)))
    valid.sort(key=lambda r: r['mtime_ns'], reverse=True)
    groups = {}
    for row in valid:
        key = f"{row['character']}/v{row['variant']}/{row['mapper']}/observed-mode{row['first_rendered_behavior']}"
        groups.setdefault(key, []).append(row)
    report = dict(status='READ_ONLY_INDEX_OF_EXISTING_COMPLETE_AUDITED_ROUTES',
        script_sha256=sha(__file__), candidate_count=len(valid), grouped_candidates=groups,
        excluded_counts=dict(excluded), errors=errors,
        qualifications=['Every entry remains bound to its original ROM/tape; no current-runtime transfer inferred.',
            'First rendered behavior is an inventory hint, not a fresh whole-run mode proof.',
            'Zero-death full route and recording flags do not establish every attack, upgrade, art, source or audible requirement.',
            'Existing negative/partial/discovery-only packets are retained and excluded, not replaced.'],
        runtime_changed=False, new_native_tests=False, main_changed=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), len(valid), 'groups', len(groups), 'errors', len(errors))
    for key, candidates in sorted(groups.items()):
        print(key, len(candidates), candidates[0]['output'], candidates[0]['ROM_sha256'][:12])


if __name__ == '__main__':
    main()
