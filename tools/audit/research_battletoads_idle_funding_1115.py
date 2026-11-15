"""Detached ae66 resolver funding research; no new ROM/code/data placement."""
from collections import Counter
from bisect import bisect_right
from copy import deepcopy
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from measure_battletoads_passthrough_fit_1114 import Code

import research_battletoads_remaining_idle_1114 as Frozen
import compose_prince_window567_1115 as Prince
import prince_cold_packet_1111 as Packet
import audit_battletoads_native_service_ingress_1114 as Containers

W,N,Frames=Frozen.W,Frozen.N,Frozen.Frames


def reference(raw):
    pin=sha256(raw).hexdigest()
    if pin==Prince.CANDIDATE:raw=Prince.inverse(raw)
    else:assert pin==Frozen.Service.CANDIDATE,'Expected exact590 or exactae66'
    assert sha256(raw).hexdigest()==Frozen.Service.CANDIDATE
    return raw


def load():
    raw=Frozen.ROM.read_bytes();parent=reference(raw)
    return raw,dict(actual_input_SHA256=sha256(raw).hexdigest(),source_binding_ae66_SHA256=sha256(parent).hexdigest(),
        actual_owning_bytes_retained=True,explicit_Prince590_inverse_for_bindings_only=raw!=parent)


def cold(raw):
    normalized=Frozen.Score.inverse(Frozen.Service.inverse(reference(raw)));factory=Frozen.Cold.F
    class Current:
        @staticmethod
        def bindings(image,key):assert image is raw;return factory.bindings(normalized,key)
    with patch.object(Frozen.Cold.Previous,'Factory',Current):m=Frozen.Cold.Previous.cold(raw,'rash')
    assert m.bundle['raw']is raw
    return m


def bundle(raw):return Frozen.Cold.bundle(Frozen.Score.inverse(Frozen.Service.inverse(reference(raw))))


def inspect(raw):
    b=bundle(raw);rows=[]
    for name,end in(('WfResolve',0xb7dc),('BwBtResolve',0xb300)):
        at=W.location(b,name);pc=W.address(b,name);data=raw[at:at+end-pc]
        memory=[0]*65536;memory[pc:end]=data;d=Disassembler(MPU(memory=memory));listing=[];cursor=pc
        while cursor<end:
            size,text=d.instruction_at(cursor);listing.append(dict(PC=cursor,bytes=bytes(memory[cursor:cursor+size]).hex(),instruction=text));cursor+=size
        labels=[]
        for n in b['syms']:
            try:where=W.location(b,n)
            except(KeyError,AssertionError):continue
            if at<=where<at+len(data):labels.append(dict(name=n,CPU=pc+where-at))
        rows.append(dict(name=name,file=[at,at+len(data)],CPU=[pc,end],bytes=data.hex(),SHA256=sha256(data).hexdigest(),listing=listing,labels=labels))
    at=W.location(b,'WfResolveTargets');table=raw[at:at+108];targets=[]
    for slot in range(36):
        lo,hi,bank=table[slot*3:slot*3+3];target=lo+256*hi;names=[]
        file=16+(bank&127)*8192+(target&8191)
        for n in b['syms']:
            try:where=W.location(b,n)
            except(KeyError,AssertionError):continue
            if where==file:names.append(n)
        targets.append(dict(slot=slot,CPU=target,bank=bank,names=names[:6]))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),resolver_spans=rows,Wf36targets=targets,
        Wf_target_banks=dict(Counter(r['bank']for r in targets)),opcode_or_data_placed=False,outputs=0)


def callers(raw):
    m=cold(raw);b=m.bundle;base=N.NesMPU;seen=[];rows=[]
    class Observe(base):
        def step(self):
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(tag,self.pc)==(207,0xb8b8):
                seen.append(dict(A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp,
                    saved_Y=m[0x100+((self.sp+1)&255)],saved_P=m[0x100+((self.sp+2)&255)],safe_A=m[0x16a]))
            return super().step()
    for name in('MegaManCollisionAdder','MegaManCollisionBox'):
        count=0;domains=Counter();snippet=[];at=W.location(b,name);pc=W.address(b,name)
        for p in range(256):
            if not p&32:continue
            for x,y in((0,0),(7,91),(255,255),(1,254)):
                seen.clear();before=tuple(map(bytes,m.ram));scratch=bytes(m[W.address(b,'R0'):W.address(b,'R7')+1])
                with patch.object(N,'NesMPU',Observe):r=N.invoke(m,name,a=85,x=x,y=y,p=p)
                assert len(seen)==1,(name,p,x,y,seen)
                s=seen[0];assert(s['A'],s['safe_A'],s['Y'])==(33,33,12 if name.endswith('Adder')else 13)
                assert s['saved_P']&1,'Owning source establishes carry before callback'
                assert(r['A'],r['X'],r['Y'],r['P']&1)==(33,x,0,1),(name,p,x,y,r)
                assert(r['P']&0x4c)==(p&0x4c),'D/I/V retained through actual full caller'
                assert tuple(map(bytes,m.ram))==before and bytes(m[W.address(b,'R0'):W.address(b,'R7')+1])==scratch
                domains[s['saved_Y'],s['saved_P']&0xef]+=1;count+=1
                if len(snippet)<4:snippet.append(dict(input_P=p,input_X=x,input_Y=y,entry=s,return_registers={k:r[k]for k in('A','X','Y','P')}))
        rows.append(dict(name=name,file=at,CPU=pc,first32=raw[at:at+32].hex(),cases=count,
            saved_frame_domains=[dict(Y=y,P=p,cases=n)for(y,p),n in sorted(domains.items())],sample=snippet))
        print('PROGRESS '+json.dumps(dict(caller=name,cases=count,carry1=True)),flush=True)
    page=raw[16+79*8192:16+80*8192];leads=[]
    for pattern in('2828a00060','6828a00060','6828a0003860','68a8283860','68a8281860'):
        data=bytes.fromhex(pattern);start=0
        while(start:=page.find(data,start))>=0:
            leads.append(dict(pattern=pattern,CPU=0xa000+start,file=16+79*8192+start));start+=1
    return dict(ROM_SHA256=sha256(raw).hexdigest(),genuine_cold=True,explicit_all128P_fourXY_component_entries=True,
        owning_callers=rows,inline_return_research='PLP/PLP/LDY0/RTS preserves owner A33 and X, restores saved C1; first PLP consumes saved Y, so temporary status/ISR still needs proof',
        existing_bank79_epilogue_literal_leads=leads,opcode_or_data_placed=False,ISR_qualified=False,outputs=0)


def frame(raw):
    b=bundle(raw);bank=raw[16+79*8192:16+80*8192];rows=[];symbols=[]
    for slot in range(36):rows.append(dict(slot=slot,CPU=0xb600+16*slot,prefix=bank[0x1600+16*slot:0x160b+16*slot].hex(),pad=bank[0x160b+16*slot:0x1610+16*slot].hex()))
    for name in('HuStart','HuResolve','HuLo','HuPairIndex','HuPairHi','HuPairBank','HuCommonRestore','HuCommonAfterSelected'):
        try:at=W.location(b,name);pc=W.address(b,name)
        except KeyError:continue
        symbols.append(dict(name=name,CPU=pc,file=at,bytes16=raw[at:at+16].hex()))
    inbound=[]
    for prg in range(128):
        page=raw[16+prg*8192:16+(prg+1)*8192]
        for pc in(0xb60b,0xb61b,0xb7eb,0xb7fb,0xb85c):
            for op in(0x20,0x4c,0x6c):
                pattern=bytes((op,pc&255,pc>>8));at=0
                while(at:=page.find(pattern,at))>=0:
                    inbound.append(dict(PRG=prg,CPU=(0xa000 if prg<126 else 0x8000 if prg==126 else 0xe000)+at,file=16+prg*8192+at,opcode=op,target=pc));at+=1
    return dict(ROM_SHA256=sha256(raw).hexdigest(),public_rows=rows,current_symbol_bindings=symbols,
        literal_inbound_leads=inbound,not_executable_or_owner_classification=True,outputs=0)


