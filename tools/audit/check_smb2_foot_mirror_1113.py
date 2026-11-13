"""Exact mirror/source/caller/ABI checks; synthetic cells, zero artifacts."""
from collections import Counter
from hashlib import sha256
import argparse
import json
from unittest.mock import patch

import compose_smb2_foot_mirror_1113 as C
import check_bub_current_budget_1113 as Frames

F=C.Flag.Check
W=F.W
N=W.N
COLD=(4,11,22,26,28,43)


def references(raw):
    q=C.plan(raw);prg=raw[16:16+128*8192];refs={}
    for pc in(0xe45b,0xe46a,0xe46d,0xe496,0xe497):
        word=pc.to_bytes(2,'little')
        found=[at+16 for at in range(len(prg)-1)if prg[at:at+2]==word]
        transfers=[at for at in found if raw[at-1]in(0x20,0x4c)]
        refs[hex(pc)]=dict(words=found,JSR_JMP_operands=transfers)
    assert refs['0xe46a']['JSR_JMP_operands']==[16+126*8192+0x1c0b,16+126*8192+0x1c14]
    assert not refs['0xe46d']['JSR_JMP_operands']
    assert not refs['0xe496']['JSR_JMP_operands']
    for pc in(0xe46a,0xe46d,0xe496,0xe497):
        lo,hi=pc&255,pc>>8
        # Literal farcall producers: LDA #lo/STA016C,LDA #hi/STA016D.
        literal=bytes((0xa9,lo,0x8d,0x6c,1,0xa9,hi,0x8d,0x6d,1))
        refs[hex(pc)]['literal_farcall_producers']=[i+16 for i in range(len(prg)-len(literal)+1)if prg[i:i+len(literal)]==literal]
    assert not refs['0xe46d']['literal_farcall_producers']and not refs['0xe496']['literal_farcall_producers']
    return dict(passed=True,plan=q,inbound=refs,old_foot_and_side_no_live_transfer_references=True,outputs=0)


def invoke(m,pc,*,y=0,p=0x31,observe=None):
    c=N.NesMPU(memory=m,pc=pc);c.a=85;c.x=7;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    low=c.sp
    for _ in range(500000):
        if(c.pc,c.sp)==(0x5b00,224):return c,low
        if observe:observe(m,c)
        assert m[c.pc],('fixed worker BRK',hex(c.pc),m.rawtags)
        low=min(low,c.sp);c.step()
    raise AssertionError(('fixed worker bound',hex(c.pc),c.sp))


def app(m):
    return(bytes(m[:0x100]),bytes(m[0x1e1:0x8000]),tuple(bytes(z)for z in m.ram),tuple(m.rawtags[:3]))


def regs(c):return(c.a,c.x,c.y,c.p,c.sp,c.pc)


def pair(seed,image,pc,*,y=0,p=0x31,native_caller=False):
    baseline=None;minimum=255
    for bank in(127,*C.MIRRORS):
        m=F.view(seed,image);m.raw_page(3,bank|128)
        if native_caller:
            ret=N.invoke(m,'DoFootCheck',y=y,p=p);state=tuple(ret[k]for k in('A','X','Y','P'))
            depth=ret['minimum_SP']
        else:
            c,depth=invoke(m,pc,y=y,p=p);state=regs(c)
        assert m.rawtags[3]==bank|128
        result=state,app(m)
        if baseline is None:baseline=result
        else:assert result==baseline,(N.get(seed,'SelectedCharacter'),hex(pc),y,p,bank)
        minimum=min(minimum,depth)
    return minimum


def native_fixture(seed,owner):
    m=F.world_fixture(seed,x=40,y=176)
    N.put(m,SelectedCharacter=owner,Local_eb=0,NmiDisable=255)
    for xx in range(0,256,16):F.cell(m,xx,208,0x54)
    return m


