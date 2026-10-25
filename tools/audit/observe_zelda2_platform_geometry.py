"""Observe original Link hurtbox and the port's native platform/body mismatch."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import load,address,location,Memory
from verify_native_relocation import NesMPU


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();b=load(a.rom);original=Path('C:/NES/Zelda II - The Adventure of Link (USA).nes').read_bytes()
    assert hashlib.sha256(original).hexdigest()=='9fca03064a5113e6a92f550d9f42bac9ac1ae248a84df1f653d7cd7f76a1803d'
    source=[]
    for shield in [0,1]:
        m=[0]*65536;m[0xc000:]=original[16+7*16384:16+8*16384]
        m[0xcc],m[0x29],m[0x17]=88,100,shield
        cpu=NesMPU(memory=m,pc=0xe975);cpu.sp=0xfd;cpu.stPushWord(0x7eff)
        for _ in range(100):
            if cpu.pc==0x7f00:break
            cpu.step()
        else:raise AssertionError(hex(cpu.pc))
        source.append(dict(shield=shield,crouched=not bool(shield),original_rectangle=m[:4],
                           adapted_offsets=dict(left=m[0]-96,top=m[1]-100,right=m[0]+m[2]-96,bottom=m[1]+m[3]-100)))
    m=Memory(b);cpu=NesMPU(memory=m)
    def put(n,v):m[address(b,n)]=v
    def get(n):return m[address(b,n)]
    def call(n):
        bank=(location(b,n)-16)//8192;m.page(1,bank);put('CurrentBank',128|bank)
        cpu.pc,cpu.sp,cpu.p=address(b,n),0xfd,0x35;cpu.stPushWord(0x7eff)
        cpu.x=0;cpu.y=0;cpu.a=0
        for _ in range(12000):
            if cpu.pc==0x7f00:break
            cpu.step()
        else:raise AssertionError((n,hex(cpu.pc)))
        assert cpu.sp==0xfd
    boxes=[]
    for fairy,crouch in [(0,0),(0,1),(8,1)]:
        for n,v in dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=fairy,GameEngineSubroutine=8,
                        Player_Rel_XPos=96,Player_Rel_YPos=100,Player_BoundBoxCtrl=18,
                        CrouchingFlag=crouch,Player_State=0,Z2NativeShield=0 if crouch else 1).items():put(n,v)
        call('LmBoundingBoxGate')
        boxes.append(dict(fairy=fairy,crouch=crouch,offsets=
            dict(left=get('BoundingBox_UL_XPos')-96,top=get('BoundingBox_UL_YPos')-100,
                 right=get('BoundingBox_LR_Corner')-96,bottom=m[address(b,'BoundingBox_LR_Corner')+1]-100)))
    positions=[]
    for fairy in [0,8]:
        for n,v in dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=fairy,GameEngineSubroutine=8,
                        Enemy_Y_Position=160,Enemy_Y_HighPos=1,Player_Y_Position=130,Player_Y_HighPos=1,
                        Player_Y_Speed=2,Player_Y_MoveForce=71).items():put(n,v)
        call('PositionPlayerOnVPlat')
        positions.append(dict(fairy=fairy,platform_y=160,actual_player_y=get('Player_Y_Position'),
                              actual_terrain_foot=get('Player_Y_Position')+(26 if fairy else 32),
                              intended_player_y=160-(26 if fairy else 32)))
    proof=dict(observation_complete=True,repair_passed=False,goal_complete=False,
               ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),original_ROM_sha256=hashlib.sha256(original).hexdigest(),
               original_body_routine_CPU='E975..E99B',original_body_routine_bytes=list(original[16+7*16384+0x2971:16+7*16384+0x299c]),
               original_actual_body_rectangles=source,current_port_boxes=boxes,current_platform_positions=positions,
               scope='Actual original USA rectangle routine and actual port bounding-box/platform placement code. Source X is rebased by8; terrain and hurtbox endpoints are separate. This diagnoses short body projection and a6px Fairy platform-foot mismatch. No source changes, native gameplay or repair admission.')
    a.output.parent.mkdir(exist_ok=False);a.output.write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
