"""Exact fast-candidate inactive pose/draw ABI and interrupt comparison."""

from itertools import product
import json

import steve_armor_idle_1113 as Idle


def check(parent,candidate,info):
    Native,Packet = Idle.Native,Idle.Native.Packet
    assert Packet.Entry.digest(candidate) == Native.IDLE_CANDIDATE
    baseline,old_info = Native.proposal(parent)
    assert Packet.Entry.digest(baseline) == Idle.BASE
    models = [Packet.load(image,layout)[0] for image,layout in
              ((baseline,old_info),(candidate,info))]
    C,N = Packet.Cold.C,Packet.Cold.N
    cuts = set()
    floor = 224
    calls = 0

    def interrupt(model,cpu):
        nonlocal floor
        bank = model.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1
        key = bank,cpu.pc
        if bank != 2 or not 0xcd00 <= cpu.pc < 0xcd88 or key in cuts:
            return
        cuts.add(key)
        for kind in ('FF','IRQ'):
            _,branch = C.Vector.clone(model,cpu)
            floor = min(floor,C.ColdVector.interrupt(branch,kind))

    def snapshot(model,cpu):
        return dict(registers=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp),
                    zero_page=bytes(model[:0x100]),
                    native_body=bytes(model[0x5c00:0x8000]),
                    oam=bytes(model[0x200:0x300]),
                    pose=bytes(model.ram[2][0x8c0:0x900]),
                    upgrade=bytes(model.ram[2][0x1f0:0x200]),
                    source_state=bytes(model.ram[2][0x900:0xa00]),
                    maps=tuple(model.rawtags),chr=tuple(model.chr_latches))

    for name,engine,face,special,player_state in product(
            ('JnSetPose','JnDraw'),(7,8),(1,2),(0,1),(0,1)):
        outputs = []
        for index,seed in enumerate(models):
            m = C.Vector.clone(seed)
            m.raw_page(1,3)
            m.raw_page(2,2)
            N.put(m,CurrentBank=3,CurrentBankC=2,GameEngineSubroutine=engine,
                  GamePauseStatus=0,PlayerFacingDir=face,Player_State=player_state,
                  Player_Rel_XPos=64,Player_Rel_YPos=176,
                  Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,
                  Player_Y_HighPos=1,CurrentOAMOffset=0)
            m[0xc1f0:0xc200] = bytes(16)
            m[0xc977] = special
            m[0x5c80],m[0x5c82],m[0x5c83],m[0x5c87] = 1,2,0xda,0
            m[0x200:0x300] = bytes([248])*256
            cpu = C.Vector.call(m,name,a=83,x=0,y=37,
                                observe=interrupt if index else None)
            outputs.append(snapshot(m,cpu))
        for field in outputs[0]:
            assert outputs[0][field] == outputs[1][field],(
                name,engine,face,special,player_state,field,
                outputs[0][field] if field == 'registers' else '',
                outputs[1][field] if field == 'registers' else '')
        calls += 1
    return dict(candidate=Native.IDLE_CANDIDATE,baseline=Idle.BASE,
                inactive_native_pose_draw_cases=calls,complete_AXYP_SP_parity=True,
                native_body_zero_page_OAM_pose_upgrade_mapper_CHR_parity=True,
                instruction_cuts=len(cuts),IRQ=len(cuts),lag_NMI=len(cuts),minimum_SP=floor,
                output_files=0,Mesen_run=False)


if __name__ == '__main__':
    parent = Idle.Native.Live.Art.D.HOST.read_bytes()
    candidate,info = Idle.proposal(parent)
    print(json.dumps(check(parent,candidate,info),sort_keys=True),flush=True)
