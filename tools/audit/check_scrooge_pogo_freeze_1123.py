"""Exact3af Scrooge natural-input far-call diagnostic; stdout, no outputs."""
import argparse,json
from collections import Counter,deque
from pathlib import Path
from unittest.mock import patch

import run_simon_ryu_stock_1123 as Stock
import inspect_rogue_missile_targets_cb95_1116 as Engine
import check_contra_force_fixed_layout_1122 as Layout

W,N,H,ROM=Stock.W,Stock.N,Stock.H,Stock.ROM
PIN='3af597a72c3ef048085de0a01e5f53443b8aa8ddf0a92d6e1882c2d225dccd1c'
NAMES=('ScroogeWeapons','ScroogeWeapons::PogoHit','ScroogeWeapons::Bridge',
       'MegaManWeapons::Blocks','MegaManWeapons::BombPoint','MegaManWeapons::Activate',
       'PlayerHeadCollision','NativeRarePlayerHeadCollision','NativeRarePlayerHeadCollisionCore',
       'CrossoverBlockSize','CrossoverSmallHeadCold','BumpBlock','BlockCode',
       'SetupPowerUp','PowerUpObjHandler','GuestClaimBlockSlot','DestroyBlockMetatile',
       'ScroogeMovement::Bounce','FarCallCommon','FarcallJmpTarget_SMC','IdleLoop','GameLoop')
NAMES+=('InventoryPreparePickup','InventorySupported','ThInventorySupported','RlSupportedDispatch',
        'LmSupportedGate','Cv3SupportedGate','Z2InventorySupportedGate')


class DiagnosticStop(Exception):pass


def cold(raw):
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    W.UI.key(m,4)
    assert W.UI.menu_name(m)[0]=='SCROOGE MCDUCK'
    assert N.get(m,'SelectedCharacter')==12 and N.get(m,'DarkwingVariant')==0
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine']
    m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Scrooge cold bound')


