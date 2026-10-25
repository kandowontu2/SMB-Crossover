"""Bind the existing measured-cycle observer to two native collision arenas."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    observer=ROOT/'tools/audit/tmnt_performance_observer.lua';text=observer.read_text()
    anchor="r('SelectedCharacter')==19";assert text.count(anchor)==1;text=text.replace(anchor,"r('SelectedCharacter')==cfg.character")
    begin=text.index(' local names=');end=text.index('\n for _,name in ipairs(names)',begin)
    names=['GameLoop','PlayerMovementSubs','ExpandedCollisionAdder','ExpandedCollisionBox','HotCollisionAdder','HotCollisionBox',
        'RlAdderDispatch','RlBoxDispatch','ExpandedMovement','ExpandedGraphics','ExpandedWeapons','CdMovement','CdGraphics','CdWeapons',
        'DrawAllMetasprites','MetaspriteRenderLoop','X5SetPhysicalChr','X5SetSpecialChr','InventoryLegacyClassic','InventorySupported']
    text=text[:begin]+' local names={'+','.join(json.dumps(n)for n in names)+'}'+text[end:]
    anchor="  for i=0,2 do if r('TnShotKind',i)~=0 then b=b+1 end end";assert text.count(anchor)==1
    text=text.replace(anchor,"  for i=0,3 do if r('MmBulletType',i)~=0 then b=b+1 end end\n  for i=0,9 do if r('RgShotType',i)~=0 then b=b+1 end end")
    text=text.replace('L.TnMovement','L.GameLoop').replace('B.TnMovement','B.GameLoop').replace('tmnt-performance','collision-performance')
    bound=out/'observer.lua';bound.write_text(text)
    fixture=ROOT/'tools/audit/collision_performance_arena_oj.lua'
    def run(case):
        name,char,slot,mode=case;d=out/name;d.mkdir()
        frozen=d/'fixture.lua';frozen.write_bytes(fixture.read_bytes())
        script=d/'run.lua';script.write_text('COLLISION_PERF_CFG={character='+str(char)+',slot='+str(slot)+',mode='+json.dumps(mode)+',observer='+json.dumps(bound.as_posix())+'}\ndofile('+json.dumps(frozen.as_posix())+')\n')
        z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(d),str(script),str(a.rom.resolve()),
            '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,capture_output=True,text=True)
        (d/'host.log').write_text(z.stdout+z.stderr)
        return dict(identity=name,exit=z.returncode,result=json.loads((d/'result.json').read_text())if(d/'result.json').exists()else None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:runs=list(pool.map(run,[('sophia',11,11,'hard'),('chip',14,13,'easy')]))
    q=dict(passed=all(r['exit']==0 and r['result']and r['result']['passed']for r in runs),ROM_sha256=sha(a.rom),
        observer_source_sha256=sha(observer),bound_observer_sha256=sha(bound),fixture_sha256=sha(fixture),runs=runs,
        scope='Two cold-menu native600-update components:120updates of idle/walk/live actors/ordinaryB/jump. State/actor placements and a fixed per-update joypad snapshot are explicitly arranged at GameLoop entry; the real controller holds the same command through each complete update. Native input decoding, terrain, movement, collision, drawing and interrupts execute. Common projectile counts exclude private carried-object pools. This is matched CPU work, not physical input-latency evidence, a natural level clear, every-item or maximum-weapon claim.')
    (out/'results.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
