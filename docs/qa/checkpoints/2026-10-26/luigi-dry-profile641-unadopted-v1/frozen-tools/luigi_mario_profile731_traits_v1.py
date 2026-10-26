"""Quantify only the new Luigi dry jump/braking traits and shared Mario coefficients."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load
from mario_luigi731_coefficients_v1 import make,movement,seed_vx,coord,q24
from luigi_mario_profile731_cpu_v1 import BASE,CURRENT,PARENT,full,tick,state
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'luigi-mario-profile731-v3';O=P/'traits-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):assert not p.exists();p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert sha(P/'candidate.nes')==CURRENT and sha(BASE)==PARENT;O.mkdir(exist_ok=False)
    old,new=load(BASE),load(P/'candidate.nes');jumps=[];coasts=[];accelerations=[];frictions=[];equivalence=[]
    for mode,speed,release in itertools.product([0,1],[0,1.25,2.5],[None,1,8]):
        both=[]
        for b,char in [(old,0),(new,8)]:
            q=make(b,char,mode);q.set('MarioSourceActive',1);seed_vx(q,0,speed);path=[]
            for t in range(180):
                movement(q,128 if release is None or t<release else 0);path.append(dict(update=t+1,x=coord(q,'X'),y=coord(q,'Y')-256,vy=q24(q,'MmVY')))
                if t and path[-1]['y']>=176:break
            else:raise AssertionError('No actual source return crossing')
            low=min(z['y'] for z in path)
            both.append(dict(character=char,rise=176-low,apex=next(z['update'] for z in path if z['y']==low),return_crossing=len(path),path=path))
        if release is None:assert 3<=both[1]['rise']-both[0]['rise']<=6
        jumps.append(dict(mode=mode,speed=speed,A_held_updates=release,cases=both))
    for mode in [0,1]:
        both=[]
        for b,char in [(old,0),(new,8)]:
            q=make(b,char,mode);q.set('MarioSourceActive',1);seed_vx(q,0,2.5);q.set('MarioRunCap',1);path=[]
            for t in range(150):
                movement(q,0);path.append(dict(update=t+1,x=coord(q,'X'),vx=q24(q,'MmVX')))
                if not q24(q,'MmVX'):break
            both.append(dict(character=char,stop_update=len(path),distance=coord(q,'X')-352,path=path))
        assert [(x['stop_update'],x['distance']) for x in both]==[(41,42),(47,48)]
        coasts.append(dict(mode=mode,cases=both))
    for mode,run in itertools.product([0,1],[False,True]):
        both=[]
        for b,char in [(old,0),(new,8)]:
            q=make(b,char,mode);q.set('MarioSourceActive',1);path=[]
            for t in range(100):movement(q,1|(64 if run else 0));path.append(q24(q,'MmVX'))
            both.append(path)
        assert both[0]==both[1]
        accelerations.append(dict(mode=mode,run=run,complete_100update_vx_equal=True,cap=both[0][-1]/65536))
    for mode,kind,speed,air in itertools.product([0,1],range(3),[-2.5,-1.25,-.8,-.25,.25,.8,1.25,2.5],[0,1]):
        q=make(new,8,mode);seed_vx(q,0,speed);q.put(Player_State=air,MarioWaterFrictionKind=kind)
        raw=abs(q24(q,'MmVX'));factor=[62344,56210,61399][kind]
        base=(raw*factor)>>16;expected=base if air else base+((raw-base)>>3)
        if kind==0 and expected<0x5555:expected=0
        if speed<0:expected=-expected
        q.invoke('LuigiSourceFriction');assert q24(q,'MmVX')==expected
        frictions.append(dict(mode=mode,kind=kind,initial_speed=speed,air=air,result_Q8_16=expected))
    fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_X_Scroll','Player_Y_Speed','Player_State','CrouchingFlag','MarioJumpRise','MmFrictionYActive','MmJumpReleased']
    for mode,air,bits,speed in itertools.product([0,1],[0,1],[1,65,2,66],[0,1.25,2.5]):
        pair=[]
        for b,char in [(old,0),(new,8)]:
            q=make(b,char,mode);q.set('MarioSourceActive',1);seed_vx(q,0,speed)
            q.put(Player_State=air,Player_Y_Speed=2 if air else 0,A_B_Buttons=bits&192,PreviousA_B_Buttons=bits&192,SavedJoypadBits=bits,Left_Right_Buttons=bits&3)
            if air:q.array('MmVY',[0,0,2])
            # Ground reverse intentionally invokes the specified traction difference.
            if not air and speed and bits&2:continue
            q.invoke('PlayerMovementSubs')
            result={n:q.get(n) for n in fields}
            for name,size in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:result[name]=[q.get(name,i) for i in range(size)]
            pair.append(result)
        if pair:
            assert len(pair)==2 and pair[0]==pair[1],(mode,air,bits,speed,pair)
            equivalence.append(dict(mode=mode,air=air,input=bits,speed=speed,current_Mario_fields_exact=True))
    # Cold original reset/imports remain actual code; first dry entry initializes source fractions.
    cold=[]
    for mode in [0,1]:
        q=full(new,mode);q.put(MarioSourceActive=0,MarioRunCap=255)
        q.array('MmVX',[91,171,2]);q.array('MmVY',[91,171,252]);q.array('MmXFraction',[133,77]);q.array('MmYFraction',[133,77])
        tick(q,0)
        assert q.get('MarioSourceActive')==1 and q24(q,'MmVX')==q24(q,'MmVY')==0
        assert coord(q,'X')==352 and coord(q,'Y')==432 and q.get('MarioRunCap')==0
        cold.append(dict(mode=mode,actual_PlayerCtrl_source_cold_init=True,result=state(q,1)))
    put(O/'measurements.json',dict(jumps=jumps,coasts=coasts,acceleration=accelerations,frictions=frictions,shared_dry_fields=equivalence,cold=cold))
    put(O/'proof.json',dict(passed=True,native_executed=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
        jump_comparisons=len(jumps),coast_comparisons=len(coasts),identical_100update_acceleration_cases=len(accelerations),
        actual_braking_formula_cases=len(frictions),shared_dry_field_cases=len(equivalence),cold_wrapper_cases=2,
        source_fields_only=True,not_native_physical_frames=True,
        bindings={str(p):sha(p) for p in [Path(__file__),P/'candidate.nes',P/'candidate.dbg',BASE,BASE.with_suffix('.dbg'),O/'measurements.json']}))
    print(json.dumps({k:v for k,v in json.loads((O/'proof.json').read_text()).items()if k!='bindings'},indent=2))


if __name__=='__main__':main()
