"""Account for the preceding NMI as well as foreground work in crowd scenes."""
from pathlib import Path
import argparse, csv, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--detail', type=Path, default=ROOT/'build/profiling/plain-walking-v37-nmi-budget-c-b')
p.add_argument('--main', type=Path, default=ROOT/'build/profiling/plain-walking-v37-core-empty-c')
p.add_argument('--checkpoint', default='roster-audit-v37-provisional-c')
p.add_argument('--mappers', default='mmc3,mmc5')
p.add_argument('--character', type=int, default=2)
p.add_argument('--output', type=Path, default=ROOT/'build/profiling/samus-nmi-followup-v37/report.json')
args = p.parse_args()
DETAIL, MAIN = args.detail, args.main


def read(path):
    return list(csv.DictReader(path.open(newline='')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


out = {
    'status': 'read-only-initialized-crowd-profile',
    'checkpoint': args.checkpoint,
    'scope': f'Character{args.character}; same20 authored standing/walking scenes,60 completed updates per scene and mapper',
    'limits': [
        'RAM-seeded native arenas, not ordinary-input traversal or a hardware measurement.',
        'Regular NMI time precedes GameLoop and consumes the same physical frame budget.',
        'GameLoop elapsed work includes any intervening lag NMI. It cannot be added to NMI totals as an independent cost.',
        'Nested routine totals likewise must not be added to their parent AudioUpdate total.',
        'The earlier37 diagnostic-a used foreground CurrentBank, an invalid gate for direct audio switches. Missing samples are not zero-cost calls.',
        'This observer watches actual mapper PRG writes. No runtime, audio, input or cadence policy changed.',
    ],
    'mappers': {},
}
for mapper in args.mappers.split(','):
    d, b = DETAIL / f'{mapper}-c{args.character}', MAIN / f'{mapper}-c{args.character}'
    canonical, reference = next(d.glob('*-canonical.csv')), next(b.glob('*-canonical.csv'))
    assert canonical.read_bytes() == reference.read_bytes(), 'Observer altered canonical gameplay'
    deadlines = read(next(d.glob('*-deadline.csv')))
    updates = read(next(d.glob('*-updates.csv')))
    audio = read(next(d.glob('*-audio.csv')))
    assert len(deadlines) == len(updates) == 1200
    required = {'RemainingAudioBegin', 'RemainingAudioTick', 'GuestAudioBegin', 'GuestAudioFinish', 'GuestAudioNativeFlush', 'AudioUpdate'}
    required |= {'SamusAudioUpdate'} if args.character == 2 else {'MegaManAudioUpdate', 'MegaManAudioNativeUpdate'}
    assert set(a['routine'] for a in audio) >= required
    if mapper == 'mmc5':
        assert any(a['routine'] == 'GuestExpansionFlush' for a in audio)
    report = {'canonical_equal_to_main': True, 'canonical_sha256': sha(canonical), 'scenes': []}
    for scene in read(next(d.glob('*-scenes.csv'))):
        key = scene['scene']
        ds = [x for x in deadlines if x['scene'] == key]
        us = [x for x in updates if x['scene'] == key]
        assert len(ds) == len(us) == 60
        assert all(x['update'] == y['update'] for x, y in zip(ds, us))
        pre = [int(x['preCoreForegroundCycles']) for x in ds]
        elapsed = [p + int(u['cycles']) for p, u in zip(pre, us)]
        regular = [(x, e) for x, e in zip(ds, elapsed) if x['previousNmiLag'] == '0']
        end_from_nmi = [int(x['gameStartSinceNmi']) + e for x, e in regular]
        nmi = [int(x['previousNmiElapsed']) for x, _ in regular]
        routines = {}
        for name in sorted({a['routine'] for a in audio}):
            calls = [a for a in audio if a['scene'] == key and a['routine'] == name]
            if not calls:
                continue
            fg = [int(a['cycles']) - int(a['irqCycles']) for a in calls]
            routines[name] = {'calls': len(calls), 'mean_cycles_excluding_nested_irq': sum(fg) / len(fg), 'max_cycles_excluding_nested_irq': max(fg)}
        report['scenes'].append({
            'scene': int(key), 'mode': scene['mode'], 'outlinesOff': int(scene['outlinesOff']),
            'enemies': int(scene['enemies']), 'physical_frames': int(scene['physicalFrames']),
            'draws': int(scene['drawCalls']), 'updates': 60,
            'pre_core_mean': sum(pre) / 60,
            'game_loop_elapsed_max': max(elapsed),
            'game_loop_elapsed_over_29781': sum(e > 29781 for e in elapsed),
            'updates_after_regular_nmi': len(regular),
            'preceding_regular_nmi_mean': sum(nmi) / len(nmi) if nmi else None,
            'preceding_regular_nmi_max': max(nmi) if nmi else None,
            'regular_start_to_update_end_max': max(end_from_nmi) if end_from_nmi else None,
            'regular_start_to_update_end_over_29781': sum(e > 29781 for e in end_from_nmi),
            'audio_routines': routines,
        })
    out['mappers'][mapper] = report
target = args.output
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, indent=2) + '\n')
for mapper, r in out['mappers'].items():
    print(mapper, next(s for s in r['scenes'] if s['scene'] == 19))
