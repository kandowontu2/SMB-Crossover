"""Rerun the unchanged authored-firebar diagnostic on an explicit current ROM.

Public settings/player/scroll seeds are the original diagnostic's writes.
Actors, OAM, CHR, CPU and hardware registers are never injected. An additional
read-only direct PPU capture supplements the retained legacy decoder image.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
OBSERVER = '''local legacyScreenshot=emu.takeScreenshot
emu.takeScreenshot=function()
 local state=emu.getState();local size=emu.getScreenSize()
 assert(size.width==256 and size.height==240)
 local buffer=emu.getScreenBuffer();assert(#buffer==256*240)
 local chunks={}
 for i=1,#buffer,8 do
  chunks[#chunks+1]=string.pack('<I4I4I4I4I4I4I4I4',buffer[i],buffer[i+1],buffer[i+2],buffer[i+3],buffer[i+4],buffer[i+5],buffer[i+6],buffer[i+7])
 end
 local f=assert(io.open(OUTPUT..'direct.argb','wb'));f:write(table.concat(chunks));f:close()
 local meta=assert(io.open(OUTPUT..'direct.json','w'))
 meta:write(string.format('{'..'"ppuFrame":%d,"cpuCycle":%d,"width":256,"height":240}',state['ppu.frameCount'],state['cpu.cycleCount']));meta:close()
 return legacyScreenshot()
end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    old = json.loads((ROOT / 'build/verification/firebar-nt-audit/manifest.json').read_text())
    fixture = ARCHIVE / '2026-10-24-firebar-nt-audit/native-firebar.lua'
    assert sha(fixture) == 'eb3e163db61484161fec0f5ed3f07c9ef4548477584074f8bafd157f9fa79925'
    frozen = out / 'native-firebar.lua'
    frozen.write_bytes(fixture.read_bytes())
    art = ROOT / 'chr/mmc5/sprites_mario.chr'
    assert sha(art) == old['frozen_source_hashes']['chr/mmc5/sprites_mario.chr']
    frozen_art = out / 'sprites_mario.chr'
    frozen_art.write_bytes(art.read_bytes())
    report = dict(passed=False, goal_complete=False, ROM_sha256=sha(a.rom),
        fixture_sha256=sha(frozen), source_art_sha256=sha(frozen_art),
        driver_sha256=sha(Path(__file__)), prior_audit_manifest_sha256=sha(ROOT / 'build/verification/firebar-nt-audit/manifest.json'),
        cases=[], scope='Four seeded native parser/render diagnostics,1-4/6-4 by character Easy/Hard.64hardware frames per case, original owner/CHR/DMA/scanline assertions unchanged. Additional timestamped direct console pixels supplement the asynchronous legacy screenshot. This is not a controller-only castle clear or universal firebar/campaign proof.')
    for world in (0, 5):
        for mode in (0, 1):
            folder = out / ('world' + str(world + 1) + '-behavior' + str(mode))
            folder.mkdir()
            script = folder / 'run.lua'
            script.write_text(OBSERVER + '\nFIREBAR_CONFIG={world=' + str(world) + ',behavior=' + str(mode)
                + ',source=' + json.dumps(frozen_art.as_posix()) + '}\n'
                + 'dofile(' + json.dumps(frozen.as_posix()) + ')\n')
            command = [sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder),
                str(script), str(a.rom.resolve()), '--timeout', '120', '--option=--nes.ramPowerOnState=AllZeros',
                '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
            with (folder / 'host.log').open('w') as log:
                code = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
            case = dict(world=world + 1, behavior=mode, exit=code, passed=False, folder=str(folder))
            if code == 0:
                result = json.loads((folder / 'result.json').read_text())
                assert result['passed'] and result['hardware_frames'] == 64 and result['owner_checks'] == 256
                raw = folder / 'direct.argb'
                assert raw.stat().st_size == 256 * 240 * 4
                pixels = np.frombuffer(raw.read_bytes(), dtype='<u4').reshape(240, 256)
                rgb = np.stack(((pixels >> 16) & 255, (pixels >> 8) & 255, pixels & 255), axis=2).astype(np.uint8)
                image = folder / 'direct.png'
                Image.fromarray(rgb).save(image)
                with Image.open(image) as decoded:
                    assert np.array_equal(np.asarray(decoded.convert('RGB')), rgb)
                case.update(passed=True, result=result, result_sha256=sha(folder / 'result.json'),
                    direct=json.loads((folder / 'direct.json').read_text()), raw_sha256=sha(raw),
                    RGB_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(), PNG_sha256=sha(image),
                    direct_RGB_roundtrip_exact=True)
            report['cases'].append(case)
            (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(case), flush=True)
    report['passed'] = all(c['passed'] for c in report['cases'])
    (out / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
