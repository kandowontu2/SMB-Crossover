"""Prepare one input-only Ryu Easy successor; keep original native FALSE."""
from pathlib import Path
import argparse
import collections
import contextlib
import csv
import io
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import current_roster_compact_11_v1 as route
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
SHA='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
POLICY=R/'tools/playthroughs/current_roster_ryu_wall_edge_v2.lua'


def controls(rom):
    b=scoped_load(rom);cases=[]
    pipe=list(b['raw'][location(b,'VerticalPipeData'):location(b,'VerticalPipeData')+4])
    assert pipe==[17,16,21,20]
    for face in [1,2]:
        start=880 if face==1 else 960;q=Arena(b,10)
        q.put(CrossoverBehaviorVersion=0,OperMode_Task=3,AreaType=1,PlayerStatus=0,
            Player_X_Position=start&255,Player_PageLoc=start>>8,Player_Y_Position=176,
            Player_State=0,ScreenLeft_PageLoc=3,ScreenLeft_X_Pos=17,
            ScreenRight_PageLoc=4,ScreenRight_X_Pos=16,ScrollLock=1,
            Player_CollisionBits=255,Player_MovingDir=face,PlayerFacingDir=face)
        q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
        for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
        for page in range(2):
            for row in [11,12]:
                for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
        for row in range(7,11):
            for col in [9,10]:q.set('Block_Buffer_1',pipe[(0 if row==7 else 2)+(1 if col==9 else 0)],208+row*16+col)
        for i in range(6):q.set('Enemy_Flag',0,i)
        def state():
            return dict(x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),
                state=q.get('Player_State'),wall=q.get('XgWall'),side=q.get('RyWallSide'),lock=q.get('XgWallLock'),
                previous=q.get('RgPreviousButtons'),previous_AB=q.get('PreviousA_B_Buttons'),consumed_AB=q.get('A_B_Buttons'),fresh=q.get('XgFresh'))
        calls=0
        def step(buttons):
            nonlocal calls
            calls+=1;q.set('SavedJoypadBits',buttons);q.invoke('GameLoop');return state()
        for _ in range(30):step(0)
        assert q.get('Player_State')==0 and q.get('Player_Y_Position')==176
        held=128+8+face
        for _ in range(60):step(held)
        top=state();assert top['wall']==face and top['side']==face and top['y']==126 and top['previous']&128 and top['previous_AB']&128
        assert top['x']==(897 if face==1 else 942)
        probe=top['x']+(21 if face==1 else -5)
        q.put(RgTempX=probe&255,RgTempPage=probe>>8,RgTempY=129)
        cpu,_=q.invoke('ExpandedMapCell');assert not cpu.p&1,'Actual source top-jump probe is clear'
        # This explicit schedule models release polls that never reach a Main
        # input reader. The native trace suggests it, but does not log readers.
        for _ in range(40):step(held)
        assert state()['x']==top['x']and state()['y']==126 and state()['fresh']&128==0
        release=step(8+face)
        assert all(release[n]&128==0 for n in ['previous','previous_AB','consumed_AB'])
        launch=step(held)
        assert launch['fresh']&128 and launch['wall']==0 and launch['lock']>0 and launch['y']<126
        cases.append(dict(face=face,full_GameLoop_calls=calls,naturally_reached_wall_top=top,
            no_consumed_release_counterfactual_calls=40,real_release=release,real_fresh_press_launch=launch,
            source_probe=dict(x=probe,y=129,carry_solid=False)))
    return dict(passed=True,native_run=False,Lua_VM_executed=False,cases=cases,
        scope='Full assembled GameLoop from typed ground support/pipe, real jump/attach/climb/held-A stop and release/press; no XgWall/history/velocity outcomes seeded. The zero-consumed-release schedule is an explicit source counterfactual, not claimed captured native reader values. Native controller uses no actor/map seeds.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    rom=R/'build/mega_proto_body_palette_9ea.nes';assert route.sha(rom)==SHA
    old=R/'build/verification/compact-ab221e-ryu-easy-v1'
    result=json.loads((old/'result.json').read_text())
    assert result['passed']is False and result['frames']==1828 and result['identity']=='ryu'and result['ROM_sha256']==SHA
    rows=list(csv.DictReader((old/'trace.csv').open(newline='')));groups=collections.Counter();previous=0
    for row in rows:
        delta=int(row['loops'])-previous;previous=int(row['loops'])
        if int(row['frame'])>=1525:groups[(int(row['mask']),delta)]+=1
    assert groups==collections.Counter({(9,0):152,(137,2):152})
    proof=controls(rom);out=a.output.resolve()
    options=argparse.Namespace(rom=rom,output=out,expected_sha256=SHA,identity='ryu',mode='easy',frames=8000,policy=POLICY,replay=None)
    with contextlib.redirect_stdout(io.StringIO()):route.prepare(options)
    put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
    put(out/'source-controls.json',proof)
    z=json.loads((out/'ready.json').read_text())
    z['ryu_input_successor']=dict(original_FALSE_preserved=True,frame=1828,x=897,y=126,reason=result['reason'],
        observed_tail=[dict(poll_mask=k[0],completed_Main_delta=k[1],physical_rows=v)for k,v in sorted(groups.items())],
        native_readback_limit='Original native trace does not log A_B_Buttons/PreviousA_B_Buttons/RgPreviousButtons/XgFresh. Phase-lock is supported by poll/completion cadence, not proven exact consumed reads.',
        actual_source_edge='XgFresh=(SavedJoypadBits xor RgPreviousButtons)&SavedJoypadBits; weapon path updates RgPreviousButtons; SaveAB updates PreviousA_B_Buttons.',
        scope='RyuEasy only,World0/Level0/groundarea1,X>=512,actualwall andclear source X+21/-5,Y+3; all other contexts delegate unchanged. Retain release until actual consumed/history readbacks clear; hold fresh press/rearm if no edge. No native seeds/product/guards changed.',
        Lua_VM_executed=False,native_run=False,source_controls=str(out/'source-controls.json'))
    put(out/'command.json',z['command'])
    paths={Path(p)for p in z['bindings']}|{Path(__file__),out/'source-controls.json',out/'command.json',
        old/'ready.json',old/'result.json',old/'inputs.csv',old/'trace.csv',old/'events.jsonl',old/'review.json',old/'selected-whole-frames.png',
        R/'src/expanded.s',R/'src/expanded_weapons.s',R/'src/roster_weapons.s',R/'src/source_motion.s',R/'src/ryu_wall.s',R/'src/ryu_platform.s',R/'src/game.s',R/'src/level_tiles.s',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and('py65'in p or str(R/'tools/audit')in p)and Path(p).is_file():paths.add(Path(p))
    z['bindings']={str(p):route.sha(p)for p in sorted(paths)};put(out/'ready.json',z)
    assert all(route.sha(p)==h for p,h in z['bindings'].items())
    print(json.dumps(dict(ready=str(out/'ready.json'),sha256=route.sha(out/'ready.json'),bindings=len(paths),source_cases=2,native_run=False,command=z['command'])))


if __name__=='__main__':main()
