"""Summarize the read-only extension measuring GameLoop's pre-core work."""
from pathlib import Path
import csv, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'build/profiling/plain-walking-v36-cache-admission-d'
DETAIL = ROOT / 'build/profiling/plain-walking-v36-outer-diagnostic-c'


def rows(path):
    return list(csv.DictReader(path.open(newline='')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


out = {
    'status': 'read-only-profile-no-runtime-change',
    'checkpoint': 'roster-audit-v36-provisional-d',
    'scope': 'Samus, unchanged20 authored crowd scenes per mapper,60 completed updates each',
    'limits': [
        'Explicit RAM-seeded benchmark, not controller traversal.',
        'First diagnostic failed to resolve the base Lua path; diagnostic-b used an invalid $A000-bank gate for fixed CODE on MMC3. Neither supplies complete outer measurements.',
        'Diagnostic-c watches the fixed $8000 GameLoop entry regardless of CurrentBank, which tracks $A000.',
        'Routine totals contain nested work and must not be added to their parent totals.',
        'Elapsed GameLoop work includes observed interrupts but excludes any following idle wait; this is not a new frame-pacing policy.',
    ],
    'mappers': {},
}
for mapper in ('mmc3', 'mmc5'):
    d, b = DETAIL/f'{mapper}-c2', BASE/f'{mapper}-c2'
    canonical, reference = next(d.glob('*-canonical.csv')), next(b.glob('*-canonical.csv'))
    assert canonical.read_bytes() == reference.read_bytes(), 'Detail observer changed gameplay receipts'
    outer = rows(next(d.glob('*-outer.csv')))
    assert len(outer) == 1200
    lookup = {(r['scene'], r['update']): r for r in outer}
    assert len(lookup) == 1200
    updates = rows(next(d.glob('*-updates.csv')))
    routine = rows(next(d.glob('*-routines.csv')))
    report = {'canonical_equal_to_main': True, 'canonical_sha256': sha(canonical), 'scenes': []}
    for scene in rows(next(d.glob('*-scenes.csv'))):
        sr = [r for r in updates if r['scene'] == scene['scene']]
        assert len(sr) == 60
        pre = [int(lookup[(r['scene'], r['update'])]['preCoreForegroundCycles']) for r in sr]
        fg = [int(r['foregroundCycles']) + p for r, p in zip(sr, pre)]
        elapsed = [int(r['cycles']) + p for r, p in zip(sr, pre)]
        report['scenes'].append({
            'scene': int(scene['scene']), 'mode': scene['mode'], 'outlinesOff': int(scene['outlinesOff']),
            'enemies': int(scene['enemies']), 'updates': 60,
            'pre_core_mean': sum(pre)/60, 'pre_core_min': min(pre), 'pre_core_max': max(pre),
            'full_foreground_mean': sum(fg)/60, 'full_foreground_max': max(fg),
            'elapsed_mean': sum(elapsed)/60, 'elapsed_max': max(elapsed),
            'elapsed_updates_over_29781': sum(v > 29781 for v in elapsed),
            'draw_calls': int(scene['drawCalls']), 'physical_frames': int(scene['physicalFrames']),
            'pre_core_routines': {r['routine']: {'calls': int(r['calls']),
                'mean_foreground_cycles': int(r['totalForegroundCycles'])/int(r['calls'])}
                for r in routine if r['scene'] == scene['scene'] and r['routine'] in ('InventoryUiTick', 'UpdateTopScore')},
        })
    out['mappers'][mapper] = report
target = ROOT/'build/profiling/samus-outer-followup-v36/report.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, indent=2)+'\n')
for mapper, report in out['mappers'].items():
    print(mapper, next(s for s in report['scenes'] if s['scene'] == 19))