def matrix(raw):
    image,info=C.all_mirrors_proposal(raw);seed=F.cold(image,4);counts=Counter();minimum=255
    # Generic path reads no private foreign state. Cold-owner contexts below
    # use their actual current menu/constructors, not this synthetic raw byte.
    for owner in range(256):
        if owner in COLD:continue
        for p in(0x30,0xf1):
            m=native_fixture(seed,owner)
            minimum=min(minimum,pair(m,image,0xe46a,p=p));counts['all_nonprivate_raw_feet_canonical_pairs']+=3
    for y in(0,1,7,14,21,28,35):
        for p in(0x30,0x31,0x70,0xf1):
            m=native_fixture(seed,25)
            for pc in(0xe45b,0xe46a,0xe497):
                minimum=min(minimum,pair(m,image,pc,y=y,p=p));counts['SMB2_head_feet_side_canonical_pairs']+=3
            minimum=min(minimum,pair(m,image,0xe46a,y=y,p=p,native_caller=True))
            counts['real_DoFootCheck_caller_canonical_pairs']+=3
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],canonical_fixed127_reference=True,
        counts=dict(counts),minimum_SP=minimum,AXYP_live_stack_native_RAM_overlay_SMC_A_C_maps_equal=True,
        each_actual_E_mirror_mapping_retained=True,synthetic_directed_cells=True,outputs=0,Mesen_run=False)


def foreign(raw):
    import audit_current_roster_powerups_1110 as Start
    image,info=C.all_mirrors_proposal(raw);rows=Start.Starts.C.inventory(raw)['rows']
    selected=[]
    for owner in COLD:
        row=next(q for q in rows if q['raw']==owner);selected.append(row)
    counts=Counter();minimum=255;names=[]
    for row in selected:
        _,seed=Start.cold(dict(W.Symbols.bundle(),raw=image),row);names.append(row['name'])
        for y in(0,1,14,30,31,32,35):
            for p in(0x31,0xf5):
                N.put(seed,Local_eb=y,NmiDisable=255)
                minimum=min(minimum,pair(seed,image,0xe46a,y=y,p=p))
                counts['actual_cold_private_foot_canonical_pairs']+=3
        for pad in(0,1,129):
            a=F.view(seed,raw);b=F.view(seed,image)
            for m in(a,b):m.controller_pad=pad;Frames.frame(m)
            assert app(a)==app(b)and a.rawtags==b.rawtags,(row['name'],pad,'actual Main')
            counts['actual_cold_foreign_Main_NMI_parent_pairs']+=1
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],actual_cold_names=names,counts=dict(counts),
        minimum_SP=minimum,synthetic_getter_y_inputs=True,ordinary_Menu_Main_opening_pairs=True,outputs=0,Mesen_run=False)


def exact_state(m):
    return(bytes(m[:0x8000]),tuple(bytes(z)for z in m.ram),tuple(m.rawtags))


def paired_interrupt(m,source_cpu,raw,image,kind):
    """Both actual old/new ISRs advance music; compare it without any mask."""
    native=N.NesMPU
    a=F.view(m,image);b=F.view(m,raw)
    cpus=[];depth=255
    before=(source_cpu.a,source_cpu.x,source_cpu.y,source_cpu.p&0xef,source_cpu.sp,source_cpu.pc)
    protected=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+source_cpu.sp:0x200]))
    audio=W.address(m.bundle,'S2AudioState');music_before=bytes(m[audio:audio+77])
    for model in(a,b):
        c=native(memory=model,pc=source_cpu.pc)
        for field in('a','x','y','p','sp'):setattr(c,field,getattr(source_cpu,field))
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(150000):
            depth=min(depth,c.sp)
            if(c.pc,c.sp)==(source_cpu.pc,source_cpu.sp):break
            assert not(0xe45b<=c.pc<0xe49a),'ISR unexpectedly entered a modified Main-only getter'
            assert model[c.pc],('paired ISR BRK',kind,hex(c.pc),model.rawtags)
            native.step(c)
        else:raise AssertionError('paired real ISR bound')
        assert(c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)==before
        assert(bytes(model[3:11]),bytes(model[0x15a:0x17b]),bytes(model[0x101+c.sp:0x200]))==protected
        cpus.append(c)
    assert exact_state(a)==exact_state(b),'Actual original/candidate ISR state or music advancement differs'
    changed=bytes(a[audio:audio+77])!=music_before
    # Original ISR has completed. Only now rebind its foreground to the new
    # getter, then compare the entire real caller continuation as well.
    b=F.view(b,image);cpus[1].memory=b
    for model,c in zip((a,b),cpus,strict=True):
        for _ in range(500000):
            if(c.pc,c.sp)==(0x5b00,224):break
            assert model[c.pc],('post-ISR getter BRK',kind,hex(c.pc))
            native.step(c)
        else:raise AssertionError('post-ISR caller bound')
    assert regs(cpus[0])==regs(cpus[1])and exact_state(a)==exact_state(b)
    return depth,changed


