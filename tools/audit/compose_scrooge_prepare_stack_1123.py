"""Short native 1-UP prepare path for Scrooge on exact06336; memory only.

Three existing adjacent47-byte Roll dispatch envelopes fund the short path.
Public entries, the original six fallback targets and all item actors stay
native. No PRG/CHR growth, scratch allocation, ROM file or emulator API.
"""
import argparse,json
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import check_scrooge_pogo_freeze_1123 as D
import compose_dkjr_head_bridge_current_1123 as Bridge
import compose_dkjr_side_epoch_fast_1123 as Fast

W,N,H,ROM=D.W,D.N,D.H,D.ROM
PIN=Bridge.CANDIDATE
CANDIDATE='82e8da0e293dee91da441347dfe4c675c88708c43b0b88d4fbd253312f00a131'
CONTROLLER_SHA256='06850f0ab745d52e342ffdd8edb993d1db77cd785fdbe23cd98d78749976102e'
LAYOUT=dict(PREPARE=(0xba1d,47),COLLECT=(0xba4c,47),NAME=(0xba7b,47))
TARGETS=((93,0xab99),(79,0xae04),(93,0xabed),(79,0xae17),(93,0xa439),(79,0xaf3f))
SOURCE=r'''
.segment "PREPARE"
Prepare:
 php
 pha
 txa
 pha
 ldx #0
 jmp Dispatch
Dispatch:
 jsr $b808
 bcc NotRoll
 inx
 bne Chosen
NotRoll:
 cpx #0
 bne Chosen
 lda $6002
 cmp #12
 bne Chosen
 lda $73df
 bne Chosen
 pla
 tax
 lda $34,x
 cmp #3
 bne RePush
 jmp ScroogeLife
 .byte $ea,$ea,$ea
.segment "COLLECT"
Collect:
 php
 pha
 txa
 pha
 ldx #2
 jmp Dispatch
ScroogeLife:
 stx $7d91
 lda #0
 sta $7d68,x
 lda #$fc
 sta $7d62,x
 pla
 plp
 lda #12
 clc
 rts
RePush:
 txa
 pha
 ldx #0
 beq Chosen
Low:
 .byte $99,$04,$ed,$17,$39,$3f
High:
 .byte $ab,$ae,$ab,$ae,$a4,$af
 .byte $ea
.segment "NAME"
Name:
 php
 pha
 txa
 pha
 ldx #4
 jmp Dispatch
Chosen:
 lda Low,x
 sta $016c
 lda High,x
 sta $016d
 lda Banks,x
 sta $0162
 pla
 tax
 pla
 sta $016a
 plp
 jmp $015d
Banks:
 .byte $dd,$cf,$dd,$cf,$dd,$cf
 .byte $ea,$ea,$ea,$ea
'''


def offset(pc):return 16+78*8192+(pc&8191)


def old_gate(low,high,bank):
    return bytes.fromhex('8d6a01a9')+bytes((low,))+bytes.fromhex('8d6c01a9')+bytes((high,))+bytes.fromhex('8d6d01a9')+bytes((bank|128,))+bytes.fromhex('4c5a01')


@lru_cache(maxsize=1)
def program():
    p=Fast.M.assemble(SOURCE,LAYOUT)
    assert p['used']==dict(PREPARE=47,COLLECT=47,NAME=47),p['used']
    for n,(pc,_)in LAYOUT.items():assert p['symbols'][n.title()]==pc
    return p


