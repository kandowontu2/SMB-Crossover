"""Zero-output proposed DK raw2 C900..CCFF lease/cold/runtime audit.

The complete page remains UNALLOCATED. Images exist only in CPU fixtures.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
import re
import sys
from contextlib import redirect_stdout

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H

B,N,W,L=P.B,H.N,H.W,H.L
LO,HI=0x900,0xd00


def source_domains(parent):
    source,*_=P.T.old_source();lines=source.splitlines()
    instructions=[line.split(';',1)[0].strip().lower()for line in lines
        if re.match(r'^\s*(?:lda|ldx|ldy|sta|stx|sty|cmp|cpx|cpy|inc|dec|asl|lsr|rol|ror|and|ora|eor|adc|sbc|bit)\s',line)]
    assert not any(re.search(r'\$c(?:9|a|b|c)[0-9a-f]{2}\b',line)for line in instructions)
    indexed=[line for line in instructions if re.search(r'\$c8[0-9a-f]{2},[xy]',line)]
    reads={'lda $c8c8,x','lda $c8c9,x','lda $c8d0,x','lda $c8d1,x','lda $c8c0,x','lda $c8c1,x',
        'lda $c800,y','cmp $c802,y','lda $c801,y','cmp $c803,y'}
    stores={'sta $c8c0,x','sta $c8c8,x','sta $c8d0,x','sta $c8c1,x','sta $c8c9,x','sta $c8d1,x','sta $c800,y'}
    assert set(indexed)==reads|stores,(set(indexed)-(reads|stores))
    assert ' ldx #6\nPublish:'in source and ' dex\n dex\n bpl Publish'in source
    # The sole selector source is constructor/reset value1, hence table X=0.
    selector_writes=[line.strip()for line in lines if re.match(r'^\s*(?:sta|stx|sty|inc|dec) \$c04a\b',line)]
    assert selector_writes==['sta $c04a','sta $c04a']
    assert source.count(' lda #1\n sta $c04a')==2
    hidden=set(re.findall(r'^(DIndirect_[0-9a-f]{4}):',source,re.M))
    fruit={f'DIndirect_{q}'for q in('d973','d978','d9b6','d9c7')}
    descriptors={f'DIndirect_{q}'for q in('eb96','eb9f','eba4','eba9','ebd0','ebd9')}
    render={f'DIndirect_{q}'for q in('ea95','eaa5','eaac','eab0','eac4','ead0','eaf6','eaf9','eaff','eb2a','eb2d','eb33','eb54')}
    assert hidden==fruit|descriptors|render and len(hidden)==23
    assert ' lda #0\n sta $c091\n lda #4\n sta $c092'in source
    assert source.count(' sta $c091\n')==source.count(' sta $c092\n')==1
    assert 'D_ea24: ; original $EA24: lda #$02\n lda #$02\nD_ea26: ; original $EA26: sta $05\n sta $c005'in source
    # Typed geometry tables publish C800/C840/C880 only; original RAM
    # descriptors below0800 plus any byte Y cannot exceed C8FE.
    # Native original immutable descriptors are relocated inside A000..BFE0.
    labels=P.frozen_labels();at=labels['DkjrSourceData']
    block=source[source.index('DData_c2cd:'):source.index('D_e893:')]
    definitions=''.join(f'{name}=${at+int(name[6:],16)-0xc2cd:x}\n'for name in sorted(set(re.findall(r'\bDData_c[0-9a-f]{3}\b',block))))
    data_image=P.T.assemble(definitions+'.segment "DATA"\n'+block,dict(DATA=(at,256)))
    assert data_image['used']['DATA']==256
    assert P.T.payload(parent)[at-0xa000:at-0xa000+256]==data_image['images']['DATA']
    data=[pc for name,pc in data_image['symbols'].items()if name.startswith('DData_')]
    assert data and all(0xa000<=pc<0xbfe0 for pc in data)
    parts=P.parts(parent);effect=P.effect_parts(parent)
    patch_instructions=[i for part in(parts['head'],parts['predicate'],parts['extras'],parts['body']['new'])for i in part['instructions']]
    for i in patch_instructions:
        operand=i.get('operand')
        if isinstance(operand,int)and 0xc900<=operand<0xcd00 and i['mode']!='rel':
            assert i['op']in('JMP','JSR'),i
    return dict(retained_source_SHA256=P.T.FROZEN_SHA,translated_indirect_sites=23,
        original_source_no_C900_CCFF_operand=True,C8_indexed_sites=len(indexed),
        geometry_publish_X=[6,4,2,0],geometry_publish_maximum=0xc8d7,
        validated_list_maximum=0xc8ff,translated_RAM_byte_index_maximum=0xc8fe,
        selector_C04A_writes=2,selector_values=[1],table_read_X=0,
        indirect_domains=dict(fruit=[0xc400,0xc41d],render=[0xc200,0xc3ff],
            descriptor=['immutableA000..BFE0','validatedC800/C840/C880']),
        current_effect_bytes_reproduced=effect['end']-effect['start'],
        new_runtime_services_do_not_write_lease=True,native_ready=False)


def manager(seed):
    m=L.clone(seed);m.bundle=dict(m.bundle,syms=dict(m.bundle['syms']),segs=dict(m.bundle['segs']))
    at=16+65*8192+0xe00
    assert m.bundle['raw'][at:at+10]==bytes.fromhex('08488a489848a900f008')
    m.bundle['segs']['DKRetireCoCold']=dict(start=str(0xae00),ooffs=str(at))
    m.bundle['syms']['CoCold']=dict(val=str(0xae00),seg='DKRetireCoCold')
    prefix=m.bundle['raw'][at:at+32];retire_prefix=bytes.fromhex('08488a489848a901')
    assert prefix.count(retire_prefix)==1
    m.bundle['syms']['CoRetire']=dict(val=str(0xae00+prefix.index(retire_prefix)),seg='DKRetireCoCold')
    return m


def cold_cases(seed,candidate,info):
    payload=P.T.payload(candidate);cookie=bytes.fromhex(info['cookie']);rows=[]
    for fault in(None,(2,0x900),(2,0xbe0),(2,0xc60),(2,0xcff),(3,0xdea),(2,0x1000),(2,0x17ff)):
        m=manager(seed);m.bundle=dict(m.bundle,raw=candidate)
        m.ram[2][LO:HI]=bytes((i*73+19)&255 for i in range(HI-LO))
        m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        N.put(m,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
            Mirror_PPUMASK=0,NmiDisable=255)
        Base=type(m)
        class Reads(Base):
            def __getitem__(self,at):
                value=Base.__getitem__(self,at)
                if isinstance(at,int)and at>=0x8000:
                    raw=self.rawtags[(at-0x8000)//8192]
                    if not raw&128:
                        key=(raw&3,at&8191)
                        if key[0]==2 and LO<=key[1]<HI:self.page_reads[key[1]]+=1
                        if self.read_fault==key:self.fault_reads+=1;return value^1
                return value
        m.__class__=Reads;m.read_fault=fault;m.fault_reads=0;m.page_reads=Counter()
        W.clear_logs(m);before=m.ppu_reads;result=N.invoke(m,'CoCold',p=0x21)
        cold_reads=m.ppu_reads-before
        assert bool(result['P']&1)==(fault is None)
        assert not m.blocked
        if fault is None:
            assert cold_reads==22550,cold_reads
            assert bytes(m.ram[2][LO:HI])==payload[8192:9216]
            assert bytes(m.ram[2][:LO])==bytes(LO)
            assert bytes(m.ram[3][:0x1fe0])==payload[:0x1fe0]
            assert bytes(m.ram[2][0x1000:0x1800])==payload[9*1024:]
            assert set(m.page_reads)==set(range(LO,HI)) and all(n==1 for n in m.page_reads.values())
            ready=[(j,b,o,v)for j,(b,o,v)in enumerate(m.ram_writes)if b in(2,3)and o==0x1fe0 and v==167]
            assert [(b,o,v)for _,b,o,v in ready]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            last_page_write=max(j for j,(b,o,v)in enumerate(m.ram_writes)if b==2 and LO<=o<HI)
            assert ready[0][0]>last_page_write
            assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
            reads=m.ppu_reads;W.clear_logs(m);warm=N.invoke(m,'CoCold',p=0x21)
            assert warm['P']&1 and m.ppu_reads==reads
            assert not any(b==2 and LO<=o<HI for b,o,v in m.ram_writes)
        else:
            assert m.fault_reads and all(m.ram[b][0x1fe0]!=167 for b in(2,3))
            pending=[]
            def watch(memory,cpu):
                if cpu.pc>=32768 and memory.rawtags[(cpu.pc-32768)//8192]==2 and 0xc900<=cpu.pc<0xcd00:
                    pending.append(cpu.pc)
            W.clear_logs(m);L.call(m,'HuMovement',p=0x21,observe=watch)
            assert not pending and all(m.ram[b][0x1fe0]!=167 for b in(2,3))
            # Failed bytes are disposable; genuine retry copies/verifies the
            # complete page before either full ready cookie becomes visible.
            m.read_fault=None;again=N.invoke(m,'CoCold',p=0x21)
            assert again['P']&1 and bytes(m.ram[2][LO:HI])==payload[8192:9216]
            assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        rows.append(dict(fault=fault,accepted=bool(result['P']&1),fault_reads=m.fault_reads,
            complete_new_page_verify=fault is None,PPU_reads=cold_reads,minimum_SP=result['minimum_SP']))
    wrong=0
    for mask,disabled,lag in((24,1,255),(0,0,255),(0,1,0)):
        m=manager(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        prior=bytes(m.ram[2][LO:HI]);N.put(m,Mirror_PPUMASK=mask,DisableScreenFlag=disabled,NmiDisable=lag)
        before=m.ppu_reads;W.clear_logs(m);result=N.invoke(m,'CoCold',p=0x21)
        assert not result['P']&1 and m.ppu_reads==before and bytes(m.ram[2][LO:HI])==prior
        wrong+=1
    return dict(rows=rows,wrong_phase_rejections=wrong,new_page_bytes_copied_and_read_back=1024,
        cold_program_pages=9,complete_page_PPU_read_cost=2050,expected_total_PPU_reads=22550,
        common_clear_remains_half_open=[0xc000,0xc900],both_headers_last_after_verify=True,
        failed_ready_rejected_and_full_retry_passed=True,warm_no_copy_or_new_page_write=True,
        native_ready=False,scope='Actual current CoCold under declared read faults, no emulator qualification claim.')


def route(seed,candidate,info,*,full=False,ride_fourth=False,fourth_window=False,ledge_wait=False,stationary_wait=False,early_stairs=False,riser_retreat=False,landing_prep=False,settled_stairs=False,roof_trace=False,contact_trace=False):
    m=L.clone(seed);page=bytes(m.ram[2][LO:HI]);counts=Counter();updates=0;trace=[];writers=[]
    previous=None;output=sys.stdout;still=None;longest_still=[]
    def finish_still():
        nonlocal still
        if still is not None:
            still['updates']=still['end']-still['start']
            if still['updates']>=12:
                longest_still.append(still)
                longest_still.sort(key=lambda row:row['updates'],reverse=True)
                del longest_still[12:]
            still=None
    source=P.T.payload(candidate)[:8160]
    state_writes={0xa000+i for i in range(len(source)-2)if source[i:i+3]==bytes.fromhex('8d6bc0')}
    class CompactOutput:
        suppress_newline=False
        def write(self,value):
            if value.startswith('SMB_NATIVE_RECEIPT '):
                receipt=json.loads(value[19:]);print('DKJR_RETIRE_CPU_RECEIPT '+json.dumps(dict(
                    canonical_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                    passed=receipt['passed'],reason=receipt['reason'],terminal=receipt['terminal']),separators=(',',':')),file=output,flush=True)
                self.suppress_newline=True
            elif value=='\n'and self.suppress_newline:self.suppress_newline=False
            else:output.write(value)
        def flush(self):output.flush()
    def observe(memory,cpu):
        if not(roof_trace or contact_trace)or updates<4200 or cpu.pc not in state_writes or memory.rawtags[1]!=3:return
        player=B.state(memory)['x']
        if (roof_trace and 930<=player<=1000)or(contact_trace and 1140<=player<=1290):
            if len(writers)>=64:del writers[16]
            writers.append(dict(update=updates,pc=cpu.pc,value=cpu.a,SP=cpu.sp,
                previous=memory.ram[2][0x6b],fall_start=memory.ram[2][0x76],source_body_y=memory.ram[2][0x210],
                native=B.state(memory),actors=[dict(slot=i,id=N.get(memory,'Enemy_ID',i),state=N.get(memory,'Enemy_State',i),
                    x=N.get(memory,'Enemy_X_Position',i)+256*N.get(memory,'Enemy_PageLoc',i),y=N.get(memory,'Enemy_Y_Position',i),
                    passenger=N.get(memory,'PlatformCollisionFlag',i))for i in range(6)if N.get(memory,'Enemy_Flag',i)]))
    def after(memory):
        nonlocal updates,previous,still
        updates+=1
        for bank,off,value in memory.ram_writes:
            if bank==2 and LO<=off<HI:counts['lease_writes']+=1
        assert bytes(memory.ram[2][LO:HI])==page
        player=B.state(memory)['x']
        now=B.state(memory)
        if previous is not None and previous['x']==player:
            if still is None:still=dict(start=updates-1,end=updates,x=player,start_y=previous['y'],end_y=now['y'])
            else:still.update(end=updates,end_y=now['y'])
        else:finish_still()
        previous=now
        if (roof_trace and 930<=player<=1000)or(contact_trace and 1140<=player<=1290):
            row=dict(update=updates,**B.state(memory),fall_start=memory.ram[2][0x76],
                actors=[dict(slot=i,id=N.get(memory,'Enemy_ID',i),state=N.get(memory,'Enemy_State',i),
                    x=N.get(memory,'Enemy_X_Position',i)+256*N.get(memory,'Enemy_PageLoc',i),y=N.get(memory,'Enemy_Y_Position',i),
                    passenger=N.get(memory,'PlatformCollisionFlag',i))for i in range(6)if N.get(memory,'Enemy_Flag',i)])
            if len(trace)<16 or updates%4==0 or row['source_state']==5:
                if len(trace)>=96:del trace[16]
                trace.append(row)
        if updates%1000==0:print('DKJR_RETIRE_ROUTE_PROGRESS '+json.dumps(dict(full=full,updates=updates,player=B.state(memory)),separators=(',',':')),flush=True)
    with redirect_stdout(CompactOutput()):result=B.route(m,candidate,12000 if full else 2000,
        controller_text=P.controller(candidate,full=full,ride_fourth=ride_fourth,fourth_window=fourth_window,ledge_wait=ledge_wait,stationary_wait=stationary_wait,early_stairs=early_stairs,riser_retreat=riser_retreat,landing_prep=landing_prep,settled_stairs=settled_stairs),after_frame=after,
        observe_extra=observe if(roof_trace or contact_trace)else None)
    assert not counts['lease_writes']
    finish_still();events=result['receipt'].get('events',[])
    intervals=sorted((dict(updates=z['Main']-a['Main'],start=a['Main'],end=z['Main'],
        event=a['event'],next_event=z['event'],start_x=a['x'],end_x=z['x'])for a,z in zip(events,events[1:])),
        key=lambda row:row['updates'],reverse=True)[:12]
    return dict(passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
        controller_SHA256=result['controller_SHA256'],receipt=dict(
            canonical_SHA256=sha256(json.dumps(result['receipt'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            passed=result['receipt']['passed'],reason=result['receipt']['reason'],terminal=result['receipt']['terminal'],
            birth_lefts=sorted(result['receipt'].get('births',{})),carry_lefts=sorted(result['receipt'].get('carries',{})),
            late_events=[row for row in result['receipt'].get('events',[])if row['x']>=2080][-24:]),
        roof_trace=trace[:8]+trace[-24:]if len(trace)>32 else trace,source_state_writers=writers,immutable_page_runtime_writes=0,
        longest_same_X_runs=longest_still,largest_phase_intervals=intervals,
        full=full,ride_fourth=ride_fourth,fourth_window=fourth_window,ledge_wait=ledge_wait,stationary_wait=stationary_wait,early_stairs=early_stairs,riser_retreat=riser_retreat,landing_prep=landing_prep,settled_stairs=settled_stairs,physical_cadence_claim=False,native_ready=False)


def header_guards(seed,info):
    calls=0
    callbacks=('HuMovement','HuDraw','HuHead','HuSide','HuFresh','HuPickup','HuPowerup')
    for bank in(2,3):
        for byte in range(16):
            for name in callbacks:
                m=L.clone(seed);m.ram[bank][0x1fe0+byte]^=1;before=tuple(bytes(q)for q in m.ram)
                seen=[]
                def watch(memory,cpu):
                    if cpu.pc>=32768 and memory.rawtags[(cpu.pc-32768)//8192]in(2,3):seen.append(cpu.pc)
                reads=m.ppu_reads;L.call(m,name,a=0,x=5,y=3,p=0x61,observe=watch)
                assert not seen and tuple(bytes(q)for q in m.ram)==before and m.ppu_reads==reads,(bank,byte,name)
                calls+=1
    return dict(both_headers_all16_bytes=True,rejected_public_calls=calls,
        private_execution_PPU_and_WRAM_unchanged=True,native_ready=False)


def retirement_lifecycle(seed,candidate,info):
    rows=[];page=P.T.payload(candidate)[8192:9216];cookie=bytes.fromhex(info['cookie'])
    for owner in(9,37,38,39,41):
        m=manager(seed);prior_page=bytes(m.ram[2][LO:HI]);status=N.get(m,'PlayerStatus')
        N.put(m,SelectedCharacter=owner,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
            Mirror_PPUMASK=0,NmiDisable=255)
        W.clear_logs(m);N.invoke(m,'CoRetire',p=0x21)
        assert all(m.ram[b][0x1fe0]!=167 for b in(2,3))
        assert bytes(m.ram[2][LO:HI])==prior_page
        seen=[]
        def watch(memory,cpu):
            if cpu.pc>=32768 and memory.rawtags[(cpu.pc-32768)//8192]in(2,3):seen.append(cpu.pc)
        L.call(m,'HuMovement',a=0,x=5,y=3,p=0x61,observe=watch)
        assert not seen
        # Declared incoming-owner fixture, not a simulated foreign game's
        # constructor. Shared retirement must already end the old lease.
        m.ram[2][LO:HI]=bytes((i*29+owner)&255 for i in range(HI-LO))
        N.put(m,SelectedCharacter=40)
        cold=N.invoke(m,'CoCold',p=0x21)
        assert cold['P']&1 and bytes(m.ram[2][LO:HI])==page
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        assert m.ram[2][0x8fe]==0
        fresh=N.invoke(m,'HuFresh',p=0x21)
        assert fresh['P']&1 and m.ram[2][0x8fe]==1
        assert m.ram[2][0x6b]==1 and m.ram[2][0x4a]==1 and N.get(m,'PlayerStatus')==status
        rows.append(dict(selected_foreign_owner=owner,shared_exit_invalidates_both=True,
            inactive_page_not_executed=True,declared_foreign_page_overwrite=True,
            complete_DK_recopy_and_constructor=True))
    return dict(rows=rows,native_ready=False,
        scope='Actual shared retirement, public wrong-owner rejection and DK cold/Fresh reentry. Foreign page contents are explicitly seeded; no complete foreign-game ingress or native gameplay claim.')


def inject_checked(cpu,kind):
    """Keep the inherited immediate ISR check except exact pending mapper STA.

    FarCallCommon writes its shadow immediately before unbanked STA5115.
    LagNMI may perform that same mapping early; no banked instruction runs
    before the pending STA. Do not repair the map or waive continuation tests.
    """
    import check_metal_head_bridge_1112 as Async
    m=cpu.memory;regs=(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)
    maps=tuple(m.rawtags);ram=tuple(bytes(q)for q in m.ram);scratch=bytes(m[3:11])
    smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes);skipped=N.get(m,'NmiSkipped')
    preimage=bytes((0x8d,))+W.address(m.bundle,'CurrentBank').to_bytes(2,'little')+bytes.fromhex('8d1551')
    pending=cpu.pc in(0x166,0x175)and bytes(m[cpu.pc-3:cpu.pc+3])==preimage and cpu.a==N.get(m,'CurrentBank')
    if pending and maps[1]!=cpu.a:
        if cpu.pc==0x166:assert m[0x100+((cpu.sp+1)&255)]==maps[1]
        else:assert m[0x162]==maps[1]
    replay=L.clone(m,cpu)if pending else None
    try:return Async.inject(cpu,N.NesMPU,kind),False
    except AssertionError:
        assert pending,('ISR immediate mismatch outside authenticated mapper window',kind,regs,maps,m.rawtags)
        assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)==regs
        assert tuple(bytes(q)for q in m.ram)==ram and bytes(m[3:11])==scratch
        assert bytes(m[0x15a:0x17b])==smc and len(m.ram_writes)==writes
        expected=list(maps);expected[1]=cpu.a
        assert m.rawtags==expected
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lagNMI'))&255
        # Repeat the same real vector on a pre-interrupt clone to measure
        # actual stack depth; do not substitute a projected push count.
        q,c=replay
        if kind=='IRQ':c.irq()
        else:c.nmi()
        low=255
        for _ in range(80000):
            low=min(low,c.sp)
            if(c.sp,c.pc)==(regs[4],regs[5]):break
            assert q[c.pc];N.NesMPU.step(c)
        else:raise AssertionError(('ISR mapper-window bound',kind,hex(c.pc)))
        assert (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)==regs
        assert q.rawtags==m.rawtags and tuple(bytes(r)for r in q.ram)==ram
        assert bytes(q[3:11])==scratch and bytes(q[0x15a:0x17b])==smc
        # Execute the pending store on a clone: the very next instruction
        # remains unbanked and commits the exact shadow before a banked fetch.
        after,step=L.clone(m,cpu);N.NesMPU.step(step)
        assert step.pc==regs[5]+3<0x8000 and after.rawtags==expected
        assert (step.a,step.x,step.y,step.p&0xef,step.sp)==regs[:5]
        assert tuple(bytes(r)for r in after.ram)==ram and bytes(after[0x15a:0x17b])==smc
        return low,True


def cold_interrupts(seed,candidate,info):
    m=manager(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
    N.put(m,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
    samples={}
    def observe(memory,cpu):
        if memory.rawtags[2]!=2 or not(0xd25e<=cpu.pc<0xd2d5):return
        if memory[5]not in(8,9)or cpu.y not in(0,127,255):return
        key=(cpu.pc,memory[5],cpu.y,cpu.p&4)
        if key not in samples:samples[key]=L.clone(memory,cpu)
    c=L.call(m,'CoCold',p=0x21,observe=observe);assert c.p&1 and samples
    def result(q):
        return(tuple(q.rawtags),tuple(bytes(r)for r in q.ram),bytes(q[0x15a:0x17b]),
            tuple(q.chr_latches),q.upper,q.lastset,q.ppu_addr,q.toggle,q.buffer,q.ppu_reads)
    expected=result(m);counts=Counter();minimum=255
    for key,(state,cpu)in sorted(samples.items()):
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and cpu.p&4:
                q,d=L.clone(state,cpu);before=(d.pc,d.sp,d.a,d.x,d.y,d.p,d.processorCycles,result(q))
                d.irq();assert before==(d.pc,d.sp,d.a,d.x,d.y,d.p,d.processorCycles,result(q))
                counts['maskedIRQ']+=1;continue
            q,d=L.clone(state,cpu);low,_=inject_checked(d,kind);minimum=min(minimum,low)
            L.finish(q,d,(0x5b00,224));assert d.p&1 and result(q)==expected,(key,kind)
            counts[kind]+=1
    assert counts['maskedIRQ']and counts['lagNMI']and minimum>=128
    return dict(cuts=dict(counts),sample_points=len(samples),minimum_ISR_SP=minimum,
        actual_ninth_row_and_done_paths=True,complete_cold_WRAM_headers_mapper_PPU_equal=True,
        native_ready=False)


def interrupts(parent,seed,candidate,info):
    import check_metal_head_bridge_1112 as Async
    parts=P.parts(parent);samples={};expected={};frame_keys=set();pending=None;deepest=255
    ranges=[(3,pc,pc+size)for pc,size in P.T.LAYOUT.values()]
    ranges.extend(((3,0xaeef,0xaf27),(3,parts['alias_address'],parts['alias_address']+22),
        (3,parts['body']['start'],parts['body']['end']),
        (3,0xb624,0xb6a5),(3,0xb7ca,0xb7e8),
        (2,0xcbe0,0xcbe0+55),(2,0xcc60,0xcc60+26)))
    m=L.clone(seed);N.put(m,NmiDisable=255,FamilyMainCommit=1,GamePauseStatus=0)
    def observe(memory,cpu):
        nonlocal pending,deepest
        if pending==(cpu.pc,cpu.sp):pending=None
        if cpu.pc==P.T.SCORE_START and memory.rawtags[1]==3:
            pending=(memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255)
        tag=memory.rawtags[(cpu.pc-32768)//8192]if cpu.pc>=32768 else None
        key=None
        if pending and cpu.sp<deepest:deepest=cpu.sp;key=(0x10000,cpu.p&4)
        if any(tag==bank and lo<=cpu.pc<hi for bank,lo,hi in ranges):key=(tag,cpu.pc,cpu.p&4)
        if key is not None and(key not in samples or cpu.sp<samples[key][1].sp):
            samples[key]=L.clone(memory,cpu);frame_keys.add(key)
    def result(memory):
        return tuple(memory.rawtags),bytes(memory.ram[2]),bytes(memory.ram[3]),B.state(memory),bytes(memory[0x15a:0x17b])
    def after(memory):
        value=result(memory)
        for key in frame_keys:expected[key]=value
        frame_keys.clear()
    natural=B.route(m,candidate,2000,controller_text=P.controller(candidate),observe_extra=observe,after_frame=after)
    assert natural['passed']and samples
    # Reuse the deepest genuine Main->refresh->C9 entry stack, then declare
    # only a fully off-left owned actor. This covers the taken native erase
    # continuation without pretending the coordinate setup was controller-only.
    entry=min((value for key,value in samples.items()if len(key)==3 and key[:2]==(2,0xcbe0)),
        key=lambda value:value[1].sp)
    q,c=L.clone(*entry);slot=c.x;assert slot<6
    N.put(q,SelectedCharacter=40,WorldNumber=0,LevelNumber=0,AreaDataLow=0xce,
        ScreenLeft_X_Pos=609&255,ScreenLeft_PageLoc=609>>8,ObjectOffset=slot)
    for name,value in dict(Enemy_Flag=1,Enemy_ID=37,Enemy_State=0,Enemy_X_Position=560&255,
        Enemy_PageLoc=560>>8,Enemy_BoundBoxCtrl=5,PlatformCollisionFlag=255).items():
        q[W.address(q.bundle,name)+slot]=value
    service_return=(q[0x100+((c.sp+1)&255)]+256*q[0x100+((c.sp+2)&255)]+1,(c.sp+2)&255)
    erase_samples={};erase_seen=False
    def erase_watch(memory,cpu):
        nonlocal erase_seen
        if cpu.pc==0x8d2f:erase_seen=True
        tag=memory.rawtags[(cpu.pc-32768)//8192]if cpu.pc>=32768 else 0
        key=(1000+tag,cpu.pc,cpu.p&4)
        if key not in erase_samples or cpu.sp<erase_samples[key][1].sp:
            erase_samples[key]=L.clone(memory,cpu)
    L.finish(q,c,service_return,observe=erase_watch)
    assert erase_seen and not N.get(q,'Enemy_Flag',slot)
    stop=(W.address(q.bundle,'IdleLoop')+12,252)
    L.finish(q,c,stop);erase_expected=result(q)
    for key,value in erase_samples.items():samples[key]=value;expected[key]=erase_expected
    counts=Counter();minimum=255;mapper_windows=0;stop=(W.address(m.bundle,'IdleLoop')+12,252)
    for key,(state,cpu)in sorted(samples.items()):
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and cpu.p&4:continue
            q,c=L.clone(state,cpu)
            try:
                low,window=inject_checked(c,kind);minimum=min(minimum,low);mapper_windows+=int(window)
            except AssertionError:
                print('DKJR_RETIRE_ISR_REJECTED_POINT '+json.dumps(dict(key=key,kind=kind,PC=cpu.pc,SP=cpu.sp,
                    maps_before=state.rawtags,maps_after=q.rawtags,
                    CurrentBank_before=N.get(state,'CurrentBank'),CurrentBank_after=N.get(q,'CurrentBank'),
                    C_before=N.get(state,'CurrentBankC'),C_after=N.get(q,'CurrentBankC'),
                    RAM_differences=[(b,i,a,z)for b,(old,new)in enumerate(zip(state.ram,q.ram))for i,(a,z)in enumerate(zip(old,new))if a!=z][:16]),separators=(',',':')),flush=True)
                raise
            counts[kind]+=1
            L.finish(q,c,stop);assert result(q)==expected[key],(key,kind,B.state(q),expected[key][3])
    assert minimum>=128 and counts['IRQ']and counts['lagNMI']
    return dict(cuts=dict(counts),points=len(samples),minimum_ISR_SP=minimum,deepest_score_SP=deepest,
        complete_Main_and_all_WRAM_equal=True,taken_erase_fixture_points=len(erase_samples),
        taken_erase_fixture_actual_Main_entry_SP=entry[1].sp,
        exact_pending_unbanked_mapper_STA_windows=mapper_windows,
        controller_SHA256=natural['controller_SHA256'],native_ready=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cold',action='store_true')
    ap.add_argument('--first',action='store_true');ap.add_argument('--full',action='store_true')
    ap.add_argument('--headers',action='store_true');ap.add_argument('--foreign',action='store_true')
    ap.add_argument('--interrupts',action='store_true');ap.add_argument('--current',action='store_true')
    ap.add_argument('--lifecycle',action='store_true')
    ap.add_argument('--cold-interrupts',action='store_true')
    ap.add_argument('--ride-fourth',action='store_true');ap.add_argument('--fourth-window',action='store_true')
    ap.add_argument('--ledge-wait',action='store_true')
    ap.add_argument('--stationary-wait',action='store_true')
    ap.add_argument('--early-stairs',action='store_true')
    ap.add_argument('--riser-retreat',action='store_true')
    ap.add_argument('--landing-prep',action='store_true')
    ap.add_argument('--settled-stairs',action='store_true')
    ap.add_argument('--roof-trace',action='store_true');ap.add_argument('--contact-trace',action='store_true');args=ap.parse_args()
    raw=B.C.ROM.read_bytes();parent,input_info=P.proof_parent(raw)
    candidate,info=P.proposal_current(raw if args.current else parent)
    assert P.inverse_current(candidate)==(raw if args.current else parent)
    print('DKJR_RETIRE_LEASE_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    print('DKJR_RETIRE_LEASE_BINDING '+json.dumps(info,separators=(',',':')),flush=True)
    print('DKJR_RETIRE_LEASE_SOURCE '+json.dumps(source_domains(parent),separators=(',',':')),flush=True)
    _,seed=H.cold(candidate,bytes.fromhex(info['cookie']))
    if args.cold:print('DKJR_RETIRE_LEASE_COLD '+json.dumps(cold_cases(seed,candidate,info),separators=(',',':')),flush=True)
    if args.cold_interrupts:print('DKJR_RETIRE_LEASE_COLD_INTERRUPTS '+json.dumps(cold_interrupts(seed,candidate,info),separators=(',',':')),flush=True)
    if args.headers:print('DKJR_RETIRE_LEASE_HEADERS '+json.dumps(header_guards(seed,info),separators=(',',':')),flush=True)
    if args.lifecycle:print('DKJR_RETIRE_LEASE_LIFECYCLE '+json.dumps(retirement_lifecycle(seed,candidate,info),separators=(',',':')),flush=True)
    if args.foreign:
        _,before=H.cold(parent,B.COOKIE)
        print('DKJR_RETIRE_LEASE_FOREIGN '+json.dumps(H.foreign(before,seed),separators=(',',':')),flush=True)
    if args.interrupts:print('DKJR_RETIRE_LEASE_INTERRUPTS '+json.dumps(interrupts(parent,seed,candidate,info),separators=(',',':')),flush=True)
    if args.first or args.full:
        result=route(seed,candidate,info,full=args.full,ride_fourth=args.ride_fourth,
            fourth_window=args.fourth_window,ledge_wait=args.ledge_wait,stationary_wait=args.stationary_wait,early_stairs=args.early_stairs,riser_retreat=args.riser_retreat,landing_prep=args.landing_prep,settled_stairs=args.settled_stairs,
            roof_trace=args.roof_trace,contact_trace=args.contact_trace)
        print('DKJR_RETIRE_LEASE_ROUTE '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed'],(result['receipt']['canonical_SHA256'],result['receipt']['reason'])


if __name__=='__main__':main()
