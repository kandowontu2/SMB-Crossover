"""Run a bounded Mesen 2 Lua test with symbols from the built ROM."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(script: Path, rom: Path, emulator: str | None = None, timeout: int = 30,
        emulator_options: list[str] | None = None) -> int:
    executable = emulator or os.environ.get('MESEN') or shutil.which('Mesen')
    if not executable and Path('C:/mesen2/Mesen.exe').exists():
        executable = 'C:/mesen2/Mesen.exe'
    if not executable:
        raise RuntimeError('Set MESEN to your Mesen 2 executable, or use --emulator.')
    output = ROOT / 'build/verification'
    output.mkdir(parents=True, exist_ok=True)
    symbols = {}
    labels = rom.with_suffix('.lbl')
    if labels.exists():
        for line in labels.read_text().splitlines():
            match = re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)', line)
            if match:
                symbols[match[2]] = int(match[1], 16)
    # VICE labels omit assembler constants. Expose metasprite IDs from the
    # debug file so visual regression checks follow the assembled definitions.
    debug = rom.with_suffix('.dbg')
    debug_archive = rom.with_suffix('.dbg.gz')
    if debug.exists() or debug_archive.exists():
        debug_text = (debug.read_text() if debug.exists() else
                      gzip.decompress(debug_archive.read_bytes()).decode('utf-8'))
        for line in debug_text.splitlines():
            if line.startswith('sym\t'):
                interrupt = re.search(r'name="(IrqScrollSplit|NonMaskableInterrupt|OAMandReadJoypad)"', line)
                size = re.search(r'(?:^|,)size=(\d+)(?:,|$)', line)
                address = re.search(r'(?:^|,)val=(0x[0-9A-Fa-f]+)(?:,|$)', line)
                if interrupt and size and address:
                    suffix = '_RTS' if interrupt[1] == 'OAMandReadJoypad' else '_RTI'
                    symbols[interrupt[1]+suffix] = int(address[1],16)+int(size[1])-1
            if not line.startswith('sym\t') or 'type=equ' not in line:
                continue
            name = re.search(r'name="((?:(?:METASPRITE_|XG_POSE_|SS_ART_|SAMUS_CHR_)[A-Z][A-Z_0-9]*)|ROSTER_POSE_COUNT)"', line)
            value = re.search(r'(?:^|,)val=(0x[0-9A-Fa-f]+)(?:,|$)', line)
            if name and value:
                symbols.setdefault(name[1], int(value[1], 16))
    wrapper = [
        'local originalAssert=assert',
        'local rawStop=emu.stop; local failed=false; local stopping=false',
        'function emu.stop(code) stopping=true; rawStop(failed and 1 or code) end',
        'local function fail(m) failed=true; local f=io.open(TEST_FAILURE_PATH,"a"); if f then f:write(tostring(m).."\\n"); f:close() end; print("FAIL "..tostring(m)); emu.stop(1) end',
        'function assert(v,m,...) if not v then fail(m); return originalAssert(v,m,...) end; return v,m,... end',
        # Mesen can continue after an error in a registered Lua callback.
        # Latch those errors as well so a later PASS cannot hide one.
        'local function guarded(fn) return function(...) if stopping then return end; local ok,a,b,c=pcall(fn,...); if not ok then fail(a); return end; return a,b,c end end',
        'local addEvent=emu.addEventCallback; function emu.addEventCallback(fn,...) return addEvent(guarded(fn),...) end',
        'local addMemory=emu.addMemoryCallback; function emu.addMemoryCallback(fn,...) return addMemory(guarded(fn),...) end',
        f'OUTPUT=[=[{output.as_posix()}/]=]',
        f'ROM_NAME=[=[{rom.stem}]=]',
        f'TEST_DIR=[=[{script.resolve().parent.as_posix()}/]=]',
        'L={}',
    ]
    wrapper.extend(f'L["{key}"]={value}' for key, value in sorted(symbols.items()))
    # Source gameplay fixtures use explicit2.02 setup. These front-end tests
    # must observe the real power-on1.0 default and ordinary Options inputs.
    frontend_tests = {'character-select', 'player-outlines', 'player-outlines-render'}
    if script.resolve().parent == ROOT/'tests' and script.stem not in frontend_tests:
        wrapper.append(f'dofile([=[{(ROOT/"tests/menu-bootstrap.lua").as_posix()}]=])')
    wrapper.append(f'local loaded,loadError=pcall(dofile,[=[{script.resolve().as_posix()}]=]); assert(loaded,loadError)')
    with tempfile.TemporaryDirectory(prefix='smb-crossover-mesen-') as directory:
        path = Path(directory) / 'test.lua'
        failure_path = Path(directory) / 'failures.txt'
        wrapper.insert(0, f'TEST_FAILURE_PATH=[=[{failure_path.as_posix()}]=]')
        path.write_text('\n'.join(wrapper), encoding='utf-8')
        result = subprocess.run(
            [executable, '--testRunner', '--enableStdout', f'--timeout={timeout}',
             *(emulator_options or []),
             str(path), str(rom.resolve())],
            capture_output=True, text=True, timeout=timeout + 15,
        )
        if failure_path.exists():
            result.stderr += '\nFAIL latched Lua assertions:\n' + failure_path.read_text()
            result.returncode = result.returncode or 1
    log = output / f'{rom.stem}-{script.stem}.log'
    differential = {
        'bill-collision-equivalence': ('bill-collision-reference.json', 'Bill'),
        'bill-av-collision-equivalence': ('bill-av-collision-reference.json', 'Bill Laser/Flare'),
        'sophia-collision-equivalence': ('sophia-collision-reference.json', 'Sophia'),
        'sophia-missile-collision-equivalence': ('sophia-missile-collision-reference.json', 'Sophia missile'),
        'samus-bomb-block-equivalence': ('samus-bomb-block-reference.json', 'Samus bomb terrain'),
        'water-corner-differential': ('water-corner-reference.json', 'Water Shield exact corners'),
    }
    if script.resolve().parent == ROOT/'tests' and script.stem in differential and not result.returncode:
        reference_file, description = differential[script.stem]
        reference = json.loads((ROOT/'tests'/reference_file).read_text())
        data = (output/f'{rom.stem}-{script.stem}.csv').read_bytes()
        reference_name = 'canonical generic corner control' if script.stem == 'water-corner-differential' else 'pre-optimization reference'
        revision = reference.get('source_revision')
        if revision:
            columns = revision['unchanged_columns']
            rows = list(csv.DictReader(io.StringIO(data.decode('utf-8'))))
            effect_revision = revision.get('enemy_effect_revision')
            if effect_revision:
                control_data = (ROOT/'tests'/effect_revision['control_csv']).read_bytes()
                if hashlib.sha256(control_data).hexdigest() != effect_revision['control_sha256']:
                    raise RuntimeError('Pinned pre-effect collision control was modified')
                controls = list(csv.DictReader(io.StringIO(control_data.decode('utf-8'))))
                changed = set(effect_revision['changed_cases'])
                mismatch = len(rows) != len(controls)
                for row, control in zip(rows, controls):
                    defeated = (control['enemyFlag'] == '1' and
                                int(control['enemyState']) & 32 and control['enemyHP'] != '40')
                    if defeated != (int(control['case']) in changed):
                        raise RuntimeError('Pinned Sophia defeated-row condition/list disagree')
                    for column, value in control.items():
                        expected = '0' if column == 'enemyFlag' and defeated else value
                        if row.get(column) != expected:
                            result.stderr += (f'\nFAIL {description} case {control["case"]} '
                                              f'{column}: expected {expected}, got {row.get(column)}.\n')
                            mismatch = True
                            break
                    # Normalize only the independently allowed removal for the
                    # historical all-physics projection, retaining its old hash.
                    if defeated:
                        row['enemyFlag'] = control['enemyFlag']
                if mismatch:
                    result.returncode = 1
                else:
                    result.stdout += (f'\nPASS {description} every pre-effect row remains exact; '
                                      f'only {len(changed)} confirmed defeated flags become0.\n')
            projection = (','.join(columns)+'\n'+''.join(','.join(row[c] for c in columns)+'\n' for row in rows)).encode('utf-8')
            if hashlib.sha256(projection).hexdigest() != revision['unchanged_output_sha256']:
                result.stderr += f'\nFAIL {description} terrain/reward/player/enemy results differ from the original pre-optimization reference.\n'
                result.returncode = 1
            else:
                result.stdout += f'\nPASS {description} all original terrain/reward/player/enemy results remain exact after the documented source correction.\n'
            reference_name = 'documented source-revision reference'
        if len(data.splitlines())-1 != reference['cases'] or hashlib.sha256(data).hexdigest() != reference['output_sha256']:
            result.stderr += f'\nFAIL {description} collision/shot-pool outcomes differ from the {reference_name}.\n'
            result.returncode = 1
        else:
            result.stdout += f"\nPASS all {reference['cases']} {description} outcomes match the {reference_name}.\n"
    if script.resolve().parent == ROOT/'tests' and script.stem in {f'expanded-decoder-{c}' for c in (6,7,9,10,11)} and not result.returncode:
        c = script.stem.rsplit('-', 1)[1]
        reference = json.loads((ROOT/'tests/expanded-decoder-reference.json').read_text())
        data = (output/f'{rom.stem}-decoder-{c}.bin').read_bytes()
        if len(data) != reference['updates'] * reference['bytes_per_update'] or hashlib.sha256(data).hexdigest() != reference['characters'][c]:
            result.stderr += f'\nFAIL expanded music register images differ from the original decoder for character {c}.\n'
            result.returncode = 1
        else:
            result.stdout += f'\nPASS expanded music register images match the original decoder for character {c}.\n'
    if script.resolve().parent == ROOT/'tests' and script.stem == 'guest-audio-flush-differential' and not result.returncode:
        reference = json.loads((ROOT/'tests/guest-audio-flush-reference.json').read_text())
        mapper = 'mmc5' if 'mmc5' in rom.stem else 'mmc3'
        data = (output/f'{rom.stem}-guest-audio-flush.bin').read_bytes()
        if hashlib.sha256(data).hexdigest() != reference['output_sha256'][mapper]:
            result.stderr += '\nFAIL ordered hardware APU writes differ from the pre-optimization flush.\n'
            result.returncode = 1
        else:
            result.stdout += '\nPASS ordered hardware APU writes exactly match the pre-optimization flush for all 11 guest drivers.\n'
    if script.resolve().parent == ROOT/'tests' and script.stem in ('mario-native-physics-control', 'luigi-native-physics') and not result.returncode:
        try:
            from luigi_native_review import review
            character = 8 if script.stem == 'luigi-native-physics' else 0
            report = review(output/f'{rom.stem}-native-brother-{character}.csv', character)
            (output/f'{rom.stem}-{script.stem}-review.json').write_text(json.dumps(report, indent=2)+'\n')
            result.stdout += f'\nPASS independent native-Mario reference comparison, character {character}, all39 mechanics trials.\n'
        except Exception as exc:
            result.stderr += f'\nFAIL independent native-Mario comparison: {exc}\n'
            result.returncode = 1
    if script.resolve().parent == ROOT/'tests' and script.stem in ('mario-native-death-control', 'luigi-normal-death') and not result.returncode:
        try:
            from luigi_native_review import review_death
            character = 8 if script.stem == 'luigi-normal-death' else 0
            report = review_death(output/f'{rom.stem}-native-death-{character}.csv', character)
            (output/f'{rom.stem}-{script.stem}-review.json').write_text(json.dumps(report, indent=2)+'\n')
            result.stdout += f'\nPASS native death matches all{report["identical_death_rows"]} independent Mario control rows, character {character}.\n'
        except Exception as exc:
            result.stderr += f'\nFAIL independent native death comparison: {exc}\n'
            result.returncode = 1
    if script.resolve().parent == ROOT/'tests' and script.stem in ('mario-native-water-pit-control', 'luigi-native-water-pit') and not result.returncode:
        try:
            from luigi_native_review import review_water_pit
            character = 8 if script.stem == 'luigi-native-water-pit' else 0
            report = review_water_pit(output/f'{rom.stem}-native-water-pit-{character}.csv', character)
            (output/f'{rom.stem}-{script.stem}-review.json').write_text(json.dumps(report, indent=2)+'\n')
            result.stdout += f'\nPASS native water pit matches all{report["identical_fall_and_life_rows"]} independent Mario fall/life rows, character {character}.\n'
        except Exception as exc:
            result.stderr += f'\nFAIL independent native water pit comparison: {exc}\n'
            result.returncode = 1
    if script.resolve().parent == ROOT/'tests' and script.stem == 'enemy-bbox-caller' and not result.returncode:
        reference = json.loads((ROOT/'tests/fixtures/enemy-bbox-caller-reference.json').read_text())
        mapper = 'mmc5' if 'mmc5' in rom.stem else 'mmc3'
        receipt = (output/f'{rom.stem}-bbox-caller.csv').read_bytes()
        control = reference[mapper]
        if (hashlib.sha256(script.read_bytes()).hexdigest() != reference['source_sha256']
                or len(receipt.splitlines())-1 != control['cases']
                or hashlib.sha256(receipt).hexdigest() != control['output_sha256']):
            result.stderr += '\nFAIL actual bbox caller registers/flags/scratch/box results differ from immutable native control.\n'
            result.returncode = 1
        else:
            result.stdout += f"\nPASS all {control['cases']} actual bbox caller results exactly match immutable native control.\n"
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    for line in (result.stdout + result.stderr).splitlines():
        if result.returncode or line.startswith(('PASS', 'FAIL', 'Error', 'Lua')):
            print(line)
    print(f'Full emulator log: {log}')
    print(f'Mesen exit: {result.returncode}')
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script', type=Path)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--emulator')
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()
    return run(args.script, args.rom, args.emulator, args.timeout)


if __name__ == '__main__':
    raise SystemExit(main())
