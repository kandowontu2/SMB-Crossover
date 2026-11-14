"""Exact E037 prefix/caller/payload/ISR canonical checks; zero output files."""
import argparse
from collections import Counter
import copy
from hashlib import sha256
import json
from unittest.mock import patch

import compose_smb2_cheat_cold_mirror_1113 as C
import check_smb2_postbg_irq_1113 as ISR

W,N=C.W,C.N
Family=C.Owner.D.Flag
Frames=C.Owner.D.Frames
CALL,RETURN=0x83a1,0x83a4
BASE_BUS=W.ControllerBus


def parent():
    raw=C.Owner.D.C.Owner.NIGHTLY.read_bytes()
    assert sha256(raw).hexdigest()==C.Owner.PIN
    return C.Owner.proposal(raw)[0]


def inputs(raw):
    image,info=C.proposal(raw);assert C.inverse(image)==raw
    return image,info


class GateMemory(list):
    def __init__(self,code):
        super().__init__([0]*65536)
        list.__setitem__(self,slice(C.BRIDGE,C.BRIDGE+45),code)
        self.writes=[]
    def __setitem__(self,at,value):
        assert at in(0x16a,0x16c,0x16d)
        self.writes.append((at,value));list.__setitem__(self,at,value)


def prefix(m,hurt,flags,p,a=85,x=71,y=109):
    list.__setitem__(m,0x6f1c,hurt);list.__setitem__(m,0x7ffb,flags)
    m.writes.clear();c=N.NesMPU(memory=m,pc=C.BRIDGE)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,246
    for _ in range(20):
        if c.pc==0x15a:
            active=bool(hurt|flags)
            assert(c.a,c.x,c.y,c.p,c.sp)==(0xcf if active else 0xbf,x,y,(p&~0x82)|0x80,246)
            assert m.writes==[(0x16a,hurt|flags),(0x16c,0xf5 if active else 0x21),
                             (0x16d,0xbd if active else 0xad)]
            return ISR.regs(c),tuple(m.writes),c.processorCycles
        assert m[c.pc]in(0xad,0x0d,0xf0,0x8d,0xa9,0x4c)
        c.step()
    raise AssertionError('Actual45-byte prefix bound')


def finite(raw):
    image,_=inputs(raw)
    models=[GateMemory(image[16+b*8192+0x2b:16+b*8192+0x2b+45])for b in(119,120,125,127)]
    pairs=0
    for hurt in range(256):
        for flags in range(256):
            expected=prefix(models[-1],hurt,flags,0x31)
            for m in models[:-1]:assert prefix(m,hurt,flags,0x31)==expected
            pairs+=1
    for value in range(256):
        for p in range(256):
            expected=prefix(models[-1],value,0,p,a=value^p,x=value,y=value^255)
            for m in models[:-1]:assert prefix(m,value,0,p,a=value^p,x=value,y=value^255)==expected
            pairs+=1
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,all_four_full45byte_windows_equal=True,
        all65536_hurt_cheat_byte_pairs=65536,all256_OR_values_all256_incoming_P=65536,
        alias_and_125_vs127_pairs=pairs*3,incoming_A_overwritten_by_first_actual_LDA=True,
        AXYP_SP_live_stack_and_ordered_SMC_writes_exact=True,
        explicit_prefix_ABI_units=True,whole_Main_or_native_claim=False,outputs=0)


class CanonicalOracle(BASE_BUS):
    """Only45 read-only canonical ROM instruction bytes; live sample map stays."""
    canonical_bank=127
    def __getitem__(self,at):
        if isinstance(at,int)and C.BRIDGE<=at<C.BRIDGE+45 and getattr(self,'rawtags',[0]*4)[3]in(247,248):
            return self.bundle['raw'][16+self.canonical_bank*8192+(at&8191)]
        return BASE_BUS.__getitem__(self,at)


