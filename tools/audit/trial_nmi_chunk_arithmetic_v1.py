"""Private linked eight-byte counter trial; never installs game source."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D / 'parodius-visibility-current50b5-v1/hud-candidate-v9'
PIN = '4b61ad59b980b30a57e7abcdcd18d05ec979ca8c84cda2293ab01d39ed18baef'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(PARENT / 'candidate.nes') == PIN
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(PARENT / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/nmi_vram_fast.s'
    raw = path.read_bytes()
    nl = b'\r\n' if b'\r\n' in raw else b'\n'
    text = raw.decode().replace('\r\n', '\n')
    old = '  sta PPUDATA\n  dex\n .endrepeat\n cpx #8\n'
    new = '  sta PPUDATA\n .endrepeat\n txa\n sec\n sbc #8\n tax\n cpx #8\n'
    assert text.count(old) == 1
    text = text.replace(old, new)
    old_end = '.endproc\n.proc FastNmiPaletteCapture\n'
    assert text.count(old_end) == 1
    text = text.replace(old_end, '.endproc\n .res 3,$ea ; retain following genuine entry PCs\n.proc FastNmiPaletteCapture\n')
    text = text.replace('; Retain the native packet/data order, pointer/Y wrap, registers and flags.\n',
        '; Retain full native UpdateScreen results and ordered data/pointer wrap.\n'
        '; Internal A/V are dead at the unchanged SEC/TYA/ADC continuation.\n')
    path.write_bytes(text.encode().replace(b'\n', nl))
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
               '--output', str(a.output / 'candidate.nes')]
    process = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(process.stdout + process.stderr)
    assert process.returncode == 0, (process.stdout + process.stderr)[-4000:]
    before, after = (PARENT / 'candidate.nes').read_bytes(), (a.output / 'candidate.nes').read_bytes()
    changed = [i for i, (b, c) in enumerate(zip(before, after)) if b != c]
    assert len(before) == len(after) and before[:16] == after[:16]
    assert changed and all(16 + 116*8192 <= i < 16 + 117*8192 for i in changed)
    assert all((source / f.relative_to(PARENT / 'source')).read_bytes() == f.read_bytes()
               for f in (PARENT / 'source').rglob('*') if f.is_file() and '__pycache__' not in f.parts
               and f.relative_to(PARENT / 'source').as_posix() != 'src/nmi_vram_fast.s')
    result = dict(prepared=True, CPU_passed=False, native_run=False, adoption_qualified=False,
                  production_changes=False, parent_ROM_sha256=PIN,
                  candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
                  changed_ROM_bytes=len(changed), changed_PRG_banks=[116],
                  changed_source=['src/nmi_vram_fast.s'], tool_sha256=sha(Path(__file__)),
                  limits='Private counter trial only. Internal A/V differ before dead-value '
                         'continuation; whole-command/full-public-call and IRQ checks required. '
                         'Inherits all unqualified final-extent prototype behavior.')
    (a.output / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
