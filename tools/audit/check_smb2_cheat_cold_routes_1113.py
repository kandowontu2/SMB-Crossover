"""Run exact readonly Lua on real cold/Main/NMI; source only, zero outputs."""
from collections import defaultdict
from hashlib import sha256
import argparse
import json
import time
from unittest.mock import patch

import replay_smb2_cheat_cold_regress_1113 as Ordinary
import replay_smb2_invincible_contact_1113 as Contact
import check_smb2_flag_handoff_1113 as Flag
import check_bub_current_budget_1113 as Frames

C=Ordinary.C
W,N=C.W,C.N


def image(*,input_kind='postbg12397'):
    import current_smb2_cheat_input_1114 as Current
    public=Current.normalize(C.Owner.D.C.Owner.NIGHTLY.read_bytes(),kind=input_kind).postbg
    parent,_=C.Owner.proposal(public)
    return C.proposal(parent)[0]


def cold(raw,contact):
    if not contact:return Flag.cold(raw,1)
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(3):W.UI.key(m,4)
    W.UI.key(m,32)
    assert N.get(m,'SelectedCharacter')==25 and N.get(m,'S2Variant')==1
    # Explicit source frontend unit, before actual Start/constructor: actual
    # CheatsMenuInput changes its flag via UI input mailboxes. No direct flag,
    # health, actor, position or ability seed. Native9f already proved real UI.
    C.Owner.D.menu_mask(m,1)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,k)for k in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'S2Ready')==178 and N.get(m,'S2Health')==31
            assert N.get(m,'CheatInvincible')==1 and N.get(m,'NumberofLives')==2
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual source Inv1 menu-call/Start/constructor bound')


def run_controller(raw,mode='contact',limit=6000):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    assert mode in('contact','ordinary')and 1<=limit<=6000
    began=time.perf_counter();contact=mode=='contact';m=cold(raw,contact)
    factory=Contact if contact else Ordinary
    text=factory.controller(raw)
    assert sha256(text.encode()).hexdigest()==factory.LUA_SHA
    lua=Contact.Full.Previous.C.D.C.Owner.Terrain.Frozen.Flag.Root.Base.LuaRuntime(unpack_returned_tuples=True)
    callbacks=defaultdict(list);writes=defaultdict(list);events=defaultdict(list)
    ctx=dict(cpu=None,instruction_pc=0,status=None,receipt=None,cycles=0)
    pads=set();minimum=31;api=lua.table()
    api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return m.vram[at&0x3fff]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def cpu_state():
        c=ctx['cpu'];s={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        s['cpu.pc']=ctx['instruction_pc']
        s['cpu.ps']=s['cpu.p'];s['cpu.cycleCount']=ctx['cycles']
        # This driver counts executed CPU instructions/cycles. It does not
        # invent physical video/APU elapsed time or DMC bytesRemaining.
        return lua.table_from(s)
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),
            ('start',16),('select',32),('b',64),('a',128))if pad[name])
        pads.add(m.controller_pad)
    def memory(fn,kind,lo,hi=None):
        assert kind in(0,1),'Source replay accepts exec and readonly write observers only'
        target=callbacks if kind==0 else writes
        for at in range(lo,lo+1 if hi is None else hi+1):target[at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read,api.convertAddress,api.getState,api.setInput=read,mapped,cpu_state,set_input
    api.addMemoryCallback=memory;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text)
    class ObservedBus(type(m)):
        def __setitem__(self,at,value):
            if isinstance(at,int):
                for fn in tuple(writes.get(at,())):fn(at,value)
            return super().__setitem__(at,value)
    m.__class__=ObservedBus
    native=N.NesMPU
    class Observed(native):
        def step(self):
            ctx['cpu']=self;ctx['instruction_pc']=self.pc
            for fn in tuple(callbacks.get(self.pc,())):fn()
            before=self.processorCycles;result=super().step()
            ctx['cycles']+=self.processorCycles-before
            return result
    with patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            assert N.get(m,'CheatInvincible')==(1 if contact else 0)
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            minimum=min(minimum,N.get(m,'S2Health'))
            if ctx['status']is not None:break
            if tick%750==749:print(json.dumps(dict(progress_mode=mode,Main=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))),flush=True)
    receipt=ctx['receipt']or{}
    terminal={n:N.get(m,n)for n in('S2Health','CheatInvincible','StarInvincibleTimer','NumberofLives',
                                 'GameEngineSubroutine','WorldNumber','LevelNumber','Player_Y_Position')}
    terminal['x']=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    return dict(passed=ctx['status']==0,mode=mode,ROM_SHA256=C.CANDIDATE,
        controller_SHA256=sha256(text.encode()).hexdigest(),source_scheduler_passes=tick+1,
        seconds=round(time.perf_counter()-began,2),reason=receipt.get('reason'),terminal=terminal,
        minimum_observed_source_health=minimum,controller_pad_values=sorted(pads),receipt=receipt,
        actual_menu_Start_constructor_and_Main_NMI=True,
        source_frontend='compiled cheat-menu-call unit before Start'if contact else'established actual cold native menu arena',
        actual_title_options_UI_authority='root fa66/9f69 native b53258a1'if contact else'original frozen no-cheat native factory',
        physical_APU_video_timing_claim=False,
        embedded_receipt_frame_units='source scheduler passes, never physical video frames',
        actor_position_health_ability_or_direct_flag_seeds=0,
        Mesen_run=False,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('ordinary','contact'),default='contact')
    p.add_argument('--input-kind',choices=('postbg12397','cheat-fa66'),default='postbg12397')
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--limit',type=int,default=6000);args=p.parse_args()
    raw=image(input_kind=args.input_kind)
    q=(Contact if args.mode=='contact'else Ordinary).metadata(raw)if args.metadata else run_controller(raw,args.mode,args.limit)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Stated readonly source controller must pass its exact scope'
