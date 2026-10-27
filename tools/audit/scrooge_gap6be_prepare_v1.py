"""Prepare one controller-only Scrooge Easy top-stair successor; no native."""
from pathlib import Path
import argparse
import contextlib
import csv
import io
import json
import re

import current_roster_compact_11_v1 as route
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena

R=route.ROOT
SHA='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
POLICY=R/'tools/playthroughs/scrooge_gap6be_policy_v1.lua'


def source_controls(rom):
    b=scoped_load(rom)
    def setup(face=1,y=104,vy=2,state=1,pogo=1):
        q=Arena(b,12)
        q.put(DarkwingVariant=0,CrossoverBehaviorVersion=0,Player_State=state,
            ScPogo=pogo,ScPrevious=69,SavedJoypadBits=0,A_B_Buttons=0,
            Player_Y_Speed=vy,Player_Y_Position=y,Player_X_Position=108,
            Player_PageLoc=9,ScreenLeft_PageLoc=8,ScreenLeft_X_Pos=252,
            RgPreviousButtons=69,AreaType=1,Player_MovingDir=face,PlayerFacingDir=face)
        q.array('MmVY',[0,0,vy]);q.invoke('CrossoverGraphicsBank')
        # Literal source staircase tile$61 with its top at144. Typed CPU
        # support arena; never written into the controller-only native run.
        for col in range(6,9):
            for row in range(7,13):q.set('Block_Buffer_1',0x61,208+row*16+col)
        return q
    def step(q,buttons):
        q.put(SavedJoypadBits=buttons,A_B_Buttons=buttons&192)
        for proc in ['ExpandedMovement','PlayerBGCollision','SamusAfterBGCollisionBridge','ExpandedWeapons']:
            cpu,_=q.invoke(proc);assert cpu.sp==253
        return dict(x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),
            y=q.get('Player_Y_Position'),state=q.get('Player_State'),pogo=q.get('ScPogo'),
            vy=[q.get('MmVY',i)for i in range(3)])
    direct=0
    for face in [1,2]:
        for state in [0,1]:
            for pogo in [0,1]:
                for buttons in [0,68,69,197]:
                    q=setup(face,state=state,pogo=pogo);q.put(SavedJoypadBits=buttons)
                    q.invoke('ScroogeMovement')
                    if buttons&68!=68:assert q.get('ScPogo')==0
                    elif state:assert q.get('ScPogo')==1
                    elif pogo:assert [q.get('MmVY',i)for i in range(3)]==[0,37,250] and q.get('Player_State')==1
                    else:assert q.get('ScPogo')==0 and q.get('Player_State')==0
                    direct+=1
    pipelines=[]
    for face in [1,2]:
        for y in [102,104]:
            for vy in [2,3]:
                q=setup(face,y,vy);states=[step(q,0)]
                assert q.get('ScPogo')==0
                for _ in range(12):
                    states.append(step(q,68))
                    if q.get('Player_State')==0:break
                else:raise AssertionError('Typed top-stair did not land')
                assert q.get('Player_Y_Position')==112 and q.get('ScPogo')==1
                states.append(step(q,69))
                assert q.get('Player_Y_Position')==106 and q.get('Player_State')==1
                assert [q.get('MmVY',i)for i in range(3)]==[0,88,250]
                pipelines.append(dict(face=face,start_y=y,start_vy=vy,states=states))
    recoveries=[]
    for face in [1,2]:
        q=setup(face,112,0,0,0);states=[step(q,196)]
        assert q.get('Player_State')==1 and q.get('ScPogo')==0
        for _ in range(128):
            states.append(step(q,68))
            if q.get('Player_State')==0:break
        else:raise AssertionError('Stationary rearm did not return to source support')
        assert q.get('Player_Y_Position')==112 and q.get('ScPogo')==1
        states.append(step(q,69));assert [q.get('MmVY',i)for i in range(3)]==[0,88,250]
        assert q.get('Player_X_Position')+256*q.get('Player_PageLoc') in [2413,2414]
        recoveries.append(dict(face=face,updates=len(states),landed_y=states[-2]['y'],rebound=states[-1]))
    return dict(passed=True,actual_assembled_direct_cases=direct,actual_complete_four_function_pipelines=pipelines,
        actual_stationary_rearm_controls=recoveries,
        code='Actual linked ScroogeMovement plus ExpandedMovement -> PlayerBGCollision -> SamusAfterBGCollisionBridge -> ExpandedWeapons; realbanked calls and nativefoot collision, not a fake landing result.',
        velocity='Before gravity native bounceFA2500 = -5.85546875px/update; complete first updateFA5800 = -5.65625, y112->106.',
        limits='Explicit typed CPU support/player states, not native acquisition or proof that the new Lua policy crosses this gap. No installed Lua parser/runtime was available; wrapper syntax/phase source is reviewed only, not executed here.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    out=a.output.resolve();rom=R/'build/samus_fixed_hud_current4a.nes'
    assert route.sha(rom)==SHA
    old=R/'build/verification/compact-next-scrooge-6be-easy-v1'
    result=json.loads((old/'result.json').read_text())
    assert result['ROM_sha256']==SHA and result['passed'] is False
    assert result['frames']==2533 and result['reason']=='Zero-death 1-1 route'
    rows=list(csv.DictReader((old/'trace.csv').open(newline='')))
    failure=rows[-1]
    assert [int(failure[k])for k in ['frame','x','y','engine','mask']]==[2533,2474,241,11,69]
    text=POLICY.read_text();assert not re.search(r'emu\.|io\.|L\[|ROSTER_CONFIG\.[\w]+\s*=',text)
    assert 'c.block(c.x+8,144)' in text and "c.r('ScPogo')" in text
    controls=source_controls(rom)
    options=argparse.Namespace(rom=rom,output=out,expected_sha256=SHA,identity='scrooge',
        mode='easy',frames=8000,policy=POLICY,replay=None)
    with contextlib.redirect_stdout(io.StringIO()):route.prepare(options)
    ready=json.loads((out/'ready.json').read_text())
    assert ready['config']['character']==12 and ready['config']['variant']==0 and ready['config']['mode_value']==0
    (out/'source-controls.json').write_text(json.dumps(controls,indent=2)+'\n')
    (out/'command.json').write_text(json.dumps(ready['command'],indent=2)+'\n')
    ready['scrooge_gap_successor']=dict(original_FALSE_preserved=True,original_ready_sha256=route.sha(old/'ready.json'),
        original_result_sha256=route.sha(old/'result.json'),original_trace_sha256=route.sha(old/'trace.csv'),
        original_events_sha256=route.sha(old/'events.jsonl'),
        failure_ledger=dict(profile='ScroogeEasy6be-v1',frame=2533,x=2474,y=241,engine=11,mask=69,
            native_result=False,zero_deaths=False,stage_power=1,last_trace_power=0,
            attribution='Continuous Down+B/right kept the lower-step rebound moving past the available top stair; a route/controller failure, not an established physics bug.'),
        observed_lower_landing=dict(frame=2459,x=2372,y=144),observed_apex=dict(frame=2484,x=2410,y=62),
        scoped_changes='ScroogeEasy only,World0/Level0/groundarea1,X2380..2511. CancelA/Down/B near upperapex, hold2412..2418, actualsolidtileatfoot144, rearmDown+B beforelanding, thenmoveRight on nativegroundrebound. Stationaryhop fallback if rearm missed.',
        no_product_changes=True,no_native_seeds=True,no_game_writes=True,
        original_shared_guards_unchanged=True,controller_only=True,source_controls=str(out/'source-controls.json'),
        body_landing_claim='A live grounded readback plus source-block support is required; no scripted grounded/pogo/velocity result is written.',
        native_unrun=True,native_grant_required=True,original8000_and_controlled_1_2=True,
        owned_files=['tools/playthroughs/scrooge_gap6be_policy_v1.lua','tools/audit/scrooge_gap6be_prepare_v1.py'])
    dependencies={Path(p)for p in ready['bindings']}
    dependencies.update({Path(__file__).resolve(),out/'source-controls.json',out/'command.json',
        old/'ready.json',old/'result.json',old/'trace.csv',old/'events.jsonl',
        R/'src/scrooge.s',R/'src/expanded.s',R/'src/collision.s',R/'src/level_tiles.s',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')})
    import sys
    for m in list(sys.modules.values()):
        f=getattr(m,'__file__',None)
        if f and ('py65' in str(f) or str(R/'tools/audit') in str(f))and Path(f).is_file():dependencies.add(Path(f))
    ready['bindings']={str(p):route.sha(p)for p in sorted(dependencies)}
    (out/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(out/'ready.json'),
        ready_sha256=route.sha(out/'ready.json'),bindings=len(dependencies),
        direct_CPU_cases=controls['actual_assembled_direct_cases'],pipelines=len(controls['actual_complete_four_function_pipelines']),
        recovery_controls=len(controls['actual_stationary_rearm_controls']),command=ready['command']),indent=2))


if __name__=='__main__':main()
