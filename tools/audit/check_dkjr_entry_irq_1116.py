"""Reached7c0f IRQ/busy-NMI, actual public continuations and next-Main parity."""
from collections import Counter
from hashlib import sha256
import json

import check_dkjr_entry_components_1116 as K
import check_dkjr_entry_predicate_1116 as Predicate
import check_dkjr_entry_fruit_1116 as Fruit
import check_dkjr_carry_camera_irq_1116 as Helpers
import check_dkjr_retire_lease_1113 as ISR
import check_dkjr_footer_ryu_1116 as Native
import check_metal_head_bridge_1112 as Async

C,N,W,L=K.C,K.N,K.W,K.L
H=lambda value:sha256(value).hexdigest()
STOP=(0x5b00,224)


def inject_checked(cpu,kind,retired):
    """Bind nested0175 return to its actual PLA, not dead NextBank0162."""
    m=cpu.memory;maps=tuple(m.rawtags);shadow=N.get(m,'CurrentBank')
    nested=cpu.pc==0x175 and maps[1]!=cpu.a and m[0x162]!=maps[1]
    if not nested:return ISR.inject_checked(cpu,kind)
    assert bytes(m[0x171:0x178])==bytes.fromhex('688d')+W.address(m.bundle,'CurrentBank').to_bytes(2,'little')+bytes.fromhex('8d1551')
    assert [row[1]for row in retired[-2:]]==[0x171,0x172]
    assert retired[-1][2]==cpu.a==shadow==m[0x100+cpu.sp]
    assert bytes(m[0x15a:0x15d])==bytes.fromhex('8d6201')and m[0x161]==0xa9
    regs=(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)
    ram=tuple(bytes(row)for row in m.ram);scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b])
    live=bytes(m[0x101+cpu.sp:0x200]);writes=len(m.ram_writes);skipped=N.get(m,'NmiSkipped')
    replay=L.clone(m,cpu)
    try:return Async.inject(cpu,N.NesMPU,kind),False
    except AssertionError:
        assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)==regs
        assert tuple(bytes(row)for row in m.ram)==ram and bytes(m[3:11])==scratch
        assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+cpu.sp:0x200])==live
        assert len(m.ram_writes)==writes
        expected=list(maps);expected[1]=cpu.a
        assert m.rawtags==expected
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lagNMI'))&255
        q,c=replay
        if kind=='IRQ':c.irq()
        else:c.nmi()
        minimum=255
        for _ in range(80000):
            minimum=min(minimum,c.sp)
            if(c.sp,c.pc)==(regs[4],regs[5]):break
            assert q[c.pc];N.NesMPU.step(c)
        else:raise AssertionError(('Nested-return ISR bound',kind,hex(c.pc)))
        assert (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)==regs
        assert q.rawtags==m.rawtags and tuple(bytes(row)for row in q.ram)==ram
        assert bytes(q[3:11])==scratch and bytes(q[0x15a:0x17b])==smc
        after,step=L.clone(m,cpu);N.NesMPU.step(step)
        assert step.pc==0x178<0x8000 and after.rawtags==expected
        assert (step.a,step.x,step.y,step.p&0xef,step.sp)==regs[:5]
        assert tuple(bytes(row)for row in after.ram)==ram and bytes(after[0x15a:0x17b])==smc
        return minimum,True


