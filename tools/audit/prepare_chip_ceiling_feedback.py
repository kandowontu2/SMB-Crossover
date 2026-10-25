"""Build a one-byte Chip/Dale ceiling-feedback candidate on both mappers."""
from pathlib import Path
import argparse
import configparser
import hashlib
import json
import shutil
import subprocess
import sys

from check_tmnt_render_oa import load, address

ROOT = Path(__file__).resolve().parents[2]
OLD = b"Vertical:\n lda Player_State\n beq Export\n lda Player_Y_Speed\n bne NotStopped"
NEW = b"Vertical:\n lda Player_State\n beq Export\n lda Player_Y_Speed\n bmi NotStopped"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feedback_source(path):
    raw = path.read_bytes()
    newline = b'\r\n' if b'\r\n' in raw else b'\n'
    before, after = (s.replace(b'\n', newline) for s in (OLD, NEW))
    assert raw.count(before) == 1, path
    return raw.replace(before, after)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['mmc3-parent', 'mmc5-parent', 'output']:
        p.add_argument('--' + n, type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT), 'Generated builds belong outside the workspace'
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for mapper in ['mmc5', 'mmc3']:
        parent = getattr(args, mapper + '_parent').resolve()
        folder = out / mapper
        source = folder / 'source'
        if mapper == 'mmc5':
            (source / 'src').mkdir(parents=True)
            original = ROOT / 'src/chip_dale_motion.s'
            shutil.copy2(ROOT / 'smb1base-mmc5-expanded.cfg', source)
        else:
            shutil.copytree(parent.parent / 'source', source,
                            ignore=shutil.ignore_patterns('*.o', '__pycache__'))
            original = parent.parent / 'source/src/chip_dale_motion.s'
        changed = source / 'src/chip_dale_motion.s'
        changed.write_bytes(feedback_source(original))
        rom = folder / 'candidate.nes'
        if mapper == 'mmc5':
            command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                       '--source-overlay', str(source), '--output', str(rom)]
            cwd = ROOT
        else:
            config = configparser.ConfigParser()
            config.optionxform = str
            config.read(source / 'build_options.ini')
            options = {k: v for section in config.values() for k, v in section.items()}
            options.update(MAPPER_MMC3='1', MAPPER_MMC5='0', ENABLE_CROSSOVER='1',
                           ENABLE_MMC3_OVERSIZED='1', ENABLE_MMC5_EXPANDED='0')
            command = [str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502x',
                       '-t', 'nes', '-g', '-Oisr', '-vm', '-T', '-C',
                       str(source / 'smb1base-mmc3-oversized.cfg'), '--ld-args',
                       '--dbgfile,' + str(rom.with_suffix('.dbg')), '--include-dir',
                       str(source), '--asm-include-dir', str(source / 'src'),
                       '--asm-include-dir', str(source), '--bin-include-dir', str(source),
                       '-m', str(rom.with_suffix('.map')), '-Ln', str(rom.with_suffix('.lbl')),
                       '-o', str(rom)]
            for k, v in options.items():
                command += ['--asm-define', k + '=' + v, '-D', k + '=' + v]
            command += [str(source / 'src/main.c'), str(source / 'src/entrypoint.s')]
            cwd = source
        with (folder / 'host-build.log').open('w') as log:
            result = subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        assert result.returncode == 0, (folder / 'host-build.log').read_text()[-3000:]
        before, after = load(parent), load(rom)
        assert len(before['raw']) == len(after['raw'])
        changed_bytes = [(i, a, b) for i, (a, b) in
                         enumerate(zip(before['raw'], after['raw'])) if a != b]
        assert len(changed_bytes) == 1, changed_bytes[:20]
        offset, a, b = changed_bytes[0]
        assert (a, b) == (0xd0, 0x30), changed_bytes
        assert all(address(before, n) == address(after, n) for n in before['syms'])
        rows.append(dict(mapper=mapper, ROM_sha256=sha(rom), parent_ROM_sha256=sha(parent),
                         source_sha256=sha(changed), ROM_offset=offset,
                         old_opcode=a, new_opcode=b, all_existing_symbol_addresses_exact=True))
    report = dict(compiled=True, adopted=False, goal_complete=False, candidates=rows,
                  scope='Private one-byte branch change per mapper: native nonnegative ceiling/stop feedback ends the rising Rescue Rangers integrator; ordinary negative ascent and already falling native velocity retain their existing path. No shared wall, map, jump kernel, RAM, CHR, OAM or music changes. CPU/native/visual admission pending.')
    (out / 'build-proof.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
