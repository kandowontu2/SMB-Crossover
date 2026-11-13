"""Every emitted native contact PC: real IRQ/busy-NMI and Main continuation."""
from collections import Counter
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_platform_contact_1113 as Q
import check_dkjr_retire_lease_1113 as Lease

T,P,H,N,W,L=Q.T,Q.P,Q.H,Q.N,Q.W,Q.L


def result(m,c):
    return (tuple(bytes(r)for r in m.ram),tuple(m.rawtags),bytes(m[:0x100]),
        bytes(m[0x15a:0x17b]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),
        bytes(m.vram),tuple(m.chr_latches),(c.a,c.x,c.y,c.p&0xef,c.sp,c.pc))


def bind_rom(m,raw):
    """Change only the read-only ROM backing, never any emulated state."""
    m.bundle=dict(m.bundle,raw=raw)
    for window,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(window,tag)


def declared_admission(m,c,origin):
    if origin!='RYU HAYABUSA authored'or c.pc!=0xb963 or m.rawtags[1]!=128:return
    # Explicit admission metadata at an actual Main callback. Apply the same
    # declared input to collection, uninterrupted and interrupted continuations.
    N.put(m,WorldNumber=0,LevelNumber=3,AreaType=3,SecondaryHardMode=0,
        GuestHurtTicks=0,RgCrouch=0,RgAttack=0,XgWall=0,RyPlatformSlot=0,
        Player_State=1,RyWallSupported=1,RyWallOldHeight=25,RyWallWasGround=1,
        RyWallOldY=(N.get(m,'Enemy_Y_Position',c.x)+1)&255,
        RyWallOldX=N.get(m,'Player_X_Position'),RyWallOldPage=N.get(m,'Player_PageLoc'))


def observed_data(at):
    return at<0x100 or 0x200<=at<0x800 or 0x5c00<=at<0x8000