class Trace:
    def __init__(self,capture_support=False):
        self.enabled=False;self.m=None;self.calls=deque(maxlen=90);self.active=[]
        self.min_sp=255;self.counts=Counter();self.main=0;self.instructions=0
        self.names={};self.points={}
        self.capture_support=capture_support;self.cut=None;self.base=N.NesMPU

    def bind(self,m):
        self.m=m;self.b=m.bundle
        self.common=W.address(self.b,'FarCallCommon')
        self.jump=W.address(self.b,'FarcallJmpTarget_SMC')
        self.loop=W.address(self.b,'GameLoop')
        for name,s in self.b['syms'].items():
            if s.get('type')!='lab' or 'seg'not in s:continue
            try:pc,at=W.address(self.b,name),W.location(self.b,name)
            except (KeyError,ValueError):continue
            if pc>=0x8000 and at>=16:self.names.setdefault(((at-16)//8192)|128,{})[pc]=name
        for name in NAMES:
            if name not in self.b['syms']:continue
            pc=W.address(self.b,name)
            if pc>=0x8000:self.points[((W.location(self.b,name)-16)//8192)|128,pc]=name
        self.enabled=True

    def point(self,pc):
        return(self.m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1,pc)

    def label(self,tag,pc):
        table=self.names.get(tag,{})
        before=[p for p in table if p<=pc]
        p=max(before)if before else None
        return f'{tag:02X}:{pc:04X}'+(' '+table[p]+f'+{pc-p:X}'if p is not None else'')

    def observe(self,c):
        if not self.enabled:return
        m=self.m;pc=c.pc;point=self.point(pc);self.instructions+=1
        self.min_sp=min(self.min_sp,c.sp)
        while self.active and(pc,c.sp,point[0])==self.active[-1]['stop']:self.active.pop()
        if pc==self.loop and point[0]==254:self.main+=1
        name=self.points.get(point)
        if name:self.counts[name]+=1
        if self.capture_support and name=='InventorySupported'and c.sp<0xa0:
            z=self.base(memory=N.fork(m),pc=c.pc)
            z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
            self.cut=z
            raise DiagnosticStop('Captured actual deep InventorySupported before its stack pushes')
        if pc==self.common:
            dst=m[self.jump+1]+256*m[self.jump+2]
            ret=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
            q=dict(main=self.main,sp=c.sp,bank=c.a,target=dst,
                   target_name=self.label(c.a,dst),return_=self.label(*self.point(ret)),
                   current=N.get(m,'CurrentBank'),c_bank=N.get(m,'CurrentBankC'),
                   stop=(ret,(c.sp+2)&255,self.point(ret)[0]))
            self.calls.append(q);self.active.append(q)
        if c.sp<=(0x70 if self.capture_support else 0x88):
            raise DiagnosticStop(('Stack reached guarded floor before RAM far-call code',hex(pc),c.sp))
        if self.instructions>35_000_000:raise DiagnosticStop('Bounded diagnostic instructions')

    def result(self,reason):
        m=self.m
        fields=('SelectedCharacter','DarkwingVariant','GameEngineSubroutine','Player_X_Position',
                'Player_PageLoc','Player_Y_Position','Player_State','PlayerStatus','ScPogo','ScAttack',
                'ScPrevious','MmVY','MmBulletType','MmBlockAttack','MmProbeIndex','MmProbeX',
                'MmProbeY','MmProbePage','CurrentBank','CurrentBankC','NmiDisable','NmiSkipped',
                'SprDataOffset_Ctrl','R2','R3','R6','R7','Block_State','NumberofLives')
        return dict(reason=reason,main_entries=self.main,minimum_SP=self.min_sp,
                    instructions=self.instructions,counts=dict(self.counts),
                    state={n:N.get(m,n)for n in fields},active=self.active,tail=list(self.calls),
                    actors=[{n:N.get(m,n,i)for n in('Enemy_Flag','Enemy_ID','PowerUpType',
                        'Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position')}for i in range(6)],
                    smc=bytes(m[0x15a:0x17c]).hex(),stack=bytes(m[0x100:0x200]).hex())


def inspect(raw):
    assert H(raw)==PIN;b=dict(W.Symbols.bundle(),raw=raw);out={}
    for name in NAMES:
        if name not in b['syms']:continue
        pc=W.address(b,name)
        if pc<0x8000:out[name]=dict(pc=pc);continue
        at=W.location(b,name);out[name]=dict(pc=pc,bank=(at-16)//8192,offset=at,hex=raw[at:at+24].hex())
    return out


def run(raw,limit=1600,*,pursue_mushroom=False,capture=None):
    assert H(raw)==PIN
    program=Stock.controller(raw,'scrooge','star').decode();program=program.replace(
        "assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha", "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",1)
    if pursue_mushroom:
        a='if C.char==5 then\n   local food=followFirstFood(c)'
        assert program.count(a)==1
        program=program.replace(a,'if C.char==5 or C.char==12 then\n   local food=followFirstFood(c)',1)
    trace=Trace(capture is not None);base=N.NesMPU
    class CPU(base):
        def step(self):trace.observe(self);return super().step()
    def enter(image):
        m=cold(image);trace.bind(m);return m
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(Engine.J,'cold',enter),patch.object(Engine.J,'PIN',PIN):
            result=Engine.run(raw,limit,text=program)
    except (DiagnosticStop,AssertionError)as e:
        if capture is not None and trace.cut is not None:capture.append(trace.cut)
        return dict(diagnostic=True,ROM_SHA256=PIN,controller_SHA256=H(program.encode()),
                    result=trace.result(str(e)),outputs=0,native=False)
    return dict(diagnostic=True,ROM_SHA256=PIN,controller_SHA256=H(program.encode()),
                result=trace.result('Replay returned'),replay=result,outputs=0,native=False)


def support_probe(raw):
    """Reject/qualify one-byte lead; never a production composer or native grant."""
    captured=[];reproduction=run(raw,1400,pursue_mushroom=True,capture=captured)
    assert len(captured)==1,reproduction
    original=captured[0];bundle=original.memory.bundle
    at=W.location(bundle,'InventorySupported')+8
    assert raw[at-1:at+3]==bytes.fromhex('e00d900d')
    changed=bytearray(raw);changed[at]=12;candidate=bytes(changed)
    assert [i for i,(a,b)in enumerate(zip(raw,candidate))if a!=b]==[at]
    def clone(c,image):
        m=N.fork(c.memory);m.bundle=dict(m.bundle,raw=image)
        for window,tag in enumerate(tuple(m.rawtags)):
            if tag&128:m.raw_page(window,tag)
        z=N.NesMPU(memory=m,pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z
    dynamic={0x162,0x16a,0x16c,0x16d,0x179}
    fixed=lambda m:bytes(m[i]for i in range(0x15a,0x17b)if i not in dynamic)
    def finish(c,stop,watch=None):
        before=fixed(c.memory);low=c.sp
        for _ in range(150000):
            low=min(low,c.sp)
            if fixed(c.memory)!=before:
                raise DiagnosticStop(('Actual ISR overwrote fixed RAM far-call opcode',hex(c.pc),c.sp,low))
            if(c.pc,c.sp)==stop:return low
            if watch:watch(c)
            assert c.memory[c.pc],('Linked BRK',hex(c.pc),c.sp)
            c.step()
        raise DiagnosticStop(('Actual ISR/return bound',hex(c.pc),c.sp,low))
    def state(m):
        return(bytes(m[:0x100]),bytes(m[0x100:0x15a]),bytes(m[0x200:0x800]),
               bytes(m[0x5c00:0x8000]),tuple(map(bytes,m.ram)),tuple(m.rawtags),tuple(m.chr_latches))
    abi=0
    # Hardware P has its unused bit5 set. Break is masked as synthetic.
    pairs=[clone(original,image)for image in(raw,candidate)]
    for p in range(256):
        if not p&32:continue
        for a,x,y in((0,0,0),(85,7,91),(252,5,255),(255,255,255)):
            out=[]
            for c in pairs:
                c.pc=original.pc;c.sp=224;c.a,c.x,c.y,c.p=a,x,y,p;c.stPushWord(0x5aff)
                finish(c,(0x5b00,224));out.append((c.a,c.x,c.y,c.p&0xef,c.sp,state(c.memory)))
            assert out[0]==out[1],('Current Scrooge query ABI',a,x,y,p)
            abi+=1
    c=clone(original,candidate);ret=(c.memory[0x101+c.sp]+256*c.memory[0x102+c.sp]+1)&65535
    cuts=[];lowest=256
    def watch(z):
        nonlocal lowest
        if z.sp<lowest:lowest=z.sp;cuts.append(clone(z,candidate))
    foreground_min=finish(c,(ret,c.sp+2),watch)
    deepest=cuts[-1];interrupts={}
    for kind in('IRQ','busyNMI'):
        z=clone(deepest,candidate);before=(z.pc,z.sp);regs=(z.a,z.x,z.y,z.p&0xef,z.sp)
        assert N.get(z.memory,'NmiDisable')==255
        if kind=='IRQ'and z.p&4:
            interrupts[kind]=dict(eligible=False);continue
        try:
            z.irq()if kind=='IRQ'else z.nmi()
            low=finish(z,before)
            assert(z.a,z.x,z.y,z.p&0xef,z.sp)==regs
            interrupts[kind]=dict(passed=True,minimum_SP=low)
        except(DiagnosticStop,AssertionError)as e:
            interrupts[kind]=dict(passed=False,reason=str(e),pc=z.pc,sp=z.sp)
    return dict(diagnostic=True,ROM_SHA256=PIN,candidate_SHA256=H(candidate),
                changed_file_offset=at,old=13,new=12,exact_query_ABI_cases=abi,
                deep_entry_SP=original.sp,foreground_query_minimum_SP=foreground_min,
                interrupts=interrupts,promoted=False,
                reproduction=dict(main=reproduction['result']['main_entries'],
                    controller_SHA256=reproduction['controller_SHA256']),outputs=0,native=False)


def parent(raw):
    if H(raw)==PIN:return raw
    import compose_dkjr_head_bridge_current_1123 as Bridge
    assert H(raw)==Bridge.CANDIDATE
    old=Bridge.inverse(raw);assert H(old)==PIN
    return old


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-source',action='store_true')
    p.add_argument('--pursue-mushroom',action='store_true')
    p.add_argument('--support-probe',action='store_true')
    p.add_argument('--limit',type=int,default=1600);a=p.parse_args();assert 800<=a.limit<=2200
    installed=ROM.read_bytes();raw=parent(installed)
    def deny(*a,**k):raise AssertionError('Source diagnostic attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=support_probe(raw)if a.support_probe else run(raw,a.limit,pursue_mushroom=a.pursue_mushroom)if a.run_source else inspect(raw)
    q=dict(installed_SHA256=H(installed),tested_parent_SHA256=PIN,result=q)
    print('SCROOGE_FREEZE_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
