"""Independent actual post-BG caller/IRQ/busy-NMI canonical oracle; zero files."""
from collections import Counter
from hashlib import sha256
import argparse
import copy
import json
from unittest.mock import patch
from types import SimpleNamespace

import compose_smb2_postbg_mirror_1113 as C
import check_smb2_flag_handoff_1113 as Family
import check_bub_current_budget_1113 as Frames

W,N=C.W,C.N
CALL,RETURN,BRIDGE=0xa173,0xa176,0xe5cc
BASE_BUS=W.ControllerBus


def load_input():
    raw=C.Owner.NIGHTLY.read_bytes();digest=sha256(raw).hexdigest()
    if digest==C.CANDIDATE:raw=C.inverse(raw)
    assert sha256(raw).hexdigest()==C.PIN
    return raw,digest


class CanonicalOracle(BASE_BUS):
    """Read-only canonical125/127 instruction bytes; actual sample map retained.

    No live RAM/SMC/register/stack/audio value is changed. The source of this
    one existing44B ROM worker is explicit, rather than executing its known
    wrong historical operands. All original ISR/sample bytes remain original.
    """
    canonical_bank=127
    def __getitem__(self,at):
        if isinstance(at,int)and BRIDGE<=at<BRIDGE+44 and getattr(self,'rawtags',[0]*4)[3]in(247,248):
            return self.bundle['raw'][16+self.canonical_bank*8192+(at&8191)]
        return BASE_BUS.__getitem__(self,at)


def oracle(seed,parent,bank=127):
    m=Family.view(seed,parent)
    z=list.__new__(CanonicalOracle);list.extend(z,list.__iter__(m))
    for key,value in m.__dict__.items():setattr(z,key,value if key=='bundle'else copy.deepcopy(value))
    z.canonical_bank=bank
    return z


def full_state(m):
    # Snapshot backing registers/RAM without reading side-effect PPU ports.
    return(bytes(list.__getitem__(m,slice(0,0x8000))),tuple(bytes(z)for z in m.ram),tuple(m.rawtags),
        bytes(m.vram),tuple(m.chr_latches),tuple(m.protection),m.ppuctrl,m.ppu_addr,m.toggle,m.buffer)


def regs(c):return(c.a,c.x,c.y,c.p,c.sp,c.pc)


def inputs(raw):
    assert sha256(raw).hexdigest()==C.PIN
    image,info=C.proposal(raw);assert C.inverse(image)==raw
    assert info['native_caller_PC']==CALL
    for bank in(125,127):
        at=16+bank*8192+(BRIDGE&8191)
        assert raw[at:at+44]==C.CANONICAL[:44]
    return image,info


def caller_cpu(m,*,a=0x93,p=0x31):
    # Explicit native caller ABI context, not a gameplay or audio-state grant.
    m.raw_page(1,129);N.put(m,CurrentBank=129)
    c=N.NesMPU(memory=m,pc=CALL);c.a=a;c.x=3;c.y=151;c.p=p;c.sp=232
    return c


def run(c,stop,observe=None,limit=500000):
    low=c.sp;hits=Counter()
    for _ in range(limit):
        if stop(c):return low,hits
        m=c.memory;tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if(c.pc,tag)==(0xb438,194):hits['canonical_target']+=1
        if(c.pc,tag)==(0xbb87,207):hits['stale_target']+=1
        if c.pc==0x16e:hits['resident_return']+=1
        if observe:observe(c)
        assert m[c.pc],('Actual postBG BRK',hex(c.pc),c.sp,tuple(m.rawtags))
        low=min(low,c.sp);c.step()
    raise AssertionError(('Bounded actual postBG continuation',hex(c.pc),c.sp,tuple(c.memory.rawtags)))


def stopped(c):return(c.pc,c.sp)==(RETURN,232)


def caller(raw):
    image,_=inputs(raw);count=0;minimum=255;totals=Counter()
    for variant in range(8):
        seed=Family.cold(image,variant)
        for alias in(119,120):
            for canonical in(125,127):
                for flags in(0x31,0xe0):
                    a=Family.view(seed,image);b=oracle(seed,raw,canonical)
                    for m in(a,b):m.raw_page(3,alias|128)
                    ca,cb=caller_cpu(a,p=flags),caller_cpu(b,p=flags)
                    da,ha=run(ca,stopped);db,hb=run(cb,stopped)
                    assert regs(ca)==regs(cb)and full_state(a)==full_state(b)
                    assert ha==hb and ha['canonical_target']==1 and ha['stale_target']==0 and ha['resident_return']
                    assert a.rawtags[1]==N.get(a,'CurrentBank')==129 and a.rawtags[3]==alias|128
                    assert bytes(a[0x101+ca.sp:0x200])==bytes(b[0x101+cb.sp:0x200])
                    minimum=min(minimum,da,db);totals.update(ha);count+=1
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,all8_real_menu_constructors=True,
        directed_native_A173_to_A176_caller_pairs=count,canonical_templates=[125,127],alias_banks=[119,120],
        minimum_SP=minimum,observed=dict(totals),all_RAM_WRAM_maps_peripheral_state_AXYP_SP_and_live_stack_equal=True,
        wrong_old_target_parity_claim=False,no_live_state_masks_or_repairs=True,
        explicit_caller_register_and_mapping_fixtures=True,outputs=0,Mesen_run=False)


