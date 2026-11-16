"""One real ffbb Main: aggregate caller work outside its CF query union."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import profile_contra_force_service_layers_1116 as S

M,C,N,W,Frames=S.M,S.C,S.N,S.W,S.Frames


def run(raw):
    m=M.cold(raw)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    b=m.bundle;game=W.address(b,'GameLoop');game_tag=((W.location(b,'GameLoop')-16)//8192)|128
    base=N.NesMPU;counts=Counter();outside=Counter();inquery=Counter();datawrites=Counter();calls=Counter();returns=Counter();objects=[]
    ctx={'cpu':None,'opcode':False};writer=type(m).__setitem__
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def ret(c):
        pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    class CPU(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.main=None;self.sfcs=[];self.queries=[];self.interrupts=[];objects.append(self)
        def interrupt(self,kind):
            old=self.pc,self.sp;out=super().nmi()if kind=='NMI'else super().irq()
            if(self.pc,self.sp)!=old:self.interrupts.append(old)
            return out
        def nmi(self):return self.interrupt('NMI')
        def irq(self):return self.interrupt('IRQ')
        def settle(self):
            while self.interrupts and(self.pc,self.sp)==self.interrupts[-1]:self.interrupts.pop()
            if self.interrupts:return
            now=self.pc,self.sp,tag(self.pc)
            while self.queries and now==self.queries[-1]:self.queries.pop()
            while self.sfcs and now==self.sfcs[-1]['return']:
                node=self.sfcs.pop();returns[node['key']]+=1
            if self.main==now:self.main=None;counts['Main_returns']+=1
        def step(self):
            self.settle();ctx['cpu']=self
            if self.interrupts:return super().step()
            owner=tag(self.pc)
            if(owner,self.pc)==(game_tag,game):
                assert self.main is None;self.main=ret(self);counts['Main_entries']+=1
            if self.main is not None:
                if self.pc==0x15a or(self.pc==0x15d and not(self.sfcs and self.sfcs[-1]['SP']==self.sp)):
                    bank=self.a if self.pc==0x15a else m[0x162];target=m[0x16c]+256*m[0x16d]
                    key=bank,target;self.sfcs.append(dict(key=key,SP=self.sp,returnPC=ret(self)))
                    self.sfcs[-1]['return']=self.sfcs[-1].pop('returnPC');calls[key]+=1
                if owner==215 and 0xb020<=self.pc<0xb08c and(self.pc-0xb020)%3==0:self.queries.append(ret(self))
            start=self.processorCycles;ctx['opcode']=True
            try:out=super().step()
            finally:ctx['opcode']=False
            if self.main is not None:
                key=self.sfcs[-1]['key']if self.sfcs else(-1,-1)
                dest='lowRAM'if owner==-1 else f'RAM{owner}'if owner<128 else f'PRG{owner&127}'
                target=inquery if self.queries else outside
                target[key[0],key[1],dest]+=self.processorCycles-start
            return out
    def write(bus,at,value):
        c=ctx['cpu']
        if ctx['opcode']and c and c.main is not None and not c.interrupts and not c.queries and isinstance(at,int):
            key=c.sfcs[-1]['key']if c.sfcs else(-1,-1)
            if not(0x100<=at<0x200 or at in(0x145,0x7da1,0x5115,0x5116)):
                datawrites[key[0],key[1],at]+=1
        return writer(bus,at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
        m.controller_pad=0;Frames.frame(m,whole_pass=True)
    for c in objects:
        c.settle();assert c.main is None and not c.sfcs and not c.queries and not c.interrupts
    assert calls==returns and counts==Counter(Main_entries=1,Main_returns=1)
    M.empty(m,'burns');targets=Counter()
    for(bank,pc,owner),cy in outside.items():targets[bank,pc]+=cy
    rows=[]
    for(bank,pc),cy in targets.most_common(32):
        rows.append(dict(bank_tag=bank,PC=pc,outside_query_cycles=cy,SFC_calls=calls[bank,pc],
            physical_owners={owner:n for(bb,pp,owner),n in outside.items()if(bb,pp)==(bank,pc)},
            nontransport_write_addresses=[dict(address=at,writes=n)for(bb,pp,at),n in datawrites.items()if(bb,pp)==(bank,pc)][:12]))
    return dict(actual_ROM_SHA256=C.H(raw),Main_entries_returns=dict(counts),
        Main_excluding_ISR_cycles=sum(outside.values())+sum(inquery.values()),
        CF_query_union_cycles=sum(inquery.values()),outside_CF_queries_cycles=sum(outside.values()),
        all_SFC_entries_returns_balanced=True,total_SFC=sum(calls.values()),
        outside_query_targets_top32=rows,remaining_outside_cycles=sum(v for _,v in targets.most_common()[32:]),
        outside_query_lowRAM_cycles=sum(v for(_,_,owner),v in outside.items()if owner=='lowRAM'),
        scope='One ordinary idle Main after genuine cold plus4warm; no per-frame or opcode trace arrays',
        zero_actors_shots=True,no_gameplay_or_private_code_changes=True,outputs=0,native=False)


if __name__=='__main__':
    parent,pin=S.load_reference();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Caller inspection attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q['actual_input_SHA256']=pin;q['reference6a3_only_RAMffbb_execution']=True
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