def oracle(seed,raw,bank):
    m=Family.view(seed,raw)
    z=list.__new__(CanonicalOracle);list.extend(z,list.__iter__(m))
    for key,value in m.__dict__.items():setattr(z,key,value if key=='bundle'else copy.deepcopy(value))
    z.canonical_bank=bank
    return z


def caller_cpu(m,p=0x31):
    # Explicit real126:83A1 ABI/map fixture. SP248 produces the actual
    # observed E02B entrySP246 and CF:BDF5 targetSP243; no actor/stat seed.
    assert m.rawtags[0]==254
    m.raw_page(1,129);N.put(m,CurrentBank=129)
    c=N.NesMPU(memory=m,pc=CALL)
    c.a,c.x,c.y,c.p,c.sp=0x93,3,151,p,248
    return c


def stopped(c):return(c.pc,c.sp)==(RETURN,248)


def run(c,observe=None):
    hits=Counter();minimum=255
    for _ in range(500000):
        if stopped(c):return minimum,hits
        m=c.memory;tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if(tag,c.pc)==(207,0xbdf5):hits['canonical_game_cold']+=1
        if(tag,c.pc)==(207,0xbdde):hits['obsolete_UI_tail']+=1
        if c.pc==0x16e:hits['farcall_returns']+=1
        if observe:observe(c)
        minimum=min(minimum,c.sp)
        assert m[c.pc],('Actual cold caller BRK',hex(c.pc),c.sp,tuple(m.rawtags))
        c.step()
    raise AssertionError(('Actual cold caller bound',hex(c.pc),c.sp,tuple(c.memory.rawtags)))


def caller(raw):
    image,_=inputs(raw);cases=0;minimum=255
    for variant in range(8):
        seed=Family.cold(image,variant)
        for mask in(0,1,31):
            context=N.fork(seed);C.Owner.D.menu_mask(context,mask)
            for alias in(119,120):
                for canonical in(125,127):
                    for p in(0x31,0xe0):
                        a=Family.view(context,image);b=oracle(context,raw,canonical)
                        for m in(a,b):m.raw_page(3,alias|128)
                        ca,cb=caller_cpu(a,p),caller_cpu(b,p)
                        da,ha=run(ca);db,hb=run(cb)
                        assert ISR.regs(ca)==ISR.regs(cb)and ISR.full_state(a)==ISR.full_state(b)
                        assert a.writes==b.writes and a.ram_writes==b.ram_writes
                        assert ha==hb and not ha['obsolete_UI_tail']
                        assert ha['canonical_game_cold']==bool(mask)
                        assert a.rawtags[1]==N.get(a,'CurrentBank')==129 and a.rawtags[3]==alias|128
                        minimum=min(minimum,da,db);cases+=1
        print(json.dumps(dict(progress_caller_variant=variant,cases=cases),separators=(',',':')),flush=True)
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,actual126_83A1_to83A4_caller_pairs=cases,
        real8_menu_Start_cold_constructors=True,cheat_masks_from_compiled_menu_units=[0,1,31],
        canonical_ROM_oracles=[125,127],actual_alias_maps=[119,120],minimum_SP=minimum,
        full_AXYP_SP_RAM_WRAM_live_stack_SMC_maps_peripherals_ordered_writes_exact=True,
        explicit_caller_register_and_mapping_fixtures=True,live_state_masks_or_repairs=0,outputs=0)


def faults(raw):
    image,q=inputs(raw);tests=[]
    for name,data,fn,at in(
        ('parent_operand',raw,C.proposal,C.EDITS[0][0]),
        ('parent_unowned',raw,C.proposal,16),('parent_sample',raw,C.proposal,q['samples'][0]['file']),
        ('parent_owner_fix',raw,C.proposal,C.Owner.SPANS[0][0]),
        ('candidate_operand',image,C.inverse,C.EDITS[1][0]),
        ('candidate_unowned',image,C.inverse,16),('candidate_sample',image,C.inverse,q['samples'][3]['file'])):
        broken=bytearray(data);broken[at]^=1;tests.append((name,fn,bytes(broken)))
    tests.extend((('parent_truncated',C.proposal,raw[:-1]),('candidate_truncated',C.inverse,image[:-1]),
                  ('parent_as_candidate',C.inverse,raw),('candidate_as_parent',C.proposal,image)))
    for name,fn,data in tests:
        try:fn(data)
        except AssertionError:pass
        else:raise AssertionError(('Strict rejection failed',name))
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,rejections=[t[0]for t in tests],
        exact_e8_inverse=True,all8_samples_and_all_unowned_bytes_exact=True,outputs=0)