def family(raw):
    image,_=inputs(raw);count=0;cycles=0
    for variant in range(8):
        a=Family.cold(image,variant)
        with patch.object(W,'ControllerBus',CanonicalOracle):b=Family.cold(raw,variant)
        assert full_state(a)==full_state(b)
        for pad in(0,1,129,1,0,2,0,64):
            for _ in range(4):
                a.controller_pad=b.controller_pad=pad
                da,db=Frames.frame(a),Frames.frame(b)
                assert da==db and full_state(a)==full_state(b)
                count+=1;cycles+=da
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,actual8cold_menu_and_Main_NMI_controller_continuations=count,
        paired_CPU_cycles=cycles,whole_state_equal=True,no_gameplay_audio_state_seeds=True,
        source_route_not_full_stage=True,outputs=0,Mesen_run=False)


def adapter(raw):
    image,_=inputs(raw)
    with patch.object(C.Owner,'NIGHTLY',SimpleNamespace(read_bytes=lambda:image)):
        parent,digest=load_input();assert parent==raw and digest==C.CANDIDATE
    bad=bytearray(image);bad[0]^=1
    with patch.object(C.Owner,'NIGHTLY',SimpleNamespace(read_bytes=lambda:bytes(bad))):
        try:load_input()
        except AssertionError:pass
        else:raise AssertionError('Unknown CLI image accepted')
    return dict(passed=True,explicit_CLI_inverse_path=[C.CANDIDATE,C.PIN],unknown_input_rejected=True,
        strict_composer_PINs_unchanged=True,outputs=0,Mesen_run=False)


def busy_prefixes(raw):
    """Two genuine controller-derived sample owners; no APU/clock repair."""
    samples={};reports={}
    def capture(m,c):
        bank=N.get(m,'S2AudioActiveBank')
        if bank not in(119,120)or bank in samples:return
        if not m[0x4015]&16 or N.get(m,'NmiDisable')!=255 or N.get(m,'S2Clock')&8:return
        if m.rawtags[1]!=N.get(m,'CurrentBank')or m.rawtags[2]!=N.get(m,'CurrentBankC'):return
        assert m.rawtags[3]==bank|128 and N.get(m,'SelectedCharacter')==25
        samples[bank]=N.fork(m)
        reports[bank]=dict(bank=bank,status4015=m[0x4015],fixed_map=m.rawtags[3],
            health=N.get(m,'S2Health'),reserve=N.get(m,'S2Vegetables'),NmiDisable=N.get(m,'NmiDisable'),
            source_clock=N.get(m,'S2Clock'),PC=c.pc,SP=c.sp,
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            sample_start=m[0x4012],sample_length=m[0x4013],sample_rate=m[0x4010])
    m=Family.cold(raw,4)
    for tick in range(240):
        m.controller_pad=1;Frames.frame(m,observe=capture)
        if 120 in samples:reports[120]['source_prefix_Main']=tick+1;break
    assert 120 in samples,'Ordinary first-Goomba injury must start bank120'
    import replay_smb2_natural_flower_1113 as Flower
    original_frame=Frames.frame
    def observing_frame(m,observe=None,**kwargs):
        def both(memory,c):
            capture(memory,c)
            if observe:observe(memory,c)
        return original_frame(m,observe=both,**kwargs)
    with patch.object(Frames,'frame',observing_frame):q=Flower.source_run(raw,4,'throw',1500)
    assert q['passed']and 119 in samples,'Earned Flower/reserve pull must start original bank119 sample'
    reports[119]['prefix_controller_SHA256']=q['controller_SHA256']
    reports[119]['complete_natural_prefix_logical_iterations']=q['logical_Main_NMI_iterations']
    return samples,reports