def construct(raw):
    b=bundle(raw);rows=[]
    for name in('HuResolve','HuDkPrepare','HuNativeWorldPalette','HuLegacyPostBG','DkEnsure','DkConstruct','GmConstruct','CmHostResolveCharacter'):
        at=W.location(b,name);pc=W.address(b,name);rows.append(dict(name=name,CPU=pc,file=at,bank=((at-16)//8192)|128,code=raw[at:at+144].hex()))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),current_constructor_bindings=rows,
        exact_unowned_bytes_changed=0,opcode_or_data_placed=False,outputs=0)


def hu_program(raw,base,changed):
    b=bundle(raw);start=W.address(b,'HuResolve');end=W.address(b,'HuDkPrepare');at=W.location(b,'HuResolve')
    old=raw[at:at+end-start];assert old[:13]==bytes.fromhex('0848ad026048babd02018d6a01')
    assert old[-13:-6]==bytes([0xea])*7 and old[-6:]==bytes.fromhex('6828ad026060')
    program=bytearray(bytes.fromhex('088d6a01ad026048')+old[13:-13]+old[-5:]if changed else old)
    assert len(old)-len(program)==(13 if changed else 0)
    memory=[0]*65536;memory[start:end]=old;d=Disassembler(MPU(memory=memory));cursor=start
    def target(offset):
        if not changed:return offset
        if offset==len(old)-6:return len(program)-5
        if 13<=offset<len(old)-13:return offset-5
        if len(old)-5<=offset<len(old):return offset-13
        if offset==0:return 0
        raise AssertionError(('New entry into removed/reordered Hu prologue or NOP',offset))
    while cursor<end:
        n,_=d.instruction_at(cursor);i=cursor-start;op=old[i]
        if not changed or 13<=i<len(old)-13 or i>=len(old)-5:
            j=target(i)
            if op in(0x20,0x4c):
                dest=int.from_bytes(old[i+1:i+3],'little')
                if start<=dest<end:program[j+1:j+3]=(base+target(dest-start)).to_bytes(2,'little')
            elif op in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                dest=i+2+(old[i+1]if old[i+1]<128 else old[i+1]-256)
                assert 0<=dest<len(old)
                delta=target(dest)-(j+2);assert-128<=delta<128;program[j+1]=delta&255
        cursor+=n
    return bytes(program),dict(old_start=start,old_end=end,old_file=at,old_bytes=len(old),new_bytes=len(program),
        early_SafeA_and_dead_saved_A_bytes=6,owned_Nops=7,bytes_funded=13,original_SHA256=sha256(old).hexdigest())


def layout(raw):
    b=bundle(raw);old_entry=W.address(b,'HuResolve');old_at=W.location(b,'HuResolve')
    a=Code(0xb8b8);a.emit('c00c');a.branch(0xf0,'Native');a.emit('c00d');a.branch(0xd0,'Original')
    a.mark('Native');a.emit('2828a00060');a.mark('Original');guard=a.done();assert len(guard)==13 and a.pc==0xb8c5
    old_start=16+79*8192+0x18b8;body=raw[old_start:old_at]
    assert len(body)==32+380 and body[:32].hex()=='a9b08d6d01a9d78d6201c0249002a024988d6c010a6d6c0169208d6c014cb2b8'
    new_hu,info=hu_program(raw,old_entry+13,True);piece=guard+body+new_hu
    old_end=W.location(b,'HuDkPrepare');assert len(piece)==old_end-old_start
    operands=[]
    for name in('HuLo','HuPairIndex','HuPairHi','HuPairBank'):
        pc=W.address(b,name);pattern=bytes((0xb9,pc&255,pc>>8));matches=[]
        for i in range(0x185c,0x18b8):
            if raw[16+79*8192+i:16+79*8192+i+3]==pattern:matches.append(16+79*8192+i)
        assert len(matches)==1,(name,matches)
        operands.append(dict(name=name,instruction_file=matches[0],old_target=pc,new_target=pc+13))
    start=16+79*8192+0x185c;end=old_start;common=raw[start:end];p=common.find(bytes.fromhex('c922b00a'));assert p>=0
    branch_cpu=0xb85c+p+2;delta=0xb8b8-(branch_cpu+2);assert-128<=delta<128
    old_bt_edges=[]
    for i in range(len(common)-1):
        if common[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
            dest=0xb85c+i+2+(common[i+1]if common[i+1]<128 else common[i+1]-256)
            if dest==0xb8b8:
                old_bt_edges.append(dict(file=start+i,opcode=common[i],old_operand=common[i+1],new_operand=common[i+1]+13))
    assert old_bt_edges==[dict(file=653450,opcode=0xd0,old_operand=0x3c,new_operand=0x49)]
    return dict(ROM_SHA256=sha256(raw).hexdigest(),detached_funded_piece=dict(file=[old_start,old_end],
        old_SHA256=sha256(raw[old_start:old_end]).hexdigest(),new_SHA256=sha256(piece).hexdigest(),bytes=len(piece),new_hex=piece.hex()),
        constructor=info,new_HuResolve_entry=old_entry+13,guard_hex=guard.hex(),guard_labels=a.labels,
        four_table_operands=operands,upper_test_proposal=dict(file=start+p,old_hex='c922b00a',new_hex=bytes((0xc9,33,0xf0,delta&255)).hex(),
            valid_only_after_all_A_le33_ingress_closed=True),
        other_cohort_branch_rebinding=old_bt_edges,
        HuDkPrepare_Palette_Legacy_PC_and_bytes_unchanged=True,all_row_pads_unchanged=True,
        opcode_or_data_placed=False,ingress_ISR_and_ABI_qualified=False,outputs=0)


def construct_units(raw):
    seed=cold(raw);b=seed.bundle;unit_base=0x5800;programs=[hu_program(raw,unit_base,flag)[0]for flag in(False,True)]
    base=type(seed)
    class View(base):
        def __getitem__(self,at):
            if isinstance(at,int)and unit_base<=at<unit_base+len(getattr(self,'unit_program',b'')):return self.unit_program[at-unit_base]
            return super().__getitem__(at)
    def clone():
        m=list.__new__(View);list.extend(m,list.__iter__(seed))
        for key,value in seed.__dict__.items():setattr(m,key,value if key=='bundle'else deepcopy(value))
        return m
    cm=W.address(b,'CmHostResolveCharacter');cm_tag=((W.location(b,'CmHostResolveCharacter')-16)//8192)|128
    assert raw[W.location(b,'CmHostResolveCharacter'):W.location(b,'CmHostResolveCharacter')+4]==bytes.fromhex('08ae0973')
    count=0;entry_X=Counter();minimum=255
    for p in range(256):
        if not p&32:continue
        for x,y in((0,0),(7,91),(255,255),(1,254)):
            for argument in(0,255):
                pairs=[];kills=[]
                for program in programs:
                    m=clone();m.unit_program=program
                    m[0x16a]=argument;m[0x16c]=unit_base&255;m[0x16d]=unit_base>>8
                    cpu=N.NesMPU(memory=m,pc=0x15a);cpu.a=207;cpu.x=x;cpu.y=y;cpu.p=p;cpu.sp=224;cpu.stPushWord(0x5aff)
                    entered=None;kill=None
                    for _ in range(200000):
                        if(cpu.pc,cpu.sp)==(0x5b00,224):break
                        tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                        if(tag,cpu.pc)==(cm_tag,cm):entered=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp);entry_X[cpu.x]+=1
                        if(tag,cpu.pc)==(cm_tag,cm+4):kill=(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp)
                        minimum=min(minimum,cpu.sp);assert m[cpu.pc];cpu.step()
                    else:raise AssertionError(('Detached actual farcall unit bound',p,x,y,argument,cpu.pc))
                    assert entered and kill
                    pairs.append((m,(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp)))
                    kills.append(kill)
                old,new=pairs;assert old[1]==new[1],(p,x,y,argument,old[1],new[1])
                assert kills[0][:4]==kills[1][:4]and kills[1][4]==kills[0][4]+1
                assert tuple(map(bytes,old[0].ram))==tuple(map(bytes,new[0].ram))
                assert old[0].rawtags==new[0].rawtags and old[0].chr_latches==new[0].chr_latches
                for lo,hi in((0,256),(0x200,0x800),(0x5c00,0x8000),(0x1e1,0x200)):
                    assert bytes(old[0][lo:hi])==bytes(new[0][lo:hi]),('Live field difference',p,x,y,argument,lo)
                count+=1
    return dict(ROM_SHA256=sha256(raw).hexdigest(),detached_unit_window=[unit_base,unit_base+max(map(len,programs))],
        actual_outer_and_nested_FarCallCommon_and_actual_CmHost_body=True,actual_compiled_Rash_cold_seed=True,
        component_entries_not_gameplay_or_natural_Select_claim=True,all128P_fourXY_twoA_cases=count,
        full_return_AXYP_SP_live_RAM_physical_RAM_maps_exact=True,after_Cm_LDX_X_and_other_registers_exact=True,
        active_Hu_stack_one_byte_shallower=True,minimum_SP=minimum,observed_Cm_entry_X=dict(entry_X),
        code_arrays_only_no_ROM_or_RAM_opcode_writes=True,ISR_qualified=False,outputs=0)


def menu_captures(raw):
    b=dict(bundle(raw),raw=raw);base=N.NesMPU;captures={};rows=[];entry=W.address(b,'HuResolve')
    for key,slot,owner in(('gimmick',25,26),('donkey_kong',27,28),('rash',23,33)):
        def point(c):
            if c.pc==entry and c.memory.rawtags[1]==207 and N.get(c.memory,'CrossoverMenuIndex')==slot:
                captures.setdefault(key,(N.fork(c.memory),{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
        class Capture(base):
            def step(self):point(self);return super().step()
        with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
            with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
            nav=[1,4,4,4]if key=='gimmick'else[2,4,4]if key=='rash'else[4]*(slot//8)+[1]*(slot%8)
            for pad in nav:W.UI.key(m,pad)
        assert N.get(m,'CrossoverMenuIndex')==slot and N.get(m,'SelectedCharacter')==owner,(key,slot,owner,N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),W.UI.menu_name(m))
        assert key in captures,('Actual menu did not enter HuResolve',key)
        rows.append(dict(key=key,slot=slot,owner=owner,name=W.UI.menu_name(m)[0],entry=captures[key][1]))
    return captures,rows


def construct_menus(raw,inspect_only=False):
    captures,rows=menu_captures(raw)
    if inspect_only:return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_compiled_menu_navigation=rows,outputs=0)
    unit_base=0x5800;programs=[hu_program(raw,unit_base,flag)[0]for flag in(False,True)];count=0;minimum=255
    for key,(seed,regs)in captures.items():
        base=type(seed)
        class View(base):
            def __getitem__(self,at):
                if isinstance(at,int)and unit_base<=at<unit_base+len(getattr(self,'unit_program',b'')):return self.unit_program[at-unit_base]
                return super().__getitem__(at)
        def clone():
            m=list.__new__(View);list.extend(m,list.__iter__(seed))
            for field,value in seed.__dict__.items():setattr(m,field,value if field=='bundle'else deepcopy(value))
            return m
        cases=0
        for p in range(256):
            if not p&32:continue
            for x,y in((0,255),(71,109)):
                pair=[]
                for program in programs:
                    m=clone();m.unit_program=program;c=N.NesMPU(memory=m,pc=unit_base)
                    for name,value in regs.items():setattr(c,name,value)
                    c.pc=unit_base;c.x=x;c.y=y;c.p=p
                    for _ in range(300000):
                        if(c.pc,c.sp)==(0x5b00,224):break
                        minimum=min(minimum,c.sp);assert m[c.pc],('Menu continuation BRK',key,hex(c.pc));c.step()
                    else:raise AssertionError(('Actual menu constructor continuation bound',key,p,x,y,hex(c.pc),c.sp))
                    pair.append((m,(c.a,c.x,c.y,c.p&0xef,c.sp)))
                (old,a),(new,z)=pair;assert a==z,(key,p,x,y,a,z)
                assert old.ram==new.ram and old.rawtags==new.rawtags and old.chr_latches==new.chr_latches
                assert old.vram==new.vram and(old.ppuctrl,old.upper)==(new.ppuctrl,new.upper)
                for lo,hi in((0,0x17b),(0x200,0x800),(0x5c00,0x8000),(0x1e1,0x200)):
                    assert bytes(old[lo:hi])==bytes(new[lo:hi]),('Menu constructor globals/SMC/live-stack',key,p,x,y,lo)
                cases+=1;count+=1
        print('PROGRESS '+json.dumps(dict(menu=key,cases=cases)),flush=True)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_compiled_menu_navigation=rows,
        all128validP_twoXY_actual_menu_continuation_cases=count,actual_full_farcall_continuation=True,
        exact_return_AXYP_SP_live_RAM_SMC_physical_RAM_VRAM_maps=True,minimum_SP=minimum,
        status_XY_replacement_is_declared_component_not_natural_input=True,
        code_arrays_only_no_ROM_or_RAM_opcode_writes=True,ISR_qualified=False,outputs=0)


def constructor_interrupts(raw):
    captures,menus=menu_captures(raw);unit=0x5800;program,info=hu_program(raw,unit,True);rows=[];minimum=255
    for key,(seed,regs)in captures.items():
        base=type(seed)
        class View(base):
            def __getitem__(self,at):
                if isinstance(at,int)and unit<=at<unit+len(program):return program[at-unit]
                return super().__getitem__(at)
        m=list.__new__(View);list.extend(m,list.__iter__(seed))
        for field,value in seed.__dict__.items():setattr(m,field,value if field=='bundle'else deepcopy(value))
        c=N.NesMPU(memory=m,pc=unit)
        for field,value in regs.items():setattr(c,field,value)
        c.pc=unit;cuts=[];changed={unit+i for i in(0,1,4,7,len(program)-5,len(program)-4,len(program)-1)}
        for _ in range(300000):
            if(c.pc,c.sp)==(0x5b00,224):break
            if c.pc in changed:cuts.append((N.fork(m),{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
            assert m[c.pc];c.step()
        else:raise AssertionError('Constructor interrupt capture bound')
        assert{r['pc']for _,r in cuts}==changed,(key,[r['pc']for _,r in cuts],changed)
        for arena,state in cuts:
            assert N.get(arena,'NmiDisable')&128,'Actual compiled menu component runs busy; no forced regular arm'
            kinds=('NMI',)if state['p']&4 else('IRQ','NMI')
            for kind in kinds:
                z=N.fork(arena);q=N.NesMPU(memory=z,pc=state['pc'])
                for field,value in state.items():setattr(q,field,value)
                before=(q.pc,q.sp,q.a,q.x,q.y,q.p);skipped=N.get(z,'NmiSkipped')
                q.irq()if kind=='IRQ'else q.nmi()
                for _ in range(200000):
                    minimum=min(minimum,q.sp)
                    if(q.pc,q.sp)==before[:2]:break
                    assert z[q.pc],('Constructor ISR BRK',key,kind,hex(q.pc));q.step()
                else:raise AssertionError('Constructor ISR bound')
                after=(q.pc,q.sp,q.a,q.x,q.y,q.p)
                assert after[:5]==before[:5]and after[5]&0xef==before[5]&0xef
                assert z.ram==arena.ram and z.rawtags==arena.rawtags and z.chr_latches==arena.chr_latches
                assert bytes(z[0x15a:0x17b])==bytes(arena[0x15a:0x17b])
                assert bytes(z[0x101+state['sp']:0x200])==bytes(arena[0x101+state['sp']:0x200])
                assert(N.get(z,'NmiSkipped')-skipped)&255==int(kind=='NMI')
                rows.append(dict(menu=key,PC=state['pc'],P=state['p'],SP=state['sp'],kind=kind))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),constructor=info,actual_compiled_menu_navigation=menus,
        reached_changed_prologue_epilogue_ISR_cuts=rows,minimum_SP=minimum,
        exact_ISR_AXYP_SP_SMC_physical_RAM_maps_live_stack=True,regular_NMI_in_busy_component_unreachable=True,
        code_arrays_only_no_ROM_or_RAM_opcode_writes=True,outputs=0)


def guard_units(raw):
    seed=cold(raw);base=type(seed);cpu_base=N.NesMPU;program=bytes.fromhex('c00cf004c00dd0052828a00060');unit=0x5800
    class View(base):
        def __getitem__(self,at):
            if isinstance(at,int)and unit<=at<unit+len(program):return program[at-unit]
            return super().__getitem__(at)
    def clone(enabled):
        m=list.__new__(View);list.extend(m,list.__iter__(seed))
        for key,value in seed.__dict__.items():setattr(m,key,value if key=='bundle'else deepcopy(value))
        m.guard_enabled=enabled;m.guard_entries=0;return m
    class CPU(cpu_base):
        def step(self):
            m=self.memory
            if m.guard_enabled and m.rawtags[1]==207 and self.pc==0xb8b8:
                assert self.a==33 and self.y in(12,13);assert m[0x100+((self.sp+2)&255)]&1
                m.guard_entries+=1;self.pc=unit
            return super().step()
    rows=[]
    for name in('MegaManCollisionAdder','MegaManCollisionBox'):
        pair=[]
        for enabled in(False,True):
            m=clone(enabled)
            with patch.object(N,'NesMPU',CPU):r=N.invoke(m,name,a=85,x=7,y=91,p=0x69)
            assert m.guard_entries==int(enabled);pair.append((m,r))
        (a,ra),(z,rz)=pair;diff=[dict(address=i,old=a[i],new=z[i])for i in[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]if a[i]!=z[i]]
        assert all(ra[n]==rz[n]for n in('A','X','Y','P'))
        assert a.ram==z.ram and a.rawtags==z.rawtags and a.chr_latches==z.chr_latches
        rows.append(dict(caller=name,return_registers={n:rz[n]for n in('A','X','Y','P')},old_cycles=ra['CPU'],new_cycles=rz['CPU'],cycles_saved=ra['CPU']-rz['CPU'],global_or_SMC_differences=diff))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),detached_guard_complete_caller_components=rows,
        optimistic_PC_redirection_only_not_source_overlay=True,ISR_qualified=False,outputs=0)


def guard_liveness(raw):
    seed=cold(raw);base=type(seed);cpu_base=N.NesMPU;program=bytes.fromhex('c00cf004c00dd0052828a00060');unit=0x5800
    ctx=dict(active=False,pc=0,tag=0);reads=Counter();writes=Counter();first=[]
    class View(base):
        def __getitem__(self,at):
            if isinstance(at,int):
                if ctx['active']and at in getattr(self,'smc_watch',{}):
                    stamp=(at,ctx['tag'],ctx['pc']);reads[stamp]+=1
                    if len(first)<16:first.append(dict(kind='read',address=at,tag=ctx['tag'],PC=ctx['pc'],value=super().__getitem__(at)))
                if unit<=at<unit+len(program):return program[at-unit]
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if isinstance(at,int)and ctx['active']and at in getattr(self,'smc_watch',{}):
                stamp=(at,ctx['tag'],ctx['pc']);writes[stamp]+=1;self.smc_watch.pop(at)
                if len(first)<16:first.append(dict(kind='overwrite',address=at,tag=ctx['tag'],PC=ctx['pc'],value=value&255))
            return super().__setitem__(at,value)
    m=list.__new__(View);list.extend(m,list.__iter__(seed))
    for key,value in seed.__dict__.items():setattr(m,key,value if key=='bundle'else deepcopy(value))
    m.smc_watch={};entries=Counter();rows=[]
    class CPU(cpu_base):
        def step(self):
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if tag==207 and self.pc==0xb8b8 and self.y in(12,13):
                assert self.a==33;entries[self.y]+=1;self.pc=unit;tag=-1
            before=self.pc;ctx.update(active=True,pc=self.pc,tag=tag)
            try:result=super().step()
            finally:ctx['active']=False
            if before==unit+12:m.smc_watch={at:True for at in(0x162,0x16c,0x16d)}
            return result
    with patch.object(N,'NesMPU',CPU):
        for phase,pad,count in(('idle',0,4),('right',1,4)):
            cycles=[]
            for _ in range(count):m.controller_pad=pad;cycles.append(Frames.frame(m,whole_pass=True))
            rows.append(dict(phase=phase,completed_passes=count,Main_cycles=cycles,pending_fields=sorted(m.smc_watch)))
            print('PROGRESS '+json.dumps(rows[-1]),flush=True)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_cold=True,ordinary_inputs=True,
        optimistic_PC_redirection_only_not_source_overlay=True,guard_entries=dict(entries),phases=rows,
        actual_reads_before_first_overwrite=[dict(address=a,tag=t,PC=p,count=n)for(a,t,p),n in sorted(reads.items())],
        actual_first_overwrites=[dict(address=a,tag=t,PC=p,count=n)for(a,t,p),n in sorted(writes.items())],
        first_events=first,not_a_static_all_consumer_proof=True,outputs=0)


def guard_return_interrupts(raw):
    seed=cold(raw);base=type(seed);cpu_base=N.NesMPU;program=bytes.fromhex('c00cf004c00dd0052828a00060');unit=0x5800
    b=seed.bundle;targets={W.address(b,n):n for n in('MegaManCollisionAdder','MegaManCollisionBox')};captures={};entry_captures={}
    class View(base):
        def __getitem__(self,at):
            if isinstance(at,int)and unit<=at<unit+len(program):return program[at-unit]
            return super().__getitem__(at)
    def clone():
        m=list.__new__(View);list.extend(m,list.__iter__(seed))
        for key,value in seed.__dict__.items():setattr(m,key,value if key=='bundle'else deepcopy(value))
        return m
    class CPU(cpu_base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[]
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if self.pending and(self.pc,self.sp)==self.pending[-1][1:]:
                name,*_=self.pending.pop();captures.setdefault((m.guard_enabled,name),(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')}))
            if tag==254 and self.pc in targets:
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                self.pending.append((targets[self.pc],ret,(self.sp+2)&255))
            if m.guard_enabled and tag==207 and self.pc==0xb8b8 and self.y in(12,13):
                entry_captures.setdefault(self.y,(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')}));self.pc=unit
            return super().step()
    for enabled in(False,True):
        m=clone();m.guard_enabled=enabled;m.controller_pad=0
        with patch.object(N,'NesMPU',CPU):Frames.frame(m,whole_pass=True)
    assert len(captures)==4,sorted(captures)
    def execute(arena,regs,kind):
        m=N.fork(arena);c=cpu_base(memory=m,pc=regs['pc'])
        for name,value in regs.items():setattr(c,name,value)
        original=tuple(regs[n]for n in('pc','sp','a','x','y','p'));minimum=c.sp
        assert N.get(m,'NmiDisable')&128,'Actual captured Main busy arm only'
        assert kind!='IRQ'or not c.p&4,'Do not claim an actually masked IRQ'
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(200000):
            minimum=min(minimum,c.sp)
            if(c.pc,c.sp)==original[:2]:break
            assert m[c.pc],('ISR BRK',kind,hex(c.pc));c.step()
        else:raise AssertionError('Actual getter-return ISR bound')
        actual=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
        assert actual[:5]==original[:5]and actual[5]&0xef==original[5]&0xef
        assert bytes(m[0x101+regs['sp']:0x200])==bytes(arena[0x101+regs['sp']:0x200])
        assert m.rawtags==arena.rawtags and m.chr_latches==arena.chr_latches and m.ram==arena.ram
        assert bytes(m[0x15a:0x17b])==bytes(arena[0x15a:0x17b])
        assert(N.get(m,'NmiSkipped')-N.get(arena,'NmiSkipped'))&255==int(kind=='NMI')
        return m,actual,minimum
    rows=[];minimum=255
    for name in targets.values():
        old,oldregs=captures[False,name];new,newregs=captures[True,name]
        assert oldregs==newregs,(name,oldregs,newregs)
        before=[i for i in[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]if old[i]!=new[i]]
        assert before==[0x162,0x16c,0x16d],(name,before)
        kinds=('NMI',)if oldregs['p']&4 else('IRQ','NMI')
        for kind in kinds:
            a,ar,lo=execute(old,oldregs,kind);z,zr,lz=execute(new,newregs,kind);minimum=min(minimum,lo,lz)
            assert ar==zr and a.ram==z.ram and a.rawtags==z.rawtags and a.chr_latches==z.chr_latches
            diff=[dict(address=i,old=a[i],new=z[i])for i in[*range(0x17b),*range(0x200,0x800),*range(0x5c00,0x8000)]if a[i]!=z[i]]
            rows.append(dict(caller=name,actual_return=oldregs,kind=kind,after_ISR_differences=diff))
    cuts=[]
    for slot,(arena,regs)in sorted(entry_captures.items()):
        m=N.fork(arena);c=cpu_base(memory=m,pc=unit)
        for name,value in regs.items():setattr(c,name,value)
        c.pc=unit;boundaries=[]
        while unit<=c.pc<unit+len(program):
            boundaries.append((N.fork(m),{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}));c.step()
        expected=(c.pc,c.sp,c.a,c.x,c.y,c.p&0xef)
        for state,boundary in boundaries:
            kinds=('NMI',)if boundary['p']&4 else('IRQ','NMI')
            for kind in kinds:
                z,_,low=execute(state,boundary,kind);minimum=min(minimum,low);q=cpu_base(memory=z,pc=boundary['pc'])
                for name,value in boundary.items():setattr(q,name,value)
                while unit<=q.pc<unit+len(program):q.step()
                actual=(q.pc,q.sp,q.a,q.x,q.y,q.p&0xef);assert actual==expected,(slot,boundary,kind,actual,expected)
                cuts.append(dict(slot=slot,PC=boundary['pc'],P=boundary['p'],SP=boundary['sp'],kind=kind))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_compiled_cold_and_Main=True,
        actual_complete_caller_return_ISR_pairs=rows,minimum_SP=minimum,regular_NMI_inside_Main_busy_unreachable=True,
        actual_reached_detached_guard_instruction_cuts=cuts,detached_guard_ISR_preserves_AXYP_SP_SMC_maps_live_stack=True,
        optimistic_PC_redirection_only_not_source_overlay=True,not_an_all_lifecycle_or_static_consumer_qualification=True,outputs=0)


def smc_readers(raw):
    b=bundle(raw);fields=(0x162,0x16c,0x16d);rows=[];ops={0xad:'LDA',0xae:'LDX',0xac:'LDY',0x6d:'ADC',0xed:'SBC',0x2d:'AND',0x0d:'ORA',0x4d:'EOR',0xcd:'CMP',0xec:'CPX',0xcc:'CPY',0x2c:'BIT',0x6c:'JMPind',0x0e:'ASL',0x2e:'ROL',0x4e:'LSR',0x6e:'ROR',0xce:'DEC',0xee:'INC'}
    locations=[]
    for name in b['syms']:
        try:where=W.location(b,name)
        except(KeyError,AssertionError):continue
        locations.append((where,name))
    locations.sort();positions=[p for p,_ in locations]
    def scan(data,base,tag,role):
        for i in range(len(data)-2):
            if data[i]not in ops or int.from_bytes(data[i+1:i+3],'little')not in fields:continue
            pc=base+i;at=16+(tag&127)*8192+(pc&8191)if tag&128 else None;names=[]
            if at is not None:
                k=bisect_right(positions,at)
                for where,name in locations[max(0,k-12):k]:
                    if 0<=at-where<=32:names.append((at-where,name))
            rows.append(dict(role=role,tag=tag,PC=pc,file=at,opcode=ops[data[i]],address=int.from_bytes(data[i+1:i+3],'little'),
                bytes=data[i:i+3].hex(),context=data[max(0,i-4):i+8].hex(),nearest_symbols=sorted(names)[:2]))
    for bank in range(128):scan(raw[16+bank*8192:16+(bank+1)*8192],0x8000 if bank==126 else 0xe000 if bank==127 else 0xa000,bank|128,'PRG')
    # These two owners have separate raw executable cache containers. The
    # source-container inventory remains a lead until execution/CFG binding.
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in('BT_STREAM','CF_CARRIER'):continue
        at=int(seg['ooffs'],0);size=int(seg['size'],0);scan(raw[at:at+size],0xa000,3,seg['name'])
    return dict(ROM_SHA256=sha256(raw).hexdigest(),absolute_SMC_read_literal_leads=rows,
        literal_leads_not_instruction_or_consumer_qualification=True,outputs=0)


def static_domains(raw):
    b=bundle(raw);bases={n:W.address(b,n)for n in('HuLo','HuPairIndex','HuPairHi','HuPairBank')};prg=raw[16:1048592]
    consumers=[]
    for name,pc in bases.items():
        pattern=bytes((0xb9,pc&255,pc>>8));hits=[];at=0
        while(at:=prg.find(pattern,at))>=0:hits.append(16+at);at+=1
        consumers.append(dict(name=name,CPU=pc,LDA_abs_Y_literal_files=hits))
    expected_files=(653484,653490,653494,653500)
    for row,expected_file in zip(consumers,expected_files,strict=True):
        assert expected_file in row['LDA_abs_Y_literal_files']
        row['other_literal_aliases']=[at for at in row['LDA_abs_Y_literal_files']if at!=expected_file]
    fields={n:W.address(b,n)for n in('MegaManCollisionAdder','MegaManCollisionBox')};calls=[]
    for name,pc in fields.items():
        hits=[]
        for op in(0x20,0x4c):
            pattern=bytes((op,pc&255,pc>>8));at=0
            while(at:=prg.find(pattern,at))>=0:hits.append(dict(file=16+at,opcode=op,context=prg[max(0,at-8):at+11].hex()));at+=1
        calls.append(dict(name=name,CPU=pc,direct_control_literal_leads=hits))
    named=set(bases)|{'HuResolve','HuCommonAfterSelected'};debug=[]
    for name in('kirby-approach-owner-1101-v3/candidate.dbg','bub-menu-candidate-1102-v2/combined-event.dbg','thomas-current-candidate-1102-v3/candidate.dbg'):
        data=(Frozen.Service.R/'build'/name).read_text();records=[]
        for line in data.splitlines():
            if not line.startswith('sym\t')or not any('name="'+n+'"'in line for n in named):continue
            row=dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if'='in x);records.append(row)
        debug.append(dict(path=name,SHA256=sha256(data.encode()).hexdigest(),records=records))
    targets=set(range(0xb84b,0xb854))|{0xb85c,0xba54}|set(bases.values());indirect=[]
    def check(role,rows):
        hits=[r for r in rows if r['bank']==207 and r['CPU']in targets];assert not hits,(role,hits)
        indirect.append(dict(role=role,rows=len(rows),targets_into_changed_entries_or_table_bases=hits))
    lo,ix,hi,bank=(W.location(b,n)for n in('HuLo','HuPairIndex','HuPairHi','HuPairBank'))
    check('Hu144',[dict(CPU=raw[lo+i]+256*raw[hi+raw[ix+i]],bank=raw[bank+raw[ix+i]])for i in range(144)])
    at=W.location(b,'WfResolveTargets');check('Wf36',[dict(CPU=raw[at+3*i]+256*raw[at+3*i+1],bank=raw[at+3*i+2])for i in range(36)])
    planes=[W.location(b,n)for n in('BwColdLo','BwColdHi','BwColdBank')]
    check('Bw8',[dict(CPU=raw[planes[0]+i]+256*raw[planes[1]+i],bank=raw[planes[2]+i])for i in range(8)])
    data=raw[16+124*8192:16+125*8192];nr=0
    for i in range(len(data)-42):
        code=data[i:i+27]
        if code[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(code[9]==code[15]==code[21]==0xb9 and code[12:15]==bytes.fromhex('8d6c01')and code[18:21]==bytes.fromhex('8d6d01')and code[24:27]==bytes.fromhex('4c0da6')):continue
        planes=[int.from_bytes(code[j:j+2],'little')&8191 for j in(10,16,22)]
        check('Nr5@'+hex(0xa000+i),[dict(CPU=data[planes[0]+j]+256*data[planes[1]+j],bank=data[planes[2]+j])for j in range(5)]);nr+=1
    assert nr==13
    # Authenticate the numeric table that produced all four B85C aliases.
    at=W.location(b,'AvHomeFriction::ProductLo');expected=bytes((i*63068)&255 for i in range(256));assert raw[at:at+256]==expected
    return dict(ROM_SHA256=sha256(raw).hexdigest(),four_bound_current_table_readers_and_literal_aliases=consumers,
        getter_direct_control_leads=calls,current_compiler_references=debug,
        structured_indirect_target_domain_exclusion=indirect,ProductLo_numeric_table=dict(file=at,bytes=256,SHA256=sha256(expected).hexdigest()),
        compiler_refs_and_literal_leads_require_owner_context=True,all_domain_closure_not_claimed=True,outputs=0)


def ingress(raw):
    b=bundle(raw);words=[];macros=[];targets=(0xb85c,0xba54)
    for prg in range(128):
        page=raw[16+prg*8192:16+(prg+1)*8192]
        for target in targets:
            start=0;pattern=target.to_bytes(2,'little')
            while(start:=page.find(pattern,start))>=0:
                words.append(dict(PRG=prg,CPU=(0xa000 if prg<126 else 0x8000 if prg==126 else 0xe000)+start,
                    file=16+prg*8192+start,target=target,preceding=page[start-1]if start else None,
                    context=page[max(0,start-10):start+8].hex()));start+=1
        pattern=bytes.fromhex('a9548d6c01a9ba8d6d01a9cf');start=0
        while(start:=page.find(pattern,start))>=0:
            macros.append(dict(PRG=prg,CPU=(0xa000 if prg<126 else 0x8000 if prg==126 else 0xe000)+start,
                file=16+prg*8192+start,bytes=page[start-3:start+15].hex()));start+=1
    at=16+79*8192;page=raw[at:at+8192];rel=[]
    for i in range(8191):
        if page[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
            dest=0xa000+i+2+(page[i+1]if page[i+1]<128 else page[i+1]-256)
            if dest==0xb85c:rel.append(dict(CPU=0xa000+i,file=at+i,bytes=page[i:i+2].hex(),in_declared_table=i>=0x18d8))
    lo=page[0x18d8:0x1968];index=page[0x1968:0x19f8];hi=page[0x19f8:0x1a26];bank=page[0x1a26:0x1a54]
    hu_targets=[dict(index=i,bank=bank[k],CPU=lo[i]+256*hi[k])for i,k in enumerate(index)]
    assert len(hu_targets)==144 and max(index)==45
    debug=[]
    for name in('kirby-approach-owner-1101-v3/candidate.dbg','bub-menu-candidate-1102-v2/combined-event.dbg','thomas-current-candidate-1102-v3/candidate.dbg'):
        path=Frozen.Service.R/'build'/name;text=path.read_text();refs=set();defs=[]
        parse=lambda line:dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if'='in x)
        for line in text.splitlines():
            if line.startswith('sym\t')and any('name="'+n+'"'in line for n in('HuResolve','HuCommonAfterSelected')):
                row=parse(line);defs.append(row);refs.update(row.get('ref','').split('+'))
        refs.discard('');lines=[];wanted=set();segments={}
        for line in text.splitlines():
            if line.startswith('seg\t'):
                row=parse(line);segments[row['id']]=row
            elif line.startswith('line\t'):
                row=parse(line)
                if row['id']in refs:lines.append(row);wanted.update(row.get('span','').split('+'))
        spans=[]
        for line in text.splitlines():
            if not line.startswith('span\t'):continue
            row=parse(line)
            if row['id']not in wanted:continue
            seg=segments[row['seg']]
            if'ooffs'not in seg:continue
            file=int(seg['ooffs'],0)+int(row['start'],0);size=int(row['size'],0)
            spans.append(dict(file=file,CPU=int(seg['start'],0)+int(row['start'],0),size=size,current=raw[file:file+size].hex(),segment=seg['name']))
        debug.append(dict(path=name,SHA256=sha256(text.encode()).hexdigest(),symbol_records=defs,reference_spans=spans))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),literal_words=words,standard_HuResolve_farcall_macros=macros,
        bank79_relative_AfterSelected_leads=rel,Hu144_structured_targets_into_entries=[r for r in hu_targets if r['bank']==207 and r['CPU']in targets],
        source_debug_references=debug,literal_scan_alone_is_not_ingress_qualification=True,decoded_containers_pending=True,
        opcode_or_data_placed=False,outputs=0)


def entry_words(data,base):
    rows=[]
    for target in(0xb85c,0xba54):
        pattern=target.to_bytes(2,'little');start=0
        while(start:=data.find(pattern,start))>=0:
            rows.append(dict(target=target,offset=start,CPU=base+start,preceding=data[start-1]if start else None,
                context=data[max(0,start-8):start+8].hex()));start+=1
    return rows


def decoded(raw):
    b=dict(bundle(raw),raw=raw);rows=[]
    with patch.object(Containers,'matches',entry_words):
        for owner in range(37,44):
            q=Containers.common_cold(raw,owner,b);rows.append(q)
            print('PROGRESS '+json.dumps(dict(owner=owner,code=q['code_target_words'],metadata=q['metadata_target_words'])),flush=True)
    head,streams,packed=Packet.extract(raw);prince=[]
    for role,base,data,n in zip(('Prince_runtime','Prince_metadata','Prince_staged_state'),(0xa000,0xc800,0xc100),streams,packed,strict=True):
        prince.append(dict(role=role,bytes=len(data),packed_bytes=n,SHA256=sha256(data).hexdigest(),entry_words=entry_words(data,base)))
    other=[];seen=set();names={'FF_STREAM','BW_STREAM','BT_STREAM','CF_CARRIER','QW_STREAM','KR_KERNEL_IMAGE','ARTHUR_CACHE_EXEC','WF_TEMPLATE_CHR'}
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in names:continue
        at=int(seg['ooffs'],0);size=int(seg['size'],0)
        if(at,size)in seen:continue
        seen.add((at,size));data=raw[at:at+size]
        other.append(dict(role=seg['name'],file=[at,at+size],bytes=size,SHA256=sha256(data).hexdigest(),entry_words=entry_words(data,0)))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),current_common7_actual_loader_results=rows,
        current590_Prince_authenticated_decoded_streams=prince,Prince_decoder_loader_words=entry_words(head[-704:],0),
        other_declared_raw_containers=other,word_hits_need_bank_reader_classification=True,
        component_forcedblank_loads_not_natural_menu_or_gameplay=True,opcode_or_data_placed=False,outputs=0)


def immediate_entries(data):
    result=[]
    for target in(0xb85c,0xba54):
        pattern=bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1,0xa9,207));start=0
        while(start:=data.find(pattern,start))>=0:
            result.append(dict(target=target,offset=start,context=data[max(0,start-3):start+15].hex()));start+=1
    return result


