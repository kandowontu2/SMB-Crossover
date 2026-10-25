"""Run ordinary-controller Zelda II terrain routes and affected-profile controls."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rom','archive','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--controls',action='store_true')
    p.add_argument('--identities',nargs='+',help='Run only named profiles in the selected group')
    p.add_argument('--stair-policy',action='store_true',help='Controller-only top-step landing before the last small gap')
    p.add_argument('--workers',type=int,choices=[1,2],default=2,help='Respect the shared native emulator worker budget')
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False);d=a.archive.resolve();b=load(a.rom)
    driver=d/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    source=json.loads((d/'native-probes-qa-v2/full-roster-aggregate-v1/proof.json').read_text())
    original=(d/'mmc3-static-call-v37/full-roster-v1/native-guard.lua').read_text()
    names=['OperMode','OperMode_Task','GameEngineSubroutine','WorldNumber','LevelNumber',
           'Player_X_Position','Player_PageLoc','Player_Y_Position','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
    delta=int(b['syms']['GameLoop']['size'],0)-1;at=location(b,'GameLoop')+delta
    assert b['raw'][at]==0x60
    hook=dict(address=address(b,'GameLoop')+delta,physical_bank=(at-16)//8192,bytes=list(b['raw'][at:at+8]))
    guard=out/'native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM='+lua({n:address(b,n)for n in names})
                     +'\nMOTION_HOOK='+lua(hook)+'\n'+original[original.index('local checks,maxWorld,maxCamera='):])
    profiles=[('link','easy'),('samus','easy'),('sophia','hard'),('mac','easy')]if a.controls else[('zelda2','easy'),('zelda2','hard')]
    if a.identities:profiles=[r for r in profiles if r[0]in a.identities]
    assert profiles
    def run(profile):
        name,mode=profile;row=next(r for r in source['runs']if r['identity']==name)
        origin=Path(row['discovery']).parent/'policy.lua';text=origin.read_text()
        if text.startswith('dofile('):text=text.split('\n',1)[1]
        if a.stair_policy and name=='zelda2':
            text='local base=(function()\n'+text+'''\nend)()
local phase,held='approach',0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2512 then return b end
 if phase=='approach'and c.grounded then phase='hop';held=0 end
 if phase=='hop'then
  held=held+1
  b={right=c.x<2406,left=c.x>2420,a=held<=10}
  if held>10 and c.grounded and c.y<=112 then phase='runup';held=0 end
  return b
 elseif phase=='runup'then
  if c.grounded and c.x>=2424 and c.vx>0 and c.vx<128 then phase='cross';held=1;return{right=true,a=true}end
  return{right=true}
 elseif phase=='cross'then
  held=held+1;return{right=true,a=held<=40}
 end
 return b
end
'''
        policy=out/(name+'-'+mode+'-policy.lua')
        policy.write_text('dofile('+lua(guard.as_posix())+')\n'+text)
        folder=out/(name+'-'+mode)
        with(out/(name+'-'+mode+'-host.log')).open('w')as log:
            result=subprocess.run([sys.executable,str(driver),name,'--rom',str(a.rom.resolve()),
                                   '--output',str(folder),'--mapper','mmc5','--behavior',mode,
                                   '--frames','18000','--capture','12','--policy',str(policy),
                                   '--chr-commit','--timeout','240'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        q=json.loads((folder/'manifest.json').read_text())if(folder/'manifest.json').exists()else{}
        motion=json.loads((folder/'completed-loop-motion.json').read_text())if(folder/'completed-loop-motion.json').exists()else{}
        native=q.get('result')or{}
        entry=dict(identity=name,mode=mode,folder=str(folder),exit=result.returncode,result=native,
                   motion=motion,source_policy_sha256=hashlib.sha256(origin.read_bytes()).hexdigest(),
                   passed=bool(result.returncode==0 and native.get('cleared')and native.get('deaths')==0
                               and motion.get('passed')and q.get('chr_commit',{}).get('passed')))
        print(json.dumps(entry),flush=True);return entry
    with ThreadPoolExecutor(max_workers=a.workers)as pool:runs=list(pool.map(run,profiles))
    proof=dict(passed=all(r['passed']for r in runs),complete=True,goal_complete=False,
               ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),runs=runs,
               scope='Fresh controller-only1-1 routes with existing policies. No geometry, inventory or physics writes. Native body-CHR and completed-loop world<=8/camera0..4 guards. Failed original policies are retained; successful discovery still requires an independent physical PPU replay. Not every powerup, moving-platform or source enemy-hitbox qualification.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2))
    raise SystemExit(0 if proof['passed']else 1)


if __name__=='__main__':main()