def vectors(raw):
    image,info=C.all_mirrors_proposal(raw);seed=F.cold(image,4)
    actual_busy=None
    for tick in range(240):
        # The original hurt request starts DMC. Walk into the authored first
        # Goomba just as the separately qualified natural-Mushroom route does.
        seed.controller_pad=1;Frames.frame(seed)
        bank=N.get(seed,'S2AudioActiveBank')
        if bank in(119,120)and seed[0x4015]&16:
            actual_busy=dict(Main=tick+1,active_bank=bank,status4015=seed[0x4015],
                x=N.get(seed,'Player_X_Position')+256*N.get(seed,'Player_PageLoc'),y=N.get(seed,'Player_Y_Position'))
            break
    assert actual_busy,'Genuine ordinary injury did not start a busy source sample'
    N.put(seed,NmiDisable=255)
    points=set();counts=Counter();minimum=255;advanced=0
    def observe(m,c):
        nonlocal minimum,advanced
        if not 0xe45b<=c.pc<0xe49a:return
        point=(m.rawtags[3],c.pc,c.sp,c.p&4)
        if point in points:return
        points.add(point)
        for kind in('IRQ','busy-lagNMI'):
            if kind=='IRQ'and c.p&4:continue
            low,changes=paired_interrupt(m,c,raw,image,kind)
            minimum=min(minimum,low);counts[kind]+=1
            if kind=='busy-lagNMI':advanced+=changes
    # Explicit mapping/cell inputs for each code mirror; the audio record and
    # busy status are controller-derived and never fabricated. Sample waveform
    # fetch parity is not inferred from this finite CPU/peripheral model.
    for bank in C.MIRRORS:
        m=F.view(seed,image);m.raw_page(3,bank|128)
        for pc in(0xe45b,0xe46a,0xe497):
            invoke(N.fork(m),pc,y=0,observe=observe)
    # Reach every comparison and the cold farcall tail under actual initialized
    # foreign owners. Their normal NMI progress is paired against the original.
    import audit_current_roster_powerups_1110 as Start
    rows=Start.Starts.C.inventory(raw)['rows'];names=[]
    for owner in COLD:
        row=next(q for q in rows if q['raw']==owner)
        _,m=Start.cold(dict(W.Symbols.bundle(),raw=image),row);names.append(row['name'])
        N.put(m,NmiDisable=255)
        for bank in C.MIRRORS:
            z=N.fork(m);z.raw_page(3,bank|128);invoke(z,0xe46a,y=0,observe=observe)
    assert counts['IRQ']and counts['busy-lagNMI']and minimum>=128 and advanced>0
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],changed_worker_points=len(points),
        real_paired_vectors=dict(counts),minimum_SP=minimum,genuine_source_busy_prefix=actual_busy,
        busy_NMIs_with_exact_paired_music_progress=advanced,foreign_initialized_owners=names,
        full_native_RAM_overlay_SMC_AXYP_live_stack_maps_and_continuation_exact=True,
        audio_or_clock_fields_masked=0,explicit_mirror_and_getter_fixtures=True,
        waveform_or_native_deadline_claim=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--matrix',action='store_true');p.add_argument('--foreign',action='store_true');p.add_argument('--vectors',action='store_true');args=p.parse_args()
    raw=F.load_input();q=vectors(raw)if args.vectors else foreign(raw)if args.foreign else matrix(raw)if args.matrix else references(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