def proposal(raw):
    assert H(raw)==PIN and len(raw)==2097168
    parent=Bridge.inverse(raw);assert H(parent)==D.PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    for n,a in dict(InvObject=0x7d91,InvRisePhase=0x7d68,InvPickup=0x7d62,
                    PowerUpType=0x34,DarkwingVariant=0x73df,SelectedCharacter=0x6002,RlIsActive=0xb808).items():
        assert W.address(b,n)==a,n
    symbols=('RlPrepareDispatch','RlCollectDispatch','RlNameDispatch')
    for name,(pc,_)in zip(symbols,LAYOUT.values()):assert W.address(b,name)==pc
    out=bytearray(raw);p=program();preimages={}
    for i,(name,(pc,size))in enumerate(LAYOUT.items()):
        expected=bytes.fromhex('08482008b8b0146828')+old_gate(TARGETS[i*2][1]&255,TARGETS[i*2][1]>>8,TARGETS[i*2][0])+bytes.fromhex('6828')+old_gate(TARGETS[i*2+1][1]&255,TARGETS[i*2+1][1]>>8,TARGETS[i*2+1][0])
        assert len(expected)==size==47
        at=offset(pc);assert raw[at:at+size]==parent[at:at+size]==expected,name
        preimages[name]=expected.hex();out[at:at+size]=p['images'][name]
    candidate=bytes(out);changed=[i for i,(a,b)in enumerate(zip(raw,candidate))if a!=b]
    assert H(candidate)==CANDIDATE
    assert changed and all(offset(0xba1d)<=i<offset(0xbaaa)for i in changed)
    assert candidate[:offset(0xba1d)]==raw[:offset(0xba1d)]and candidate[offset(0xbaaa):]==raw[offset(0xbaaa):]
    q=dict(parent_SHA256=PIN,candidate_SHA256=H(candidate),same_length=True,changed_bytes=len(changed),
           file_extent=[offset(0xba1d),offset(0xbaaa)],PRG_bank=78,public_entries=symbols,
           public_PCs=[pc for pc,_ in LAYOUT.values()],used=p['used'],
           old_preimages=preimages,source_SHA256=H(SOURCE.encode()),outputs=0,Mesen=False)
    return candidate,q


def inverse(raw):
    assert len(raw)==2097168
    out=bytearray(raw)
    p=program()
    for i,(name,(pc,size))in enumerate(LAYOUT.items()):
        at=offset(pc);assert raw[at:at+size]==p['images'][name]
        out[at:at+size]=bytes.fromhex('08482008b8b0146828')+old_gate(TARGETS[i*2][1]&255,TARGETS[i*2][1]>>8,TARGETS[i*2][0])+bytes.fromhex('6828')+old_gate(TARGETS[i*2+1][1]&255,TARGETS[i*2+1][1]>>8,TARGETS[i*2+1][0])
    result=bytes(out);assert H(result)==PIN
    return result


def model_state(m):
    return(bytes(m[:0x100]),bytes(m[0x100:0x15a]),bytes(m[0x200:0x800]),
           bytes(m[0x5c00:0x8000]),tuple(map(bytes,m.ram)),tuple(m.rawtags),tuple(m.chr_latches))


def rebind(m,raw):
    z=N.fork(m);z.bundle=dict(z.bundle,raw=raw)
    for window,tag in enumerate(tuple(z.rawtags)):
        if tag&128:z.raw_page(window,tag)
    return z


