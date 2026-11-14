"""Private cheat-owner actual Main/cold/foreign/ISR checks; zero output files."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch
from py65.disassembler import Disassembler

import compose_smb2_cheat_owner_1113 as C
import check_smb2_postbg_irq_1113 as ISR
import check_current_roster_stage_ingress_1110 as Starts

D,W,N=C.D,C.W,C.N
Frames=D.Frames
Family=D.Flag


def inputs(raw):
    image,info=C.proposal(raw);assert C.inverse(image)==raw
    return image,info


def points(raw):
    b=dict(W.Symbols.bundle(),raw=raw)
    result={(W.address(b,n),((W.location(b,n)-16)//8192)|128):n
            for n in D.NAMES if n!='CheatsGameRoutinesGate::Native'}
    result[0xa2ce,191]='CheatsGameRoutinesGate::Native'
    return result


def owners(raw):
    image,_=inputs(raw);pts=points(image);counts=Counter();rows=[]
    for variant in range(8):
        seed=Family.cold(image,variant)
        reference=Family.cold(raw,variant)
        assert ISR.full_state(seed)==ISR.full_state(reference)
        # All-off goes through the untouched fixed fast path. This includes
        # actual controller, renderer, source actor and native parser state.
        a,b=N.fork(seed),N.fork(reference)
        for pad in (0,1,129,1,0,2,0,64):
            for _ in range(2):
                a.controller_pad=b.controller_pad=pad
                da,db=Frames.frame(a,whole_pass=True),Frames.frame(b,whole_pass=True)
                assert da==db and ISR.full_state(a)==ISR.full_state(b)
                assert a.writes==b.writes and a.ram_writes==b.ram_writes
                counts['all_off_complete_Main_NMI_exact_pairs']+=1
        for mask in range(32):
            m=N.fork(seed);D.menu_mask(m,mask);before=D.snapshot(m);calls=Counter()
            def observe(mm,c):
                if c.pc>=0x8000:
                    name=pts.get((c.pc,mm.rawtags[(c.pc-0x8000)//8192]))
                    if name:calls[name]+=1
            for _ in range(8):
                m.controller_pad=1;Frames.frame(m,observe,whole_pass=True)
            after=D.snapshot(m)
            assert after['CheatInvincible']==mask and after['NumberofLives']==2
            assert after['S2Ready']==178 and after['S2Health']>0
            assert after['GameEngineSubroutine']==8 and after['SavedJoypadBits']==1
            assert (after['S2Clock']-before['S2Clock'])&255==8
            assert after['x']>before['x']==40 and after['S2Held']==1 and after['S2VX']>0
            assert all(calls[n]==8 for n in ('S2MainGame','S2MainPlayer','S2NativeStart'))
            if mask:
                assert calls['CheatsGameRoutinesGate']==calls['CheatsGameRoutinesGate::Native']==8
                assert calls['S2BoundaryGame']==0
            else:assert calls['CheatsGameRoutinesGate']==0 and calls['S2BoundaryGame']==8
            rows.append(dict(variant=variant,mask=mask,before=before,after=after,calls=dict(calls)))
            counts['all8_all31_nonzero_masks_move'if mask else 'all8_zero_masks_move']+=1
        print(json.dumps(dict(progress_owner_variant=variant,cases=len(rows)),separators=(',',':')),flush=True)
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,counts=dict(counts),cases=len(rows),
        semantic_trace_SHA256=sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        all8_genuine_cold_menu_Start_constructors=True,
        flags_via_actual_compiled_menu_units=True,actor_position_health_ability_flag_seeds=0,
        full_stage_or_title_opening_source_claim=False,E037_aliases_unrepaired=True,outputs=0)


def roster(raw):
    inventory=Starts.C.inventory(raw)
    unique={(r['slot'],r['raw'],r['name']):r for r in inventory['rows']}
    assert len(unique)==101 and all(r['confirm_starts']for r in unique.values())
    return list(unique.values())


def cold(raw,row):
    """Actual current Select/Start/parser/cold; only established menu arena."""
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,row['slot'])
    for _ in range(row['cycle']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==row['name']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,k)for k in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError(('Genuine current cold bound',row['name']))


def foreign(raw):
    image,_=inputs(raw);rows=roster(raw);done=[];total=0;reached=Counter()
    for row in rows:
        if row['raw']==25:continue
        seed=cold(raw,row);owner=N.get(seed,'SelectedCharacter')
        # Constructor is all-off; candidate never changes that path. Keep
        # actual cold bytes/state and remap only the authenticated candidate.
        for mask in ((1,31)if owner in(0,2,24)else(1,)):
            a=N.fork(seed);b=Family.view(seed,image)
            D.menu_mask(a,mask);D.menu_mask(b,mask)
            calls=Counter()
            def observe(mm,c):
                if c.pc in(0xa2ce,0xaaf0)and mm.rawtags[1]==191:calls[hex(c.pc)]+=1
            for pad in(0,1,129,1,0,2,0,64):
                a.controller_pad=b.controller_pad=pad
                Frames.frame(a,whole_pass=True);Frames.frame(b,observe,whole_pass=True)
                assert ISR.full_state(a)==ISR.full_state(b),(row['name'],mask,pad,'full state')
                assert a.writes==b.writes and a.ram_writes==b.ram_writes,(row['name'],mask,pad,'ordered writes')
                total+=1
            reached.update(calls)
            done.append(dict(name=row['name'],owner=owner,mask=mask,calls=dict(calls)))
        print(json.dumps(dict(progress_foreign=row['name'],profiles=len(done)),separators=(',',':')),flush=True)
    assert len({r['name']for r in done})==93 and reached['0xaaf0']
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,actual_current_named_foreign_constructors=93,
        cheat_profiles=len(done),complete_Main_NMI_pairs=total,actual_foreign_calls=dict(reached),
        complete_RAM_WRAM_maps_peripherals_ordered_writes_exact=True,
        signature_SHA256=sha256(json.dumps(done,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        all_foreign_raw_owner_all_P_restore_ABI='Frozen b5df draft-abi65280pairs',
        menu_call_units=True,natural_full_stage_claim=False,outputs=0)


def faults(raw):
    image,_=inputs(raw);rejects=[]
    for name,data,fn,at in (
        ('parent_owned',raw,C.proposal,C.SPANS[0][0]),
        ('parent_padding',raw,C.proposal,C.SPANS[1][0]),
        ('parent_unowned',raw,C.proposal,16),
        ('parent_E037',raw,C.proposal,16+120*8192+0x37),
        ('parent_sample',raw,C.proposal,16+119*8192+0x1140),
        ('candidate_owned',image,C.inverse,C.SPANS[0][0]),
        ('candidate_unowned',image,C.inverse,16),
        ('candidate_retained_FF',image,C.inverse,518927)):
        broken=bytearray(data);broken[at]^=1
        try:fn(bytes(broken))
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Fault accepted',name))
    for name,fn,data in(('parent_truncated',C.proposal,raw[:-1]),
                       ('candidate_truncated',C.inverse,image[:-1]),
                       ('parent_as_candidate',C.inverse,raw),('candidate_as_parent',C.proposal,image)):
        try:fn(data)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Wrong image accepted',name))
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,strict_rejections=rejects,
                exact_inverse=True,all_unowned_bytes_and_all_DMC_sample_banks_exact=True,outputs=0)


def power_observation(raw):
    """Observe mask16 owner stats; no claim about all cheat trigger semantics."""
    image,_=inputs(raw);rows=[]
    for variant in range(8):
        m=Family.cold(image,variant);D.menu_mask(m,16);calls=Counter()
        names=('S2Health','S2MaxHealth','S2Vegetables','PlayerStatus','PlayerSize','S2Size')
        before={n:N.get(m,n)for n in names}
        pts={(W.address(m.bundle,n),((W.location(m.bundle,n)-16)//8192)|128):n
             for n in('NrFullPower','CheatsFullPower','S2FullPower')}
        def observe(mm,c):
            if c.pc>=0x8000:
                name=pts.get((c.pc,mm.rawtags[(c.pc-0x8000)//8192]))
                if name:calls[name]+=1
        for _ in range(8):m.controller_pad=1;Frames.frame(m,observe,whole_pass=True)
        after={n:N.get(m,n)for n in names}
        rows.append(dict(variant=variant,before=before,after=after,calls=dict(calls)))
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,mask16_observations=rows,
        observation_only=True,all_cheat_semantics_claim=False,
        wrap_and_midair_jump_triggers_not_qualified=True,source_stat_seeds=0,outputs=0)


def cpu_copy(m,c):
    z=N.NesMPU(memory=m,pc=c.pc)
    for field in('a','x','y','p','sp'):setattr(z,field,getattr(c,field))
    return z


def finish_main(c,stop,observe=None):
    for _ in range(500000):
        if c.processorCycles and(c.pc,c.sp)==stop:return
        if observe:observe(c)
        assert c.memory[c.pc],('Actual Main BRK',hex(c.pc),c.sp,tuple(c.memory.rawtags))
        c.step()
    raise AssertionError(('Actual Main bound',hex(c.pc),c.sp))


def interrupt_pair(m,c,raw,image,kind,stop):
    # Same actual cut, original parent ISR as the oracle. Only ROM is rebound
    # after RTI for the intended new foreground. No RAM/SMC/stack/audio repair.
    a=N.fork(m);b=Family.view(m,raw)
    ca,cb=cpu_copy(a,c),cpu_copy(b,c)
    protected=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]))
    music_at=W.address(m.bundle,'S2AudioState')
    music_before=bytes(m[music_at:music_at+77])
    expected=ISR.regs(c);minimum=255;pending=0
    assert N.get(m,'NmiDisable')==255,'Genuine Main busy admission'
    for model,cpu in((a,ca),(b,cb)):
        oldmaps=tuple(model.rawtags);skipped=N.get(model,'NmiSkipped')
        cpu.irq()if kind=='IRQ'else cpu.nmi()
        for _ in range(150000):
            minimum=min(minimum,cpu.sp)
            if(cpu.pc,cpu.sp)==(c.pc,c.sp):break
            tag=model.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1
            assert not(tag==191 and(0xa2a9<=cpu.pc<0xa2e2 or 0xaaf0<=cpu.pc<0xaaff))
            assert model[cpu.pc],('Original ISR BRK',kind,hex(cpu.pc),cpu.sp)
            cpu.step()
        else:raise AssertionError(('Original ISR bound',kind,hex(cpu.pc)))
        assert ISR.regs(cpu)==expected,('ISR registers',kind,hex(c.pc),expected,ISR.regs(cpu))
        assert(bytes(model[3:11]),bytes(model[0x15a:0x17b]),bytes(model[0x101+cpu.sp:0x200]))==protected
        if tuple(model.rawtags)!=oldmaps:
            assert c.pc in(0x166,0x175)and bytes(m[c.pc:c.pc+3])==bytes.fromhex('8d1551')
            assert kind=='busyNMI'and cpu.a==N.get(model,'CurrentBank')==model.rawtags[1]
            assert oldmaps[:1]+oldmaps[2:]==tuple(model.rawtags[:1]+model.rawtags[2:])
            pending+=1
        assert N.get(model,'NmiSkipped')==(skipped+(kind=='busyNMI'))&255
    assert ca.processorCycles==cb.processorCycles and ISR.full_state(a)==ISR.full_state(b)
    assert a.writes==b.writes and a.ram_writes==b.ram_writes
    advanced=bytes(a[music_at:music_at+77])!=music_before
    # Rebind only b's instruction ROM to the already authenticated candidate.
    # Its complete state/ordered writes at RTI already equals a, without edits.
    b=Family.view(b,image);cb.memory=b
    finish_main(ca,stop);finish_main(cb,stop)
    assert ISR.regs(ca)==ISR.regs(cb)and ISR.full_state(a)==ISR.full_state(b)
    assert a.writes==b.writes and a.ram_writes==b.ram_writes
    return minimum,advanced,pending//2


def vectors(raw):
    image,_=inputs(raw);rows=roster(raw)
    examples=[next(r for r in rows if r['slot']==0 and r['cycle']==0),
              next(r for r in rows if r['raw']==25 and r['cycle']==1),
              next(r for r in rows if r['slot']==1 and r['cycle']==0)]
    counts=Counter();seen=set();minimum=255;advanced=0;pending=0;contexts=[]
    for index,row in enumerate(examples):
        m=cold(image,row)
        # Ordinary neutral updates choose a real music-admitted busy phase;
        # no source clock, NMI-disable or audio field is seeded.
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        if index==2:
            # Explicit injury-service caller unit: actual InventoryHurt and
            # source HurtStart run; no source-health/hurt-kind/tick grant.
            N.invoke(m,'GuestInjuryStart',a=0,x=0,y=0,p=0x31)
            assert N.get(m,'GuestHurtKind')==1 and N.get(m,'GuestLegacyHurt')==1
            assert N.get(m,'GameEngineSubroutine')==9 and N.get(m,'GuestHurtTicks')==0
            declared='compiled GuestInjuryStart legacy frozen-swap unit after actual MegaMan cold'
        else:
            D.menu_mask(m,1);declared='actual Main after compiled menu-call Inv1 unit'
        m.controller_pad=1;W.clear_logs(m);N.consume(m)
        idle=W.address(m.bundle,'IdleLoop');c=N.NesMPU(memory=m,pc=idle)
        c.sp,c.p=255,0x31;c.stPushWord(0xe33b);stop=(idle,253)
        active=False;reached=set()
        def observe(cpu):
            nonlocal active,minimum,advanced,pending
            mm=cpu.memory;tag=mm.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1
            if(tag,cpu.pc)==(191,0xa2a9):active=True
            if active and((tag,cpu.pc)in((246,0xb86f),(129,0xa021),(138,0xb7c9))):active=False
            relevant=tag==191 and(0xa2a9<=cpu.pc<0xa2e2 or 0xaaf0<=cpu.pc<0xaaff or 0xad40<=cpu.pc<0xad52)
            relevant|=active and 0x15a<=cpu.pc<0x17b
            if not relevant:return
            key=(index,tag,cpu.pc,cpu.sp)
            if key in seen:return
            seen.add(key);reached.add(cpu.pc)
            for kind in('IRQ','busyNMI'):
                if kind=='IRQ'and cpu.p&4:continue
                low,music,maps=interrupt_pair(mm,cpu,raw,image,kind,stop)
                minimum=min(minimum,low);advanced+=music;pending+=maps;counts[kind]+=1
        finish_main(c,stop,observe)
        contexts.append(dict(name=row['name'],raw=N.get(m,'SelectedCharacter'),
            declared_fixture=declared,points=len(reached),source_clock=N.get(m,'S2Clock')))
        print(json.dumps(dict(progress_vector=row['name'],cuts=dict(counts)),separators=(',',':')),flush=True)
    memory=D.UnitMemory(True);dis=Disassembler(N.NesMPU(memory=memory))
    required=set()
    for lo,hi in((0xa2a9,0xa2e2),(0xaaf0,0xaaff)):
        pc=lo
        while pc<hi:required.add(pc);pc+=dis.instruction_at(pc)[0]
        assert pc==hi
    reached={pc for _,tag,pc,_ in seen if tag==191}
    assert required<=reached and counts['IRQ']and counts['busyNMI'] and minimum>=128
    assert advanced,'Real source music advances equally; no audio-state mask'
    return dict(passed=True,ROM_SHA256=C.CANDIDATE,contexts=contexts,
        reached_cut_instruction_SP_points=len(seen),cuts=dict(counts),minimum_SP=minimum,
        all_granted_instruction_PCs_reached=sorted(required),paired_real_music_advances=advanced,
        exact_pending_A_map_completions=pending,
        original_parent_ISR_and_complete_new_Main_continuations_exact=True,
        registers_RAM_WRAM_peripherals_live_stack_SMC_maps_ordered_writes_exact=True,
        live_state_masks_or_repairs=0,natural_damage_or_full_stage_claim=False,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('owners','foreign','faults','vectors','power'),default='owners')
    args=p.parse_args();raw=D.C.Owner.NIGHTLY.read_bytes()
    q=(owners(raw)if args.mode=='owners'else foreign(raw)if args.mode=='foreign'
       else vectors(raw)if args.mode=='vectors'else power_observation(raw)if args.mode=='power'else faults(raw))
    print(json.dumps(q,separators=(',',':')),flush=True)
