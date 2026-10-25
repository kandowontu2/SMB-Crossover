"""Build a current-source, immediate tail-coalescing HUD candidate privately."""
from pathlib import Path
import configparser
import argparse
import hashlib
import json
import re
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]
O = R / 'build/verification/hud-tail-dz'
C = O / 'source'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    global O, C
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', default='hud-tail-dz')
    parser.add_argument('--template', type=Path, default=R / 'tools/audit/hud_tail_dz.s')
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', args.tag)
    O = R / 'build/verification' / args.tag
    C = O / 'source'
    parent=json.loads((R/'build/checkpoints/water-visible-cw/manifest.json').read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in parent['ROMs'].items()), 'This archived private builder requires the unmodified CW parent; use its frozen source for later experiments'
    assert not O.exists()
    C.mkdir(parents=True)
    seed = json.loads((R / 'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names = set(seed['source_hashes']) | {p.relative_to(R).as_posix() for p in (R / 'src').rglob('*') if p.is_file()}
    before = {n: sha(R / n) for n in names}
    for name in names:
        dst = C / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(R / name, dst)
    for name in seed['generated11']:
        dst = C / 'build/generated' / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(R / 'build/generated' / name, dst)
    original = (R / 'src/bill_native_rare.s').read_text()
    start = original.index('.proc NativeRarePrintStatusBarNumbersCore\n')
    end = original.index('.endproc', start) + len('.endproc')
    core = original[start:end].replace('NativeRarePrintStatusBarNumbersCore', 'HudPrintStatusNumbersLocal', 1)
    source = args.template.read_text()
    (C / 'src/hud_tail.s').write_text(source + '\n.pushseg\n.segment "HUD_TAIL_COLD"\n' + core + '\n.popseg\n')
    path = C / 'src/entrypoint.s'
    text = path.read_text()
    anchor = '.include "water_shield_enemies.s"\n'
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, anchor + '.include "hud_tail.s"\n'))
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)$', (R / 'build/smb-crossover-mmc3.lbl').read_text(), re.M)}
    span = labels['CoinTallyOffsets'] - labels['UpdateNumber']
    assert span == 19, span
    path = C / 'src/screen_render.s'
    text = path.read_text()
    start = text.index('UpdateNumber:\n')
    end = text.index('CoinTallyOffsets:', start)
    block = text[start:end]
    replacement = ('.if ::ENABLE_CROSSOVER\nUpdateNumber:\n  jmp HudUpdateNumberLocal\n'
                   f'  .res {span}-(*-UpdateNumber), $ea\n.else\n' + block + '.endif\n\n')
    path.write_text(text[:start] + replacement + text[end:])
    path = C / 'smb1base.cfg'
    text = path.read_text()
    anchor = '    RENDER:     load = PRGA_03, type = ro;'
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, anchor + '\n    HUD_TAIL_COLD: load=PRGA_03, type=ro, optional=yes, start=$be97;'))
    report = dict(status='BUILDING_PRIVATE_IMMEDIATE_HUD_TAIL_CANDIDATE',
                  parent_ROMs={m: sha(R / f'build/smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')},
                  new_RAM_bytes=0, deferred_requests=False,
                  scope='Immediate numeric output. Coalesces only a complete final coin/score pair at a validated packet boundary. No foreign queue compaction, no GameLoop/Inventory or direct PrintStatusBarNumbers change.',
                  goal_complete=False)
    (O / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(C / 'build_options.ini')
    options = {n: v for section in cfg.values() for n, v in section.items()}
    builds = []
    for mapper, baseline in [('mmc3', False), ('mmc5', False), ('mmc3', True), ('mmc5', True)]:
        name = f'smb-crossover-{mapper}' + ('-baseline' if baseline else '')
        obj = C / 'build/objects' / name
        obj.mkdir(parents=True)
        for filename in ('main.c', 'entrypoint.s'):
            shutil.copyfile(C / 'src' / filename, obj / filename)
        opts = dict(options, MAPPER_MMC3=str(int(mapper == 'mmc3')), MAPPER_MMC5=str(int(mapper == 'mmc5')), ENABLE_CROSSOVER=str(int(not baseline)))
        command = [str(R / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502x', '-t', 'nes', '-g', '-Oisr', '-vm', '-T', '-C', 'smb1base.cfg',
                   '--ld-args', f'--dbgfile,build/{name}.dbg', '--include-dir', '.', '--asm-include-dir', '.', '--asm-include-dir', 'src', '--bin-include-dir', '.',
                   '-m', f'build/{name}.map', '-Ln', f'build/{name}.lbl', '-o', f'build/{name}.nes']
        for key, value in opts.items():
            command += ['--asm-define', f'{key}={value}', '-D', f'{key}={value}']
        command += [str(obj / 'main.c'), str(obj / 'entrypoint.s')]
        with (O / f'{name}.log').open('wb') as log:
            result = subprocess.run(command, cwd=C, stdout=log, stderr=subprocess.STDOUT)
        print(name, result.returncode, flush=True)
        assert result.returncode == 0
        if baseline:
            assert sha(C / f'build/{name}.nes') == sha(R / f'build/{name}.nes')
        builds.append(dict(name=name, ROM_sha256=sha(C / f'build/{name}.nes')))
    assert all(sha(R / n) == value for n, value in before.items())
    report.update(status='PRIVATE_HUD_TAIL_FOUR_BUILDS_PASS_NOT_ADOPTED', builds=builds,
                  source_hashes={p.relative_to(C).as_posix(): sha(p) for p in C.rglob('*') if p.is_file() and 'build' not in p.relative_to(C).parts})
    (O / 'build.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
