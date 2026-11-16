"""One current ordinary Main: C-window ownership/access aggregates only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_contra_force_readonly_9826_1116 as M

N,W,Frames=M.N,M.W,M.Frames
BRIDGE_SHA='d765d86cc8556d16ed3c366111905a4f2969a07641e0edc5aa3edb386274a54b'


def run(raw):
    assert M.H(Path(M.__file__).read_bytes())==BRIDGE_SHA
    q=M.bindings(raw);m=M.cold(raw);b=m.bundle
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    game=W.address(b,'GameLoop');game_tag=((W.location(b,'GameLoop')-16)//8192)|128
    base=N.NesMPU;reader=type(m).__getitem__;writer=type(m).__setitem__
    counts=Counter();fetches=Counter();reads=Counter();writes=Counter();maps=Counter();queries=Counter();watched=Counter();instances=[]
    context={'CPU':None,'opcode':False}
    fields={W.address(b,n):n for n in('SelectedCharacter','FmGroups','CurrentPlayer','FamilyMainCommit','GamePauseStatus','OperMode','DisableScreenFlag','NmiDisable')}
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def returned(c):
        pc=(m[256+((c.sp+1)&255)]+256*m[256+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    class CPU(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.main=None;self.isrs=[];instances.append(self)
        def interrupt(self,kind):
            old=self.pc,self.sp;out=super().nmi()if kind=='NMI'else super().irq()
            if(self.pc,self.sp)!=old:self.isrs.append(old)
            return out
        def nmi(self):return self.interrupt('NMI')
        def irq(self):return self.interrupt('IRQ')
        def settle(self):
            while self.isrs and(self.pc,self.sp)==self.isrs[-1]:self.isrs.pop()
            if not self.isrs and self.main==(self.pc,self.sp,tag(self.pc)):
                self.main=None;counts['Main_returns']+=1
        def step(self):
            self.settle();context['CPU']=self
            owner=tag(self.pc)
            if not self.isrs and(owner,self.pc)==(game_tag,game):
                assert self.main is None;self.main=returned(self);counts['Main_entries']+=1
            active=self.main is not None and not self.isrs
            pc=self.pc;mode=self.disassemble[m[pc]][1]
            size=1 if mode in('acc','imp')else 2 if mode in('imm','zpg','zpx','zpy','rel','inx','iny')else 3
            context.update(active=active,owner=owner,PC=pc,fetch_end=pc+size)
            if active:
                maps[m.rawtags[2],reader(m,0x7da1)]+=1
                if 0xc000<=pc<0xe000:fetches[owner,pc>>8]+=1
                if owner==215 and 0xb020<=pc<0xb08c and(pc-0xb020)%3==0:
                    queries[(pc-0xb020)//3,m.rawtags[2],reader(m,0x7da1)]+=1
            start=self.processorCycles;context['opcode']=True
            try:out=super().step()
            finally:context['opcode']=False
            if active:counts['Main_cycles']+=self.processorCycles-start
            return out
    def access(bus,at,value=None):
        if context['opcode']and context.get('active')and isinstance(at,int):
            c=context['CPU'];owner=context['owner'];pc=context['PC']
            physical=tag(at)
            is_fetch=owner==physical and pc<=at<context['fetch_end']
            if 0xc000<=at<0xe000 and not is_fetch:
                dest=writes if value is not None else reads
                dest[physical,at,owner,pc]+=1
            if value is not None:
                name=fields.get(at)
                if physical in(2,3)and at>=0x8000 and 0x1fe0<=at&8191<0x1ff0:name='RAM'+str(physical)+' header'+str((at&8191)-0x1fe0)
                if name:watched[name,owner,pc,reader(bus,at),value&255]+=1
        return reader(bus,at)if value is None else writer(bus,at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__getitem__',lambda bus,at:access(bus,at)),patch.object(type(m),'__setitem__',lambda bus,at,v:access(bus,at,v)):
        m.controller_pad=0;Frames.frame(m,whole_pass=True)
    for c in instances:c.settle();assert c.main is None and not c.isrs
    assert counts['Main_entries']==counts['Main_returns']==1
    assert sum(queries.values())==14;M.empty(m)
    def aggregate(counter):
        pages=Counter();sites=Counter()
        for(physical,at,owner,pc),n in counter.items():pages[physical,at>>8]+=n;sites[physical,owner,pc]+=n
        rows=[dict(physical_tag=t,caller_tag=o,caller_PC=pc,accesses=n)for(t,o,pc),n in sites.most_common(24)]
        return dict(total=sum(counter.values()),distinct_cells=len({(t,at)for(t,at,o,pc)in counter}),pages=[dict(tag=t,page=pg,accesses=n)for(t,pg),n in sorted(pages.items())],top24_callers=rows,remaining_caller_accesses=sum(n for _,n in sites.most_common()[24:]),all_cell_caller_counts_SHA256=M.H(json.dumps(sorted((list(k),v)for k,v in counter.items()),separators=(',',':')).encode()))
    out=dict(passed=True,owning_SHA256=M.H(raw),binding=q['current_proof'],Main=dict(counts),
        Cwindow_instruction_fetches=[dict(tag=t,page=p,instructions=n)for(t,p),n in sorted(fetches.items())],
        Cwindow_data_reads=aggregate(reads),Cwindow_data_writes=aggregate(writes),
        Cmap_shadow_instruction_counts=[dict(mapped=t,shadow=s,instructions=n)for(t,s),n in sorted(maps.items())],
        actual_query_domains=[dict(slot=i,mapped=t,shadow=s,calls=n)for(i,t,s),n in sorted(queries.items())],
        all_watched_protocol_writes=[dict(field=name,writer_tag=t,writer_PC=pc,before=old,after=new,writes=n)for(name,t,pc,old,new),n in sorted(watched.items())],
        scope='One original current Main after genuine cold+4warm; access aggregates, no instruction trace arrays. This cannot prove all-state D0 liveness, all header writers or ISR closure.',
        no_proposed_code_or_state_or_native_or_cadence_claim=True,outputs=0)
    out['receipt_SHA256']=M.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=M.load_current_image();original=Path.read_bytes
    def read(path):
        assert path.resolve()!=M.ROM.resolve(),'No second mutable Nightly read'
        return original(path)
    def deny(*a,**kw):raise AssertionError('Read-only C-window audit attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