def functional(raw):
    candidate,receipt=proposal(raw);base=D.cold(raw)
    machines=[rebind(base,image)for image in(raw,candidate)]
    count=0;minimum=[255,255]
    # Native actor defaults and deliberately stale item metadata. The short
    # path must perform the real three writes, without changing owner/type.
    for variant in(0,1):
        for kind in((3,)if variant==0 else(0,1,2,3)):
            for slot in range(6):
                for p in(range(32,256)if variant==0 else(0x21,0x61,0xa1,0xe5)):
                    if not p&32:continue
                    out=[]
                    for i,m in enumerate(machines):
                        N.put(m,SelectedCharacter=12,DarkwingVariant=variant,PlayerStatus=1,
                              InvObject=0xa6,DwHealth=4,DwAdaptor=0)
                        for n,v in dict(PowerUpType=kind,Enemy_Flag=1,Enemy_ID=46,Enemy_State=1,
                                        InvRisePhase=0x35,InvPickup=0x12,InvPickupOwner=0x84,
                                        InvPickupSaveLo=0x10,InvPickupSaveHi=0x20).items():
                            m[W.address(m.bundle,n)+slot]=v
                        W.clear_logs(m)
                        q=N.invoke(m,'RlPrepareDispatch',a=p^85,x=slot,y=p^170,p=p)
                        minimum[i]=min(minimum[i],q['minimum_SP'])
                        out.append((q['A'],q['X'],q['Y'],q['P']&0xef,model_state(m)))
                    assert out[0]==out[1],('Native prepare state/AXYP',variant,kind,slot,p)
                    count+=1
    # All three ordinary fallback entries reach the same original target
    # with the same live stack, input registers, mapper and transport image.
    def target(m,entry,a,x,y,p):
        pc=W.address(m.bundle,entry)
        m[0x16a]=a;m[0x16c]=pc&255;m[0x16d]=pc>>8
        c=N.NesMPU(memory=m,pc=0x15a);c.a=206;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
        for _ in range(300):
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            if(tag&127,c.pc)in TARGETS:
                return(c.a,c.x,c.y,c.p&0xef,c.sp,bytes(m[0x101+c.sp:0x200]),
                       bytes(m[0x15a:0x17b]),model_state(m))
            assert c.pc!=0x5b00,('Unexpected short path',entry,N.get(m,'SelectedCharacter'))
            c.step()
        raise AssertionError('Fallback target bound')
    fallbacks=0
    for entry in('RlPrepareDispatch','RlCollectDispatch','RlNameDispatch'):
        for owner in range(44):
            for roll in(0,1):
                for variant in(0,1):
                    if entry=='RlPrepareDispatch'and owner==12 and variant==0:continue
                    for m in machines:
                        N.put(m,SelectedCharacter=owner,RlVariant=roll,DarkwingVariant=variant)
                    a=target(machines[0],entry,85,5,91,0xe1)
                    b=target(machines[1],entry,85,5,91,0xe1)
                    assert a==b,('Original fallback target/ABI',entry,owner,roll,variant)
                    fallbacks+=1
    receipt.update(functional_passed=True,full_prepare_cases=count,fallback_target_cases=fallbacks,
                   standalone_prepare_minimum_SP=minimum,source_only=True)
    return receipt


def controller(candidate):
    """Root's native replay: genuine Mushroom, pogo 1-UP, native life +25."""
    raw=inverse(candidate);parent=Bridge.inverse(raw)
    cfg=D.Stock.bindings(parent,'scrooge','life')
    cfg=dict(cfg,sha=H(candidate),ram=dict(cfg['ram']))
    for n in('MmBlockAttack','MmBulletType','MmProbeX','MmProbeY','MmProbePage'):
        cfg['ram'][n]=W.address(dict(W.Symbols.bundle(),raw=candidate),n)
    for n,h in cfg['hooks'].items():
        at=16+h['offset'];assert candidate[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex']),n
    text=D.Stock.controller(parent,'scrooge','life').decode()
    text='local C='+D.Stock.value(cfg)+'\n'+text.split('\n',1)[1]
    edits=[("if C.char==5 then\n   local food=followFirstFood(c)",
            "if C.char==5 or C.char==12 then\n   local food=followFirstFood(c)"),
           ("if c.x<target-72 then return base(c)end", "if kind==3 or c.x<target-72 then return base(c)end"),
           ('local lifePending','local lifePending\nlocal pogoProof'),
           ('phase=ROBOT_STOCK_STATE or {},sound_cues=cues,controller_only=true',
            'phase=ROBOT_STOCK_STATE or {},pogo=pogoProof,sound_cues=cues,controller_only=true'),
           ("if name=='PlayerHeadCollision' then\n  local s=state()", """if name=='PlayerHeadCollision' then
  local s=state()
  if cpu['cpu.a']==96 and r('MmBlockAttack')==1 and r('ScPogo')==1
     and r('MmBulletType')==10 and r('MmProbePage')==4 and r('MmProbeX')<16 and r('MmProbeY')==128 then
   assert(r('MmVY',2)<128 and r('SavedJoypadBits')&68==68,'Real descending native pogo request')
   pogoProof={player=s,pad=r('SavedJoypadBits'),type=r('MmBulletType'),probeX=r('MmProbeX'),
              probePage=r('MmProbePage'),probeY=r('MmProbeY'),tile=cpu['cpu.a']}
  end"""),
           ("q.birth={actor=a,player=s}", "if a.kind==3 then assert(pogoProof,'Actual pogo reveals the authored1UP')end;q.birth={actor=a,player=s}")]
    for a,b in edits:
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1)
    D.Stock.LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    assert H(text.encode())==CONTROLLER_SHA256
    return text


