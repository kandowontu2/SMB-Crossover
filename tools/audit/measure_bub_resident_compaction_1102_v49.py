"""Source-reproduce and measure owner-frame funding; no auth reuse or ROM file."""
import json,re
from pathlib import Path
import measure_bub_landing_1102_v21 as L
import check_bubble_bobble_common_cold_1102_v4 as C

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address
O=L.O;PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def build():
    _,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes'
    b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    oldlabels=P.P.labels(L.B/'native-event-v9-owner.lbl')
    src=(L.B/'native-event-v9-owner.s').read_text()
    for name,pc in [('CoExCookie',0xaff3),('CoBBCookie',0xb003)]:
        at=16+65*8192+(pc&8191);value=b['raw'][at:at+16]
        src,n=re.subn(name+r':\.incbin "[^"]+"',name+':.byte '+','.join('$%02x'%q for q in value),src)
        assert n==1
    cfg='MEMORY{P:start=$ae00,size=$213,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}'
    # The exact current owner preimage is established before any rewrite.
    reproduced=L.assemble('auth-frame-v49-reproduce',src,cfg)
    before=(O/'auth-frame-v49-reproduce.bin').read_bytes()
    at=16+65*8192+0xe00
    assert before==b['raw'][at:at+len(before)] and len(before)==531
    assert all(reproduced[n]==oldlabels[n] for n in oldlabels)
    def once(old,new):
        nonlocal src
        assert src.count(old)==1,(old,src.count(old));src=src.replace(old,new)
    once(' jsr CoCheckHeaders\n bcc CoColdBegin\n jmp CoYes\n',
         ' jsr CoCheckHeaders\n bcs CoYes\n')
    once('CoGuardNo:\n jmp CoNo\nCoColdBegin:\n','CoColdBegin:\n')
    once('CoColdMode:\n','CoGuardNo:\n jmp CoNo\nCoColdMode:\n')
    # In each loop, X is still the published physical C bank: every body
    # instruction changes A/Y/P only. Actual interrupts must restore X.
    assert src.count(' ldx CurrentBankC\n dex\n cpx #1\n')==2
    src=src.replace(' ldx CurrentBankC\n dex\n cpx #1\n',' dex\n cpx #1\n')
    once(' CoFar CoWorker,$fb\n',' ldx #0\n jsr CoFarIndexed\n')
    once(' CoFar BbNativeRetire,3\n',' ldx #1\n jsr CoFarIndexed\n')
    once('CoPublishChr:\n CoFar X5PublishChr,Bank_X5PublishChr\n rts\n',
         'CoPublishChr:\n ldx #2\n jmp CoFarIndexed\n')
    once(' lda CoDescriptorHi,x\n',' lda #>CoExDescriptor\n')
    once('CoSmc:\n','''; Cold/retirement-only factoring. Incoming X is not an import.
CoFarIndexed:
 sta SafecallA_SMC+1
 lda CoFarLo,x
 sta FarcallJmpTarget_SMC+1
 lda CoFarHi,x
 sta FarcallJmpTarget_SMC+2
 lda CoFarBank,x
 jmp FarCallCommon
CoFarLo:.byte <CoWorker,<BbNativeRetire,<X5PublishChr
CoFarHi:.byte >CoWorker,>BbNativeRetire,>X5PublishChr
CoFarBank:.byte $fb,3,Bank_X5PublishChr
CoFundingStart:
 .res 0,$ea
CoSmc:
''')
    once('CoDescriptorHi:.byte >CoExDescriptor,>CoBBDescriptor\n',
         'CoDescriptorHiFunding:.byte $ea,$ea\n')
    src+='\n.export CoFundingStart,CoDescriptorHiFunding,CoFarIndexed\n'
    measured=L.assemble('auth-frame-v49-compact',src,cfg)
    padding=0xafe6-measured['CoFundingStart'];assert padding>=0
    once(' .res 0,$ea\n',f' .res {padding},$ea\n')
    labels=L.assemble('auth-frame-v49-compact',src,cfg)
    blob=(O/'auth-frame-v49-compact.bin').read_bytes();assert len(blob)==531
    for name in ['CoCold','CoRetire','CoSmc','CoOwnerEnd']:
        assert labels[name]==oldlabels[name],(name,labels[name],oldlabels[name])
    assert blob[0x1f3:]==before[0x1f3:] # Both cookies keep their exact addresses.
    contiguous=labels['CoSmc']-labels['CoFundingStart']
    assert contiguous==20,contiguous
    new=dict(b);rr=bytearray(b['raw']);rr[at:at+531]=blob
    # Exactly one current bank65 JSR consumes the private auth entry. Fixed
    # scene/retirement entries and saved-SMC table remain at their addresses.
    needle=bytes([0x20,oldlabels['CoCheckCode']&255,oldlabels['CoCheckCode']>>8])
    bank=rr[16+65*8192:16+66*8192]
    references=[i for i in range(8190) if bank[i:i+3]==needle]
    assert len(references)==1,references
    pos=16+65*8192+references[0]+1;rr[pos:pos+2]=labels['CoCheckCode'].to_bytes(2,'little')
    new['raw']=bytes(rr)
    return b,new,layout,route,oldlabels,labels,contiguous,references


