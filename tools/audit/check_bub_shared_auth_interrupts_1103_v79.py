"""Actual IRQ/FF NMI at reached changed shared-auth/cold boundaries.

Only compact context/winner aggregates persist; CPU/RAM fixtures stay in memory.
"""
from collections import Counter
import json
from pathlib import Path
import check_bub_shared_auth_lifecycle_1103_v78 as P
import check_bub_head_interrupts_1102_v57 as H
from check_tmnt_render_oa import location
O,R,N,Q,address,sha=P.O,P.R,P.N,P.Q,P.address,P.sha
SOUND=[0x7d8,0x7da,0x7db,0x7dc]


def view(m):
    native=bytearray(m[0x200:0x800])
    for a in SOUND:native[a-0x200]=0
    return ([bytes(x)for x in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(native),
        N.get(m,'SelectedCharacter'),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
        bytes(m.vram),tuple(m.chr_latches),m.upper,m.lastset,m.ppu_addr,m.toggle,m.buffer,m.ppuctrl)


def sites(b):
    result=H.audio_sites(b)
    for prefix in ['GuestSharedSfx::','SoundEngine::']:
        for suffix,delta,code in [('PlayBrickShatter',2,'8ddc07'),('DecrementSfx3Length',0,'cedc07')]:
            name=prefix+suffix;pc=address(b,name)+delta;at=location(b,name)+delta
            assert b['raw'][at:at+3]==bytes.fromhex(code)
            result[(((at-16)//8192)|128,pc)]=(name,delta,code)
    return result


def main():
    destination=O/'shared-auth-v79-ISR.json';assert not destination.exists()
    old,b,route,q,manifest,ol,nl,patches,refs=P.P.P.build()
    CPU=N.NesMPU;seen=set();counts=Counter();audio_writes=Counter();pending=Counter();winners={};scenarios=[]
    minimum=224;deepest=None;current=None;ordinal=0;fore_min=224;entry_count=0
    writer_sites=sites(b)
    def probe(c,kind):
        nonlocal minimum,deepest
        m=N.fork(c.memory);P.P.C.clear(m)
        z=CPU(memory=m,pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        regs=(z.a,z.x,z.y,z.p,z.sp,z.pc);before=view(m);maps=m.rawtags[:]
        live=bytes(m[0x101+z.sp:0x200]);audio_before=tuple(m[a]for a in SOUND)
        # Native IRQ legitimately publishes PPU split/CHR selection state.
        # Compare those outputs to the actual unchanged old native handler
        # from the identical interrupted CPU/bus state, rather than requiring
        # the PPU registers not to change. No register value is normalized.
        reference=N.fork(m);reference.bundle=old
        for window,tag in enumerate(reference.rawtags[:]):
            if tag&128:reference.raw_page(window,tag)
        ref=CPU(memory=reference,pc=c.pc);ref.a,ref.x,ref.y,ref.p,ref.sp=regs[:5]
        ref.irq()if kind=='IRQ'else ref.nmi()
        for _ in range(200000):
            if(ref.pc,ref.sp)==(regs[5],regs[4]):break
            assert reference[ref.pc]!=0,('Reference ISR BRK',current,kind,hex(ref.pc))
            ref.step()
        else:raise AssertionError('Reference ISR bound')
        skipped=N.get(m,'NmiSkipped');commit=N.get(m,'FamilyMainCommit')
        lag,regular=H.I.path(m);lh=rh=0;touched=set()
        assert N.get(m,'NmiDisable')==255
        z.irq()if kind=='IRQ'else z.nmi()
        for steps in range(200000):
            if(z.pc,z.sp)==(regs[5],regs[4]):break
            if z.sp<minimum:minimum=z.sp;deepest=dict(scenario=current,kind=kind,foreground_PC=c.pc,foreground_SP=c.sp,handler_PC=z.pc,handler_SP=z.sp)
            lh+=int(z.pc==lag);rh+=int(z.pc==regular)
            assert m[z.pc]!=0,('ISR BRK',current,kind,hex(c.pc),hex(z.pc),z.sp)
            if kind=='FF'and not z.p&4:
                cut=(z.pc,z.sp,m.rawtags[1],m.rawtags[2]);key=(current[0],cut[0],cut[2],cut[3])
                if key not in winners or cut[1]<winners[key]['handler_cut'][1]:
                    winners[key]=dict(handler_cut=cut,scenario=current,foreground_ordinal=ordinal,
                        foreground_cut=(c.pc,c.sp,c.memory.rawtags[1],c.memory.rawtags[2],c.p),
                        live_native_audio=list(audio_before))
            ins=bytes(m[z.pc:z.pc+3])
            if ins in [bytes.fromhex(x)for x in ['8dd807','ced807','8dda07','8ddb07','eedb07','8ddc07','cedc07']]:
                tag=m.rawtags[(z.pc-0x8000)//8192];assert(tag,z.pc)in writer_sites
                target=int.from_bytes(ins[1:],'little');touched.add(target)
                audio_writes[f'{tag:02x}:{z.pc:04x}:'+writer_sites[tag,z.pc][0]]+=1
            z.step()
        else:raise AssertionError(('ISR return bound',current,kind,hex(c.pc)))
        assert regs[:3]==(z.a,z.x,z.y)and regs[3]&0xef==z.p&0xef and regs[4:]==(z.sp,z.pc),('ISR AXYP/SP',current,kind,hex(c.pc))
        after=view(m)
        if after[:7]!=before[:7]or after[7:]!=view(reference)[7:]or tuple(m[a]for a in SOUND)!=tuple(reference[a]for a in SOUND):
            diagnostic=dict(passed=False,scenario=current,kind=kind,foreground_PC=c.pc,
                changed_view_fields=[i for i,(a,z)in enumerate(zip(before,after))if a!=z],
                native_differences=[dict(address=0x200+i,old=a,new=z)for i,(a,z)in enumerate(zip(before[3],after[3]))if a!=z][:16],
                PPU_before=before[9:],PPU_after=after[9:])
            negative=O/'shared-auth-v79-initial-state-negative.json'
            if not negative.exists():negative.write_text(json.dumps(diagnostic,indent=2)+'\n')
            raise AssertionError(('ISR source/native/PPU/scratch/SMC state',diagnostic))
        assert bytes(m[0x101+z.sp:0x200])==live,('Live stack',current,kind,hex(c.pc))
        for a,v in zip(SOUND,audio_before):
            if m[a]!=v:assert kind=='FF'and a in touched,('Unbound audio change',hex(a),v,m[a])
        if kind=='IRQ':assert lh==rh==0 and N.get(m,'NmiSkipped')==skipped and tuple(m[a]for a in SOUND)==audio_before
        else:assert lh==1 and rh==0 and N.get(m,'NmiSkipped')==(skipped+1)&255
        assert N.get(m,'FamilyMainCommit')==(commit if kind=='IRQ'else commit&1)
        if maps!=m.rawtags:
            ins=bytes(m[z.pc:z.pc+3]);assert ins in [bytes.fromhex(x)for x in ['8d1551','8d1651','8e1651','8c1651']],('Pending mapper bus write',current,kind,hex(z.pc),maps,m.rawtags,ins.hex())
            window=1 if ins[1]==0x15 else 2
            assert m.rawtags[window]==N.get(m,'CurrentBank'if window==1 else'CurrentBankC')
            assert all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)
            pending[f'{m.rawtags[1]:02x}:{z.pc:04x}:{ins.hex()}']+=1
        counts[kind]+=1
    class Trace(CPU):
        def step(self):
            nonlocal ordinal,fore_min,entry_count
            ordinal+=1;fore_min=min(fore_min,self.sp)
            m=self.memory;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            watched=tag==193 and(0xa800<=pc<0xa849 or 0xae00<=pc<0xb013 or 0xab72<=pc<0xabce)
            watched=watched or 0x15a<=pc<0x17b
            if watched:
                key=(current,pc,self.sp,m.rawtags[1],m.rawtags[2],self.p&0xcf)
                if key not in seen:
                    seen.add(key);entry_count+=1
                    if not self.p&4:probe(self,'IRQ')
                    probe(self,'FF')
            return super().step()
    def run(name,action):
        nonlocal current,ordinal,fore_min,entry_count
        current=name;ordinal=0;fore_min=224;entry_count=0
        N.NesMPU=Trace
        try:result=action()
        finally:N.NesMPU=CPU
        scenarios.append(dict(name=name,reached_foreground_instructions=ordinal,
            minimum_foreground_SP=fore_min,unique_watched_contexts=entry_count))
        print('Shared auth ISR',name,'cuts',entry_count,'minimum',minimum,flush=True)
        return result
    for owner in [36,37,38,39,40]:
        # Actual cold has I0 before the source SEI and I1 afterwards. FF is
        # tested at both reached states; IRQ is admitted only when I0.
        N.Bus=P.P.C.cold.__globals__['C'].C.V.ControllerBus;seed=N.fresh(b)
        for k in [2,3]:seed.ram[k][:]=bytes([0x9d])*8192;seed.ram[k][0x1fe0:0x1ff0]=bytes(16)
        P.P.C.fields(seed,owner);P.P.C.clear(seed)
        run(('cold',owner),lambda seed=seed,owner=owner:P.P.public(seed,0xae00 if owner!=36 else 0xac1d))
        P.P.C.clear(seed)
        run(('Fresh',owner),lambda seed=seed:N.invoke(N.fork(seed),'HuFresh',a=83,x=0,y=109,p=0x21))
        m=N.fork(seed);N.put(m,SelectedCharacter=0,NmiDisable=255,FamilyMainCommit=1)
        run(('retire',owner),lambda m=m:P.P.public(m,0xae0b))
    for owner,identity in [(36,0),(39,0),(39,1)]:
        if owner==36:
            m,_=P.P.cold(b,36);N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)
        else:m=Q.Q.fresh(b,route,identity)
        Q.L.E.main_fields(m);N.put(m,NmiDisable=255,FamilyMainCommit=1,DisableScreenFlag=0,Mirror_PPUMASK=30,
            TimerControl=0,FrameCounter=1,SavedJoypadBits=1,SavedJoypad1Bits=1,VRAM_Buffer1_Offset=0)
        for name in ['Block_Buffer_1','Block_Buffer_2']:
            at=address(b,name);m[at:at+208]=bytes(208)
            for row in [11,12]:m[at+row*16:at+row*16+16]=bytes([84])*16
        P.P.C.clear(m)
        run(('Main',owner,identity),lambda m=m:N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x21))
    result=dict(passed=True,CPU_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        actual_ISR_counts=dict(counts),minimum_ISR_SP=minimum,deepest=deepest,scenarios=scenarios,
        watched_contexts=len(seen),source_bound_audio_writers=dict(audio_writes),source_bound_next_bus_writes=dict(pending),
        nested_handler_winners=list(winners.values()),
        scope='Genuine full native IRQ and NmiDisableFF lag-NMI injected at every unique reached PC/SP/A/C/architectural-P context in changed Sh/raw39/owner/extra code and RAM FarCallCommon, across five real cold/Fresh/foreign-retire owners and Sh/Bub/Bob actual Main. IRQ only atI0; FF includes actualI1. Exact private RAM, native0200..07FF, R0..7, live stack, SMC, owner and map shadows survive. Actual PPU/CHR split outputs and all four native audio clocks equal the unchanged baseline handler from identical interrupted state; no PPU register is normalized or presumed unwritten. Audio writers are source-bound and IRQ preserves clocks. A next native mapper bus write is allowed only with exact current opcode and every other window strict. Handler deepest I0 witnesses retained for nested replay, not yet nested-qualified.',
        remaining=['Deepest actual lag-handler nestedIRQ replay across all retained contexts.','Complete external caller/reference closure and pending combined-owner source rebind.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),Path(H.__file__),
            O/'shared-auth-v76-funding.json',O/'shared-auth-v77-contracts.json',O/'shared-auth-v78-lifecycle.json',
            O/'shared-auth-v76.s',O/'shared-auth-v76.bin',O/'shared-auth-v76-extra.bin',O/'shared-auth-v76-Sh.bin',
            R/'src/music_drivers/vanilla_sfx.s',R/'src/reset.s']})
    destination.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps({k:result[k]for k in ['passed','actual_ISR_counts','minimum_ISR_SP','deepest','watched_contexts']}))


if __name__=='__main__':main()
