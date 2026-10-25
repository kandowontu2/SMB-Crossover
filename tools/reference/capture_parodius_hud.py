"""Capture original Parodius power-bar nametables/patterns using ordinary controls."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/NES/Parodius Da! (Japan).nes')
SOURCE_SHA = 'ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--emulator', required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    assert sha(SOURCE) == SOURCE_SHA
    out.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / 'tests/parodius-hud-source.lua'
    rows = []
    for variant in [1, 2, 3]:
        folder = out / str(variant)
        folder.mkdir()
        script = folder / 'source.lua'
        script.write_text('PN_SOURCE_VARIANT=' + str(variant) + '\n' + fixture.read_text())
        with (folder / 'host.log').open('w') as log:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'),
                                     '--output', str(folder), '--emulator', args.emulator,
                                     str(script), str(SOURCE), '--timeout', '40',
                                     '--option=--doNotSaveSettings',
                                     '--option=--nes.ramPowerOnState=AllZeros',
                                     '--option=--nes.randomizeCpuPpuAlignment=false',
                                     '--option=--nes.randomizeMapperPowerOnState=false'],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert result.returncode == 0, folder
        values = np.frombuffer((folder / 'screen.argb').read_bytes(), dtype='<u4').reshape(240, 256)
        rgb = np.stack(((values >> 16) & 255, (values >> 8) & 255, values & 255), axis=2).astype(np.uint8)
        Image.fromarray(rgb).save(folder / 'source.png')
        rows.append(dict(requested_variant=variant, state=(folder / 'source-state.txt').read_text(),
                         PPU_sha256=sha(folder / 'ppu.bin'), pixels_sha256=sha(folder / 'screen.argb')))
        rows[-1].update(HUD_PPU_sha256=sha(folder / 'hud-ppu.bin'),
                        HUD_capture_time=(folder / 'hud-capture-time.txt').read_text())
    report = dict(captured=True, validated=False, source_ROM_sha256=SOURCE_SHA,
                  fixture_sha256=sha(fixture), memory_or_equipment_writes=False, runs=rows,
                  scope='Original cartridge research only. Ordinary menu controls, actual mapped PPU patterns/nametables/palettes and direct screen-buffer pixels. Validate selection and bar pixels before generating integration assets.')
    (out / 'capture.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
