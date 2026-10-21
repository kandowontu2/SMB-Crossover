"""Capture independent character observations; preserve mismatches as findings.

This audit runner does not assert that port behavior matches the references.
Its explicit fixtures supplement, rather than replace, controller clear proofs.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/roster-audit'
NAMES = ['Mario', 'Mega Man', 'Samus', 'Bill', 'Link', 'Simon', 'Pit',
         'Rygar', 'Luigi', 'Bass', 'Ryu', 'Sophia']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(mapper, character):
    directory = OUT / mapper / f'character-{character}'
    directory.mkdir(parents=True, exist_ok=True)
    script = directory / f'capture-{character}.lua'
    script.write_text(f'AUDIT_CHARACTER={character}\nAUDIT_OUTPUT=[=[{directory.as_posix()}/]=]\n'
                      f'dofile([=[{(ROOT / "tests/menu-bootstrap.lua").as_posix()}]=])\n'
                      f'dofile([=[{(ROOT / "tests/roster-reference-observation.lua").as_posix()}]=])\n')
    rom = ROOT / f'build/smb-crossover-{mapper}.nes'
    result = subprocess.run([sys.executable, 'tools/run_mesen.py', str(script), str(rom),
                             '--timeout', '90'], cwd=ROOT, capture_output=True, text=True)
    (directory / 'run.log').write_text(result.stdout + result.stderr)
    rows = list(csv.DictReader((directory / 'motion.csv').open())) if (directory / 'motion.csv').exists() else []
    complete = result.returncode == 0 and 'PASS reference observations' in result.stdout and len(rows) == 2100
    return {'character': character, 'name': NAMES[character], 'mapper': mapper,
            'capture_complete': complete, 'exit_code': result.returncode, 'rows': len(rows),
            'motion_sha256': sha(directory / 'motion.csv') if rows else None,
            'weapons_sha256': sha(directory / 'weapons.csv') if rows else None}


def sprite_budget():
    results = {}
    for path in (ROOT / 'src').glob('*_metasprites.inc'):
        poses, aliases, current = {}, {}, None
        for line in path.read_text().splitlines():
            label = re.match(r'^(\w+):\s*$', line)
            alias = re.match(r'^(\w+)\s*=\s*(\w+)\s*$', line)
            part = re.search(r'MetaspriteVramOffset\{.*?\},.*?,\s*\$[a-fA-F0-9]+,\s*(-?\d+),\s*(-?\d+)\s*$', line)
            if label:
                current = label[1]; poses[current] = []
            elif alias:
                aliases[alias[1]] = alias[2]; current = None
            elif part and current:
                poses[current].append(int(part[1]))
        def resolve(name, seen=None):
            seen = set() if seen is None else seen
            if name in seen:
                raise RuntimeError('Metasprite alias cycle: ' + name)
            seen.add(name)
            return resolve(aliases[name], seen) if name in aliases else poses.get(name, [])
        all_poses, empty_poses = {}, []
        for name in poses.keys() | aliases.keys():
            ys = resolve(name)
            if not name.endswith(('Left', 'Right')):
                continue
            if not ys:
                empty_poses.append(name)
                continue
            peak = max(sum(y <= scan < y + 16 for y in ys) for scan in range(min(ys), max(ys) + 16))
            all_poses[name] = {'sprites': len(ys), 'scanline_peak': peak}
        results[path.stem.removesuffix('_metasprites')] = {
            'file_sha256': sha(path), 'poses': len(all_poses),
            'max_scanline': max((p['scanline_peak'] for p in all_poses.values()), default=0),
            'overloaded_poses': {k: v for k, v in all_poses.items() if v['scanline_peak'] > 8},
            'empty_poses': sorted(empty_poses),
            'all_poses': all_poses,
            'limits': 'Static 8x16 metasprite rows, including packed transparent padding. Runtime may select a subset or composite multiple poses.'}
    return results


def source_index():
    paths = []
    for base in ('reference/crossover/decompiled/scripts/com/smbc',
                 'reference/crossover2/extracted/scripts/com/smbc'):
        base = ROOT / base
        paths.extend((base / 'characters').rglob('*.as'))
        paths.extend((base / 'projectiles').glob('*.as'))
        paths.extend(base / 'data' / name for name in ('DamageValue.as', 'HealthValue.as', 'AnimationTimers.as'))
        paths.append(base / 'main/AnimatedObject.as')
    paths.extend(ROOT / '.upstream/smbc-v3/src/com/smbc' / name for name in
                 ('characters/Pit.as', 'characters/Character.as', 'main/AnimatedObject.as',
                  'projectiles/PitProjectile.as', 'data/DamageValue.as', 'data/HealthValue.as'))
    result = []
    for path in sorted(set(paths)):
        text = path.read_text()
        result.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                       'lines': len(text.splitlines()),
                       'methods': [{'name': m[1], 'line': text[:m.start()].count('\n') + 1}
                                   for m in re.finditer(r'\bfunction\s+(\w+)\(', text)]})
    return result


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observe', action='store_true')
    parser.add_argument('--mapper', choices=('mmc3', 'mmc5', 'both'), default='both')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--output',type=Path,default=OUT)
    args = parser.parse_args()
    OUT=args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'sources.json').write_text(json.dumps(source_index(), indent=2) + '\n')
    (OUT / 'sprite-budgets.json').write_text(json.dumps(sprite_budget(), indent=2) + '\n')
    if args.observe:
        mappers = ('mmc3', 'mmc5') if args.mapper == 'both' else (args.mapper,)
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            work = [pool.submit(capture, mapper, character) for mapper in mappers for character in range(12)]
            for future in concurrent.futures.as_completed(work):
                item = future.result(); results.append(item)
                print(f'{item["mapper"]} {item["name"]}: capture={item["capture_complete"]}, rows={item["rows"]}', flush=True)
        manifest = {'roms': {m: sha(ROOT / f'build/smb-crossover-{m}.nes') for m in mappers},
                    'fixture_sha256': sha(ROOT / 'tests/roster-reference-observation.lua'),
                    'memory_writes': True, 'controller_clear': False, 'parity_claim': False,
                    'results': sorted(results, key=lambda r: (r['mapper'], r['character']))}
        (OUT / 'runtime-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if not all(r['capture_complete'] for r in results):
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
