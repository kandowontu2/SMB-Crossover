"""Pack a legible front end from the existing genuine 19 portrait sources."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/new-roster-1-1-nd/menu-art-v2'


def main():
    assert not OUT.exists()
    spec = ROOT/'build/verification/mac-adoption-mw/menu-input.json'
    assert len(json.loads(spec.read_text())['portraits']) == 19
    subprocess.run([sys.executable, str(ROOT/'tools/reference/build_x5_menu.py'),
        '--manifest', str(spec), '--output', str(OUT), '--polished'], cwd=ROOT, check=True)
    before = OUT/'before'
    before.mkdir()
    for name in ('chr/raw/x5-character-select.bin', 'chr/characters/packed-mmc5-expanded.chr'):
        shutil.copyfile(ROOT/name, before/Path(name).name)
    # Navigation positions are deliberately unchanged; no character remapping.
    layout=(OUT/'x5-menu-layout.inc').read_text()
    assert layout[:layout.index('X5MenuCursorLo:')] == (ROOT/'src/x5_menu_layout.inc').read_text().split('X5MenuCursorLo:')[0]
    (ROOT/'src/x5_menu_layout.inc').write_text(layout)
    shutil.copyfile(OUT/'x5-menu.bin', ROOT/'chr/raw/x5-character-select.bin')
    packed = bytearray((ROOT/'chr/characters/packed-mmc5-expanded.chr').read_bytes())
    packed[4096:8192] = (OUT/'x5-menu.chr').read_bytes()
    (ROOT/'chr/characters/packed-mmc5-expanded.chr').write_bytes(packed)
    print(json.dumps(dict(portraits=19, navigation_unchanged=True,
        polished_menu_sha256=hashlib.sha256((OUT/'x5-menu.bin').read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