def source_route(raw,limit=1800):
    from check_mini_funded_actor_1108_v3 import slim_fork
    candidate,receipt=proposal(raw);program_text=controller(candidate)
    program_text=program_text.replace("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",
        "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",1)
    base=N.NesMPU;trace=D.Trace();cuts={};gate=None
    def clone(c):
        z=base(memory=slim_fork(c.memory),pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z
    class CPU(base):
        def step(self):
            nonlocal gate
            if trace.enabled:
                trace.observe(self);m=self.memory
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
                if tag==206 and self.pc==0xba1d and N.get(m,'MmBlockAttack')==1 and N.get(m,'ScPogo')==1 and N.get(m,'PowerUpType',self.x)==3:
                    gate=(0x16e,self.sp+2)
                if gate and(self.pc,self.sp)==gate:gate=None
                if gate and(tag==206 and(0xba1d<=self.pc<0xbaaa or 0xb808<=self.pc<0xb815)):
                    if self.pc not in cuts or self.sp<cuts[self.pc].sp:cuts[self.pc]=clone(self)
            return super().step()
    def enter(image):
        m=D.cold(image);trace.bind(m);return m
    with patch.object(N,'NesMPU',CPU),patch.object(D.Engine.J,'cold',enter),patch.object(D.Engine.J,'PIN',H(candidate)):
        q=D.Engine.run(candidate,limit,text=program_text)
    print('SCROOGE_POGO_ROUTE '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],q
    assert q['receipt']['pogo']and len(cuts)>20
    receipt.update(route_passed=True,route_receipt_SHA256=q['receipt_SHA256'],
                   controller_SHA256=H(controller(candidate).encode()),source_passes=q['source_passes'],
                   pogo=q['receipt']['pogo'],life=q['receipt']['items']['3'],
                   terminal=q['receipt']['terminal'],Main_minimum_SP=trace.min_sp,
                   hot_prepare_minimum_SP=min(c.sp for c in cuts.values()))
    return receipt,cuts


def interrupts(cuts):
    from check_mini_funded_actor_1108_v3 import slim_fork
    def clone(c):
        z=N.NesMPU(memory=slim_fork(c.memory),pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z
    dynamic={0x162,0x16a,0x16c,0x16d,0x179}
    def fixed(m):return bytes(m[i]for i in range(0x15a,0x17b)if i not in dynamic)
    def regs(c):return(c.a,c.x,c.y,c.p&0xef,c.sp)
    def live(c):return bytes(c.memory[0x101+c.sp:0x200])
    def finish(c,stop,nested=None):
        old=fixed(c.memory);minimum=c.sp
        for _ in range(150000):
            minimum=min(minimum,c.sp)
            assert fixed(c.memory)==old,('Interrupt changed RAM call opcode',hex(c.pc),c.sp)
            if(c.pc,c.sp)==stop:return minimum
            if nested is not None and not c.p&4 and(not nested or c.sp<nested[0].sp):
                nested[:]=[clone(c)]
            assert c.memory[c.pc],('Interrupt BRK',hex(c.pc),c.sp)
            c.step()
        raise AssertionError(('Interrupt return bound',hex(c.pc),c.sp))
    def restore(c,stop,before,stack,smc,maps):
        assert(c.pc,c.sp)==stop and regs(c)==before and live(c)==stack
        assert bytes(c.memory[0x15a:0x17b])==smc
        assert(tuple(c.memory.rawtags),tuple(c.memory.chr_latches))==maps
    counts=dict(IRQ=0,busyNMI=0,nested_IRQ=0);minimum=dict(IRQ=255,busyNMI=255,nested_IRQ=255)
    for original in cuts.values():
        for kind in('IRQ','busyNMI'):
            if kind=='IRQ'and original.p&4:continue
            c=clone(original);stop=(c.pc,c.sp);before=regs(c);stack=live(c)
            smc=bytes(c.memory[0x15a:0x17b]);maps=(tuple(c.memory.rawtags),tuple(c.memory.chr_latches))
            assert N.get(c.memory,'NmiDisable')==255
            c.irq()if kind=='IRQ'else c.nmi()
            nested=[]if kind=='busyNMI'else None
            low=finish(c,stop,nested);restore(c,stop,before,stack,smc,maps)
            counts[kind]+=1;minimum[kind]=min(minimum[kind],low)
            if nested:
                n=clone(nested[0]);end=(n.pc,n.sp);nr=regs(n);ns=live(n)
                code=bytes(n.memory[0x15a:0x17b]);nm=(tuple(n.memory.rawtags),tuple(n.memory.chr_latches))
                n.irq();minimum['nested_IRQ']=min(minimum['nested_IRQ'],finish(n,end))
                restore(n,end,nr,ns,code,nm)
                finish(n,stop);restore(n,stop,before,stack,smc,maps)
                assert model_state(n.memory)==model_state(c.memory),('Nested IRQ continuation',original.pc)
                counts['nested_IRQ']+=1
    assert counts['IRQ']and counts['busyNMI']==len(cuts)and counts['nested_IRQ']==len(cuts)
    return dict(passed=True,hot_instruction_contexts=len(cuts),cases=counts,minimum_SP=minimum,
                exact_native_handlers=True,caller_AXYP_live_stack_SMC_maps_restored=True,
                nested_IRQ_at_deepest_eligible_busy_NMI_point=True)


def native_root(raw):
    """Root must stage candidate.nes first; only controller.lua is replaced."""
    candidate,_=proposal(raw);program_text=controller(candidate).encode()
    slot,script=D.Stock.OUT/'candidate.nes',D.Stock.OUT/'controller.lua'
    guard=D.Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(D.Stock.OUT.iterdir())=={slot,script}and slot.read_bytes()==candidate
    before=script.read_bytes()
    try:
        with D.Stock.preserve_script(script,slot,candidate)as stage:
            stage(program_text);q=D.Stock.run(script,slot,D.Stock.OUT/'capture',CANDIDATE,180)
        print('SCROOGE_POGO_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==CONTROLLER_SHA256 and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and slot.read_bytes()==candidate
        assert ROM.read_bytes()==raw and D.Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true')
    p.add_argument('--route-check',action='store_true');p.add_argument('--interrupt-check',action='store_true')
    p.add_argument('--run',action='store_true',help='Root only; requires an already staged private candidate')
    a=p.parse_args()
    if a.run:
        assert not(a.check or a.route_check or a.interrupt_check)
        return int(not native_root(ROM.read_bytes())['passed'])
    def deny(*a,**k):raise AssertionError('Source proposal attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw=ROM.read_bytes();candidate,q=proposal(raw);assert inverse(candidate)==raw
        if a.check:q=functional(raw)
        if a.route_check or a.interrupt_check:
            q,cuts=source_route(raw)
            if a.interrupt_check:q['interrupts']=interrupts(cuts)
    print('SCROOGE_PREPARE_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':raise SystemExit(main())
