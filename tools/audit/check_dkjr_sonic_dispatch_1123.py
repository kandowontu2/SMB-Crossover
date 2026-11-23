"""Bounded source/linked-CPU qualification of exact287 combined dispatch.

No emulator, file outputs, ROM staging, or delivery. Logical Main timing is
instruction-cycle evidence; physical video cadence remains Root's native QA.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch

import compose_dkjr_sonic_dispatch_1123 as C
import check_sonic_current_auth_epoch_1122 as Old
from check_mini_funded_actor_1108_v3 import registers, run, slim_fork, live_stack

D,S,M,N,W,B=C.D,C.S,C.M,Old.N,Old.W,Old.B


def clone(c):
    z=N.NesMPU(memory=slim_fork(c.memory),pc=c.pc)
    z.a,z.x,z.y,z.p,z.sp=registers(c)
    if hasattr(c.memory,'combined_terminal'):
        z.memory.combined_terminal=c.memory.combined_terminal
    return z


def enter(raw,owner):
    slot,cycles,name={'DK':(27,1,'DONKEY KONG JR'),'Sonic':(25,3,'SONIC'),
                      'Super':(25,4,'SUPER SONIC'),'Mini':(0,8,'MINI MARIO')}[owner]
    with patch.object(N,'Bus',W.ControllerBus):m=B.UI.seed(dict(W.Symbols.bundle(),raw=raw),slot)
    # This is an initialization-adversary fixture, not a gameplay write. The
    # real cold constructor must invalidate stale predecessor auth state.
    m.ram[2][0x8ff]=0x77;m.ram[2][0x3f0]=0x79
    for _ in range(cycles):B.UI.key(m,32)
    assert B.UI.menu_name(m)[0]==name
    assert N.get(m,'SelectedCharacter')=={'DK':40,'Sonic':43,'Super':43,'Mini':41}[owner]
    start=B.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    return m


def compare(a,b,owner):
    native=(*range(0x17b),*range(0x1fe,0x800),*range(0x5c00,0x8000))
    bad=[hex(i) for i in native if a[i]!=b[i]]
    assert not bad,('Native mismatch',owner,bad[:20])
    assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
    assert a.vram==b.vram and a.ppuctrl==b.ppuctrl
    old,new=C.program()[1]['images']['SONIC_EPOCH'],S.program()['images']['SONIC_EPOCH']
    sonic_changes={0x1a40+i for i,(x,y) in enumerate(zip(old,new,strict=True)) if x!=y}
    for bank,(old,new) in enumerate(zip(a.ram,b.ram,strict=True)):
        allowed=set(range(0x1fe0,0x1ff0)) if bank in (2,3) else set()
        if bank==2:
            if owner=='DK':allowed.update(range(D.MAIN&8191,(D.MAIN&8191)+D.MAIN_SIZE));allowed.add(0x8ff)
            if owner in ('Sonic','Super'):allowed.update(sonic_changes)
        bad=[hex(i) for i,(x,y) in enumerate(zip(old,new,strict=True)) if x!=y and i not in allowed]
        assert not bad,('WRAM mismatch',owner,bank,bad[:20])


class Trace:
    def __init__(self,owner,cuts=None):
        self.owner=owner;self.cuts=cuts;self.count=Counter();self.rows=[];self.upper=[]
    def capture(self,c):
        if self.cuts is None:return
        m=c.memory;tag=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        reached=((tag==193 and (0xa738<=c.pc<0xa7bf or 0xa7d5<=c.pc<0xa7da))
                 or(tag==213 and(0xa8dc<=c.pc<0xa900 or 0xb06b<=c.pc<0xb08f or 0xb8f0<=c.pc<0xb900))
                 or(tag==2 and(0xda40<=c.pc<0xda88 or D.MAIN<=c.pc<D.MAIN+D.MAIN_SIZE))
                 or(tag==254 and 0x80c2<=c.pc<0x80c9))
        if reached:
            key='Sonic' if self.owner=='Super' else self.owner,tag,c.pc,c.sp,c.p&5
            if key not in self.cuts:self.cuts[key]=clone(c)
    def run(self,c,stop):
        m=c.memory;m.combined_terminal=stop
        combined=m.bundle['raw'][S.off(85,0xb06b)]==0xe0
        for _ in range(500000):
            if (c.pc,c.sp)==stop:return
            tag=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
            if (tag,c.pc)==(193,0xaf27):
                self.count['full']+=1;self.rows.append((m[0x16c]-0x8c)//3)
            if (tag,c.pc)==(213,0xa8dc):self.count['quick']+=1
            if (tag,c.pc)==(210,0xb16d):self.upper.append((c.a,c.x,c.y,c.p))
            if combined and tag==213 and c.pc==C.program()[0]['symbols']['ReadEpoch']+7:
                assert self.owner!='DK','DK read Mini/Sonic C3F0'
                self.count['shared_epoch_reads']+=1
            if combined and tag==213 and c.pc==C.program()[0]['symbols']['ReadEpoch']+2:self.count['DK_epoch_probe']+=1
            assert not(tag==213 and 0xb08c<=c.pc<0xb08f),'Retired row-zero mirror executed'
            self.capture(c)
            assert m[c.pc],('Linked BRK',self.owner,hex(c.pc),tag)
            ri=len(m.ram_writes);pc=c.pc
            c.step()
            if self.owner=='DK' and tag==2 and D.MAIN<=pc<D.MAIN+D.MAIN_SIZE:
                for bank,at,value in m.ram_writes[ri:]:
                    if bank==2 and at==0x8ff:
                        assert pc==D.MAIN+C.program()[3]['images']['MAIN'].index(bytes.fromhex('8dffc8'))
                        assert value==m[0x0e]
                        self.count['DK_success_stamp']+=1
        raise AssertionError(('Linked bound',self.owner,hex(c.pc)))


def profiles(parent,candidate,collect=False,owners=('DK','Sonic','Super','Mini')):
    receipts=[];seeds={};cuts={}
    for owner in owners:
        machines=[enter(raw,owner) for raw in (parent,candidate)]
        for frame in range(300):
            ready=[tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8) for m in machines]
            assert ready[0]==ready[1]
            if all(ready):break
            for m in machines:B.main_step(m,0,Trace(owner))
            compare(*machines,owner)
        else:raise AssertionError(('Cold bound',owner))
        assert machines[1].ram[2][0x8ff]==0
        if owner!='DK':assert machines[1].ram[2][0x3f0]==0
        phases={}
        for phase,pad,count in (('settle',0,4),('idle',0,12),('Right',1,16),
                                ('tap',0x81,1),('air',1,10),('release',0,10)):
            totals=[0,0];counts=[Counter(),Counter()];rows=[]
            for _ in range(count):
                traces=[Trace(owner),Trace(owner,cuts if collect else None)]
                for i,(m,tr) in enumerate(zip(machines,traces,strict=True)):
                    totals[i]+=B.main_step(m,pad,tr)[0];counts[i].update(tr.count)
                compare(*machines,owner)
                assert traces[0].upper==traces[1].upper,('Prince predicate changed',owner)
                if phase in ('idle','Right'):
                    assert traces[1].rows==([] if owner=='Mini' else [0]),(owner,phase,traces[1].rows,dict(traces[1].count))
                    if owner=='Mini':assert traces[0].rows==[] and traces[1].count['quick']==traces[0].count['quick']==1
                    if owner=='DK':assert traces[0].count['full']==13
                    if owner in ('Sonic','Super'):assert traces[0].count['full']==1
                rows=traces[1].rows
            phases[phase]=dict(returns=count,parent_cycles=totals[0],candidate_cycles=totals[1],
                cycles_saved_per_Main=(totals[0]-totals[1])/count,entries=list(map(dict,counts)),last_full_rows=rows)
        assert phases['idle']['cycles_saved_per_Main']>4500 if owner=='DK' else True
        if owner in ('Sonic','Super'):
            assert machines[0].ram[2][0x3f0]==machines[1].ram[2][0x3f0]==machines[1].ram[2][0x11b]
        if owner=='DK':assert machines[1].ram[2][0x8ff]==machines[1][0x0e] or machines[1].ram[2][0x8ff]==(machines[1][0x0e]-1)&255
        q=dict(owner=owner,cold_Main_returns=frame,phases=phases)
        receipts.append(q);seeds[owner]=machines[1]
        print('COMBINED PROFILE '+json.dumps(q,separators=(',',':')),flush=True)
    return seeds,receipts,cuts


def source_ownership(parent):
    # The source-owned helper table was introduced as38 duplicate checks, not
    # public services. Only MiniTry accepts a variable row; normalized row0 now
    # branches to the full checker before that call. Independent native Mini
    # callers use fixed row16 (B0BC), B400 or B451, all retained byte-for-byte.
    source=C.selector_source()
    assert ' pha\n beq MiniFullCheck\n cmp #114' in source
    assert source.index(' beq MiniFullCheck')<source.index(' beq MiniTry')
    base=M.R/'tools/reference'
    box=(base/'mini_box_transport_1110_v1.s').read_text()
    assert 'MiniBoxService = $b0bc' in box and 'lda #$d5\n    jsr FarCall' in box
    assert 'MapC = $80c2' in box
    movement=(base/'mini_movement_prefix_1110.s').read_text()
    after=(base/'mini_after_bg_1110_v1.s').read_text()
    assert 'lda #$00\n    sta TargetLo\n    lda #$b4' in movement
    assert 'lda #$51\n    sta FarTarget\n    lda #$b4' in after
    # Resource-proof source is retained compressed text, read directly into
    # memory. Existing lease verifier classifies every indexed/indirect site.
    import check_dkjr_retire_lease_1113 as Lease
    frozen,*_=Lease.P.T.old_source()
    assert not re.search(r'\$c8ff\b',frozen,re.I)
    assert ' cpy #60\n bcc ' in frozen
    assert 'PublishEnd:\n ldy WCount\n lda #$ff\nStoreEnd:\n sta $c800,y' in frozen
    assert 'ListOffsets:.byte $40,$40,$80,0,0' in frozen
    labels=Lease.P.frozen_labels()
    definitions='\n'.join(line for line in frozen.splitlines()
        if re.match(r'^\w+\s*=\s*(?:\$[0-9a-fA-F]+|[0-9]+)\s*(?:;.*)?$',line))+'\n'
    reproduced=[]
    for first,last in (('PublishEnd','; A growing native vine'),('AppendRect','ListOffsets:')):
        start=frozen.index(first+':');end=frozen.index(last,start)
        text=frozen[start:end]
        local=set(re.findall(r'^(\w+):',text,re.M))
        defs=''.join(f'{name}=${value:x}\n' for name,value in labels.items() if name not in local)+definitions
        # These two leaf fragments have only relative internal branches and
        # typed absolute state operands; local labels were not all exported.
        part=M.assemble(defs+'.segment "BOUND"\n'+Lease.P.expand_branches(text),dict(BOUND=(0xa000,256)))['images']['BOUND']
        assert D.packet(parent).count(part)==1,('Current list bound drift',first)
        at=D.packet(parent).index(part)
        reproduced.append(dict(label=first,PC=at+0xa000,bytes=len(part),SHA256=C.H(part)))
    world=labels['DkjrNativeWorldBuild']-0xa000
    body=D.packet(parent)
    assert body[world:world+12]==bytes.fromhex('a9008dddc88defc8aedbc8bd')
    table=int.from_bytes(body[world+12:world+14],'little')
    assert body[table-0xa000:table-0xa000+5]==bytes.fromhex('4040800000')
    # Decode current executable roots, not historical body preimages: later
    # delivered ready/carry/render changes legitimately changed those bodies.
    packet=D.packet(parent)
    memory={0xa000+i:value for i,value in enumerate(packet[:8192])}
    memory.update({0xc900+i:value for i,value in enumerate(packet[8192:9216])})
    memory.update({0xd000+i:value for i,value in enumerate(packet[9216:])})
    roots=[0xa000+3*i for i in range(38)]+[labels[name] for name in
        ('DkjrNativeFruitSet','DkjrNativeFruitReset','DkjrNativeFruitProject','DkjrNativeFruitRemove')]
    sizes=dict(imp=1,acc=1,imm=2,zpg=2,zpx=2,zpy=2,inx=2,iny=2,rel=2,abs=3,abx=3,aby=3,ind=3)
    todo=list(roots);decoded={};opaque=set()
    while todo:
        pc=todo.pop()
        if pc in decoded:continue
        if pc not in memory:opaque.add(pc);continue
        op,mode=N.NesMPU.disassemble[memory[pc]]
        assert op not in ('???','BRK'),('Current DK closure decode',hex(pc),op)
        size=sizes[mode];operand=memory.get(pc+1,0)+(memory.get(pc+2,0)*256 if size==3 else 0)
        decoded[pc]=op,mode,operand
        following=pc+size
        if op=='JSR':todo.extend((operand,following))
        elif op=='JMP':
            assert mode=='abs',('Unclassified DK indirect jump',hex(pc))
            todo.append(operand)
        elif mode=='rel':todo.extend((following,following+operand-(256 if operand&128 else 0)))
        elif op not in ('RTS','RTI'):todo.append(following)
    aliases=[]
    for pc,(op,mode,operand) in decoded.items():
        assert not(mode=='abs' and operand==0xc8ff),('Prior direct DK epoch user',hex(pc),op)
        if mode not in ('abx','aby') or not operand<=0xc8ff<=operand+255:continue
        if operand<0xc800:raise AssertionError(('Unclassified upper DK indexed base',hex(pc),hex(operand)))
        if operand in (0xc8c0,0xc8c1,0xc8c8,0xc8c9,0xc8d0,0xc8d1):
            assert mode=='abx' and op in ('LDA','STA')
            maximum=operand+(6 if op=='STA' else 0)
        elif operand in (0xc800,0xc801,0xc802,0xc803):
            assert mode=='aby' and op in ('LDA','CMP','STA')
            maximum=0xc8bc if op=='STA' else operand+188
        elif operand==0xc8e4:
            assert mode=='abx' and op=='LDA';maximum=operand+3
        elif operand==0xc8e8:
            assert mode=='aby' and op=='ADC';maximum=operand+2
        else:raise AssertionError(('Unclassified C8FF alias',hex(pc),op,mode,hex(operand)))
        assert maximum<0xc8ff
        aliases.append(dict(PC=pc,op=op,mode=mode,base=operand,maximum=maximum))
    assert len(aliases)==21,len(aliases)
    domains=dict(retained_source_SHA256=Lease.P.T.FROZEN_SHA,current_roots=len(roots),
        current_reached_instructions=len(decoded),current_direct_C8FF_users=0,
        current_possible_indexed_aliases=sorted(aliases,key=lambda q:q['PC']),
        native_opaque_targets=sorted(opaque),current_bound_fragments=reproduced,
        bounded_list_maximum=0xc8bc,translated_RAM_byte_index_maximum=0xc8fe,
        original_indirect_sites=23,
        inherited_indirect_domains=dict(fruit=[0xc400,0xc41d],render=[0xc200,0xc3fe],
            descriptor=['immutable A000..BFE0','validated C800/C840/C880']),
        cold_clear_C8FF_requires_invalid_headers=True)
    return dict(private_row0_not_public=True,mandatory_first_full_before_private_call=True,
        retained_private_table_rows=list(range(1,38)),fixed_other_native85_targets=[0xb0bc,0xb400,0xb451],
        MapC_fixed_contract=parent[S.off(126,0x80c2):S.off(126,0x80c2)+7].hex(),
        fixed_MapC_preserves_XY=True,DK_C8FF_prior_writer_domains=domains,
        scope='Known source caller closure plus reached linked CPU; arbitrary corrupted caller pointers are not granted inputs')


def selector_controls(seed,cuts=None):
    count=Counter()
    original_maps=None
    def dispatch(owner,high,low,mutate=None):
        m=slim_fork(seed);m.raw_page(1,193);m[0x145]=193
        N.put(m,SelectedCharacter=owner,FrameCounter=9)
        m[0x5fff]=1;m[0x1fa]=0x83;m[0x1f9]=0x52
        m.ram[2][0x119]=m.ram[2][0x11a]=1
        m.ram[2][0x11b]=m.ram[2][0x3f0]=m.ram[2][0x8ff]=9
        for bank in (2,3):m.ram[bank][0x1fe0:0x1ff0]=bytes((0xa7,owner,1))+bytes(range(13))
        # Use exact owner cookie: complete checking must reject any byte below.
        at=D.COOKIE if owner==40 else M.COOKIE_AT if owner==43 else 536595
        for bank in (2,3):m.ram[bank][0x1fe0:0x1ff0]=m.bundle['raw'][at:at+16]
        m[0x16c],m[0x16d]=low,high
        if mutate:mutate(m)
        maps=tuple(m.rawtags)
        m.combined_terminal=(0,0)
        prior=set(cuts) if cuts is not None else set()
        c=N.NesMPU(memory=m,pc=0xa743);c.a,c.x,c.y,c.p,c.sp=73,11,19,0x31,210
        tr=Trace('DK' if owner==40 else 'Sonic' if owner==43 else 'Mini',cuts)
        for _ in range(1200):
            if c.pc in (0xab12,0xab4f) and m.rawtags[1]==193:
                assert c.sp==210 and tuple(m.rawtags)==maps
                if cuts is not None:
                    for key in set(cuts)-prior:cuts[key].memory.combined_terminal=(c.pc,c.sp)
                return c.pc,tr
            # Trace.run requires a single terminal. One instruction retains
            # the actual two-exit closure while collecting the same evidence.
            if (m.rawtags[1],c.pc)==(193,0xaf27):tr.count['full']+=1
            if (m.rawtags[1],c.pc)==(213,0xa8dc):tr.count['quick']+=1
            assert not(m.rawtags[1]==213 and 0xb08c<=c.pc<0xb08f)
            tr.capture(c)
            assert m[c.pc],(owner,hex(c.pc),m.rawtags)
            c.step()
        raise AssertionError(('Selector bound',owner,high,low,hex(c.pc)))
    for owner in (40,41,43):
        for high in (0,0xa9,0xaf,0xb0,0xb1,0xff):
            for low in (0,0x87,0x8b,0x8c,0x8f,0xfb,0xfd,0xfe,0xff):
                if high==0xb0 and 0x8c<=low<0xfe:continue
                pc,tr=dispatch(owner,high,low)
                assert pc==0xab4f and tr.count==Counter(),(owner,high,low,dict(tr.count))
                count['bounded_target_rejection']+=1
        pc,tr=dispatch(owner,0xb0,0x8c)
        assert pc==0xab12 and tr.count==Counter(full=1),(owner,dict(tr.count))
        count['first_row_full']+=1
        for bank in (2,3):
            for byte in range(16):
                def corrupt(m,bank=bank,byte=byte):m.ram[bank][0x1fe0+byte]^=1
                pc,tr=dispatch(owner,0xb0,0x8c,corrupt)
                assert pc==0xab4f and tr.count==Counter(full=1),(owner,bank,byte,dict(tr.count))
                count['first_row_corrupt_complete_header']+=1
        pc,tr=dispatch(owner,0xb0,0xa7)
        assert pc==0xab12 and tr.count==Counter(quick=1),(owner,dict(tr.count))
        count['current_epoch_both_prefixes']+=1
        for bank in (2,3):
            for byte in (0,1):
                def corrupt(m,bank=bank,byte=byte):m.ram[bank][0x1fe0+byte]^=1
                pc,tr=dispatch(owner,0xb0,0xa7,corrupt)
                assert pc==0xab4f and tr.count==Counter(quick=1,full=1)
                count['live_prefix_corruption']+=1
        for epoch in (0,8):
            def stale(m,epoch=epoch):m.ram[2][0x8ff if owner==40 else 0x3f0]=epoch
            pc,tr=dispatch(owner,0xb0,0xa7,stale)
            assert pc==0xab12 and tr.count==Counter(quick=1,full=1)
            count['stale_zero_fallback']+=1
        def zero_frame(m):
            N.put(m,FrameCounter=0)
            m.ram[2][0x8ff]=m.ram[2][0x3f0]=m.ram[2][0x11b]=0
        pc,tr=dispatch(owner,0xb0,0xa7,zero_frame)
        assert pc==0xab12 and tr.count==Counter(quick=1,full=1)
        count['zero_frame_fallback']+=1
    return dict(count)


def main_contract(parent,candidate):
    # Exact native main behavior for all source state bytes and both failures.
    count=0
    for state in range(256):
        for first,second in ((True,True),(False,True),(True,False)):
            outcomes=[]
            for raw in (parent,candidate):
                memory=[0]*65536
                memory[D.MAIN:D.MAIN+D.MAIN_SIZE]=raw[D.MAIN_FILE:D.MAIN_FILE+D.MAIN_SIZE]
                for pc,okay in ((0xbfc1,first),(0xb940,second)):
                    memory[pc:pc+2]=[0x38 if okay else 0x18,0x60]
                memory[0xd240]=0x60
                memory[0x75],memory[0xbd],memory[0xc06b],memory[0x0e]=32,176,state,9
                c=N.NesMPU(memory=memory,pc=D.MAIN);c.a,c.x,c.y,c.p,c.sp=31,7,13,0x71,224
                c.stPushWord(0x5aff)
                run(c,lambda z:(z.pc,z.sp)==(0x5b00,224))
                outcomes.append((registers(c),bytes(memory[:256]),bytes(memory[0x700:0x702])))
                if raw is candidate:assert memory[0xc8ff]==(9 if first and second else 0)
            assert outcomes[0]==outcomes[1],(state,first,second,outcomes)
            count+=1
    return dict(exact_Main_A_X_Y_P_SP_and_native_writes=count,all_source_states=256,
                first_and_second_failure_leave_epoch_ungranted=True)


def interrupts(cuts):
    counts=Counter();minimum=255
    for original in cuts.values():
        for kind in ('IRQ','busyNMI'):
            if kind=='IRQ' and original.p&4:continue
            a,b=clone(original),clone(original)
            for z in (a,b):N.put(z.memory,NmiDisable=255)
            before=registers(b),b.pc;stack=live_stack(b);private=tuple(bytes(q) for q in b.memory.ram)
            if kind=='IRQ':b.irq()
            else:b.nmi()
            run(b,lambda z:(registers(z),z.pc)==before)
            minimum=min(minimum,b.sp)
            assert live_stack(b)==stack and tuple(bytes(q) for q in b.memory.ram)==private,(kind,before)
            end=original.memory.combined_terminal
            for z in (a,b):run(z,lambda z:(z.pc,z.sp)==end)
            assert registers(a)==registers(b)
            assert tuple(bytes(q) for q in a.memory.ram)==tuple(bytes(q) for q in b.memory.ram)
            assert tuple(a.memory.rawtags)==tuple(b.memory.rawtags)
            assert tuple(a.memory.chr_latches)==tuple(b.memory.chr_latches)
            assert live_stack(a)==live_stack(b)
            assert Old.state(a.memory)==Old.state(b.memory)
            counts[kind]+=1
    return dict(cuts=len(cuts),returns=dict(counts),minimum_return_SP=minimum,
                scope='Actual Main and native ISR; same full WRAM/live stack/register/mapping endpoint')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--interrupts',action='store_true')
    p.add_argument('--contracts-only',action='store_true')
    args=p.parse_args()
    def deny(*a,**k):raise AssertionError('Combined source proof attempted an output/process')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        parent=M.ROM.read_bytes();candidate,composition=C.proposal(parent)
        print('COMBINED CANDIDATE '+composition['candidate_SHA256'],flush=True)
        result=dict(composition=composition,ownership=source_ownership(parent),
                    Main_contract=main_contract(parent,candidate))
        print('COMBINED SOURCE '+json.dumps({k:result[k] for k in ('ownership','Main_contract')},separators=(',',':')),flush=True)
        seeds,proofs,cuts=profiles(parent,candidate,args.interrupts,('DK','Sonic','Super') if args.contracts_only else ('DK','Sonic','Super','Mini'))
        result['profiles']=proofs
        result['controls']=selector_controls(seeds['Sonic'],cuts if args.interrupts else None)
        result['Sonic_scope_fallbacks']=Old.fallbacks(seeds['Sonic'])
        result['upper_predicate']=Old.upper_predicate(seeds['Sonic'],parent,candidate)
        if args.interrupts:
            result['interrupts']=interrupts(cuts)
        result.update(passed=True,outputs=0,Mesen=False,physical_cadence_qualified=False)
    result['receipt_SHA256']=C.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('COMBINED RESULT '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
