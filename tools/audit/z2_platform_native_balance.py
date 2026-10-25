"""Qualify the exact private Zelda II platform candidate in native Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw
from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua
from z2_platform_late_check import Machine

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--emulator', required=True)
    p.add_argument('--slot', type=int, default=-1)
    p.add_argument('--observe', action='store_true')
    p.add_argument('--focus', default='')
    p.add_argument('--trap-alignment', action='store_true')
    p.add_argument('--trap-render', action='store_true')
    p.add_argument('--prepare-only', action='store_true')
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    b = load(a.rom)
    names = ['PauseSkip', 'RunLargePlatform', 'RunSmallPlatform', 'Z2PlatformBodyPrepare',
             'Z2PlatformBodyFinish', 'Z2PositionOnPlatform', 'NonMaskableInterrupt']
    names += ['CrossoverLiftSecondY', 'Z2NativeSmallPlatformCollision', 'L94F8', 'CrossoverDrawSmallPlatform', 'MetaspriteRenderLoop', 'RlNativeRenderDispatch']
    hooks = {}
    for n in names:
        at = location(b, n)
        hooks[n] = dict(address=address(b, n), physical_bank=(at-16)//8192,
                        bytes=list(b['raw'][at:at+3]))
    n = 'NonMaskableInterrupt'
    delta = int(b['syms'][n]['size'], 0)-1
    at = location(b, n)+delta
    hooks['NmiReturn'] = dict(address=address(b, n)+delta, physical_bank=(at-16)//8192,
                              bytes=list(b['raw'][at:at+1]))
    cases = []
    for fairy in [0, 8]:
        for stand in [3, 0]:
            cases.append(dict(name=f'{"fairy" if fairy else "normal"}-balance-{"parent" if stand==3 else "child"}',
                              fairy=fairy,slot=3,child=0,stand=stand,kind='balance',ident=0x24,second=0,
                              px=160,x=164 if stand==3 else 84,seed_y=112 if stand==3 else 144))
    if a.focus:
        cases = [q for q in cases if a.focus in q['name']]
    assert cases
    fixture = ROOT/'tools/audit/z2_platform_native_balance.lua'
    used_names = set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'", fixture.read_text()))
    native_at = location(b, 'Z2NativeSmallPlatformCollision')
    native_size = int(b['syms']['Z2NativeSmallPlatformCollision']['size'], 0)
    helper = address(b, 'CrossoverLiftSecondY')
    needle = bytes([0x20, helper&255, helper>>8])
    calls = [address(b, 'Z2NativeSmallPlatformCollision')+i for i in range(native_size-2)
             if b['raw'][native_at+i:native_at+i+3] == needle]
    cfg = dict(hooks=hooks, cases=cases, observe=int(a.observe), trap_alignment=int(a.trap_alignment),
               trap_render=int(a.trap_render),
               foreign_jsr=calls,
               ram={n: address(b, n) for n in used_names if n in b['syms']},
               smc_fields=[address(b, n)+1 for n in ['NextBank_SMC', 'SafecallA_SMC',
                            'SafereturnA_SMC', 'FarcallJmpTarget_SMC']]+
                          [address(b, 'FarcallJmpTarget_SMC')+2])
    # Execute the actual two native initializations, not an invented pair.
    m = Machine(b)
    for n,v in dict(BalPlatformAlignment=255,SecondaryHardMode=0,AreaType=3).items():m.put(n,v)
    for slot,rel,y in [(0,80,146),(3,160,114)]:
        x=4*256+226+rel
        for n,v in dict(Enemy_Flag=1,Enemy_ID=0x24,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,
                        Enemy_Y_Position=y,Enemy_Y_HighPos=1,ObjectOffset=slot).items():m.put(n,v,0 if n=='ObjectOffset'else slot)
        m.call('InitBalPlatform',x=slot)
    fields=['Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos',
            'Enemy_State','Enemy_BoundBoxCtrl','Enemy_MovingDir','Enemy_X_Speed','Enemy_Y_Speed',
            'Enemy_X_MoveForce','Enemy_Y_MoveForce','Enemy_YMoveForceFractional','PlatformCollisionFlag']
    cfg['pair']=[dict(name=n,slot=slot,value=m.get(n,slot))for slot in [0,3]for n in fields]
    cfg['pair_addresses']={n:address(b,n)for n in fields}
    assert m.get('Enemy_State',0)==255 and m.get('Enemy_State',3)==0
    assert m.get('Enemy_Flag',0)==m.get('Enemy_Flag',3)==1
    assert m.get('Enemy_Y_Position',0)==144 and m.get('Enemy_Y_Position',3)==112
    (out/'native-init-pair.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),
        initial_native_calls=[dict(slot=0,raw_x=1330,raw_y=146),dict(slot=3,raw_x=1410,raw_y=114)],
        calls='Actual InitBalPlatform in linked candidate; firstchild0 thenparent3; loader flags1; initial alignmentFF',
        resulting_fields=cfg['pair']),indent=2))
    cfg['body_poses'] = {}
    cfg['body_bank'] = (location(b, 'Z2ArtBegin')-16)//8192
    for pose in range(27):
        for face in ['Right', 'Left']:
            n = f'Z2Pose{pose}{face}'
            at = location(b, n)
            size = b['raw'][at]
            cfg['body_poses'][str(address(b, n))] = [
                dict(tile=b['raw'][at+i], dy=b['raw'][at+i+2], dx=b['raw'][at+i+3])
                for i in range(1, size+1, 4)]
    script = out/'run.lua'
    script.write_text('Z2_PLATFORM_NATIVE_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
    if a.prepare_only:
        print(json.dumps(dict(prepared=True,cases=len(cases),output=str(out),native_run=False)))
        return
    with (out/'host.log').open('w') as log:
        result = subprocess.run([sys.executable, str(ROOT/'tools/audit/run_mesen_isolated.py'),
                  '--output', str(out), '--emulator', a.emulator, str(script), str(a.rom.resolve()),
                  '--timeout', '110', '--option=--doNotSaveSettings',
                  '--option=--nes.ramPowerOnState=AllZeros',
                  '--option=--nes.randomizeCpuPpuAlignment=false',
                  '--option=--nes.randomizeMapperPowerOnState=false'], cwd=ROOT, stdout=log,
                  stderr=subprocess.STDOUT)
    proof = json.loads((out/'proof.json').read_text()) if (out/'proof.json').exists() else dict(passed=False)
    pixels = []
    pngs = []
    for raw in sorted(out.glob('*.argb')):
        v = np.frombuffer(raw.read_bytes(), dtype='<u4').reshape(240, 256)
        rgb = np.stack(((v>>16)&255, (v>>8)&255, v&255), axis=2).astype(np.uint8)
        Image.fromarray(rgb).save(raw.with_suffix('.png'))
        pixels.append(dict(file=raw.name, sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
        pngs.append(raw.with_suffix('.png'))
    if pngs:
        cols = 4
        sheet = Image.new('RGB', (cols*256, ((len(pngs)+cols-1)//cols)*260), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(pngs):
            with Image.open(path) as im:
                sheet.paste(im, (i%cols*256, i//cols*260+20))
            draw.text((i%cols*256+3, i//cols*260+2), path.stem, fill='white')
        sheet.save(out/'overview.png')
    proof.update(ROM_sha256=hashlib.sha256(b['raw']).hexdigest(), emulator_exit=result.returncode,
                 ROM_path=str(a.rom.resolve()), emulator_path=str(Path(a.emulator).resolve()),
                 emulator_sha256=hashlib.sha256(Path(a.emulator).read_bytes()).hexdigest(),
                 passed=result.returncode == 0 and proof.get('passed', False),
                 physical_pixel_files=pixels, fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
                 runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 generated_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                 dependencies={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in [ROOT/'tools/run_mesen.py', ROOT/'tools/audit/run_mesen_isolated.py']},
                 goal_complete=False)
    (out/'native-proof.json').write_text(json.dumps(proof, indent=2))
    print(json.dumps(dict(passed=proof['passed'], ROM_sha256=proof['ROM_sha256'],
                         emulator_exit=result.returncode, cases=len(proof.get('cases', [])),
                         physical_pixel_files=len(pixels), output=str(out))), flush=True)
    raise SystemExit(0 if proof['passed'] else 1)


if __name__ == '__main__':
    main()
