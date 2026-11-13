"""Bounded native instruction/entry fixtures for the fixed309 handoff.

These are declared native ABI/control-input fixtures, separate from the
unseeded cold/menu/full-stage run. No source health/weapon/physics is seeded.
"""
from hashlib import sha256
import argparse
import json

import prince_entrance_handoff_1113 as E
import check_prince_earned_sword_combat_1113 as F
import check_prince_brick_support_1111 as B
from verify_native_relocation import NesMPU

P,N=F.P,F.P.N


def flat(raw,bank):
    memory=bytearray(65536)
    memory[0xa000:0xc000]=raw[16+8192*bank:16+8192*(bank+1)]
    return memory


def run(memory,start,stops,*,limit=2000,a=85,x=7,y=91,p=0x61):
    cpu=NesMPU(memory=memory,pc=start)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p,224
    cpu.stPushWord(0x5aff)
    seen=[]
    for _ in range(limit):
        if cpu.pc in stops:return cpu,seen
        seen.append(cpu.pc)
        assert memory[cpu.pc],('BRK in actual native instruction fixture',hex(cpu.pc))
        cpu.step()
    raise AssertionError(('Instruction fixture bound',hex(start),hex(cpu.pc)))


def compiled_semantics(raw):
    """Run the actual compiled gates, rather than merely recording hashes."""
    bundle=F.P.W.Symbols.bundle()
    at=lambda name:F.P.W.address(bundle,name)
    put=lambda m,**fields:[m.__setitem__(at(name),value) for name,value in fields.items()]
    native=flat(raw,1)
    assert native[0xa6a0:0xa6c1]==bytes.fromhex(
        'ad1107d01ca51ec903d0034c0cb78d6a01a9468d6c01a9a08d6d01a9bc205a0160')
    assert native[0xa81e:0xa82d]==bytes.fromhex('ad1107d00cad58052980f0052d5b05')
    mm=[]
    for state,spring,expected in ((0,1,'CrossoverVanillaMovement'),(3,0,'MegaManClimbing'),
                                  (0,0,'source')):
        m=flat(raw,1)
        put(m,SelectedCharacter=1,GameEngineSubroutine=8,Player_State=state,JumpspringAnimCtrl=spring)
        stops={at('CrossoverVanillaMovement'),at('MegaManClimbing'),0x15a}
        cpu,path=run(m,at('CrossoverGuestControl'),stops)
        if expected=='source':
            assert cpu.pc==0x15a
            assert (m[0x16c]+256*m[0x16d],cpu.a)==(at('SpecialMovement'),188)
        else:assert cpu.pc==at(expected),(state,spring,hex(cpu.pc))
        mm.append(dict(state=state,spring=spring,destination=expected))
    # SpecialMovement's freeze path returns; its MM branch makes the actual
    # MegaManMovement farcall, never re-entering native PlayerPhysicsSub.
    for frozen in (0,1):
        m=flat(raw,60)
        put(m,SelectedCharacter=1,SsFreeze=frozen,SsBodyStop=0)
        cpu,path=run(m,at('SpecialMovement'),{0x15a,0x5b00})
        if frozen:assert cpu.pc==0x5b00
        else:assert (cpu.pc,m[0x16c]+256*m[0x16d],cpu.a)==(0x15a,at('MegaManMovement'),131)
    # State3 returns from native PlayerPhysicsSub before fresh-A. A spring
    # rejects a fresh A; no A and a retained A reject before ProcJumping.
    native_physics=[]
    for state,spring,buttons,previous in ((3,0,128,0),(0,1,128,0),(0,0,0,0),(0,0,128,128)):
        m=flat(raw,1)
        put(m,SelectedCharacter=1,GameEngineSubroutine=8,Player_State=state,
            JumpspringAnimCtrl=spring,A_B_Buttons=buttons,PreviousA_B_Buttons=previous,
            Up_Down_Buttons=0,Player_CollisionBits=255)
        stop=0x5b00 if state==3 else at('X_Physics')
        cpu,path=run(m,at('PlayerPhysicsSub'),{stop,at('CrossoverJumpProfile')})
        assert cpu.pc==stop and at('CrossoverJumpProfile') not in path
        native_physics.append(dict(state=state,spring=spring,buttons=buttons,previous=previous,profile=False))
    m=flat(raw,1)
    put(m,Player_State=0,JumpspringAnimCtrl=0,A_B_Buttons=128,PreviousA_B_Buttons=0,SwimmingFlag=0)
    cpu,path=run(m,at('PlayerPhysicsSub'),{at('CrossoverJumpProfile')})
    assert cpu.pc==at('CrossoverJumpProfile')
    assert at('InitJS') in path and at('GetYPhy') in path
    # The fresh-A condition is real. Legitimate MM cannot jointly satisfy
    # it and enter this native path: the actual dispatch cases above block it.
    injury=[]
    m=flat(raw,59)
    assert m[0xa132:0xa153]==bytes.fromhex(
        'ad0260c901f017c909f013c902f00fc904f00bc905f007c90af0034cfba18d1c6f')
    put(m,SelectedCharacter=1,GameEngineSubroutine=8,TimerControl=77)
    cpu,path=run(m,0xa132,{at('GuestInjuryStart::Mega')})
    assert at('GuestInjuryStart::Source') in path
    assert m[at('GuestHurtKind')]==1 and m[at('TimerControl')]==0 and m[15]==8
    injury.append(dict(kind='modern prepared-MM branch',engine=m[15],timer=m[at('TimerControl')]))
    m=flat(raw,59)
    assert m[0xb8c2:0xb8d8]==bytes.fromhex('ad02608d1c6fc901d00ca9008d13608d1260a90fd015')
    put(m,SelectedCharacter=1,GameEngineSubroutine=8)
    cpu,path=run(m,0xb8c2,{0xb90c})
    assert m[15]==9 and m[at('GuestPowerupActive')]==1 and m[at('TimerControl')]==255
    assert m[at('GuestHurtKind')]==1 and m[at('GuestPowerupPose')]==15
    injury.append(dict(kind='legacy prepared-MM branch',engine=m[15],timer=m[at('TimerControl')]))
    m=flat(raw,10)
    put(m,GuestHurtKind=1,SavedJoypadBits=255,A_B_Buttons=255,Left_Right_Buttons=255,Up_Down_Buttons=255)
    cpu,path=run(m,at('GuestInjuryMovement'),{at('MegaManHurtMovement')})
    assert all(m[at(name)]==0 for name in ('SavedJoypadBits','A_B_Buttons','Left_Right_Buttons','Up_Down_Buttons'))
    assert at('GuestInjuryMovement::FixedProfile') in path
    injury.append(dict(kind='compiled recoil dispatch',destination='MegaManHurtMovement',parsed_controls=0))
    tasks=[]
    for name,target,bank in (('PlayerChangeSize','NrNativePowerupDispatch',252),
                             ('PlayerFireFlower','NrNativePowerupDispatch',252),
                             ('PlayerDeath','MegaManDeathUpdate',136)):
        m=flat(raw,1);put(m,SelectedCharacter=1)
        cpu,path=run(m,at(name),{0x15a})
        assert (m[0x16c]+256*m[0x16d],cpu.a)==(at(target),bank),(name,hex(cpu.pc),cpu.a)
        tasks.append(dict(native_entry=name,destination=target))
    return dict(passed=True,MM_engine8_dispatch=mm,native_physics_admission=native_physics,
        impossible_MM_fresh_A_native_branch_positive_control=True,actual_injury_branches=injury,
        guest_non8_tasks=tasks,scope='Actual compiled instruction windows and declared native control/prepared-injury fixtures. No source actor, health, inventory or outcome writes.',outputs=0)


