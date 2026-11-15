"""Current f11 BT service/validation dispatch census; no performance placement."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
from py65.disassembler import Disassembler

import compose_battletoads_camera_handoff_1114 as C
import check_battletoads_camera_candidate_1114 as Cold
import check_bub_current_budget_1113 as Frames
import current_battletoads_dispatch_input_1114 as Input

W,N=Cold.W,Cold.N


def census(raw):
    b=dict(W.Symbols.bundle(),raw=raw);cache=raw[C.BASE:C.BASE+8192]
    table=W.address(b,'BtCacheServices');assert table==0xa000
    at=W.location(b,'BtServiceVeneers');veneer=W.address(b,'BtServiceVeneers');tag=((at-16)//8192)|128
    rows=[]
    for slot in range(36):
        private=cache[3*slot:3*slot+3];public=raw[at+3*slot:at+3*slot+3]
        assert private[0]==public[0]==0x4c
        target=int.from_bytes(private[1:],'little');public_target=int.from_bytes(public[1:],'little')
        code=cache[target&8191:(target&8191)+16]
        names=[n for n,s in b['syms'].items()if n.startswith('Bt')and int(s.get('val','0'),0)==target]
        rows.append(dict(slot=slot,private_target=target,private_names=names,private_code=code.hex(),
            exact_CLC_RTS=code[:2]==bytes.fromhex('1860'),public_veneer=veneer+slot*3,public_target=public_target))
    related=[]
    for name in('BtRouter','CfOrBtCheck','BtCheck','BtServiceVeneers','MmNativeHeadShortcut',
            'MmNativeSideShortcut','MmSideDispatchPrefix','MmSideDispatchTail','BillHeadDispatch',
            'BlockBufferColli_Head','BlockBufferColli_Side','NrHead','NrSide','HotCollisionAdder','HotCollisionBox'):
        try:
            pos=W.location(b,name);pc=W.address(b,name)
        except KeyError:continue
        related.append(dict(name=name,CPU=pc,raw_tag=((pos-16)//8192)|128,file=pos,
            segment=b['segs'][b['syms'][name]['seg']],first96bytes=raw[pos:pos+96].hex()))
    m=Cold.cold(raw,'rash');base=N.NesMPU;events=[];counts=Counter();contexts={};point={}
    for p in related:
        if p['name']in('BtRouter','CfOrBtCheck','BtCheck'):point[p['raw_tag'],p['CPU']]=p['name']
    for r in rows:point[tag,r['public_veneer']]='BtServiceSlot'+str(r['slot'])
    class Probe(base):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);self.calls=[]
        def step(self):
            mm=self.memory;t=mm.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if mm[self.pc]==0x20:
                self.calls.append(dict(raw_tag=t,PC=self.pc,target=mm[self.pc+1]+256*mm[self.pc+2],SP=self.sp))
                if len(self.calls)>16:self.calls.pop(0)
            name=point.get((t,self.pc))
            if name:
                ret=(mm[256+((self.sp+1)&255)]+256*mm[256+((self.sp+2)&255)]+1)&65535
                row=dict(name=name,PC=self.pc,raw_tag=t,SP=self.sp,return_PC=ret,
                    A=self.a,X=self.x,Y=self.y,P=self.p,farcall_target=mm[0x16c]+256*mm[0x16d])
                events.append(row);assert len(events)<256;counts[name]+=1
                if name.startswith('BtServiceSlot')and name not in contexts:contexts[name]=list(self.calls)
            return super().step()
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    with patch.object(N,'NesMPU',Probe):
        for _ in range(2):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    listing=[];m.raw_page(1,215);cpu=base(memory=m,pc=W.address(b,'BtRouter'));dis=Disassembler(cpu);pc=cpu.pc
    while pc<0xb100:
        size,text=dis.instruction_at(pc);listing.append(dict(PC=pc,bytes=bytes(m[pc:pc+size]).hex(),instruction=text));pc+=size
    callers=[]
    for name,history in contexts.items():
        actual=[r for r in history if r['raw_tag']>=128]
        assert actual
        call=actual[-1];pos=16+(call['raw_tag']&127)*8192+(call['PC']&8191)
        aliases=[]
        for n,s in b['syms'].items():
            if'seg'not in s:continue
            try:where=W.location(b,n)
            except(KeyError,AssertionError):continue
            if pos-96<=where<=pos:aliases.append((pos-where,n,W.address(b,n)))
        callers.append(dict(service=name,actual_farcall=call,nearest_symbols=sorted(aliases)[:8],
            surrounding_file=[pos-24,pos+24],surrounding_bytes=raw[pos-24:pos+24].hex(),recent_JSR=history))
    return dict(ROM_SHA256=sha256(raw).hexdigest(),service_table=rows,ROM_dispatch_points=related,router_listing=listing,
        actual_caller_contexts=callers,
        actual_two_idle_Main_events=events,actual_event_counts=dict(counts),
        exact_unavailable_slots=[r['slot']for r in rows if r['exact_CLC_RTS']],
        source_read_only=True,performance_proposal_placed=False,allocation_granted=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw,input_info=Input.load()
    def forbid(*args,**kwargs):raise RuntimeError('BT dispatch census attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):q=census(raw)
    q.update(input_info);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