def immediates(raw):
    b=bundle(raw);regions=[]
    # Exact source-page domains authenticated by actual current590 loader
    # receipt036c9d2b... in --decoded49105. Joining all descriptor rows is an
    # overapproximation across the code/metadata boundary, not a new decode.
    descriptor_pages={37:(728,729,730,731,732,733,734,735),38:(617,619),
        39:(301,305,337,362,363,440,819,666,441),40:(960,961),41:(967,),42:(991,992),43:(328,)}
    for owner,pages in descriptor_pages.items():
        data=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
        regions.append(dict(role='actual_common_descriptor_rows_'+str(owner),bytes=len(data),SHA256=sha256(data).hexdigest(),farcall_immediates=immediate_entries(data)))
    head,streams,_=Packet.extract(raw)
    for role,data in zip(('Prince_runtime','Prince_metadata','Prince_staged_state'),streams,strict=True):
        regions.append(dict(role=role,bytes=len(data),SHA256=sha256(data).hexdigest(),farcall_immediates=immediate_entries(data)))
    regions.append(dict(role='Prince_decoder_loader',bytes=704,farcall_immediates=immediate_entries(head[-704:])))
    seen=set();names={'FF_STREAM','BW_STREAM','BT_STREAM','CF_CARRIER','QW_STREAM','KR_KERNEL_IMAGE','ARTHUR_CACHE_EXEC','WF_TEMPLATE_CHR'}
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in names:continue
        at=int(seg['ooffs'],0);size=int(seg['size'],0)
        if(at,size)in seen:continue
        seen.add((at,size));data=raw[at:at+size]
        regions.append(dict(role=seg['name'],file=[at,at+size],farcall_immediates=immediate_entries(data)))
    context=[]
    for at in(54677,54741,54805,54869,973412):
        labels=[];segments=[]
        for name,s in b['segs'].items():
            if'ooffs'not in s:continue
            start,size=int(s['ooffs'],0),int(s['size'],0)
            if start<=at<start+size:segments.append(dict(id=name,name=s['name'],file=[start,start+size]))
        for name in b['syms']:
            try:where=W.location(b,name)
            except(KeyError,AssertionError):continue
            if at-32<=where<=at:labels.append((at-where,name))
        context.append(dict(file=at,segments=segments,nearest_symbols=sorted(labels)[:8]))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_loader_receipt='036c9d2b5bfb580bcaadd39dbf9add34e3bd1b28733388d576bba57dd547eb28',
        decoded_and_declared_container_immediate_census=regions,remaining_word_contexts=context,
        raw_or_numeric_data_is_not_automatically_an_entry=True,opcode_or_data_placed=False,outputs=0)


