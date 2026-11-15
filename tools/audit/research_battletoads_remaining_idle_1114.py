"""Exact ae66 remaining Main/NMI attribution; no new opcode placement or ROM output."""
from collections import Counter
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import compose_battletoads_native_service_1114 as Service
import compose_native_floatey_score_1114 as Score
import check_battletoads_camera_candidate_1114 as Cold
import profile_battletoads_current_idle_1114 as Previous
from measure_battletoads_passthrough_fit_1114 import Code

W,N,Frames=Previous.W,Previous.N,Previous.Frames
ROM=Previous.F.ROM


def load():
    raw=ROM.read_bytes();pin=sha256(raw).hexdigest()
    if pin==Service.PIN:image=Service.proposal(raw)[0];kind='571-existing-ae66-composition'
    elif pin==Service.CANDIDATE:Service.inverse(raw);image=raw;kind='ae66-current'
    else:raise AssertionError('Expected exact571 or exactae66; no automatic dirty fallback')
    return image,dict(actual_input_SHA256=pin,research_owning_SHA256=sha256(image).hexdigest(),kind=kind)


def cold(raw):
    assert sha256(raw).hexdigest()==Service.CANDIDATE
    normalized=Score.inverse(Service.inverse(raw));factory=Cold.F
    class Current:
        @staticmethod
        def bindings(image,key):
            assert image is raw
            return factory.bindings(normalized,key)
    with patch.object(Cold.Previous,'Factory',Current):m=Cold.Previous.cold(raw,'rash')
    assert m.bundle['raw']is raw
    return m


