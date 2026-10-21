"""Retain both unsuccessful fixed-input transfers without relabeling the GQ clear."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS = 'frame poll world level area areaType x y yHigh state vx vy power engine mode task lives camera buttons'.split()


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    out = R / 'build/verification/root49-combined-samus-transfer-a.json'
    assert not out.exists()
    baseline = R / 'build/roster-through-2-2/specialist-gq-samus-fixed-bc-2-v0-mmc3'
    old = rows(baseline / 'trace.csv')
    cases = []
    for mapper in ('mmc3', 'mmc5'):
        folder = R / f'build/roster-through-2-2/root49-combined-samus-a-2-v0-{mapper}'
        actual = rows(folder / 'trace.csv')
        result = json.loads((folder / 'result.json').read_text())
        identity = json.loads((folder / 'ordinary-identity.json').read_text())
        assert identity['observed'] and identity['selected'] == 2 and identity['behavior'] == 0
        assert (baseline / 'inputs.csv').read_bytes().startswith((folder / 'inputs.csv').read_bytes())
        assert result['failure'] == 'death' and not result['cleared']
        first = next(i for i, (a, b) in enumerate(zip(old, actual)) if any(a[k] != b[k] for k in FIELDS))
        a, b = old[first], actual[first]
        cases.append(dict(mapper=mapper, result=result, identity=identity,
            ROM_sha256=sha(folder / f'smb-crossover-{mapper}.nes'),
            reference_scope='GQ MMC3 same-mapper' if mapper == 'mmc3' else 'GQ MMC3 cross-mapper input probe; no prior MMC5 clear is asserted',
            first_movement_difference=dict(frame=int(b['frame']), fields={k: [a[k], b[k]] for k in FIELDS if a[k] != b[k]},
                previous=dict(reference=old[first-1], actual=actual[first-1]), current=dict(reference=a, actual=b)),
            stop_frame=int(actual[-1]['frame']), endpoint=actual[-1],
            files={p.name: sha(p) for p in folder.iterdir() if p.is_file()}))
    report = dict(status='RETAINED_FIXED_SAMUS_INPUT_TRANSFER_NEGATIVES_BOTH_MAPPERS', script_sha256=sha(__file__),
        immutable_candidate='build/verification/root49-sophia-land-fix-a/source-e', cases=cases,
        interpretation='M3 first movement divergence coincides with a skipped-update counter increment while GQ advances. This is timing evidence, not a diagnosed source collision defect. The M5 attempt is a cross-mapper probe from the M3 input. Both stop at a first death transition; a zero completed-death counter is not a clear.',
        needed='Adapt ordinary controller timing on the final candidate and independently replay; retain the separate GQ Samus proof.',
        root_live_handles=[], controller_only=True, emulated_writes=False, recorded=False,
        main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), first_frames=[c['first_movement_difference']['frame'] for c in cases])))


if __name__ == '__main__':
    main()