def main():
    old,new,layout,route,oldlabels,labels,free,refs=build();checks={}
    cold=[]
    for owner in [37,39]:
        for case,fault in [('cold',None),('code-readback',(3,2048)),('protected','locked'),('disabled-NMI',None)]:
            pair=[];out=[]
            for b,labs in [(old,oldlabels),(new,labels)]:
                m=C.ready(b);N.put(m,SelectedCharacter=owner)
                if fault=='locked':m.protection=[0,0]
                elif fault:m.corrupt_at=fault
                pair.append(m);out.append(C.call(m,labs['CoCold'],nmi=case=='disabled-NMI',flags=0x31))
            assert [out[0][k] for k in ['A','X','Y','P']]==[out[1][k] for k in ['A','X','Y','P']],(owner,case,out)
            assert pair[0].ram==pair[1].ram and pair[0].rawtags==pair[1].rawtags,(owner,case,'RAM/maps')
            assert bytes(pair[0][3:11])==bytes(pair[1][3:11])
            assert pair[0].ppu_reads==pair[1].ppu_reads and pair[0].upper==pair[1].upper==0
            for m in pair:assert m.ppuctrl==160 and m.toggle==0
            cold.append(dict(owner=owner,case=case,baseline=out[0],compact=out[1]))
    checks['actual_whole_cold_ABI_RAM_maps_R0_7_PPU']=cold
    poisons=0;warm=[]
    for identity in [0,1]:
        seeds=[Q.fresh(b,route,identity) for b in [old,new]]
        for bank in [2,3]:
            for index in range(16):
                out=[];pair=[]
                for seed,labs in zip(seeds,[oldlabels,labels]):
                    m=N.fork(seed);m.ram[bank][0x1fe0+index]^=1;pair.append(m)
                    before=[bytes(q) for q in m.ram];scratch=bytes(m[3:11]);maps=list(m.rawtags)
                    out.append(C.call(m,labs['CoCheckCode'],flags=0x31))
                    assert not out[-1]['P']&1 and before==[bytes(q) for q in m.ram]
                    assert scratch==bytes(m[3:11]) and maps==m.rawtags
                assert [out[0][k] for k in ['A','X','Y','P']]==[out[1][k] for k in ['A','X','Y','P']]
                poisons+=1
        for m,labs in zip(seeds,[oldlabels,labels]):
            warm.append(C.call(m,labs['CoCheckCode'],flags=0x31))
    checks['whole_two_header_direct_auth_poison_differentials']=poisons
    checks['direct_warm_auth']=warm
    # Full actual GameCore compares native/private state, R0..7, maps, final
    # AXYP/SP and the complete original actor/draw/import entry trace. The
    # rewritten resident internal PCs are deliberately not normalized into
    # a claim of identical resident instruction traces.
    native=N.NesMPU;maincases=[]
    for identity in [0,1]:
        for keys in [0,1,2,129,64]:
            seeds=[Q.fresh(b,route,identity) for b in [old,new]];traces=[];out=[]
            for m in seeds:
                L.E.main_fields(m);trace=[]
                class Trace(native):
                    def step(self):
                        mem=self.memory;pc=self.pc;tag=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
                        if tag==3 and 0xa000<=pc<0xbfe0:
                            trace.append((pc,self.a,self.x,self.y,self.p,self.sp))
                        elif tag==2 and 0xd320<=pc<0xd400:
                            trace.append((pc,self.a,self.x,self.y,self.p,self.sp))
                        return native.step(self)
                N.NesMPU=Trace
                try:
                    outputs=[]
                    for epoch in range(4):
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                        outputs.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
                    out.append(outputs)
                finally:N.NesMPU=native
                traces.append(trace)
            assert traces[0]==traces[1],('Original/private instruction AXYP/SP trace',identity,keys)
            for a,z in zip(*out):assert [a[k] for k in ['A','X','Y','P']]==[z[k] for k in ['A','X','Y','P']]
            assert seeds[0].ram==seeds[1].ram and seeds[0].rawtags==seeds[1].rawtags
            assert bytes(seeds[0][3:11])==bytes(seeds[1][3:11])
            maincases.append(dict(identity=identity,keys=keys,Main_calls=4,
                baseline_CPU=sum(z['CPU'] for z in out[0]),compact_CPU=sum(z['CPU'] for z in out[1]),
                original_private_instruction_trace_entries=len(traces[0]),
                original_private_instruction_trace_SHA256=P.sha(json.dumps(traces[0]).encode()),
                AXYP_SP_native_private_RAM_draw_input_R0_7_maps_exact=True))
    checks['whole_Main_differentials']=maincases
    # All reached warm-auth PC/SP cuts, actual IRQ and busy/lag NMI. The
    # source-funded LDX removal is legal only if real ISR restores X.
    cuts=set();seed=Q.fresh(new,route,1);N.put(seed,NmiDisable=255)
    class Trace(native):
        def step(self):
            if self.memory.rawtags[1]==193 and labels['CoCheckCode']<=self.pc<labels['CoCheckHeaders']+70:
                cuts.add((self.pc,self.sp))
            return native.step(self)
    N.NesMPU=Trace
    try:C.call(N.fork(seed),labels['CoCheckCode'],flags=0x31)
    finally:N.NesMPU=native
    interrupt_counts={}
    for kind in ['IRQ','lagNMI']:
        for cut in sorted(cuts):
            m=N.fork(seed);injected=False
            class Interrupt(native):
                def step(self):
                    nonlocal injected
                    mem=self.memory
                    if not injected and mem.rawtags[1]==193 and (self.pc,self.sp)==cut:
                        injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc)
                        maps=list(mem.rawtags);scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
                        private=[bytes(q) for q in mem.ram]
                        self.irq() if kind=='IRQ' else self.nmi()
                        for _ in range(200000):
                            if (self.pc,self.sp)==(regs[-1],regs[-2]):break
                            assert mem[self.pc]!=0;native.step(self)
                        else:raise AssertionError(('ISR bound',kind,cut))
                        assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)
                        map_ok=maps==mem.rawtags
                        if not map_ok:
                            instruction=bytes(mem[self.pc:self.pc+3]);prior=bytes(mem[self.pc-3:self.pc])
                            assert kind=='lagNMI' and instruction[0] in [0x8d,0x8e] and instruction[1:]==bytes.fromhex('1651')
                            assert prior==bytes([instruction[0]])+address(new,'CurrentBankC').to_bytes(2,'little')
                            assert maps[0:2]+maps[3:]==mem.rawtags[0:2]+mem.rawtags[3:]
                            assert mem.rawtags[2]==mem[address(new,'CurrentBankC')]
                        assert private==[bytes(q) for q in mem.ram] and scratch==bytes(mem[3:11]) and smc==bytes(mem[0x15a:0x17b])
                    return native.step(self)
            N.NesMPU=Interrupt
            try:result=C.call(m,labels['CoCheckCode'],flags=0x31)
            finally:N.NesMPU=native
            assert injected and result['P']&1
            interrupt_counts[kind]=interrupt_counts.get(kind,0)+1
    checks['warm_full_auth_actual_ISR_cuts']=interrupt_counts
    out=dict(passed=True,proposal_only=True,ROM_written=False,source_mutated=False,cache_implemented=False,
        base_ROM_SHA256=PIN,checks=checks,owner_bytes=531,contiguous_source_funding_bytes=free,
        contiguous_half_open=[labels['CoFundingStart'],0xafe6],other_source_funding_half_open=[0xaff1,0xaff3],
        existing_dispatch_padding_half_open=[0xa7f8,0xa800],funding_total=free+2+8,
        fixed_public_cold_retire_SMC_and_cookie_addresses_preserved=True,
        moved_private_aliases={n:[oldlabels[n],labels[n]] for n in oldlabels if labels[n]!=oldlabels[n]},
        exact_current_auth_JSR_rebindings=[dict(physical_PRG=65,bank_offset=i+1,old=oldlabels['CoCheckCode'],new=labels['CoCheckCode']) for i in refs],
        remaining=['No lease bit/state is allocated or used. This compaction alone preserves13 full checks/Main and is funding, not the large performance fix.',
            'Before a candidate: complete foreign retirement/trapped AI, changed cold/farcall instruction IRQ/disabledNMI cuts and all hardcoded private-alias consumer rebinding are still required.',
            'Any scoped-auth successor separately needs Main/direct-call/header-owner-writer lifetime proof and root resource review.'],
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes()) for p in [Path(__file__),O/'combined-current-landing.nes',
            O/'auth-frame-v49-reproduce.s',O/'auth-frame-v49-reproduce.bin',
            O/'auth-frame-v49-compact.s',O/'auth-frame-v49-compact.bin',O/'auth-frame-v49-compact.lbl',
            L.B/'native-event-v9-owner.s',L.B/'native-proxy-routes.s',O/'auth-lifetime-v48.json']})
    dst=O/'resident-compaction-v49.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ROM_written=False,cache_implemented=False,funding_bytes=free+2+8,
        contiguous=free,whole_Main_cases=len(maincases),poison_cases=poisons,ISR_cuts=interrupt_counts,
        receipt=str(dst.relative_to(R)))))


if __name__=='__main__':main()
