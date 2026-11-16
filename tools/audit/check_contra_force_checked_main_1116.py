"""Paired actual91dc/44b ordinary Main costs; no physical cadence claim."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import contra_force_checked_resolver_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def observe(m,busy,count=4):
    base=N.NesMPU;instances=[];calls=Counter();cost=Counter();ISR=Counter();rows=[];minimum=255
    game=W.address(m.bundle,'GameLoop');at=W.location(m.bundle,'GameLoop');game_tag=((at-16)//8192)|128
    draw=(W.location(m.bundle,'DrawAllMetasprites')-16)//8192|128,W.address(m.bundle,'DrawAllMetasprites')
    movement=C.Plan.Rejected.Source.C.Plan.inputs(C.reference(M.parent(m.bundle['raw'])))[1]['CfHostMovement']
    class CPU(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.pending=None;self.interrupts=[];self.ISR=0;self.injected=False;instances.append(self)
        def interrupt(self,kind):
            ret=(self.pc,self.sp);start=self.processorCycles;out=super().nmi()if kind=='NMI'else super().irq()
            if(self.pc,self.sp)!=ret:self.interrupts.append((ret,start,kind))
            return out
        def nmi(self):return self.interrupt('NMI')
        def irq(self):return self.interrupt('IRQ')
        def settle(self):
            while self.interrupts and(self.pc,self.sp)==self.interrupts[-1][0]:
                _,start,kind=self.interrupts.pop();cy=self.processorCycles-start
                if not self.interrupts:self.ISR+=cy;ISR[kind]+=cy
            if self.interrupts:return
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if self.pending and(self.pc,self.sp,tag)==self.pending['return']:
                p=self.pending;self.pending=None;cycles=self.processorCycles-p['start']-(self.ISR-p['ISR'])
                key=(p['draw'],p['checks']);cost[key]+=cycles;calls[key]+=1
                rows.append(dict(cycles=cycles,draw=p['draw'],checks=p['checks'],return_PC=self.pc,SP=self.sp))
        def step(self):
            nonlocal minimum
            self.settle()
            if self.interrupts:return super().step()
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if busy and not self.injected and(tag,self.pc)==(3,movement):
                assert N.get(m,'NmiDisable')&128;self.injected=True;self.nmi();return
            if(tag,self.pc)==(game_tag,game):
                assert self.pending is None
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                rt=m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                self.pending=dict(start=self.processorCycles,ISR=self.ISR,draw=0,checks=0)
                self.pending['return']=(ret,(self.sp+2)&255,rt)
            if self.pending:
                if(tag,self.pc)==(197,0xbf47):self.pending['checks']+=1
                if(tag,self.pc)==draw:self.pending['draw']+=1
            minimum=min(minimum,self.sp);return super().step()
    with patch.object(N,'NesMPU',CPU):
        for _ in range(count):Frames.frame(m,whole_pass=True);M.empty(m)
    for c in instances:c.settle();assert not c.pending and not c.interrupts
    return dict(classes=[dict(draw=d,checks=n,calls=k,total_cycles=cost[d,n],mean_cycles=cost[d,n]/k)for(d,n),k in sorted(calls.items())],
        Main_returns=sum(calls.values()),ISR_cycles=dict(ISR),minimum_SP=minimum,rows=rows,
        final_CPU_SP=[c.sp for c in instances])


def compare(pair):
    a,z=pair;diff=[i for i in range(0x8000)if a[i]!=z[i]]
    outside=[i for i in diff if not 0x100<=i<0x200 or 0x15a<=i<0x17b]
    assert not outside,('Main nonstack/SMC difference',[(hex(i),a[i],z[i])for i in outside[:16]])
    assert tuple(map(bytes,a.ram))==tuple(map(bytes,z.ram)),'Full current private RAM mismatch'
    assert a.rawtags==z.rawtags and a.vram==z.vram and a.ppuctrl==z.ppuctrl
    assert bytes(a[0x1fe:0x200])==bytes(z[0x1fe:0x200]),'Live caller stack bytes'
    return dict(all_nonstack_RAM_and_SMC33_privateRAM_maps_VRAM_PPuctrl_exact=True,
        dead_stack_difference_addresses=diff,dead_stack_liveness_separate_pending=True)


def run(parent,busy):
    image,_=C.proposal(parent);pair=[M.cold(raw)for raw in(parent,image)]
    for m in pair:
        for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True);M.empty(m)
    rows=[]
    for phase,pad in(('idle',0),('Right',1)):
        before=[]
        for m in pair:m.controller_pad=pad;before.append(observe(m,busy))
        parity=compare(pair);old,new=before
        assert old['Main_returns']==new['Main_returns']
        rows.append(dict(phase=phase,busy_NMI_component=busy,parent=old,candidate=new,parity=parity,
            total_saved=sum(r['cycles']for r in old['rows'])-sum(r['cycles']for r in new['rows'])))
        print('PROGRESS '+json.dumps(dict(phase=phase,busy=busy,Main=old['Main_returns'],saved=rows[-1]['total_saved'])),flush=True)
    q=dict(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,phases=rows,
        actual_new_CPU_no_redirect=True,genuine_compiled_Burns_cold_and_empty_idle_Right=True,
        no_health_actor_position_terrain_ability_seeds=True,stack_ledger_and_rejected_publication_still_pending=True,
        no_native_FPS_or_fullroute_claim=True,outputs=0)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--busy',action='store_true');args=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Paired Main check attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,args.busy)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
