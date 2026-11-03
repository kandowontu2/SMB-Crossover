"""Quantify full-auth native primitives with an explicitly unfunded test kernel.

The 57-byte kernel is injected only into CPU-fixture RAM5800, never a ROM.
That test address is not a host RAM lease or candidate placement proposal.
"""
import json
from pathlib import Path
import measure_bub_full_auth_helper_1103_v73 as F

O,R,N,Q,address,sha=F.O,F.R,F.N,F.Q,F.address,F.sha
TEST=0x5800


def build():
    old,auth,route,q,head,manifest,ol,nl,changes=F.build()
    source='''.setcpu "6502"
.segment "TEST_KERNEL"
.export NativePrimitives,NativeNormal,NativeSide,NativeSec,NativeEnd
NativePrimitives:
 lda $6002
 cmp #39
 bne NativeNormal
 lda $016c
 cmp #27
 beq NativeSec
 cmp #102
 beq NativeSec
 cmp #42
 beq NativeSide
NativeNormal:
 lda #2
 sta $7da1
 jmp $ab1a
NativeSide:
 tsx
 ldy $0107,x
 lda $010a,x
 pha
 plp
 jsr $958b
 jmp $ab38
NativeSec:
 tsx
 lda $010a,x
 ora #1
 sta $010a,x
 jmp $ab58
NativeEnd:
'''
    cfg='MEMORY{K:start=$5800,size=$80,file=%O;}SEGMENTS{TEST_KERNEL:load=K,type=ro;}'
    labels=F.L.assemble('complete-auth-v74-kernel',source,cfg)
    kernel=(O/'complete-auth-v74-kernel.bin').read_bytes();assert len(kernel)==57
    # This exact hook is after complete auth/range checks and before the
    # resident transport mapsC2/restores original arguments for nested FRC.
    raw=bytearray(auth['raw']);at=16+65*8192+0xb15
    assert raw[at:at+5]==bytes.fromhex('a9028da17d')
    raw[at:at+5]=bytes([76,TEST&255,TEST>>8,234,234])
    return old,auth,dict(auth,raw=bytes(raw)),route,q,ol,nl,kernel,labels


def seed_kernel(m,kernel):
    m[TEST:TEST+len(kernel)]=kernel


def fresh(bb,route,identity,kernel):
    Bus=N.Bus
    class TestBus(Bus):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);seed_kernel(self,kernel)
    N.Bus=TestBus
    try:return Q.Q.fresh(bb,route,identity)
    finally:N.Bus=Bus