def start(seed,labels,case):
    if case.get('fruit'):
        m=Fruit.prepared(seed,labels,4,0,0,190)
        m.ram[2][0x8fe]=2
        N.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,PlayerEntranceCtrl=0,TimerControl=0)
    else:m=Predicate.prepared(seed,**case.get('fields',{}))
    N.put(m,NmiDisable=255,FamilyMainCommit=1,CurrentOAMOffset=4)
    if case.get('ready')is not None:m.ram[2][0x8fe]=case['ready']
    if case.get('private'):
        c=N.NesMPU(memory=m,pc=case['private']);c.a=85
    else:
        name=case.get('entry','HuMovement');pc=N.address(m.bundle,name)
        m[0x16a]=85;m[0x16c],m[0x16d]=pc&255,pc>>8
        c=N.NesMPU(memory=m,pc=N.address(m.bundle,'FarCallCommon'))
        c.a=((N.location(m.bundle,name)-16)//8192)|128
    c.x,c.y,c.p,c.sp=0,18,case.get('P',0x31),224;c.stPushWord(0x5aff)
    W.clear_logs(m)
    return m,c


def replace_native_backing(m,raw):
    m.bundle=dict(m.bundle,raw=raw)
    for window,page in enumerate(m.rawtags):
        if page&128:m.raw_page(window,page)


def run():
    parent,raw,composition,fit,labels,sites,allowed,seeds,openings=K.setup()
    source_ranges=[(row['PC'],row['end_exclusive'])for row in fit['fragments']]
    cases=[dict(name='pending-zero',fields={'Player_Y_Speed':0}),
        dict(name='pending-positive-V1D1',fields={'Player_Y_Speed':2},P=0x69),
        dict(name='pending-timerFF',fields={'TimerControl':255,'Player_Y_Speed':2}),
        dict(name='ready2-normal',ready=2,fields={'Player_State':0,'Player_Y_Position':176}),
        dict(name='pending-draw-fall',entry='HuDraw',fields={'Player_Y_Speed':2}),
        dict(name='pending-draw-ground',entry='HuDraw',fields={'Player_State':0,'Player_Y_Position':176}),
        dict(name='ready2-typed-fruit',fruit=True),
        dict(name='ready0-defensive',private=0xbfc1,ready=0,next_Main=False),
        dict(name='context-reject-defensive',private=0xbfc1,fields={'profile':0},next_Main=False),
        dict(name='visible-reject-rising',entry='HuDraw',fields={'Player_State':1,'Player_Y_Speed':255})]
    counts=Counter();contexts=[];seen=set();reached=set();minimum=255;foreground_min=255
    for case in cases:
        base,cpu=start(seeds[1],labels,case)
        Helpers.run(base,cpu,STOP)
        expected=Helpers.gameplay(base,cpu)
        m,c=start(seeds[1],labels,case);cuts=0;own_seen=0;retired=[]
        for step in range(200000):
            if(c.pc,c.sp)==STOP:break
            tag=Helpers.tag(c);foreground_min=min(foreground_min,c.sp)
            own=tag==3 and any(lo<=c.pc<hi for lo,hi in source_ranges)
            bridge=(own_seen and(0x15a<=c.pc<0x17b or(tag,c.pc)in
                ((129,0xab48),(190,0xbaf9),(190,0xba75),(254,0x8bf8))))
            if own:own_seen+=1;reached.add(c.pc)
            key=(tag,c.pc,c.sp,c.p&0xcf)
            if(own or bridge)and key not in seen:
                seen.add(key);cuts+=1
                for kind in('IRQ','lagNMI'):
                    if kind=='IRQ'and c.p&4:
                        q,z=L.clone(m,c);before=Helpers.full(q,z);cycles=z.processorCycles;z.irq()
                        assert Helpers.full(q,z)==before and z.processorCycles==cycles
                        counts['masked_IRQ']+=1;continue
                    models=[]
                    for backing in(parent,raw):
                        q,z=L.clone(m,c);replace_native_backing(q,backing)
                        live=bytes(q[0x101+z.sp:0x200]);smc=bytes(q[0x15a:0x17b])
                        nested=z.pc==0x175 and q.rawtags[1]!=z.a and q[0x162]!=q.rawtags[1]
                        if nested:counts['authenticated_nested_return_windows']+=1
                        try:low,pending=inject_checked(z,kind,retired)
                        except AssertionError:
                            failure=dict(case=case['name'],kind=kind,cut=list(key),PC=z.pc,SP=z.sp,A=z.a,P=z.p,
                                maps=list(q.rawtags),CurrentBank=N.get(q,'CurrentBank'),NextBank0162=q[0x162],
                                popped_stack_byte=q[0x100+z.sp],preimage_171_17B=bytes(q[0x171:0x17b]).hex(),
                                SMC33=bytes(q[0x15a:0x17b]).hex(),ready=q.ram[2][0x8fe],
                                source_phase=q.ram[2][0x6b],native_Y=N.get(q,'Player_Y_Position'))
                            print('DKJR_ENTRY_IRQ_FIRST_FAILURE '+json.dumps(failure,separators=(',',':')),flush=True)
                            raise
                        minimum=min(minimum,low)
                        assert bytes(q[0x101+z.sp:0x200])==live and bytes(q[0x15a:0x17b])==smc
                        counts['pending_mapper_commit']+=int(pending)
                        models.append((q,z))
                    assert Helpers.full(*models[0])==Helpers.full(*models[1]),('Actual native ISR mismatch',case['name'],key,kind)
                    for q,z in models:
                        replace_native_backing(q,raw);Helpers.run(q,z,STOP)
                        assert Helpers.gameplay(q,z)==expected,('Continuation vs no-extra-ISR gameplay',case['name'],key,kind)
                    assert Helpers.full(*models[0])==Helpers.full(*models[1]),('Complete caller return',case['name'],key,kind)
                    if case.get('next_Main',True):
                        for q,z in models:Native.Q.frame(q,0)
                        assert Native.native_data(models[0][0])==Native.native_data(models[1][0]),('Next actual Main',case['name'],key,kind)
                        counts['next_actual_Main_pairs']+=1
                    counts[kind]+=1
            retired.append((tag,c.pc,c.a,c.sp))
            if len(retired)>2:retired.pop(0)
            N.NesMPU.step(c)
        else:raise AssertionError(('Reached-case bound',case['name'],hex(c.pc)))
        assert own_seen>0,('Public fixture did not reach new code',case['name'])
        contexts.append(dict(name=case['name'],new_cut_shapes=cuts,new_code_steps=own_seen,foreground_steps=step))
        print('DKJR_ENTRY_IRQ_PROGRESS '+json.dumps(dict(case=case['name'],cuts=len(seen),vectors=dict(counts)),separators=(',',':')),flush=True)
    assert all(any(lo<=pc<hi for pc in reached)for lo,hi in source_ranges)
    report=dict(passed=True,candidate_SHA256=H(raw),parent_native_ISR_backing_SHA256=H(parent),
        reached_new_PC_count=len(reached),unique_reached_PC_SP_P_shapes=len(seen),vectors=dict(counts),
        minimum_foreground_SP=foreground_min,minimum_ISR_SP=minimum,contexts=contexts,
        live_stack_and_all33_common_SMC_bytes_preserved=True,
        actual_parent_and_candidate_native_ISRs_full_state_equal=True,
        complete_caller_gameplay_matches_no_extra_ISR=True,next_actual_Main_pairs_equal=True,
        declared_components_only=True,no_unreached_instruction_coverage_claim=True,
        nested_return_binding='Actual0171 PLA ->0172 STA CurrentBank ->0175 STA5115; A==shadow==just-popped stack. NextBank remains byte-exact but is not a live callee-map witness after nested calls.',
        P_break_bit_normalization='Existing actual RP2A03 ISR comparator normalizes only nonphysical B; C/V/I/D/N/Z preserved.',outputs=0)
    return report


if __name__=='__main__':
    report=run();text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_IRQ '+text,flush=True)
    print('DKJR_ENTRY_IRQ_SHA256 '+H(text.encode()),flush=True)