def normalizer(raw):
    at=16+79*8192+0x184b;old=raw[at:at+9]
    assert old==bytes.fromhex('ade55f2944c940d005')
    # Same bit6=1/bit2=0 predicate. All fallback A values become4. BIT's
    # temporary V change must be discharged by the actual saved-P epilogue.
    new=bytes.fromhex('a9042ce55f5007d005')
    return at,old,new


def selector_bus(raw,changed):
    b=dict(bundle(raw),raw=raw);at,old,new=normalizer(raw);base=N.Bus
    class View(base):
        def __getitem__(self,key):
            if isinstance(key,int)and changed and 0xb84b<=key<0xb854 and self.rawtags[1]==207:return new[key-0xb84b]
            return super().__getitem__(key)
    m=View(b);m.raw_page(1,207);N.put(m,CurrentBank=207,CurrentBankC=m.rawtags[2]);return m


def normalize_units(raw):
    b=bundle(raw);ms=[selector_bus(raw,flag)for flag in(False,True)];cases=0;domains=Counter();minimum=255
    fields={n:W.address(b,n)for n in('SelectedCharacter','FmAlts','RdVariant')}
    # Exhaust all FM byte values with four status corners, then every valid
    # status with the four predicate classes. These are declared selector
    # component inputs; they do not claim natural menu/gameplay coverage.
    vectors={(fm,p)for fm in range(256)for p in(0x20,0x31,0x69,0xe5)}
    vectors.update((fm,p)for fm in(0,4,64,68)for p in range(256)if p&32)
    endpoints=Counter()
    for fm,p in sorted(vectors):
        for slot in range(36):
            pair=[]
            for changed,m in enumerate(ms):
                m[fields['SelectedCharacter']]=10;m[fields['FmAlts']]=fm;m[fields['RdVariant']]=0
                cpu=N.NesMPU(memory=m,pc=0xb600+16*slot);cpu.a=85;cpu.x=7;cpu.y=91;cpu.p=p;cpu.sp=224;cpu.stPushWord(0x5aff)
                visited=[]
                for step in range(1000):
                    if cpu.pc in(0x15a,0x15d,0x5b00):break
                    assert m.rawtags[1]==207
                    if cpu.pc==0xb85c:
                        visited.append(cpu.a)
                        if changed:assert cpu.a<=33
                    minimum=min(minimum,cpu.sp);assert m[cpu.pc];cpu.step()
                else:raise AssertionError(('Normalized selector bound',fm,p,slot,cpu.pc))
                pair.append((cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,bytes(m[:0x100]),bytes(m[0x200:0x800]),
                    bytes(m[0x15a:0x17b]),bytes(m[0x100+cpu.sp+1:0x200]),tuple(map(bytes,m.ram)),tuple(m.rawtags)))
                if changed:domains.update(visited)
            assert pair[0]==pair[1],('Complete selector endpoint differs',fm,p,slot,pair[0][:6],pair[1][:6])
            endpoints[pair[0][0]]+=1;cases+=1
    at,old,new=normalizer(raw)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),selector_component_cases=cases,all256_FmAlts_four_P=True,
        all128_valid_P_four_predicate_classes=True,all36_public_services=True,owner=10,
        exact_endpoint_AXYP_SP_live_RAM_physical_RAM_SMC_maps=True,AfterSelected_A_domain=dict(domains),
        endpoints=dict(endpoints),minimum_SP=minimum,normalization=dict(file=at,old_hex=old.hex(),new_hex=new.hex()),
        old_domain_negative=dict(job=67227,owner=10,FmAlts=68,slot=0,P=32,AfterSelected_A=68),
        transient_BIT_V_not_ISR_qualified=True,code_arrays_only_no_ROM_or_RAM_opcode_writes=True,outputs=0)


