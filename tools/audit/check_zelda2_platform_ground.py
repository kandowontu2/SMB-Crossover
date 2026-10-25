"""Prove the native jump adapter retains only real nongrid platform origins."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_zelda2_platform import Machine
from check_tmnt_render_oa import address


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','rom','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();old,new=Machine(a.parent),Machine(a.rom)
    counts=dict(native_jump=0,supported=0,unsupported_exact=0)
    outputs=['Z2NativeVY','Z2NativeAir','Z2NativeGravityFraction','Z2NativeLandCrouch',
             'Z2AttackStage','Player_Y_HighPos','Player_Y_Speed']
    for slot,kind,origin,pressed,vx,jump,scenario in itertools.product(
            [0,3,5],[0x25,0x27,0x2b,0x2c],[80,81,95,112,127,176,191],
            [0,128],[0,24,232],[0,2],['valid','inactive','wrong_flag','wrong_Y','offscreen','air']):
        small=kind>=0x2b;flag=1 if kind==0x2c else 2 if small else slot
        fields=dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=0,GameEngineSubroutine=8,
                    Player_Y_Position=origin,Player_Y_HighPos=1,Player_Y_Speed=0,Player_State=0,
                    Z2NativeElevator=0,Z2NativeContacts=4,Z2NativeAir=0,Z2NativeVY=0,
                    Z2NativeVX=vx,Z2NativePressedAB=pressed,SavedJoypadBits=pressed,
                    Z2NativeJumpFlag=jump,Z2NativeGravityFraction=0,Z2NativeLandCrouch=0,
                    Z2AttackStage=0,AreaPointer=0,WorldNumber=0)
        if scenario=='air':fields['Player_State']=2
        for machine in [old,new]:
            for i in range(6):
                for name in ['Enemy_Flag','Enemy_ID','PlatformCollisionFlag']:
                    machine.m[address(machine.b,name)+i]=0
            machine.m[address(machine.b,'Enemy_Flag')+slot]=0 if scenario=='inactive'else 1
            machine.m[address(machine.b,'Enemy_ID')+slot]=kind
            machine.m[address(machine.b,'Enemy_Y_HighPos')+slot]=2 if scenario=='offscreen'else 1
            machine.m[address(machine.b,'PlatformCollisionFlag')+slot]=255 if scenario=='wrong_flag'else flag
            top=origin+32+(scenario=='wrong_Y')
            machine.m[address(machine.b,'Enemy_Y_Position')+slot]=(top-(128 if small and flag==1 else 0))&255
        r1=old.call('Link_Jumping_routine',fields)
        r2=new.call('Link_Jumping_routine',fields)
        supported=scenario=='valid'and origin%16!=0
        displacement=origin%16 if supported else 0
        assert new.get('Player_Y_Position')==(old.get('Player_Y_Position')+displacement)&255,(slot,kind,origin,pressed,vx,jump,scenario)
        assert [old.get(n)for n in outputs]==[new.get(n)for n in outputs]
        assert r1[1:3]==r2[1:3]
        assert r1[3]&0x7d==r2[3]&0x7d
        if not supported:assert r1==r2,(scenario,origin,r1,r2)
        counts['native_jump']+=1;counts['supported'if supported else'unsupported_exact']+=1
    proof=dict(passed=True,goal_complete=False,ROM_sha256=hashlib.sha256(new.b['raw']).hexdigest(),cases=counts,
               scope='Actual complete native Link_Jumping_routine against accepted parent. Only real preceding platform support retains nongrid origin; inactive/wrongflag/wrongY/offscreen/air cases retain exact native A/X/Y/P. Native jump impulse/gravity/air state and C/V/D/I unchanged even with freshA, both jump strengths and signed running speeds. No native carry/release/PPU or performance admission.')
    a.output.write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
