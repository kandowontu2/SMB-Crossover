"""Repair SMB3 shrink CHR phase using its authenticated final animation frame."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/render-dispatch-ov'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    parent = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'candidate.nes') == parent['rom_sha256']
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    stage = out / 'source'
    with zipfile.ZipFile(PARENT / 'source.zip') as z:
        assert z.testzip() is None
        assert all((stage / n).resolve().is_relative_to(stage.resolve()) for n in z.namelist())
        z.extractall(stage)
    assert all(sha(stage / n) == h for n, h in parent['source_files'].items())
    target = stage / 'src/smb3_mario_render.s'
    before = sha(target)
    text = target.read_text()
    old = ' lda M3Growth\n lsr\n lsr\n and #1\n sta M3Scratch\n lda SmChrBank\n'
    new = (' ; Native shrink reverses the growth index before choosing CHR phase.\n'
           ' ; Frame39 is every odd final index; frames11/14 are even. Bit5\n'
           ' ; therefore supplies the native phase for either direction. The\n'
           ' ; existing consumer tests this private scratch only for zero.\n'
           ' lda M3RenderFrame\n lsr\n lsr\n and #8\n sta M3Scratch\n lda SmChrBank\n')
    assert text.count(old) == 1
    target.write_text(text.replace(old, new))
    result = subprocess.run([sys.executable, str(stage / 'tools/build_mmc5_expanded.py'), '--workspace', str(stage),
                             '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                             '--output', str(out / 'candidate.nes')], cwd=stage, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    old_bytes, new_bytes = (PARENT / 'candidate.nes').read_bytes(), (out / 'candidate.nes').read_bytes()
    differences = [i for i, (x, y) in enumerate(zip(old_bytes, new_bytes)) if x != y]
    assert len(old_bytes) == len(new_bytes) and len(differences) == 2
    assert all((i - 16) // 8192 == 90 for i in differences)
    assert old_bytes[:16] == new_bytes[:16] and old_bytes[16 + 1048576:] == new_bytes[16 + 1048576:]
    q = dict(prepared=True, accepted=False, ROM_sha256=sha(out / 'candidate.nes'), parent_ROM_sha256=parent['rom_sha256'],
             source_changes={'src/smb3_mario_render.s': dict(before=before, after=sha(target))},
             changed_ROM_bytes=[dict(offset=i, old=old_bytes[i], new=new_bytes[i]) for i in differences],
             scope='Two operand bytes change in the existing M3Graphics growth branch. Instruction count/addresses and CHR are unchanged; the zero/nonzero private scratch now follows the final growth frame, including reversed shrink. Requires actual original growth/OAM/CHR comparison and native damage replay before adoption.')
    (out / 'preparation.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