def normalizer_interrupts(raw):
    base=N.NesMPU;captured=[];b=dict(bundle(raw),raw=raw)
    class Capture(base):
        def step(self):
            m=self.memory
            if self.pc==0xb84b and m.rawtags[1]==207 and N.get(m,'OperMode')==1 and N.get(m,'GameEngineSubroutine')==8 and not captured:
                captured.append((N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')}))
            return super().step()
    with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        for pad in(4,1,1,32,32):W.UI.key(m,pad)
        name=W.UI.menu_name(m)[0]
        assert(name,N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'FmAlts')&0x44)==('THOMAS',10,10,64)
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Actual Thomas cold constructor bound')
        assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        assert N.invoke(m,'ThCheck')['P']&1,'Actual current Thomas cache/header check'
        m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(captured)==1 and N.get(m,'SelectedCharacter')==10 and N.get(m,'FmAlts')&0x44==0x40
    seed,regs=captured[0];unit=0x5800;program=bytes.fromhex('a9042ce55f5005d0034c54b84c59b8');parent=type(seed)
    class View(parent):
        def __getitem__(self,at):
            if isinstance(at,int)and unit<=at<unit+len(program):return program[at-unit]
            return super().__getitem__(at)
    def clone():
        m=list.__new__(View);list.extend(m,list.__iter__(seed))
        for field,value in seed.__dict__.items():setattr(m,field,value if field=='bundle'else deepcopy(value))
        return m
    def finish(m,state):
        c=base(memory=m,pc=state['pc'])
        for field,value in state.items():setattr(c,field,value)
        for _ in range(1000):
            if c.pc==0x15d:return c,(c.pc,c.sp,c.a,c.x,c.y,c.p&0xef)
            assert m[c.pc];c.step()
        raise AssertionError('Thomas normalizer endpoint bound')
    rows=[];minimum=255
    for fm in(0,4,64,68):
        arena=clone();N.put(arena,FmAlts=fm);c=base(memory=arena,pc=unit)
        for field,value in regs.items():setattr(c,field,value)
        c.pc=unit;cuts=[]
        for _ in range(1000):
            if c.pc==0x15d:break
            if unit<=c.pc<unit+9:cuts.append((N.fork(arena),{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
            assert arena[c.pc];c.step()
        else:raise AssertionError('Normalizer capture bound')
        expected=(c.pc,c.sp,c.a,c.x,c.y,c.p&0xef)
        for state,r in cuts:
            assert N.get(state,'NmiDisable')&128
            kinds=('NMI',)if r['p']&4 else('IRQ','NMI')
            for kind in kinds:
                pair=[]
                for toggle_V in(False,True):
                    z=N.fork(state);v=base(memory=z,pc=r['pc'])
                    for field,value in r.items():setattr(v,field,value)
                    if toggle_V:v.p^=64
                    before=(v.pc,v.sp,v.a,v.x,v.y,v.p);skipped=N.get(z,'NmiSkipped')
                    v.irq()if kind=='IRQ'else v.nmi()
                    for _ in range(200000):
                        minimum=min(minimum,v.sp)
                        if(v.pc,v.sp)==before[:2]:break
                        assert z[v.pc],('Normalizer ISR BRK',fm,kind,hex(v.pc));v.step()
                    else:raise AssertionError('Normalizer ISR bound')
                    after=(v.pc,v.sp,v.a,v.x,v.y,v.p)
                    assert after[:5]==before[:5]and after[5]&0xef==before[5]&0xef
                    assert bytes(z[0x101+r['sp']:0x200])==bytes(state[0x101+r['sp']:0x200])
                    assert bytes(z[0x15a:0x17b])==bytes(state[0x15a:0x17b])
                    assert z.rawtags==state.rawtags and z.chr_latches==state.chr_latches
                    assert(N.get(z,'NmiSkipped')-skipped)&255==int(kind=='NMI')
                    pair.append((z,{n:getattr(v,n)for n in('pc','sp','a','x','y','p')}))
                assert pair[0][0].ram==pair[1][0].ram
                for lo,hi in((0,0x17b),(0x200,0x800),(0x5c00,0x8000)):
                    assert bytes(pair[0][0][lo:hi])==bytes(pair[1][0][lo:hi]),('IRQ data depends on transient V',fm,kind,lo)
                _,actual=finish(*pair[0]);assert actual==expected,(fm,r,kind,actual,expected)
                rows.append(dict(FmAlts=fm,PC=r['pc'],P=r['p'],SP=r['sp'],kind=kind))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_compiled_Thomas_cold=True,real_name=name,actual_prefix_entry=regs,
        reached_detached_prefix_ISR_cuts=rows,minimum_SP=minimum,actual_FmAlts64=True,
        other_FmAlts_are_declared_predicate_component_inputs=True,toggle_V_pairs_are_explicit_ISR_components=True,
        exact_ISR_AXYP_SP_SMC_maps_live_stack=True,IRQ_all_RAM_effects_independent_of_transient_V=True,
        native_ISR_audio_effects_allowed_only_by_exact_paired_comparison=True,restored_selector_endpoints_exact=True,
        regular_NMI_in_actual_Main_busy_unreachable=True,code_arrays_only_no_ROM_or_RAM_opcode_writes=True,outputs=0)


def domain(raw,normalized=False):
    b=dict(bundle(raw),raw=raw);m=selector_bus(raw,normalized)
    N.put(m,CurrentBank=207,CurrentBankC=m.rawtags[2]);owners=Counter();cases=0;max_steps=0;private_entries=[]
    fields={n:W.address(b,n)for n in('SelectedCharacter','FmAlts','RdVariant')}
    for slot in range(36):
        at=16+79*8192+0x1600+16*slot
        assert raw[at:at+11]==bytes.fromhex('8d6a01089848a0')+bytes((slot,))+bytes.fromhex('4c40b8')
    for owner in range(256):
        variants=[(f,0)for f in(0,4,32,36,64,68,96,100)]if owner in(9,10)else[(0,r)for r in(0,1,2)]if owner==2 else[(0,0)]
        for fm,rd in variants:
            for slot in range(36):
                for p in(0x20,0x31,0x69,0xe5):
                    m[fields['SelectedCharacter']]=owner;m[fields['FmAlts']]=fm;m[fields['RdVariant']]=rd
                    cpu=N.NesMPU(memory=m,pc=0xb600+16*slot);cpu.a=85;cpu.x=7;cpu.y=91;cpu.p=p;cpu.sp=224;cpu.stPushWord(0x5aff)
                    for step in range(1000):
                        if cpu.pc in(0x15a,0x15d,0x5b00):break
                        assert m.rawtags[1]==207
                        if cpu.pc==0xb85c:
                            owners[cpu.a]+=1;assert cpu.a<=33,(owner,fm,rd,slot,p,cpu.a)
                        assert m[cpu.pc],('Selector BRK',owner,slot,hex(cpu.pc));cpu.step()
                    else:raise AssertionError(('Public selector domain bound',owner,fm,rd,slot,p,cpu.pc))
                    max_steps=max(max_steps,step);cases+=1
        if owner%64==63:print('PROGRESS '+json.dumps(dict(public_owner=owner,cases=cases)),flush=True)
    # Direct private aliases are not arbitrary public A-entrypoints: one is
    # dominated by the selected<34 path and CMP9; the other explicitly LDA9.
    page=raw[16+79*8192:16+80*8192]
    assert page[0x160b:0x1610]==bytes.fromhex('c9194cebb7')
    assert page[0x17eb:0x17f0]==bytes.fromhex('f01e4cfbb7')
    assert page[0x17fb:0x1800]==bytes.fromhex('c9094c1bb6')
    assert page[0x161b:0x1620]==bytes.fromhex('f0d84c5cb8')
    assert page[0x162b:0x1630]==bytes.fromhex('a9094c5cb8')
    return dict(ROM_SHA256=sha256(raw).hexdigest(),public36_selector_cases=cases,
        all256_selected_values=True,all_Quick_Thief_relevant_FmAlts_bits_and_Ryu_RdVariant_cases=True,
        component_statuses=[0x20,0x31,0x69,0xe5],AfterSelected_A_domain=dict(owners),maximum_instructions=max_steps,
        private_aliases=[dict(PC=0xb61b,domain='Original selected<34, after CMP25/CMP9; both predicates preserve A'),
            dict(PC=0xb62b,domain='Explicit LDA9 before sole JMPAfterSelected')],
        endpoint='Stop before any external farcall/callback; this is selector-domain evidence, not gameplay',
        normalizer_detached=normalized,actual_opcode_arrays_unchanged=not normalized,opcode_or_data_placed=False,outputs=0)


if __name__=='__main__':
    modes={'callers':callers,'frame':frame,'construct':construct,'layout':layout,
        'construct-units':construct_units,'ingress':ingress,'decoded':decoded,'immediates':immediates,
        'domain':domain,'normalize-units':normalize_units,'normalized-domain':lambda raw:domain(raw,True),
        'menu-inspect':lambda raw:construct_menus(raw,True),'construct-menus':construct_menus,
        'guard-units':guard_units,'guard-liveness':guard_liveness,'smc-readers':smc_readers,
        'guard-return-interrupts':guard_return_interrupts,'constructor-interrupts':constructor_interrupts,
        'static-domains':static_domains,'normalizer-interrupts':normalizer_interrupts}
    ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group()
    for mode in modes:group.add_argument('--'+mode,action='store_true')
    args=ap.parse_args();raw,info=load()
    action=next((fn for name,fn in modes.items()if getattr(args,name.replace('-','_'))),inspect)
    def forbid(*a,**kw):raise RuntimeError('Funding research attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Frozen.Cold.Runner.Native,'run',forbid):q=action(raw)
    q.update(info);q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
