"""Verify native graphical Parodius HUD pixels and publication for all ships."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image
from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--art', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--emulator', required=True)
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    b = load(args.rom)
    def hook(n, last=False):
        delta = int(b['syms'][n]['size'], 0)-1 if last else 0
        at = location(b, n) + delta
        return dict(address=address(b, n)+delta, physical_bank=(at-16)//8192,
                    bytes=list(b['raw'][at:at+8]))
    names = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'SelectedCharacter',
             'VvVariant', 'CrossoverMenuState', 'CrossoverMenuIndex', 'VvMeter',
             'VvHudDirty', 'InvHudActive', 'InvHudPhysical', 'X5HudChrUpper']
    config = dict(ram={n:address(b,n) for n in names}, loop=hook('GameLoop'),
                  nmi=hook('NonMaskableInterrupt'), nmi_return=hook('NonMaskableInterrupt', True),
                  smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC',
                              'SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    art = json.loads((args.art / 'manifest.json').read_text())
    fixture = ROOT / 'tests/parodius-hud-render.lua'
    report = dict(passed=False, complete=False, goal_complete=False, ROM_sha256=sha(args.rom),
                  fixture_sha256=sha(fixture), art_manifest_sha256=sha(args.art/'manifest.json'), runs=[])
    for row in art['rows']:
        variant = row['variant']
        folder = out / str(variant)
        folder.mkdir()
        config.update(variant=variant, font=row['intended_physical_page'], cells=row['mapped_cells'])
        script = folder / 'run.lua'
        script.write_text('PN_HUD_CONFIG=' + lua(config) + '\n' + fixture.read_text())
        with (folder / 'host.log').open('w') as log:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'),
                                     '--output', str(folder), '--emulator', args.emulator,
                                     str(script), str(args.rom.resolve()), '--timeout', '60',
                                     '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
                                     '--option=--nes.randomizeCpuPpuAlignment=false',
                                     '--option=--nes.randomizeMapperPowerOnState=false'],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        proof = json.loads((folder/'proof.json').read_text()) if (folder/'proof.json').exists() else {}
        if result.returncode == 0:
            for raw in folder.glob('case-*.argb'):
                values=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256)
                rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
                Image.fromarray(rgb).save(raw.with_suffix('.png'))
        report['runs'].append(dict(variant=variant, exit=result.returncode,
                                   passed=result.returncode==0 and proof.get('passed') is True,
                                   native=proof, folder=str(folder)))
        (out/'progress.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report['runs'][-1]),flush=True)
        if result.returncode:
            break
    report.update(complete=len(report['runs'])==3, passed=len(report['runs'])==3 and all(r['passed'] for r in report['runs']))
    (out/'proof.json').write_text(json.dumps(report,indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