def profile(raw,count=8):
    m=cold(raw);b=m.bundle;base=N.NesMPU;idle=W.address(b,'IdleLoop')
    entries=Previous.points(raw,b);macros=Previous.save_blocks(raw,b)
    for slot in range(36):entries[215,0xb020+3*slot]=['public_slot'+str(slot)]
    # Current ae66 bytes, not the historical prefix symbol at E4A7.
    entries[255,0xe4ab]=['ae66_fixed_side_prefix']
    tail=W.location(b,'MmSideDispatchTail')
    entries[((tail-16)//8192)|128,W.address(b,'MmSideDispatchTail')]=['MmSideDispatchTail_actual']
    entries[161,0xbea2]=['MmNativeSideShortcut_actual']
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    phases=[]
    for phase,pad in(('idle',0),('walk_right',1)):
        calls=Counter();returned=Counter();inclusive=Counter();exclusive=Counter();pcs=Counter();banks=Counter()
        macro_cost=Counter();macro_calls=Counter();cpus=[];rows=[];minimum=255;opening=Previous.state(m)
        jsr_cost=Counter();jsr_calls=Counter();nonlocal_unwinds=Counter()
        class Probe(base):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.pending=[];self.jsrs=[];self.kind='Main'if self.pc==idle else'NMI';cpus.append(self)
            def step(self):
                nonlocal minimum
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.jsrs:
                    done=self.jsrs[-1]
                    if(self.pc,self.sp)==done['return']:
                        self.jsrs.pop();jsr_cost[done['key']]+=self.processorCycles-done['cycle'];jsr_calls[done['key']]+=1
                    elif self.sp>done['return'][1]:
                        # Nr's real A1CC/A554 legacy transfer consumes its JSR
                        # frame and resumes the outer router, rather than RTS
                        # to the table loads. Keep it separate from call costs.
                        self.jsrs.pop();nonlocal_unwinds[done['key']]+=1
                    else:break
                while self.pending and(self.pc,self.sp)==self.pending[-1]['return']:
                    done=self.pending.pop();inclusive[self.kind,done['name']]+=self.processorCycles-done['cycle'];returned[self.kind,done['name']]+=1
                for name in entries.get((tag,self.pc),()):
                    ret=(m[256+((self.sp+1)&255)]+256*m[256+((self.sp+2)&255)]+1)&65535
                    self.pending.append(dict(name=name,cycle=self.processorCycles,**{'return':(ret,(self.sp+2)&255)}))
                    calls[self.kind,name]+=1
                pc=self.pc;before=self.processorCycles;minimum=min(minimum,self.sp)
                if m[pc]==0x20:
                    target=m[pc+1]+256*m[pc+2]
                    target_tag=m.rawtags[(target-0x8000)//8192]if target>=0x8000 else-1
                    self.jsrs.append(dict(key=(self.kind,tag,pc,target_tag,target),cycle=self.processorCycles,**{'return':((pc+3)&65535,self.sp)}))
                result=super().step();cost=self.processorCycles-before
                banks[self.kind,tag]+=cost;pcs[self.kind,tag,pc]+=cost
                if self.pending:exclusive[self.kind,self.pending[-1]['name']]+=cost
                if tag==3:
                    for name,spans in macros.items():
                        for lo,hi in spans:
                            if lo<=pc<hi:
                                macro_cost[self.kind,name]+=cost
                                if pc==lo:macro_calls[self.kind,name]+=1
                return result
        with patch.object(N,'NesMPU',Probe):
            for t in range(count):
                e,r=calls['Main','GameLoop'],returned['Main','GameLoop'];start=len(cpus)
                m.controller_pad=pad;cycles=Frames.frame(m,whole_pass=True)
                assert(calls['Main','GameLoop']-e,returned['Main','GameLoop']-r)==(1,1)
                s=Previous.state(m);assert(s['HP'],s['lives'],s['power'],s['star'])==(47,2,0,0)and not s['actors']
                rows.append(dict(Main=t+1,Main_cycles=cycles,NMI_cycles=sum(c.processorCycles for c in cpus[start:]if c.kind=='NMI')))
        assert not any(c.pending or c.jsrs for c in cpus),'Every tracked actual function and JSR returned'
        hot=[]
        for(kind,tag,caller,target_tag,target),value in jsr_cost.most_common(40):
            names=[]
            if target_tag&128 and target_tag>=128:
                target_file=16+(target_tag&127)*8192+(target&8191)
                for name in b['syms']:
                    try:where=W.location(b,name)
                    except(KeyError,AssertionError):continue
                    if where==target_file:names.append(name)
            hot.append(dict(kind=kind,caller_tag=tag,caller_PC=caller,target_tag=target_tag,target_PC=target,
                target_names=names[:6],cycles_per_Main=value/count,calls_per_Main=jsr_calls[kind,tag,caller,target_tag,target]/count))
        phases.append(dict(phase=phase,Main_count=count,one_entry_return_each=True,opening=opening,final=Previous.state(m),per_Main=rows,
            mean_Main_cycles=sum(q['Main_cycles']for q in rows)/count,mean_scheduled_NMI_cycles=sum(q['NMI_cycles']for q in rows)/count,
            inclusive=[dict(kind=k,name=n,cycles_per_Main=v/count,calls_per_Main=calls[k,n]/count)for(k,n),v in inclusive.most_common()],
            innermost=[dict(kind=k,name=n,cycles_per_Main=v/count)for(k,n),v in exclusive.most_common()],
            bank_cycles=[dict(kind=k,tag=t,cycles_per_Main=v/count)for(k,t),v in banks.most_common()],
            top_PCs=[dict(kind=k,tag=t,PC=p,cycles_per_Main=v/count)for(k,t,p),v in pcs.most_common(30)],
            top_actual_JSR=hot,
            nonlocal_JSR_unwinds=[dict(kind=k,caller_tag=t,caller_PC=p,target_tag=tt,target_PC=tp,count=n)for(k,t,p,tt,tp),n in sorted(nonlocal_unwinds.items())],
            save_restore=[dict(kind=k,name=n,calls_per_Main=macro_calls[k,n]/count,cycles_per_Main=v/count)for(k,n),v in macro_cost.items()],minimum_SP=minimum))
        print('PROGRESS '+json.dumps(dict(phase=phase,Main=phases[-1]['mean_Main_cycles'],NMI=phases[-1]['mean_scheduled_NMI_cycles'])),flush=True)
    return dict(ROM_SHA256=Service.CANDIDATE,phases=phases,regular_NMI_scheduler=True,hardware_cadence_claim=False,
        gameplay_seeds=0,new_opcode_placement=False,ROM_output=False,Mesen=False,outputs=0)


def inspect(raw):
    b=Cold.bundle(Score.inverse(Service.inverse(raw)));rows=[]
    for name in('HotCollisionAdder','HotCollisionBox','NrAdder','NrBox','JnAdderDispatch','JnBoxDispatch','MmNativeSideShortcut',
            'MmSideDispatchTail','BlockBufferColli_Head','BlockBufferColli_Side','BtRouter','CfOrBtCheck','BtCheck'):
        at=W.location(b,name);pc=W.address(b,name);code=raw[at:at+112]
        memory=[0]*65536;memory[pc:pc+len(code)]=code;d=Disassembler(MPU(memory=memory));listing=[];cursor=pc
        while cursor<pc+min(112 if name in('NrAdder','NrBox','MmNativeSideShortcut')else 48,len(code)):
            size,text=d.instruction_at(cursor);listing.append(dict(PC=cursor,bytes=bytes(memory[cursor:cursor+size]).hex(),instruction=text));cursor+=size
        rows.append(dict(name=name,CPU=pc,file=at,tag=((at-16)//8192)|128,first72=code.hex(),listing=listing))
    cache=raw[Service.Model.BT.BASE:Service.Model.BT.BASE+8192];private=[]
    for slot in(0,2,9,10,12,13,14,29,34):
        api=cache[slot*3:slot*3+3];assert api[0]==0x4c
        pc=int.from_bytes(api[1:],'little');private.append(dict(slot=slot,target=pc,code24=cache[pc&8191:(pc&8191)+24].hex()))
    geometry=[];segment=raw[16+124*8192:16+125*8192]
    for name in('NrAdder','NrBox'):
        # Current entry stores SafeA/P, checks the explicit argument, then
        # preserves Y and calls the common pure index helper before 3 planes.
        found=[]
        for delta in range(64):
            p=(W.address(b,name)&8191)+delta
            if segment[p:p+5]==bytes.fromhex('984820cca1'):found.append(0xa000+p)
        assert len(found)==1,(name,found)
        start=found[0];code=segment[start&8191:(start&8191)+23]
        assert code[5]==code[11]==code[17]==0xb9
        planes=[int.from_bytes(code[i:i+2],'little')for i in(6,12,18)]
        geometry.append(dict(name=name,reader=start,planes=planes,
            entries=[dict(index=i,CPU=segment[(planes[0]&8191)+i]+256*segment[(planes[1]&8191)+i],
                bank=segment[(planes[2]&8191)+i],files=[16+124*8192+(pc&8191)+i for pc in planes])for i in range(5)]))
    native=[]
    for prg in(124,126,127):
        page=raw[16+prg*8192:16+(prg+1)*8192]
        for kind,pattern in(('adder',bytes.fromhex('a0003860')),('box',bytes.fromhex('a00060'))):
            p=0
            while(p:=page.find(pattern,p))>=0:
                file=16+prg*8192+p;labels=[]
                for name,s in b['syms'].items():
                    if'seg'not in s:continue
                    try:where=W.location(b,name)
                    except(KeyError,AssertionError):continue
                    if file-40<=where<=file:labels.append((file-where,name))
                native.append(dict(kind=kind,PRG=prg,file=file,CPU=(0xa000 if prg==124 else 0x8000 if prg==126 else 0xe000)+p,
                    nearest_symbols=sorted(labels)[:5]));p+=1
    return dict(ROM_SHA256=Service.CANDIDATE,functions=rows,private_services=private,geometry_planes=geometry,
        current_index_helper_code=segment[0x1cc:0x1f8].hex(),native_leaf_literal_leads=native,
        new_opcode_placement=False,outputs=0)


def route(raw):
    m=cold(raw);b=m.bundle;base=N.NesMPU;rows=[];active=None
    starts={W.address(b,n):n for n in('NrAdder','NrBox')}
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    class Probe(base):
        def step(self):
            nonlocal active
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if tag==252 and self.pc in starts:
                assert active is None
                active=dict(name=starts[self.pc],entry=dict(A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp),edges=[],loads=[],stores=[])
            if active and tag==215 and self.pc in(0xb044,0xb047):
                active['public_slot']=(self.pc-0xb020)//3;rows.append(active);active=None
            pc=self.pc;op=m[pc];operands=bytes(m[pc:pc+3]);start=(tag,pc)
            a,x,y,p,sp=self.a,self.x,self.y,self.p,self.sp
            result=super().step()
            if active:
                if op in(0x20,0x4c,0x6c,0x60):active['edges'].append(dict(tag=tag,PC=pc,bytes=operands.hex(),A=a,X=x,Y=y,P=p,SP=sp,next=self.pc))
                if op in(0xb9,0xbd,0xb1):active['loads'].append(dict(tag=tag,PC=pc,bytes=operands.hex(),X=x,Y=y,value=self.a))
                if op in(0x8d,0x8e,0x8c)and int.from_bytes(operands[1:],'little')in(0x16a,0x16c,0x16d,0x162):
                    active['stores'].append(dict(tag=tag,PC=pc,bytes=operands.hex(),A=a,X=x,Y=y))
            return result
    m.controller_pad=0
    with patch.object(N,'NesMPU',Probe):Frames.frame(m,whole_pass=True)
    assert active is None and len(rows)==2,rows
    return dict(ROM_SHA256=Service.CANDIDATE,genuine_cold=True,raw33_actual_ordinary_routes=rows,final=Previous.state(m),
        new_opcode_placement=False,outputs=0)


def code(raw):
    b=Cold.bundle(Score.inverse(Service.inverse(raw)));rows=[]
    for prg,pc,size in((79,0xb840,0x94),(124,0xa4fb,0x80),(96,0xb79d,96)):
        at=16+prg*8192+(pc&8191);data=raw[at:at+size];memory=[0]*65536;memory[pc:pc+size]=data
        d=Disassembler(MPU(memory=memory));listing=[];cursor=pc
        while cursor<pc+size:
            n,text=d.instruction_at(cursor);listing.append(dict(PC=cursor,bytes=bytes(memory[cursor:cursor+n]).hex(),instruction=text));cursor+=n
        labels=[]
        for name in b['syms']:
            try:where=W.location(b,name)
            except(KeyError,AssertionError):continue
            if at<=where<at+size:labels.append(dict(name=name,CPU=pc+where-at))
        rows.append(dict(PRG=prg,file=at,CPU=pc,bytes=data.hex(),listing=listing,labels=labels))
    return dict(ROM_SHA256=Service.CANDIDATE,source_ranges=rows,unallocated_inspection_only=True,outputs=0)


def proposal(raw):
    """Detached selector only. Address4000 is a test address, not an allocation."""
    at=16+79*8192+0x18b8;old=raw[at:at+32]
    assert old.hex()=='a9b08d6d01a9d78d6201c0249002a024988d6c010a6d6c0169208d6c014cb2b8'
    a=Code(0x4000);a.emit('ad0260c921');a.branch(0xd0,'Original')
    a.emit('9829fec90c');a.branch(0xd0,'Original')
    a.emit('a9a6c00c');a.branch(0xf0,'Store');a.emit('a9c3')
    a.mark('Store');a.emit('8d6c01a9a78d6d01a9e08d62014cb2b8');a.mark('Original');a.code.extend(old)
    new=a.done();assert len(new)==70
    targets=(('JnAdderDispatch',0xa7a6,bytes.fromhex('a0003860')),('JnBoxDispatch',0xa7c3,bytes.fromhex('a00060')))
    for name,pc,data in targets:
        b=Cold.bundle(Score.inverse(Service.inverse(raw)));start=W.location(b,name);base=W.address(b,name)
        assert raw[start+pc-base:start+pc-base+len(data)]==data
    memories=[]
    for program in(old,new):
        memory=[0]*65536;memory[0x4000:0x4000+len(program)]=program;memories.append(memory)
    exact=changed=0
    for owner in range(256):
        for y in range(256):
            for p in(0x20,0x31,0x69,0xe5):
                pair=[]
                for memory in memories:
                    memory[0x6002]=owner
                    for pos in(0x162,0x16a,0x16c,0x16d):memory[pos]=85
                    cpu=MPU(memory=memory,pc=0x4000);cpu.a=owner;cpu.x=7;cpu.y=y;cpu.p=p;cpu.sp=224
                    for _ in range(48):
                        if cpu.pc==0xb8b2:break
                        cpu.step()
                    else:raise AssertionError(('Detached selector bound',owner,y,p,cpu.pc))
                    pair.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,tuple(memory[pos]for pos in(0x162,0x16a,0x16c,0x16d))))
                if owner==33 and y in(12,13):
                    assert pair[1][1:3]==(7,y)and pair[1][4]==224
                    assert pair[1][5]==(224,85,0xa6 if y==12 else 0xc3,0xa7);changed+=1
                else:assert pair[0]==pair[1],(owner,y,p,pair);exact+=1
    return dict(ROM_SHA256=Service.CANDIDATE,detached_test_base=0x4000,not_a_resource_address=True,
        current_envelope=dict(PRG=79,CPU=[0xb8b8,0xb8d8],file=[at,at+32],old_hex=old.hex(),SHA256=sha256(old).hexdigest()),
        detached_selector_and_original_bytes=70,additional_bytes_needed_before_any_fit=38,
        detached_code_hex=new.hex(),detached_code_SHA256=sha256(new).hexdigest(),
        existing_immutable_targets=[dict(PRG=96,CPU=pc,bytes=data.hex(),name=name+'::Own')for name,pc,data in targets],
        exact_foreign_and_otherY_terminal_cases=exact,intentional_native_geometry_cases=changed,
        scope='Only selected33/slots12,13 choose existing immutable geometry leaves; explicit invalid-cache Nr/host admission change. No public BT API changed.',
        code_funding_closed=False,actual_opcode_mounted=False,whole_ROM_composed=False,ISR_or_gameplay_qualified=False,outputs=0)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=8);ap.add_argument('--inspect',action='store_true');ap.add_argument('--route',action='store_true');ap.add_argument('--code',action='store_true');ap.add_argument('--proposal',action='store_true');a=ap.parse_args();assert 1<=a.count<=32
    raw,info=load()
    def forbid(*a,**kw):raise RuntimeError('Remaining BT research attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):q=proposal(raw)if a.proposal else code(raw)if a.code else route(raw)if a.route else inspect(raw)if a.inspect else profile(raw,a.count)
    q.update(info);q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
