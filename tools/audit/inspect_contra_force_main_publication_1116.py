"""Read-only real-parent Main publication accesses; no batch flag or rewrite."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_c2_direct_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def run(parent):
    assert C.H(parent)==C.PIN
    m=M.cold(parent)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True);M.empty(m)
    address=W.address(m.bundle,'FamilyMainCommit');assert address==0x5fff
    game=W.address(m.bundle,'GameLoop');game_tag=(W.location(m.bundle,'GameLoop')-16)//8192|128
    base=N.NesMPU;rows=[];context={'inside':False,'cpu':None};read=type(m).__getitem__;write=type(m).__setitem__
    for phase,pad in(('idle',0),('Right',1)):
        counts=Counter();outside=Counter();points=[];pending=[];Main=Counter();queries=0;order=0;objects=[]
        class CPU(base):
            def __init__(self,*a,**kw):super().__init__(*a,**kw);objects.append(self)
            def step(self):
                nonlocal queries,order
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while pending and(self.pc,self.sp,tag)==pending[-1]:pending.pop();Main['returned']+=1
                if(tag,self.pc)==(game_tag,game):
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    rt=m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                    pending.append((ret,(self.sp+2)&255,rt));Main['entry']+=1
                    if len(points)<16:points.append(dict(kind='Main entry',order=order,PC=self.pc,tag=tag,SP=self.sp,commit=m[address]))
                if(tag,self.pc)==(215,0xb08e):queries+=1
                context.update(cpu=self,PC=self.pc,tag=tag,opcode=m[self.pc],inside=True)
                order+=1
                try:return super().step()
                finally:context['inside']=False
        def observed_read(bus,at):
            value=read(bus,at)
            if bus is m and at==address:
                if context['inside']:counts['read',context['tag'],context['PC'],context['opcode'],value]+=1
                else:outside['read',value]+=1
            return value
        def observed_write(bus,at,value):
            if bus is m and at==address:
                if context['inside']:
                    counts['write',context['tag'],context['PC'],context['opcode'],value]+=1
                    if len(points)<16:points.append(dict(kind='CPU commit write',order=order,tag=context['tag'],PC=context['PC'],opcode=context['opcode'],value=value,queries_before=queries))
                else:outside['write',value]+=1
            return write(bus,at,value)
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__getitem__',observed_read),patch.object(type(m),'__setitem__',observed_write):
            m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        M.empty(m);assert Main['entry']==1 and Main['returned']==1 and not pending
        rows.append(dict(phase=phase,Main=dict(Main),queries=queries,events=points,
            CPU_accesses=[dict(kind=k,tag=t,PC=pc,opcode=op,value=v,count=n)for(k,t,pc,op,v),n in sorted(counts.items())],
            out_of_CPU_model_accesses=[dict(kind=k,value=v,count=n)for(k,v),n in sorted(outside.items())]))
    q=dict(parent_SHA256=C.PIN,actual_parent_only=True,FamilyMainCommit=address,phases=rows,
        source_frame_driver=str(Path(Frames.__file__).relative_to(C.R)),no_new_flag_allocation_or_write=True,
        global_and_foreign_protocol_closure_not_claimed=True,no_native_or_physical_cadence_claim=True,outputs=0)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Publication observer attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
