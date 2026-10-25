"""Read-only broader native cost breakdown using the unchanged input arena."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
NAMES=['GameCoreRoutine','PauseRoutine','HpPauseCold','X5BounceUiDispatch','InventoryUiTick','PlayerCtrlRoutine',
       'PlayerMovementSubs','X5BounceMovementDispatch','X5NewMovementFinish','ScrollHandler','VvScrollBridge',
       'MegaManCollisionBox','LmBoundingBoxGate','PlayerBGCollision','EnemiesAndLoopsCore','GuestPostEnemyCollision',
       'PlayerGfxHandler','BlockObjMT_Updater','BlockObjectsCore','MiscObjectsCore','ProcessCannons','ProcessWhirlpools',
       'FlagpoleRoutine','RunGameTimer','HpPrepareNativePointers','TnUpdateShot','TnReadCell','TnUpdateDrops',
       'WorldFirebarDrawAdmission','DrawMetasprite','RlNativeRenderDispatch','InventorySupported','LmWeaponsGate',
       'TnPrivatePickup','SamusDrawShots','DrawBrickDebris','GetPlayerOffscreenBits','RelativePlayerPosition']
NAMES+=['MegaManCollisionAdder','ExpandedCollisionAdder','RlAdderDispatch','LmAdderGate','TnAdderDispatch',
        'BillBGHeadConsumer','BillHeadDispatch','KbNativeHeadBridge','LmHeadGate','TnHeadDispatch',
        'CrossoverSourceFootProbe','CrossoverSourceSideProbe','LmSideGate','TnSideDispatch',
        'BlockBufferColli_Head','BlockBufferColli_Side','BlockBufferColli_Feet','BlockBufferCollision',
        'CheckForCoinMTiles','GuestLandingWindow','HandlePipeEntry','GuestFootContactSide']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    base=ROOT/'tools/audit/tmnt_performance_observer.lua';text=base.read_text();anchor=" local names={'GameLoop',"
    assert text.count(anchor)==1
    text=text.replace(anchor," local names={"+','.join(json.dumps(n)for n in NAMES)+",'GameLoop',")
    observer=a.output/'observer.lua';observer.write_text(text)
    def run(c):
        name,variant,mode=c;d=a.output/name;d.mkdir();s=d/'run.lua'
        s.write_text('TMNT_CFG={variant='+str(variant)+',mode='+json.dumps(mode)+',observer='+json.dumps(observer.as_posix())+'}\ndofile('+json.dumps((ROOT/'tests/tmnt-performance.lua').as_posix())+')\n')
        z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(d),str(s),str(a.rom),
            '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True)
        (d/'host.log').write_text(z.stdout+z.stderr)
        return dict(identity=name,exit=z.returncode,result=json.loads((d/'result.json').read_text())if(d/'result.json').exists()else None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[('leonardo',0,'easy'),('donatello',3,'hard')]))
    q=dict(passed=all(q['exit']==0 and q['result']['passed']for q in results),ROM_sha256=sha(a.rom),
           base_observer_sha256=sha(base),observer_sha256=sha(observer),runs=results,read_only_observer=True)
    (a.output/'results.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
    return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
