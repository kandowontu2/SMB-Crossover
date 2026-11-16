"""Parent-only Main/query depth and exact selector cost; no stack writes."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import contra_force_c2_direct_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def run(raw,busy=False):
    assert C.H(raw)==C.PIN
    m=M.cold(raw)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True);M.empty(m)
    game=W.address(m.bundle,'GameLoop');gtag=((W.location(m.bundle,'GameLoop')-16)//8192)|128
    base=N.NesMPU;rows=[]
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def ret(c):
        pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    for phase,pad in(('idle',0),('Right',1)):
        counts=Counter();keys=Counter();cycles=Counter();queries=[];instances=[]
        class CPU(base):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.main=None;self.query=[];self.irqs=[];self.injected=False;instances.append(self)
            def interrupt(self,kind):
                old=self.pc,self.sp;out=super().nmi()if kind=='NMI'else super().irq()
                if(self.pc,self.sp)!=old:self.irqs.append(old)
                return out
            def nmi(self):return self.interrupt('NMI')
            def irq(self):return self.interrupt('IRQ')
            def settle(self):
                while self.irqs and(self.pc,self.sp)==self.irqs[-1]:self.irqs.pop()
                if self.irqs:return
                now=self.pc,self.sp,tag(self.pc)
                while self.query and now==self.query[-1]:self.query.pop();counts['query_returns']+=1
                if self.main and now==self.main['return']:
                    assert not self.query;self.main=None;counts['Main_returns']+=1
            def step(self):
                self.settle();owner=tag(self.pc)
                if busy and not self.injected and self.main and(owner,self.pc)==(3,0xa91b):
                    assert N.get(m,'NmiDisable')&128;self.injected=True;self.nmi();return
                if not self.irqs and(owner,self.pc)==(gtag,game):
                    assert self.main is None
                    self.main=dict(SP=self.sp,return_=ret(self));self.main['return']=self.main.pop('return_');counts['Main_entries']+=1
                if self.main and not self.irqs:
                    if(owner,self.pc)==(252,0xa4fb):
                        keys[self.a,self.y,self.main['SP']-self.sp,bool(self.query)]+=1
                    if(owner,self.pc)==(215,0xb08e):
                        word=m[0x16c]+256*m[0x16d];slot=(word-0xb020)//3
                        assert 0<=slot<36 and word==0xb020+3*slot
                        origin=self.main['SP'];mainword=m[0x100+((origin+1)&255)]+256*m[0x100+((origin+2)&255)]
                        assert len(queries)<32
                        queries.append(dict(slot=slot,SP=self.sp,Main_SP=origin,depth=origin-self.sp,
                            actual_Main_return_word=mainword,actual_query_return=ret(self),
                            CurrentC=N.get(m,'CurrentBankC'),actualC=m.rawtags[2],
                            live_stack_top_words=[m[0x100+((self.sp+1+j)&255)]+256*m[0x100+((self.sp+2+j)&255)]for j in(0,2,4)]))
                        self.query.append(ret(self));counts['query_entries']+=1
                return super().step()
        # Bind the pre-instruction PC explicitly; a JMP may leave the selector.
        original_step=CPU.step
        def step(c):
            pc,owner,start=c.pc,tag(c.pc),c.processorCycles
            in_main=bool(c.main);in_irq=bool(c.irqs);in_query=bool(c.query)
            out=original_step(c)
            if in_main and not in_irq and owner==252 and 0xa4fb<=pc<0xa509:
                cycles['inside_query'if in_query else'outside_query']+=c.processorCycles-start
            return out
        CPU.step=step
        with patch.object(N,'NesMPU',CPU):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        for c in instances:c.settle();assert c.main is None and not c.query and not c.irqs
        assert counts['Main_entries']==counts['Main_returns']and counts['query_entries']==counts['query_returns']
        M.empty(m)
        rows.append(dict(phase=phase,counts=dict(counts),queries=queries,exact_linear_search_cycles=dict(cycles),
            lookup_inputs=[dict(checksum=k,old_native_X=x,depth=d,inside_query=iq,calls=n)for(k,x,d,iq),n in sorted(keys.items())]))
    q=dict(parent_SHA256=C.PIN,actual_parent_only=True,busy_component=busy,phases=rows,
        token_or_flag_allocated=False,stack_read_only=True,wrapper_not_implemented=True,
        new_game_arrays_CPU_or_overlay=False,no_native_or_physical_cadence_claim=True,outputs=0)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--busy',action='store_true');a=p.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Parent stack observer attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.busy)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