def headers(raw):
    changed,_=E.proposal(raw)
    cases=0
    for header in range(256):
        destinations=[]
        for image in (raw,changed):
            m=flat(image,1);m[0x713]=header;m[0x587]=0x55
            cpu,path=run(m,E.HOOK,{0xa05d,0xa0ad,E.HELPER})
            destinations.append((cpu.pc,cpu.a,cpu.p))
        if header in (6,7):
            assert destinations[0]==destinations[1],(header,destinations)
        else:
            assert destinations[0][0]==0xa0ad and destinations[1][0]==E.HELPER
        cases+=1
    return dict(passed=True,all_8bit_headers=cases,pipes6_7_AXYP_after_unchanged_first_LDA_exact=True)


def typed(seed,**fields):
    m=B.Q.Sonic.slim_fork(seed)
    N.put(m,SelectedCharacter=38,GameEngineSubroutine=7,OperMode=1,NmiDisable=255,
        DisableScreenFlag=0,Mirror_PPUMASK=30,PlayerEntranceCtrl=1,AltEntranceControl=0,
        AreaType=2,Player_Y_Position=48,Player_Y_HighPos=1,Player_State=2,
        Player_Y_Speed=2,Player_Y_MoveForce=88,Player_SprAttrib=0,JoypadOverride=0)
    N.put(m,**fields)
    return m


