"""Current exact DK authentication call/row and legal opening-write census.

Read-only source CPU diagnostic. No cache, bypass, resource grant, ROM output,
native physical cadence claim, or global external-writer closure is implied.
"""
from collections import Counter
from contextlib import redirect_stdout
import io
import json
from unittest.mock import patch

import replay_dkjr_final_handoff_1114 as F

G,T=F.Gate,F.T
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def main():
    parent,raw=F.load_inputs();e73=T.Old.reverse(parent)
    bank=raw[16+65*8192:16+66*8192]
    candidates=[0xa000+i for i in range(0xe00,0xf27)if bank[i:i+8]==bytes.fromhex('ad026038e925c907')]
    assert len(candidates)==1,candidates
    auth_entry=min(candidates)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);model=Q.mounted(seed,raw)
    for settle in range(160):
        s=P.B.state(model)
        if s['y']==176 and s['source_state']==1 and s['state']==0:break
        Q.frame(model,0)
    else:raise AssertionError(('Natural opening did not settle',s))
    rows=[];CPU=N.NesMPU
    for phase,pad in(('idle',0),('walk_right',1)):
        m=L.clone(model);initial=P.B.state(m);rows_by_target=Counter();auth_cycles=[];headers=0
        callers=Counter();pending=[];write_counts=Counter();write_values={};values=[];banks=Counter();pcs=Counter()
        Base=type(m)
        class Writes(Base):
            def __setitem__(self,at,value):
                if isinstance(at,int)and self.record_writes:
                    kind=None
                    if at>=32768:
                        tag=self.rawtags[(at-32768)//8192]
                        if tag in(2,3)and 0x1fe0<=at&8191<0x1ff0:kind=f'header{tag}:{at&8191:04x}'
                    elif at in(0x6002,0x5fff):kind=f'native:{at:04x}'
                    if kind:
                        key=(self.writer_tag,self.writer_pc,kind);write_counts[key]+=1
                        write_values.setdefault(key,set()).add(int(value)&255)
                return super().__setitem__(at,value)
        m.__class__=Writes;m.record_writes=False;m.writer_tag=-1;m.writer_pc=0
        class Probe(CPU):
            def step(self):
                nonlocal headers
                tag=m.rawtags[(self.pc-32768)//8192]if self.pc>=32768 else-1
                while pending and(self.pc,self.sp)==pending[-1][:2]:
                    auth_cycles.append(self.processorCycles-pending[-1][2]);pending.pop()
                if(tag,self.pc)==(193,auth_entry):
                    target=m[0x16c]+256*m[0x16d]
                    assert 0xb08c<=target<0xb0fe and(target-0xb08c)%3==0
                    rows_by_target[(target-0xb08c)//3]+=1
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    callers[ret]+=1;pending.append((ret,(self.sp+2)&255,self.processorCycles))
                if(tag,self.pc)==(193,0xaf27):headers+=1
                m.writer_tag=tag;m.writer_pc=self.pc
                before=self.processorCycles;pc=self.pc;result=super().step();cost=self.processorCycles-before
                banks[tag]+=cost
                if tag!=193:pcs[tag,pc]+=cost
                return result
        m.record_writes=True
        with patch.object(N,'NesMPU',Probe):
            for _ in range(32):
                values.append(Q.frame(m,pad))
                assert P.B.state(m)['lives']==2 and m.ram[2][0x6b]==1
                assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
        m.record_writes=False
        assert not pending and len(auth_cycles)==sum(rows_by_target.values())
        rows.append(dict(phase=phase,Main_returns=32,initial=initial,final=P.B.state(m),
            mean_Main_cycles=sum(values)/32,full_auth_calls=len(auth_cycles),full_header_calls=headers,
            inclusive_full_auth_cycles_per_Main=sum(auth_cycles)/32,
            auth_service_rows=dict(sorted(rows_by_target.items())),auth_return_PC_counts=dict(callers),
            cycles_by_mapped_bank=dict(banks),
            hottest_non193_instructions=[dict(bank=b,PC=pc,cycles_per_Main=count/32)for(b,pc),count in pcs.most_common(12)],
            observed_writes=[dict(bank=b,PC=pc,target=kind,count=count,values=sorted(write_values[(b,pc,kind)]))
                for(b,pc,kind),count in sorted(write_counts.items())]))
    print('DKJR_AUTH_OPENING '+json.dumps(dict(candidate_SHA256=T.PIN,auth_entry=auth_entry,rows=rows,
        outputs_written=0,cache_or_bypass_implemented=False,
        scope='Exact genuine settled opening, no actor/geometry seeds;32 scheduled Main calls each. Runtime ingress/write census only, not an exhaustive legal foreign-writer proof or physical cadence.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