def main():
    dst=O/'complete-auth-v74-measurement.json';assert not dst.exists()
    old,auth,new,route,q,ol,nl,kernel,labels=build();cases=[];direct=0;bad=0
    # Every direct public test enters through actual RAM FarCallCommon.
    # Its final LDA SafereturnA normalizes NZ fromA; NativeSec keeps all
    # six other architectural flags and setsC. Same-bank raw entry remains
    # an explicit source-caller closure requirement before any candidate.
    seeds=[fresh(bb,route,0,kernel)for bb in [old,new]]
    for m in seeds:seed_kernel(m,kernel)
    for raw in range(256):
        for row in [9,14,34]:
            for a in [0,1,128,255]:
                pair=[N.fork(m)for m in seeds];out=[]
                for m in pair:
                    N.put(m,SelectedCharacter=raw)
                    m[address(m.bundle,'SafecallA_SMC')+1]=a
                    # Cold.call supplies A83 by contract, so use the real
                    # typed veneer through the public symbol wrapper here.
                    name={9:'HuVertSkip',14:'HuSide',34:'HuWeapon'}[row]
                    target=0xb08c+row*3
                    z=F.D.C.I.invoke(m,193,target,(a,71,14,0xf1 if a&1 else 0x21))
                    out.append(dict(zip(['A','X','Y','P'],z['regs'][:4]),CPU=z['CPU']))
                F.parity(*pair,out);direct+=1
    for bank in [2,3]:
        for offset in range(16):
            for row in [9,14,34]:
                pair=[N.fork(m)for m in seeds];out=[]
                for m in pair:
                    m.ram[bank][0x1fe0+offset]^=1
                    z=F.D.C.I.invoke(m,193,0xb08c+row*3,(83,71,14,0x21))
                    out.append(dict(zip(['A','X','Y','P'],z['regs'][:4]),CPU=z['CPU']))
                F.parity(*pair,out);assert not out[0]['P']&1;bad+=1
    CPU=N.NesMPU
    for identity in [0,1]:
        for phase,keys in [('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[fresh(bb,route,identity,kernel)for bb in [old,new]];traces=[];outputs=[];auth_calls=[];primitive_calls=[]
            for index,m in enumerate(pair):
                seed_kernel(m,kernel);Q.L.E.main_fields(m);trace=[];count=0;calls={'side':0,'sec':0,'normal':0}
                class Trace(CPU):
                    def step(self):
                        nonlocal count
                        mm=self.memory;pc=self.pc;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                        if bank==193 and pc==(ol if index==0 else nl)['CoCheckCode']:count+=1
                        for kind,name in [('side','NativeSide'),('sec','NativeSec'),('normal','NativeNormal')]:
                            if pc==labels[name]:calls[kind]+=1
                        if bank in [2,3]and not(bank==3 and pc in [0xa01b,0xa02a,0xa066,0xb57c,0xb57d]):
                            trace.append((bank,pc,self.a,self.x,self.y,self.p,self.sp))
                        return super().step()
                N.NesMPU=Trace
                try:
                    out=[]
                    for epoch in range(12):
                        held=(keys&127)|(128 if keys&128 and epoch==1 else 0)
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=held,SavedJoypad1Bits=held,VRAM_Buffer1_Offset=0)
                        out.append(N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31))
                    outputs.append(out)
                finally:N.NesMPU=CPU
                traces.append(trace);auth_calls.append(count);primitive_calls.append(calls)
            F.parity(*pair,[z[-1]for z in outputs]);assert traces[0]==traces[1],(identity,phase,'source/remaining bridge instruction AXYP/SP')
            for a,z in zip(*outputs):assert [a[k]for k in ['A','X','Y','P']]==[z[k]for k in ['A','X','Y','P']]
            assert auth_calls==[156,156]and primitive_calls[1]==dict(side=48,sec=24,normal=84)
            before=sum(z['CPU']for z in outputs[0])/12;after=sum(z['CPU']for z in outputs[1])/12
            row=dict(identity=identity,phase=phase,Main_updates=12,baseline_CPU=before,proposal_CPU=after,
                saving_CPU=before-after,saving_percent=100*(before-after)/before,full_auth_calls=auth_calls,
                primitive_calls=primitive_calls[1],remaining_private_trace_entries=len(traces[0]),
                public_AXYP_SP_private_native_R0_7_SMC_maps_exact=True)
            cases.append(row);print(json.dumps(row),flush=True)
    result=dict(passed=True,CPU_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        cache_used=False,resource_granted=False,unfunded_kernel_bytes=len(kernel),test_only_kernel_RAM=[TEST,TEST+len(kernel)],
        no_host_RAM_lease_inferred=True,canonical_base='DK79 plus exact Prince130 over deliveredcf7',
        public_outer_farcall_cases=direct,individual_header_poison_rejections=bad,Main_cases=cases,
        field_semantics=dict(side='Raw39 only; exact immutable fixed958B getter with originalY/P; capture through existing AB38 result copy.',
            sec='Raw39 only; rows9/34 have actual SEC/RTS B57C. Sets original savedP carry, restores current frame, and returns via existing outer FRC which sets NZ from returnedA.',
            foreign='All other raw owners/routes take the original transport continuation with full auth and original argument restoration.',
            auth='Both full16B headers compared on all13 calls; no grouping, epoch, owner flag or lease.'),
        remaining=['The57B executable kernel is UNFUNDED test instrumentation at5800, not a legal host RAM use or cartridge placement. Canonical149/DK combined placement must first recover resident bytes from exact sources.',
            'Actual veneer caller closure must establish the supported outer FarCallCommon return semantics, including raw direct entry and nested IRQ/FF observers.',
            'All changed resident/cold/retire references, complete ISR/nested cuts and native performance/fullstage checks remain before any candidate.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(F.__file__),
            O/'full-auth-v73-measurement.json',O/'complete-auth-v74-kernel.s',O/'complete-auth-v74-kernel.bin',O/'complete-auth-v74-kernel.lbl']})
    dst.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
