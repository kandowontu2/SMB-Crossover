"""Actual16a lifecycle/foreign cold and explicit invalid-cookie components."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_body_transition_candidate_1115 as Candidate
import check_prince_window567_lifecycle_1114 as Previous

C,N,W,Frames=Candidate.C,Candidate.N,Candidate.W,Candidate.Frames


def farcall(m,bank,target):
    """Existing native FarCallCommon, not a mounted test stub."""
    b=m.bundle;m[W.address(b,'SafecallA_SMC')+1]=83
    at=W.address(b,'FarcallJmpTarget_SMC');m[at+1]=target&255;m[at+2]=target>>8
    c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=bank,71,109,0x21,224
    c.stPushWord(0x5aff)
    for _ in range(4000000):
        if c.pc==0x5b00:break
        assert m[c.pc],('Native component BRK',hex(c.pc));c.step()
    else:raise AssertionError('Native component return bound')
    assert c.sp==224
    return[c.a,c.x,c.y,c.p,c.sp]


def idle(m,count,*,cold=False):
    for _ in range(count):m.controller_pad=0;Frames.frame(m,cold=cold,whole_pass=True)
    N.invoke(m,'X5PublishChr',a=0,x=0,y=0)


def native_world(m):
    q=Previous.snapshot(m);assert q['mode'][1:5]==[0]*4 and q['latches'][1:5]==[16,17,18,19]
    return q


def alternate(raw,cycles):
    bundle=dict(W.Symbols.bundle(),raw=raw);prior=N.Bus;N.Bus=W.ControllerBus
    try:m=W.UI.seed(bundle,29)
    finally:N.Bus=prior
    for _ in range(cycles):W.UI.key(m,32)
    assert N.get(m,'SelectedCharacter')==37
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,k)for k in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True,whole_pass=True)
    else:raise AssertionError('Compiled alternate cold bound')
    idle(m,8);return m,dict(compiled_Select_cycles=cycles,Main_parser=tick,**Previous.snapshot(m))


def run(parent):
    raw,info=C.proposal(parent);m,opening=Candidate.cold(raw);idle(m,8);initial=native_world(m)
    same=N.fork(m);N.invoke(same,'LoadAreaPointer',a=0,x=0,y=0);idle(same,8);area=native_world(same)
    death=N.fork(m);N.invoke(death,'KillPlayer',a=0,x=0,y=0);death_entry=Previous.snapshot(death);lives=N.get(death,'NumberofLives')
    for tick in range(480):
        idle(death,1,cold=True)
        if N.get(death,'NumberofLives')<lives and N.get(death,'GameEngineSubroutine')==8:break
    death_end=native_world(death);assert death_end['lives']==lives-1 and death_end['engine']==8
    foreign=[]
    for cycles in(0,2):
        a,old=alternate(parent,cycles);b,new=alternate(raw,cycles)
        assert old==new and a.ram==b.ram,'Foreign compiled cold/private state changed'
        assert bytes(a[:0x800])==bytes(b[:0x800])and a.rawtags==b.rawtags and a.chr_latches==b.chr_latches,'Foreign native cold state changed'
        foreign.append(dict(**new,all_private_native_RAM_mapper_and_CHR_exact590=True))
    # Explicit corruption and foreign-selector component units. These are
    # not ordinary gameplay or natural death/character-switch episodes.
    bank=193;table=0xb08c;physical=16+(bank&127)*8192+(table&8191)
    assert raw[physical:physical+111]==parent[physical:physical+111]and raw[physical]==0x4c
    # Authenticate the current core through its exact owning bytes and a
    # literal caller in the published A740 router. Do not use an inactive
    # callback row's C0 as evidence that its cookie check actually ran.
    core=0xaee2;core_at=16+65*8192+(core&8191)
    assert raw[core_at:core_at+9]==bytes.fromhex('ad026038e925c907b0')
    router=raw[16+65*8192+0x740:16+65*8192+0x7e4]
    assert bytes.fromhex('20e2ae')in router
    positive=N.fork(m);before=[bytes(row)for row in positive.ram];valid_regs=farcall(positive,bank,core)
    assert valid_regs[3]&1 and before==[bytes(row)for row in positive.ram],'Valid current headers must pass exact core first'
    rejected=[]
    for ram_bank in(2,3):
        for index in range(16):
            clone=N.fork(m);clone.ram[ram_bank][0x1fe0+index]^=1;before=[bytes(row)for row in clone.ram]
            regs=farcall(clone,bank,core)
            assert not regs[3]&1 and before==[bytes(row)for row in clone.ram],('Bad cookie entered private callback',ram_bank,index)
            rejected.append([ram_bank,index])
    # The current published row19 JMPs to B100, whose actual JSR enters
    # AE0A. Old AE0B skips PHP after a historical one-byte compaction.
    retirement=table+3*19;at=16+65*8192+(retirement&8191)
    assert raw[at:at+3]==bytes.fromhex('4c00b1')
    assert raw[16+65*8192+0x1100:16+65*8192+0x1105]==bytes.fromhex('200aae3860')
    retired=N.fork(m);N.put(retired,SelectedCharacter=0);retire_regs=farcall(retired,193,retirement)
    assert retire_regs[3]&1 and retire_regs[:3]==[83,71,109]
    assert retired.ram[2][0x1fe0]==retired.ram[3][0x1fe0]==0 and retired.ram[2][0xaa]==retired.ram[2][0xab]==0
    q=dict(passed=True,composition=info,opening=opening,actual_cold_world=initial,same_area_LoadAreaPointer=area,
        explicit_compiled_death_entry=death_entry,explicit_compiled_death_respawn=death_end,death_Main=tick+1,
        compiled_foreign_Select_cycles=foreign,bad_header_component_cases=len(rejected),both16byte_headers_rejected=True,
        valid_header_positive_control=True,actual_header_core=core,current_header_core_caller='Published A740 router JSR AEE2',
        explicit_foreign_selector_retirement=True,native_public_callback_table_exact590=True,
        current_retirement_path=[retirement,0xb100,0xae0a],old_AE0B_failure_retained=True,
        actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),source_array_mounts=0,
        scope='Actual16a compiled cold/same-area/death/Select units; corruption and selector-retirement are explicit components, not natural gameplay',
        native_cadence_qualified=False,full_stage_qualified=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Lifecycle source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