def regs(m):
    q=N.invoke(m,'PlayerEntrance',a=85,x=7,y=91,p=0x61)
    return tuple(q[k] for k in ('A','X','Y','P'))


def landing_isr(raw):
    """Separate actual-cold, native header2/floor/PlayerRdy cut fixture."""
    image,_=E.proposal(raw)
    seed,cold=B.cold(image)
    m=typed(seed,PlayerEntranceCtrl=2)
    B.terrain(m,lambda col,y:0x54 if y>=208 else 0)
    N.put(m,GameTimerSetting=1,FetchNewGameTimerFlag=1,ScreenLeft_PageLoc=0)
    N.invoke(m,'Entrance_GameTimerSetupCore',a=85,x=0,y=0,p=0x61)
    assert (N.get(m,'Player_Y_Position'),N.get(m,'Player_State'),N.get(m,'GameEngineSubroutine'))==(176,0,7)
    cuts=B.Async.stress('native Prince supported entry and original PlayerRdy',m,regs,
        [(129,E.HOOK,E.HOOK+11),(129,E.PROFILE,E.PROFILE+41),(129,0xa0ad,0xa0c1)])
    result=B.Q.Sonic.slim_fork(m)
    regs(result)
    assert N.get(result,'GameEngineSubroutine')==8 and N.get(result,'Player_Y_Position')==176
    assert result.ram[2][0x6cf]==5 and result.ram[2][0x6c6]==0 and result.ram[2][0xa6]==0
    return dict(passed=True,actual_candidate_cold=cold,cuts=cuts,
        scope='Declared flat native terrain/header2 after actual common cold; native constructor suppliesY176 and nativeAutoControl completes actualfloor before originalPlayerRdy. No source actor/health/physics seeds.',outputs=0)