def family(raw):
    image,_=inputs(raw);count=0
    for variant in range(8):
        a=Family.cold(image,variant)
        with patch.object(W,'ControllerBus',CanonicalOracle):b=Family.cold(raw,variant)
        assert ISR.full_state(a)==ISR.full_state(b)
        for mask in(0,1,31):
            x,y=N.fork(a),N.fork(b)
            C.Owner.D.menu_mask(x,mask);C.Owner.D.menu_mask(y,mask)
            for pad in(0,1,129,1,0,2,0,64):
                for _ in range(2):
                    x.controller_pad=y.controller_pad=pad
                    dx,dy=Frames.frame(x,whole_pass=True),Frames.frame(y,whole_pass=True)
                    assert dx==dy and ISR.full_state(x)==ISR.full_state(y)
                    assert x.writes==y.writes and x.ram_writes==y.ram_writes
                    count+=1
        print(json.dumps(dict(progress_family_variant=variant,Main_pairs=count),separators=(',',':')),flush=True)
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,actual8cold_menu_Start_constructors=True,
        complete_Main_NMI_canonical_pairs=count,masks_from_actual_compiled_menu_units=[0,1,31],
        full_state_cycles_and_ordered_writes_exact=True,live_state_masks_or_repairs=0,outputs=0)


def interrupt_pair(m,source_cpu,raw,image,canonical,kind):
    a=Family.view(m,image);b=oracle(m,raw,canonical)
    expected=ISR.regs(source_cpu)
    protected=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+source_cpu.sp:0x200]))
    music_at=W.address(m.bundle,'S2AudioState');music_before=bytes(m[music_at:music_at+77])
    cpus=[];minimum=255;completed=0
    assert N.get(m,'NmiDisable')==255
    for model in(a,b):
        c=N.NesMPU(memory=model,pc=source_cpu.pc)
        for field in('a','x','y','p','sp'):setattr(c,field,getattr(source_cpu,field))
        maps=tuple(model.rawtags);skip=N.get(model,'NmiSkipped')
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(150000):
            minimum=min(minimum,c.sp)
            if(c.pc,c.sp)==(source_cpu.pc,source_cpu.sp):break
            assert not C.BRIDGE<=c.pc<C.BRIDGE+45,'ISR entered Main-only cold gate'
            assert model[c.pc],('Actual ISR BRK',kind,hex(c.pc),c.sp)
            c.step()
        else:raise AssertionError(('Actual ISR bound',kind,hex(c.pc)))
        assert ISR.regs(c)==expected
        assert(bytes(model[3:11]),bytes(model[0x15a:0x17b]),bytes(model[0x101+c.sp:0x200]))==protected
        if tuple(model.rawtags)!=maps:
            assert kind=='busyNMI'and c.pc in(0x166,0x175)
            assert bytes(m[c.pc-3:c.pc+3])==bytes.fromhex('8d45018d1551')
            assert c.a==N.get(model,'CurrentBank')==model.rawtags[1]
            assert maps[:1]+maps[2:]==tuple(model.rawtags[:1]+model.rawtags[2:])
            completed+=1
        assert N.get(model,'NmiSkipped')==(skip+(kind=='busyNMI'))&255
        cpus.append(c)
    assert ISR.full_state(a)==ISR.full_state(b)and a.writes==b.writes and a.ram_writes==b.ram_writes
    advanced=bytes(a[music_at:music_at+77])!=music_before
    if completed:
        assert completed==2
        for model,c in zip((a,b),cpus,strict=True):
            pc=c.pc;c.step()
            assert c.pc==pc+3 and model.rawtags[1]==N.get(model,'CurrentBank')
    for c in cpus:run(c)
    assert ISR.regs(cpus[0])==ISR.regs(cpus[1])and ISR.full_state(a)==ISR.full_state(b)
    assert a.writes==b.writes and a.ram_writes==b.ram_writes
    assert a.rawtags[1]==N.get(a,'CurrentBank')==129
    return minimum,advanced,completed//2