def matched_isr(state,cpu,parent,kind,changed):
    """Compare the real candidate ISR with the real original ISR at RTI.

    Both start from exactly the same cut CPU, hardware stack and live audio
    state. The original control stops before any changed foreground fetch.
    No audio-stack slot is masked or repaired.
    """
    outputs=[];traces=[];minimum=255;pending=False
    for raw in(state.bundle['raw'],parent):
        m,c=L.clone(state,cpu);bind_rom(m,raw)
        Base=type(m);events=[]
        class Bus(Base):
            def __getitem__(self,at):
                value=super().__getitem__(at)
                if isinstance(at,int)and observed_data(at)and self.isr_cpu is not None:
                    events.append(('R',self.isr_cpu.pc,at,value))
                return value
            def __setitem__(self,at,value):
                if isinstance(at,int)and observed_data(at)and self.isr_cpu is not None:
                    events.append(('W',self.isr_cpu.pc,at,value&255))
                return super().__setitem__(at,value)
        m.__class__=Bus;m.isr_cpu=None
        CPU=N.NesMPU
        class Trace(CPU):
            def step(self):
                self.memory.isr_cpu=self
                if self.pc>=0x8000:
                    tag=self.memory.rawtags[(self.pc-0x8000)//8192]
                    assert(tag,self.pc&8191)not in changed,('ISR entered changed foreground',kind,tag,hex(self.pc))
                return CPU.step(self)
        with patch.object(N,'NesMPU',Trace):low,window=Lease.inject_checked(c,kind)
        m.isr_cpu=None;minimum=min(minimum,low);pending|=window
        outputs.append((m,c));traces.append(events)
    (q,c),(mate,d)=outputs
    assert result(q,c)==result(mate,d),(kind,'candidate versus original ISR at RTI')
    assert bytes(q[0x100:0x200])==bytes(mate[0x100:0x200]),(kind,'ISR hardware stack')
    assert traces[0]==traces[1],(kind,'actual original ISR audio reader/writer trace')
    assert(c.a,c.x,c.y,c.p,c.sp,c.pc,c.processorCycles)==(d.a,d.x,d.y,d.p,d.sp,d.pc,d.processorCycles)
    # Restore only the control's ROM binding before foreground resumption.
    bind_rom(mate,state.bundle['raw'])
    return q,c,mate,d,minimum,pending,traces[0]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--debug-mini',action='store_true');ap.add_argument('--debug-ryu',action='store_true')
    args=ap.parse_args();diagnostic=args.debug_mini or args.debug_ryu
    parent=T.load_parent()
    candidate,_=T.transform(parent);linked,_=T.parts()
    changed={(((i-16)//8192)|128,(i-16)&8191)
        for i,(a,b)in enumerate(zip(parent,candidate))if a!=b}
    emitted={(128 if item['segment']in('RYU','NATIVE','RESTORE')else 186,item['pc'])for item in linked['instructions']}
    samples={};expected={};ends={};keys=set();active=None;last=None;origin='first'
    def watch(m,c):
        nonlocal active,last
        last=c
        if active==(c.pc,c.sp):active=None
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        declared_admission(m,c,origin)
        if(tag,c.pc)==(128,T.ENTRY):
            active=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,(c.sp+2)&255)
        own=(tag,c.pc)in emitted or(tag==128 and c.pc==0xb43f)
        transport=active is not None and 0x15a<=c.pc<0x17b
        if own or transport:
            token=(origin,tag,c.pc,c.p&0xc7)
            if token not in samples or c.sp<samples[token][1].sp:
                samples[token]=L.clone(m,c);keys.add(token)
    def after(m):
        nonlocal active
        value=result(m,last)
        for token in keys:expected[token]=value;ends[token]=L.clone(m,last)
        keys.clear();active=None

    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    m=Q.mounted(seed,candidate)
    text=P.once(T.controller(candidate),' if game then\n',
        " if game then\n  if epoch>=490 then finish(true,'native-contact-vector-prefix');return end\n")
    if diagnostic:prefix=dict(passed=True,logical_updates=0)
    else:
        with redirect_stdout(io.StringIO()):prefix=P.B.route(m,candidate,800,controller_text=text,
            observe_extra=watch,after_frame=after)
        assert prefix['passed']
    inventory=Q.Roster.Starts.C.inventory(parent)['rows']
    targets=(('RYU HAYABUSA','authored'),)if args.debug_ryu else(('MINI MARIO','ordinary'),)if args.debug_mini else(
        ('MINI MARIO','ordinary'),('RYU HAYABUSA','ordinary'),
        ('RYU HAYABUSA','authored'),('ZELDA II LINK','ordinary'))
    for name,scene in targets:
        origin=name+' '+scene;row=next(r for r in inventory if r['name']==name)
        b=W.Symbols.bundle();b['raw']=candidate
        _,m=Q.Roster.cold(b,row)
        for slot in range(6):N.invoke(m,'EraseEnemyObject',x=slot)
        slot=3
        if name=='RYU HAYABUSA':
            N.put(m,WorldNumber=0,LevelNumber=3 if scene=='authored'else 0,AreaType=3,SecondaryHardMode=0)
        for field,value in dict(Enemy_ID=40 if name=='RYU HAYABUSA'else 37,Enemy_Flag=1,Enemy_State=0,
            Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
            Enemy_Y_Position=160 if name=='RYU HAYABUSA'else(N.get(m,'Player_Y_Position')+32)&255,Enemy_Y_HighPos=1).items():
            m[W.address(m.bundle,field)+slot]=value
        N.invoke(m,'InitEnemyObject',x=slot)
        m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
        for age in range(32 if name=='RYU HAYABUSA'else 4):
            Q.frame(m,128 if name=='RYU HAYABUSA'and age<12 else 0,watch);after(m)
    reached={(tag,pc)for _,tag,pc,_ in samples}
    if not diagnostic:assert emitted<=reached,('Unreached emitted instructions',sorted(emitted-reached))
    print('DKJR_PLATFORM_VECTOR_SAMPLES '+json.dumps(dict(candidate_SHA256=T.PIN,
        emitted_instructions=len(emitted),Main_cut_points=len(samples),
        actual_unchanged_prefix_updates=prefix['logical_updates']),separators=(',',':')),flush=True)
    counts=Counter();minimum=255;pending=0;stack_differences=0;audio_differences=Counter()
    for index,(token,(state,cpu))in enumerate(sorted(samples.items())):
        for kind in('IRQ','lagNMI'):
            q,c=L.clone(state,cpu);live=bytes(q[0x101+c.sp:0x200])
            if kind=='IRQ'and c.p&4:
                before=(result(q,c),c.processorCycles);c.irq()
                assert before==(result(q,c),c.processorCycles);counts['maskedIRQ']+=1;continue
            q,c,mate,d,low,window,traced=matched_isr(state,cpu,parent,kind,changed)
            minimum=min(minimum,low);pending+=int(window)
            assert bytes(q[0x101+c.sp:0x200])==live,(token,kind,'live stack/footer changed by ISR')
            data_addresses=(*range(0x100),*range(0x200,0x800),*range(0x5c00,0x8000))
            isr_changes={at for at in data_addresses if state[at]!=q[at]}
            isr_values={at:q[at]for at in isr_changes}
            isr_writes={at for op,_,at,_ in traced if op=='W'}
            assert isr_changes<=isr_writes,(token,kind,'untraced original ISR data change')
            foreground=[];Bus=type(q)
            class Foreground(Bus):
                def __getitem__(self,at):
                    value=super().__getitem__(at)
                    if isinstance(at,int)and at in self.foreground_audio and self.foreground_active:
                        foreground.append(('R',self.foreground_pc,at,value))
                    return value
                def __setitem__(self,at,value):
                    if isinstance(at,int)and at in self.foreground_audio and self.foreground_active:
                        foreground.append(('W',self.foreground_pc,at,value&255))
                    return super().__setitem__(at,value)
            q.__class__=Foreground;q.foreground_audio=isr_changes;q.foreground_active=False
            def watch_foreground(m,cpu):
                declared_admission(m,cpu,token[0]);m.foreground_active=True;m.foreground_pc=cpu.pc
            stop=(W.address(q.bundle,'IdleLoop')+12,252)
            L.finish(q,c,stop,observe=watch_foreground);q.foreground_active=False
            L.finish(mate,d,stop,observe=lambda m,c:declared_admission(m,c,token[0]))
            assert result(q,c)==result(mate,d),(token,kind,'complete Main versus matched original ISR')
            actual=result(q,c);original=expected[token]
            assert actual[:2]==original[:2]and actual[3]==original[3]and actual[6:]==original[6:],(token,kind,'complete Main WRAM/SMC/maps/graphics/registers')
            # Retain exact comparison of every live audio stack byte against
            # the original-ISR oracle. An extra genuine busy NMI can advance
            # a live macro pointer, so no-extra-NMI SRAM is a separate oracle.
            baseline,_=ends[token]
            different={at for at in data_addresses if q[at]!=baseline[at]}
            accessed={at for _,_,at,_ in foreground}
            assert different<=isr_changes and not different&accessed,(token,kind,'foreground consumes extra-ISR audio change',different,foreground)
            stacklo=W.address(q.bundle,'XgAudioStackLo');stackend=W.address(q.bundle,'XgAudioStackBank')+32
            decoder=range(W.address(q.bundle,'XgAudioPtr'),W.address(q.bundle,'XgAudioZeroPageEnd'))
            apu=range(W.address(q.bundle,'XgMusicApu'),stackend)
            history=range(W.address(q.bundle,'XgLzHistory'),W.address(q.bundle,'XgLzHistory')+2048)
            # Exact contiguous .res declarations in src/guest_audio.s,
            # ending before the following owner's allocation.
            guest_apu=range(W.address(q.bundle,'GuestNativeApu'),W.address(q.bundle,'GuestSweepTicks')+1)
            # Exact shared native driver RAM/ZP-save declarations in
            # src/roster_audio.s. Their conditional aliases are not new owners.
            roster_audio=range(W.address(q.bundle,'RgAudioRam'),W.address(q.bundle,'GuestNativeApu'))
            sound_counter=W.address(q.bundle,'Squ1_SfxLenCounter')
            unknown={at for at in different if at not in decoder and at not in apu and at not in history and at not in guest_apu and at not in roster_audio and at!=sound_counter}
            assert not unknown,(token,kind,'unclassified ISR results',sorted(hex(at)for at in unknown))
            for at in different:
                assert q[at]==isr_values[at]and baseline[at]==state[at]
                audio_differences[hex(at)]+=1
            baseline,_=L.clone(*ends[token])
            differences={at for at in range(0x17b,0x1fd)if q[at]!=baseline[at]}
            # Only discarded hardware stack differs. Prove every actual later
            # read is preceded by a new write, while all live/SMC bytes compare.
            for model in(q,baseline):
                Base=type(model)
                class Tracked(Base):
                    def __getitem__(self,at):
                        if isinstance(at,int)and at in self.vector_discarded:
                            assert at in self.vector_written,('discarded stack read before writer',token,kind,hex(at))
                        return super().__getitem__(at)
                    def __setitem__(self,at,value):
                        if isinstance(at,int):self.vector_written.add(at)
                        return super().__setitem__(at,value)
                model.__class__=Tracked;model.vector_discarded=differences;model.vector_written=set()
            observer=lambda m,c:declared_admission(m,c,token[0])
            Q.frame(q,0,observer);Q.frame(baseline,0,observer);Q.frame(mate,0,observer)
            # Foreground return registers are already compared above; this
            # additional complete Main checks data and discarded-stack liveness.
            assert result(q,c)[:-1]==result(mate,d)[:-1],(token,kind,'next Main versus matched original ISR')
            assert q.contact_frame_registers==mate.contact_frame_registers
            stack_differences+=len(differences);counts[kind]+=1
        if index%40==0:print('DKJR_PLATFORM_VECTOR_PROGRESS '+json.dumps(dict(done=index+1,total=len(samples))),flush=True)
    assert counts['IRQ']and counts['lagNMI']and minimum>=128
    print('DKJR_PLATFORM_VECTORS '+json.dumps(dict(passed=True,candidate_SHA256=T.PIN,
        checker_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),cuts=dict(counts),
        emitted_instructions=len(emitted),cut_points=len(samples),minimum_ISR_SP=minimum,
        diagnostic_Mini_only=args.debug_mini,diagnostic_Ryu_only=args.debug_ryu,all_emitted_PCs_reached=emitted<=reached,
        declared_Ryu_source_admission_fixture=not args.debug_mini,
        exact_unbanked_pending_mapper_windows=pending,dead_stack_differences_reader_after_writer=stack_differences,
        matched_original_ISR_audio_stack_progress=dict(audio_differences),
        complete_live_audio_SRAM_equal_to_original_ISR_oracle=True,
        saved_footer_and_live_stack_exact=True,complete_Main_and_following_Main_WRAM_SMC_maps_graphics_equal=True,
        actual_busy_NMI_not_regular_branch=True,ROM_written=False,outputs_written=0,
        scope='Genuine first-item controller prefix and genuine foreign Main with declared platform actors. Not natural collection/fullstage/native readiness.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