def entry_matrix(raw,*,interrupts=False):
    image,_=E.proposal(raw)
    # Exact current cold streams are mounted by the real common loader. The
    # following contexts are explicitly directed native entrance ABI inputs.
    before,old_cold=B.cold(raw)
    after,new_cold=B.cold(image)
    assert tuple(map(bytes,before.ram))==tuple(map(bytes,after.ram))
    B.Q.Sonic.O.clear_logs(before)
    B.Q.Sonic.O.clear_logs(after)
    print(json.dumps(dict(event='actual_cold_pair',PPU_reads=[old_cold['PPU_reads'],new_cold['PPU_reads']])),flush=True)
    count=0
    for character in range(256):
        if character==38:continue
        a,b=[typed(seed,SelectedCharacter=character) for seed in (before,after)]
        assert regs(a)==regs(b),(character,'foreign entrance return')
        assert tuple(map(bytes,a.ram))==tuple(map(bytes,b.ram)),(character,'foreign private RAM')
        for name in ('GameEngineSubroutine','PlayerFacingDir','AltEntranceControl','DisableCollisionDet','JoypadOverride'):
            assert N.get(a,name)==N.get(b,name),(character,name)
        count+=1
    print(json.dumps(dict(event='foreign_native_entrances',cases=count)),flush=True)
    excluded=[]
    for fields in (dict(AreaType=0),dict(PlayerEntranceCtrl=6),dict(PlayerEntranceCtrl=7),
                   dict(AltEntranceControl=2,Player_Y_Position=150),
                   dict(AltEntranceControl=2,JoypadOverride=8,Vine_Height=96,Player_State=3,Player_Y_Position=160)):
        a,b=[typed(seed,**fields) for seed in (before,after)]
        assert regs(a)==regs(b),fields
        assert tuple(map(bytes,a.ram))==tuple(map(bytes,b.ram)),fields
        assert bytes(a[:0x800])==bytes(b[:0x800]),fields
        excluded.append(fields)
    rows=[]
    for state in (0,2):
        m=typed(after)
        # Common source cold alone does not parse a native scene or initialize
        # its gravity tables. Execute the genuine header constructor first;
        # this directed native ABI scene declares ordinary flat ground.
        B.terrain(m,lambda col,y:0x54 if y>=208 else 0)
        N.put(m,GameTimerSetting=1,FetchNewGameTimerFlag=1,ScreenLeft_PageLoc=0)
        N.invoke(m,'Entrance_GameTimerSetupCore',a=85,x=0,y=0,p=0x61)
        assert N.get(m,'GameEngineSubroutine')==7 and N.get(m,'VerticalForceDown')==40
        N.put(m,Player_Y_Position=48,Player_State=state,Player_Y_Speed=2,Player_Y_MoveForce=88)
        initial_hp=m.ram[2][0x6cf]
        for tick in range(48):
            regs(m)
            row=dict(tick=tick,engine=N.get(m,'GameEngineSubroutine'),y=N.get(m,'Player_Y_Position'),
                state=N.get(m,'Player_State'),speed=N.get(m,'Player_Y_Speed'),
                fraction=N.get(m,'Player_Y_MoveForce'),hp=m.ram[2][0x6cf],
                fall_count=m.ram[2][0x6c6],phase=m.ram[2][0xa6])
            if tick<2 or row['engine']==8:rows.append(dict(initial_state=state,**row))
            assert row['hp']==initial_hp and row['fall_count']==0 and row['phase']==0,row
            if row['engine']==8:
                assert row['y']==176 and row['state']==0 and row['speed']==0 and row['fraction']==0,row
                break
        else:raise AssertionError(('Typed native entrance landing bound',rows))
    print(json.dumps(dict(event='ordinary_native_ground',rows=rows)),flush=True)
    cuts=None
    if interrupts:
        m=typed(after)
        cuts=B.Async.stress('native Prince ordinary entrance post-call floor handoff',m,regs,
            [(129,E.HOOK,E.HOOK+11),(129,E.PROFILE,E.PROFILE+41)])
    return dict(passed=True,actual_cold=[old_cold,new_cold],all_foreign_character_IDs=count,
        unchanged_exclusions=excluded,ordinary_Prince_rows=rows,interrupts=cuts,
        scope='Directed native entrance controls/coordinates and flat native terrain after actual common cold and native header construction; not a natural stage route. No source health/weapon/physics/outcome seeds.',outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--matrix',action='store_true')
    p.add_argument('--interrupts',action='store_true')
    p.add_argument('--landing-isr-only',action='store_true')
    args=p.parse_args()
    raw=E.frozen_parent()
    if args.landing_isr_only:
        out=dict(landing_ISR=landing_isr(raw))
    else:
        out=dict(compiled=compiled_semantics(raw),headers=headers(raw),dispatcher=E.dispatcher_abi(raw))
        print(json.dumps(dict(event='finite',**out)),flush=True)
        if args.matrix or args.interrupts:
            out['matrix']=entry_matrix(raw,interrupts=args.interrupts)
    out['receipt_SHA256']=sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(out,sort_keys=True),flush=True)