def interrupt_pair(m,source_cpu,raw,image,canonical,kind):
    """Both actual ISRs and complete intended caller, without live-state edits."""
    native=N.NesMPU;a=Family.view(m,image);b=oracle(m,raw,canonical)
    expected=regs(source_cpu);protected=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+source_cpu.sp:0x200]))
    music_at=W.address(m.bundle,'S2AudioState');music_before=bytes(m[music_at:music_at+77])
    cpus=[];minimum=255;map_completions=0
    for model in(a,b):
        c=native(memory=model,pc=source_cpu.pc)
        for field in('a','x','y','p','sp'):setattr(c,field,getattr(source_cpu,field))
        before_maps=tuple(model.rawtags);skip=N.get(model,'NmiSkipped')
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(150000):
            minimum=min(minimum,c.sp)
            if(c.pc,c.sp)==(source_cpu.pc,source_cpu.sp):break
            assert not BRIDGE<=c.pc<BRIDGE+44,'ISR entered Main-only postBG bridge'
            assert model[c.pc],('Original ISR BRK',kind,hex(c.pc),c.sp,tuple(model.rawtags))
            native.step(c)
        else:raise AssertionError(('Actual ISR bound',kind,hex(c.pc)))
        assert regs(c)==expected,('ISR ABI',kind,hex(source_cpu.pc),expected,regs(c))
        assert(bytes(model[3:11]),bytes(model[0x15a:0x17b]),bytes(model[0x101+c.sp:0x200]))==protected
        if tuple(model.rawtags)!=before_maps:
            assert kind=='busyNMI'and before_maps[:1]+before_maps[2:]==tuple(model.rawtags[:1]+model.rawtags[2:])
            assert bytes(m[source_cpu.pc-3:source_cpu.pc+3])==bytes.fromhex('8d45018d1551')
            assert model.rawtags[1]==N.get(model,'CurrentBank')==c.a
            map_completions+=1
        assert N.get(model,'NmiSkipped')==(skip+(kind=='busyNMI'))&255
        cpus.append(c)
    assert full_state(a)==full_state(b)and a.writes==b.writes and a.ram_writes==b.ram_writes
    advanced=bytes(a[music_at:music_at+77])!=music_before
    for model,c in zip((a,b),cpus,strict=True):run(c,stopped)
    assert regs(cpus[0])==regs(cpus[1])and full_state(a)==full_state(b)
    assert a.writes==b.writes and a.ram_writes==b.ram_writes
    assert a.rawtags[1]==N.get(a,'CurrentBank')==129
    return minimum,advanced,map_completions//2


def vectors(raw):
    image,_=inputs(raw);samples,prefixes=busy_prefixes(raw)
    points=set();counts=Counter();minimum=255;advanced=0;completed=0
    required={(bank|128,pc)for bank in(119,120)for pc in(0xe5e9,0xe5ee,0xe5f3)}
    reached=set()
    for bank in(119,120):
        for canonical in(125,127):
            m=Family.view(samples[bank],image);c=caller_cpu(m,p=0x31)
            def observe(cpu):
                nonlocal minimum,advanced,completed
                memory=cpu.memory;pc=cpu.pc
                tag=memory.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
                relevant=tag==bank|128 and BRIDGE<=pc<BRIDGE+44 or 0x15a<=pc<0x17b
                if not relevant:return
                key=(bank,canonical,tag,pc,cpu.sp,cpu.p&4)
                if key in points:return
                points.add(key);reached.add((tag,pc))
                for kind in('IRQ','busyNMI'):
                    if kind=='IRQ'and cpu.p&4:continue
                    low,music,done=interrupt_pair(memory,cpu,raw,image,canonical,kind)
                    minimum=min(minimum,low);counts[bank,kind]+=1
                    if kind=='busyNMI':advanced+=music;completed+=done
            run(c,stopped,observe)
    assert required<=reached and all(counts[b,k]for b in(119,120)for k in('IRQ','busyNMI'))
    assert advanced and minimum>=128
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,reached_foreground_instruction_SP_points=len(points),
        cuts=[dict(bank=b,kind=k,cases=n)for(b,k),n in sorted(counts.items())],minimum_SP=minimum,
        all_six_changed_operand_instructions_reached=sorted(required),
        genuine_busy_prefixes=prefixes,exact_paired_music_advances=advanced,pending_A_map_completions=completed,
        actual_ISR_and_complete_native_caller_RAM_WRAM_AXYP_SP_live_stack_SMC_maps_ordered_writes_equal=True,
        canonical_ROM_only_oracles=[125,127],live_state_masks_or_repairs=0,
        source_audio_and_sample_waveform_or_deadline_native_claim=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('family','vectors','adapter'):p.add_argument('--'+name,action='store_true')
    args=p.parse_args()
    raw,digest=load_input();q=vectors(raw)if args.vectors else family(raw)if args.family else adapter(raw)if args.adapter else caller(raw)
    q['actual_input_SHA256']=digest
    print(json.dumps(q,separators=(',',':')),flush=True)
