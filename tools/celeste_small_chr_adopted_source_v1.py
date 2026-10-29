"""Bind the actual normal-build dependencies after Celeste's CHR owner repair."""
from pathlib import Path
import configparser
import hashlib
import json
import re
import subprocess

R = Path(__file__).resolve().parents[1]
B = R / 'build'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    prefix = 'celeste-small-chr-adopted-source-v1'
    out = B / (prefix + '.json')
    assert not out.exists(), 'Preserve the original receipt'
    rom = B / 'roster-shared-celeste-small-chr-v1.nes'
    assert sha(rom) == 'f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
    assert sha(R / 'src/celeste_mario_render_small_host.inc') == '585c42f720ae3a3a0503dcf95b1ce6c1acf68cb618dca9d76bdce596562f1b81'
    dep = B / (prefix + '.d')
    obj = B / (prefix + '.o')
    entry = B / 'roster-shared-celeste-small-chr-v1-objects/entrypoint.s'
    assert entry.read_bytes() == (R / 'src/entrypoint.s').read_bytes()
    options = configparser.ConfigParser()
    options.optionxform = str
    options.read(R / 'build_options.ini')
    definitions = {key: value for section in options.values() for key, value in section.items()}
    definitions.update(MAPPER_MMC3='0', MAPPER_MMC5='1', ENABLE_CROSSOVER='1', ENABLE_MMC5_EXPANDED='1')
    command = [str(R / 'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502x', '-g',
               '-I', str(R / 'src'), '-I', str(R), '--bin-include-dir', str(R),
               '--create-full-dep', str(dep), '-o', str(obj)]
    for key, value in definitions.items():
        command += ['-D', key + '=' + value]
    command.append(str(entry))
    result = subprocess.run(command, cwd=R, capture_output=True, text=True)
    (B / (prefix + '.log')).write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    dependencies = {}
    words = re.split(r'(?<!\\)\s+', dep.read_text().split(':\t', 1)[1].strip().removesuffix(':'))
    for word in words:
        path = Path(word.replace('\\ ', ' '))
        path = (path if path.is_absolute() else R / path).resolve()
        assert path.is_file(), str(path)
        dependencies[str(path)] = sha(path)
    required = ['src/celeste_mario_core_small_host.inc', 'src/celeste_mario_render_small_host.inc',
                'src/celeste_mario_host_entry.s', 'src/celeste_mario_host.s', 'src/celeste_mario_host_state.inc',
                'src/river_city_core_host_v8.inc', 'src/river_city_shared_palette_host_v8.inc',
                'src/river_city_wall_prepass_v2.inc', 'src/roster_expansion_menu.inc',
                'src/mac_roster.s', 'src/character_select.s',
                'chr/characters/packed-mmc5-roster-expanded.chr', 'chr/raw/roster-expansion-menu.bin']
    for name in required:
        assert str((R / name).resolve()) in dependencies, name
    for name in ['src/celeste_mario_core.s', 'src/celeste_mario_render.s', 'src/celeste_mario_state.inc']:
        assert str((R / name).resolve()) not in dependencies, name
    bindings = dict(dependencies)
    for path in [Path(__file__), rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), dep,
                 R / 'smb1base-mmc5-expanded.cfg', R / 'build_options.ini']:
        bindings[str(path.resolve())] = sha(path)
    out.write_text(json.dumps(dict(source_CPU_only=True, native_run=False,
                                  ROM_sha256=sha(rom), actual_ASM_dependencies=len(dependencies),
                                  actual_normal_build_inputs_confirmed=True,
                                  old_Celeste_big_render_and_conflicting_state_not_consumed=True,
                                  command=command, bindings=bindings), indent=2) + '\n')
    print(json.dumps(dict(passed=True, ASM=len(dependencies), bindings=len(bindings), sha256=sha(out))))


if __name__ == '__main__':
    main()
