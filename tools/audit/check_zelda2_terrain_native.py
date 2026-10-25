"""Run native staged Zelda II head/pipe/floor/HUD geometry, retain PPU pixels."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image,ImageDraw
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rom','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--emulator',required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False);b=load(a.rom)
    def hook(n,last=False):
        delta=int(b['syms'][n]['size'],0)-1 if last else 0
        at=location(b,n)+delta
        return dict(address=address(b,n)+delta,physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+8]))
    names=['OperMode','OperMode_Task','GameEngineSubroutine','SelectedCharacter','Z2Variant',
           'CrossoverMenuState','CrossoverMenuIndex','Enemy_Flag','Player_X_Position','Player_PageLoc',
           'Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Z2NativeVY','Z2NativeGravityFraction',
           'Z2NativeAir','Player_State','Z2NativeVX','Player_X_Speed','Player_X_Scroll','Z2NativeXFraction',
           'CrouchingFlag','Z2ActiveSpells','SmCeilingHit','BlockBounceTimer','DisableCollisionDet',
           'Block_X_Position','Block_PageLoc','Block_State']
    cfg=dict(ram={n:address(b,n)for n in names},bg=hook('PlayerBGCollision'),after=hook('MegaMan202AfterBG'),
             nmi=hook('NonMaskableInterrupt'),nmi_return=hook('NonMaskableInterrupt',True),
             smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    cfg['ram']['Z2PreviousTerrainY']=address(b,'Z2BodyScratch')+11
    cfg['cases']=[
        dict(name='normal-question-ceiling',x=348,y=158,vy=252,oldY=162,wantX=348,wantY=160,blockX=352),
        dict(name='crouched-used-block-ceiling',x=348,y=158,vy=252,oldY=162,crouch=1,wantX=348,wantY=160),
        dict(name='normal-right-pipe',x=434,y=170,vy=0,wantX=432,wantY=170),
        dict(name='normal-left-pipe',x=478,y=170,vy=0,wantX=479,wantY=170),
        dict(name='normal-land-pipe',x=450,y=145,vy=3,oldY=142,wantX=450,wantY=144),
        dict(name='fairy-right-pipe',x=436,y=180,vy=0,fairy=1,wantX=434,wantY=180),
        dict(name='fairy-left-pipe',x=475,y=180,vy=0,fairy=1,wantX=477,wantY=180),
        dict(name='fairy-land-pipe',x=450,y=152,vy=3,oldY=149,fairy=1,wantX=450,wantY=150),
        dict(name='fairy-used-block-ceiling',x=348,y=150,vy=252,oldY=154,fairy=1,wantX=348,wantY=152),
        dict(name='fairy-head-above-HUD',x=348,y=23,vy=252,oldY=27,fairy=1,wantX=348,wantY=23),
        dict(name='fairy-head-at-HUD-edge',x=348,y=24,vy=252,oldY=28,fairy=1,wantX=348,wantY=24)]
    fixture=ROOT/'tests/zelda2-terrain-native.lua';script=out/'run.lua'
    script.write_text('Z2_TERRAIN_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
    with(out/'host.log').open('w')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),
                               '--output',str(out),'--emulator',a.emulator,str(script),str(a.rom.resolve()),
                               '--timeout','90','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros',
                               '--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],
                              cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    q=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False)
    rows=[]
    if result.returncode==0:
        for raw in sorted(out.glob('case-*.argb')):
            v=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256)
            rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8)
            Image.fromarray(rgb).save(raw.with_suffix('.png'))
            rows.append(dict(file=raw.name,sha256=hashlib.sha256(raw.read_bytes()).hexdigest()))
        sheet=Image.new('RGB',(4*256,3*260),(24,28,36));draw=ImageDraw.Draw(sheet)
        for i,case in enumerate(cfg['cases']):
            images=sorted(out.glob('case-'+str(i+1)+'-frame-*.png'));assert images
            with Image.open(images[len(images)//2])as im:sheet.paste(im,(i%4*256,i//4*260+20))
            draw.text((i%4*256+3,i//4*260+2),case['name'],fill='white')
        sheet.save(out/'overview.png')
    q.update(ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),emulator_exit=result.returncode,
             passed=result.returncode==0 and q.get('passed',False),physical_pixel_files=rows,
             fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),goal_complete=False)
    (out/'native-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
    raise SystemExit(0 if q['passed']else 1)


if __name__=='__main__':main()