def vectors(raw):
    image,_=inputs(raw)
    # Reuse only the existing frozen ordinary source prefixes, not a restored
    # output tree. They naturally earn119 through Flower/B lift and120 from
    # first-Goomba injury. Only ROM is rebound for this directed caller unit.
    public=C.Owner.inverse(raw);legacy=C.Owner.D.C.inverse(public)
    samples,prefixes=ISR.busy_prefixes(legacy)
    seen=set();reached=set();counts=Counter();minimum=255;music=completed=0
    for bank in(119,120):
        context=Family.view(samples[bank],image)
        assert N.get(context,'SelectedCharacter')==25
        C.Owner.D.menu_mask(context,1)
        for canonical in(125,127):
            m=N.fork(context);c=caller_cpu(m)
            def observe(cpu):
                nonlocal minimum,music,completed
                mm=cpu.memory;tag=mm.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1
                relevant=tag==bank|128 and C.BRIDGE<=cpu.pc<C.BRIDGE+45 or 0x15a<=cpu.pc<0x17b
                if not relevant:return
                key=(bank,canonical,tag,cpu.pc,cpu.sp,cpu.p&4)
                if key in seen:return
                seen.add(key);reached.add((tag,cpu.pc))
                for kind in('IRQ','busyNMI'):
                    if kind=='IRQ'and cpu.p&4:continue
                    low,advanced,maps=interrupt_pair(mm,cpu,raw,image,canonical,kind)
                    minimum=min(minimum,low);music+=advanced;completed+=maps;counts[bank,kind]+=1
            run(c,observe)
            print(json.dumps(dict(progress_vectors_bank=bank,canonical=canonical,cuts=sum(counts.values())),separators=(',',':')),flush=True)
    assert {(247,0xe036),(248,0xe036)}<=reached
    assert all(counts[b,k]for b in(119,120)for k in('IRQ','busyNMI'))and music and minimum>=128
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,reached_instruction_SP_points=len(seen),
        cuts=[dict(bank=b,kind=k,cases=n)for(b,k),n in sorted(counts.items())],minimum_SP=minimum,
        both_changed_LDA_immediate_instructions_reached=True,
        genuine_source_sample_prefixes=prefixes,frozen_source_prefix_ROM_SHA256=sha256(legacy).hexdigest(),
        current_ROM_rebound_only_for_explicit_native_caller_unit=True,
        real_compiled_menu_Inv1_unit=True,paired_original_music_advances=music,
        exact_pending_A_map_completions=completed,pending_STA_executes_before_PRG_fetch=True,
        canonical125_127_ROM_only_oracles_actual119_120_sample_maps=True,
        complete_caller_RAM_WRAM_AXYP_SP_live_stack_SMC_maps_peripherals_ordered_writes_exact=True,
        audio_or_live_state_masks_or_repairs=0,natural_full_stage_or_waveform_deadline_claim=False,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('finite','caller','faults','family','vectors'),default='finite')
    args=p.parse_args();raw=parent()
    q=(finite(raw)if args.mode=='finite'else caller(raw)if args.mode=='caller'
       else family(raw)if args.mode=='family'else vectors(raw)if args.mode=='vectors'else faults(raw))
    print(json.dumps(q,separators=(',',':')),flush=True)
