"""Native jump entry preserves the source origin of either balance partner."""
from pathlib import Path
import argparse, hashlib, itertools, json
from check_zelda2_platform import Machine
from check_tmnt_render_oa import address


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','rom','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();old,new=Machine(a.parent),Machine(a.rom)
    count,supported_count=0,0
    cases=itertools.product([(3,0),(0,3),(5,2)],[0,1],[81,95],[0,128],[0,2],
        ['valid','inactive_parent','inactive_target','no_flag','out_of_pair','wrong_Y','offscreen','air'])
    for (parent,child),side,origin,pressed,jump,scenario in cases:
        target=child if side else parent;other=parent if side else child
        fields=dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=0,GameEngineSubroutine=8,
                    Player_Y_Position=origin,Player_Y_HighPos=1,Player_Y_Speed=0,Player_State=int(scenario=='air')*2,
                    Z2NativeElevator=0,Z2NativeContacts=4,Z2NativeAir=0,Z2NativeVY=0,
                    Z2NativeVX=24,Z2NativePressedAB=pressed,SavedJoypadBits=pressed,
                    Z2NativeJumpFlag=jump,Z2NativeGravityFraction=0,Z2NativeLandCrouch=0,Z2AttackStage=0)
        for m in [old,new]:
            for i in range(6):
                for n in ['Enemy_Flag','Enemy_ID','Enemy_State','PlatformCollisionFlag']:
                    m.m[address(m.b,n)+i]=0
            def put(n,i,v):m.m[address(m.b,n)+i]=v
            for i in [parent,child]:
                put('Enemy_Flag',i,1);put('Enemy_ID',i,0x24);put('Enemy_Y_HighPos',i,1)
                put('PlatformCollisionFlag',i,255)
            put('Enemy_State',parent,child);put('Enemy_State',child,255)
            put('PlatformCollisionFlag',parent,target)
            put('Enemy_Y_Position',target,origin+32);put('Enemy_Y_Position',other,origin+64)
            if scenario=='inactive_parent':put('Enemy_Flag',parent,0)
            if scenario=='inactive_target':put('Enemy_Flag',target,0)
            if scenario=='no_flag':put('PlatformCollisionFlag',parent,255)
            if scenario=='out_of_pair':put('PlatformCollisionFlag',parent,4)
            if scenario=='wrong_Y':put('Enemy_Y_Position',target,origin+33)
            if scenario=='offscreen':put('Enemy_Y_HighPos',target,2)
        x=old.call('Link_Jumping_routine',fields);y=new.call('Link_Jumping_routine',fields)
        supported=scenario=='valid'
        delta=origin%16 if supported else 0
        assert new.get('Player_Y_Position')==(old.get('Player_Y_Position')+delta)&255,(parent,child,side,scenario)
        assert x[1:3]==y[1:3]and x[3]&0x7d==y[3]&0x7d
        for n in ['Z2NativeVY','Z2NativeAir','Z2NativeGravityFraction','Z2NativeLandCrouch',
                  'Z2AttackStage','Player_Y_HighPos','Player_Y_Speed']:
            assert old.get(n)==new.get(n),(n,scenario)
        if not supported:assert x==y
        count+=1;supported_count+=supported
    q=dict(passed=True,goal_complete=False,ROM_sha256=hashlib.sha256(new.b['raw']).hexdigest(),
           cases=count,supported=supported_count,unsupported_exact=count-supported_count,
           scope='Complete real native Link_Jumping_routine, legal parent/child slot permutations and actual native pair flag/state schema. Both support targets preserve nongrid Y; inactive/missing/out-of-pair/wrong-Y/offscreen/air retain original arithmetic. Original velocity/gravity/air state, X/Y and C/V/D/I exact. Separate native paired arenas supply carry/render evidence.')
    a.output.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
