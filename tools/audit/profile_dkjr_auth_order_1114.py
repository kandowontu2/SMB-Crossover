"""Pinned769 empty-opening auth order versus successful Main completion.

Source CPU observation only. No epoch/cache or game bytes are changed.
"""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

import profile_dkjr_auth_calls_1114 as Base

F,G=Base.F,Base.G
Q,P,H,N,L=G.Q,G.P,G.H,G.N,G.L


def main():
    parent,raw=F.load_inputs();assert sha256(raw).hexdigest()==F.T.PIN
    e73=F.T.Old.reverse(parent);labels=P.frozen_labels()
    bank=raw[16+65*8192:16+66*8192]
    entry=[0xa000+i for i in range(0xe00,0xf27)if bank[i:i+8]==bytes.fromhex('ad026038e925c907')]
    assert entry==[0xaee2]
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
    for _ in range(160):
        s=P.B.state(m)
        if s['y']==176 and s['source_state']==1 and s['state']==0:break
        Q.frame(m,0)
    else:raise AssertionError('Genuine opening did not settle')
    CPU=N.NesMPU;phase='before_Main';main_pending=None;score_pending=None;auth_pending=[]
    counts=Counter();cycles=Counter();samples=[];returns=Counter();main_cycles=[];main_start=None
    callback_pending=[];callback_cycles=Counter();callback_counts=Counter();mapped_cycles=Counter()
    def token(c,m):return ((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535,(c.sp+2)&255)
    class Probe(CPU):
        def step(self):
            nonlocal phase,main_pending,score_pending,main_start
            mem=self.memory;tag=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            while callback_pending and(self.pc,self.sp)==callback_pending[-1][:2]:
                ret,sp,row,start=callback_pending.pop()
                callback_cycles[row]+=self.processorCycles-start;callback_counts[row]+=1
            if score_pending==(self.pc,self.sp):
                phase='after_ScoreFlush';score_pending=None;returns['ScoreFlush']+=1
            if main_pending==(self.pc,self.sp):
                assert phase=='after_ScoreFlush',phase
                main_cycles.append(self.processorCycles-main_start)
                phase='after_Main';main_pending=None;returns['Main']+=1
            if auth_pending and(self.pc,self.sp)==auth_pending[-1][:2]:
                ret,sp,start,kind,row=auth_pending.pop();cycles[kind,row]+=self.processorCycles-start
            if (tag,self.pc)==(2,0xd65e):
                assert main_pending is None
                main_pending=token(self,mem);main_start=self.processorCycles;phase='inside_Main_before_ScoreFlush'
            if(tag,self.pc)==(3,labels['DkScoreFlush']):
                assert main_pending is not None
                score_pending=token(self,mem)
            if(tag,self.pc)==(193,0xaee2):
                target=mem[0x16c]+256*mem[0x16d];row=(target-0xb08c)//3
                assert target==0xb08c+3*row and 0<=row<38
                counts[phase,row]+=1
                ret,sp=token(self,mem);auth_pending.append((ret,sp,self.processorCycles,phase,row))
                if len(samples)<28:samples.append(dict(phase=phase,row=row))
            if tag==3 and labels['DkServices']<=self.pc<labels['DkServices']+114 and(self.pc-labels['DkServices'])%3==0:
                row=(self.pc-labels['DkServices'])//3;ret,sp=token(self,mem)
                callback_pending.append((ret,sp,row,self.processorCycles))
            before=self.processorCycles;result=super().step();mapped_cycles[tag]+=self.processorCycles-before
            return result
    costs=[]
    with patch.object(N,'NesMPU',Probe):
        for _ in range(32):
            phase='before_Main';costs.append(Q.frame(m,0))
            assert main_pending is None and score_pending is None and not auth_pending and not callback_pending
            assert P.B.state(m)['lives']==2 and m.ram[2][0x6b]==1
            assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
    assert returns==Counter(Main=32,ScoreFlush=32)
    assert sum(counts.values())==448 and sum(cycles.values())==32*9142
    eligible=sum(count for(kind,row),count in counts.items()if kind in ('after_ScoreFlush','after_Main'))
    print('DKJR_AUTH_ORDER '+json.dumps(dict(passed=True,private_SHA256=F.T.PIN,
        genuine_empty_idle_Main=32,returns=dict(returns),full_auth_calls=448,
        inclusive_full_auth_cycles_per_Main=sum(cycles.values())/32,mean_Main_cycles=sum(costs)/32,
        actual_private_Main_cycles=sum(main_cycles)/32,
        rows=[dict(phase=kind,row=row,calls=count,cycles_per_Main=cycles[kind,row]/32)
            for(kind,row),count in sorted(counts.items())],first_two_Main_auth_order=samples,
        calls_after_current_proposed_stamp_per_Main=eligible/32,
        actual_private_callbacks=[dict(row=row,calls=callback_counts[row],inclusive_cycles_per_Main=cycles/32)
            for row,cycles in sorted(callback_cycles.items())],
        exclusive_mapped_bank_cycles_per_Main={tag:cycles/32 for tag,cycles in mapped_cycles.most_common()},
        estimate_is_call_eligibility_not_saved_cycles=True,cache_implemented=False,
        ROM_written=False,outputs_written=0,physical_cadence_claim=False,
        scope='Actual source call ordering on pinned769 settled no-actor idle; no cache funding, legal global writer closure, candidate or native performance result.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
