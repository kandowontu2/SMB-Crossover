"""Genuine opening costs and returned update counts; no physical FPS claim."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
import dkjr_original_cpu_1102_v1 as Donor


def stats(values):
    return dict(samples=len(values),minimum=min(values),mean=sum(values)/len(values),maximum=max(values))


def original():
    cpu,opening=Donor.active();rows=[]
    for phase,pad in(('idle',0),('walk_right',1)):
        values=[];returned=0;entered=0;pending=[];initial=Donor.state(cpu)
        def observe(c):
            nonlocal entered,returned
            if pending and(c.pc,c.sp)==pending[-1]:pending.pop();returned+=1
            if c.pc==0xd412:
                m=c.memory;entered+=1
                pending.append((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1,(c.sp+2)&255))
        for _ in range(32):
            before=cpu.processorCycles;Donor.frame(cpu,pad,observe);values.append(cpu.processorCycles-before)
        assert not pending and entered==returned and returned>0,(phase,entered,returned,pending)
        rows.append(dict(phase=phase,supplied_NMI_epochs=32,original_motor_entries=entered,
            original_motor_returns=returned,instruction_cycles=stats(values),initial=initial,final=Donor.state(cpu)))
    return dict(original_SHA256=Donor.SHA,normal_boot_NMI_epochs=opening,rows=rows,
        scope='Original NROM reset/NMI/actor instructions, authored original scene. Untimed PPU-ready services; DMA/raster stalls not modeled.')


def current():
    Q,P,H,N,W,L=Gate.Q,Gate.P,Gate.H,Gate.N,Gate.W,Gate.L
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);model=Q.mounted(seed,candidate)
    for settle in range(160):
        s=P.B.state(model)
        if s['y']==176 and s['source_state']==1 and s['state']==0:break
        Q.frame(model,0)
    else:raise AssertionError(('Natural opening did not settle',s))
    rows=[];Base=N.NesMPU
    for phase,pad in(('idle',0),('walk_right',1)):
        m=L.clone(model);banks=Counter();pcs=Counter();entered=returned=0;pending=[];source_cost=[]
        initial=P.B.state(m);values=[];actors=[]
        class Profile(Base):
            def step(self):
                nonlocal entered,returned
                tag=m.rawtags[(self.pc-32768)//8192]if self.pc>=32768 else-1
                if pending and(self.pc,self.sp)==pending[-1][:2]:
                    source_cost.append(self.processorCycles-pending[-1][2]);pending.pop();returned+=1
                if(tag,self.pc)==(2,0xd65e):
                    entered+=1
                    pending.append((m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1,(self.sp+2)&255,self.processorCycles))
                key=(tag,self.pc);before=self.processorCycles
                result=super().step();cost=self.processorCycles-before
                banks[tag]+=cost;pcs[key]+=cost
                return result
        with patch.object(N,'NesMPU',Profile):
            for _ in range(32):
                values.append(Q.frame(m,pad))
                actors.append(sum(bool(N.get(m,'Enemy_Flag',i))for i in range(6)))
                assert P.B.state(m)['lives']==2 and m.ram[2][0x6b]==1
        assert not pending and entered==returned and returned>0,(phase,entered,returned,pending)
        assert max(actors)==0,('Opening measurement contains native actors',phase,actors)
        rows.append(dict(phase=phase,complete_native_Main_returns=32,DK_Main_entries=entered,
            DK_Main_returns=returned,complete_Main_instruction_cycles=stats(values),
            DK_Main_instruction_cycles=stats(source_cost),native_actor_max=max(actors),
            initial=initial,final=P.B.state(m),cycles_by_mapped_bank=dict(banks),
            hottest_instructions=[dict(bank=tag,PC=pc,cycles=n)for(tag,pc),n in pcs.most_common(16)]))
    return dict(candidate_SHA256=sha256(candidate).hexdigest(),opening_settle_updates=settle,rows=rows,
        scope='Genuine current menu/cold/parser/settled opening and ordinary controller inputs. One native Main scheduled per model call; no physical NMI cadence inference.')


if __name__=='__main__':
    out=dict(original=original(),current=current(),input_polls_used_as_update_counter=False,
        physical_cadence_claim=False,source_or_native_seed_writes=False,outputs_written=0)
    print('DKJR_OPENING_COST '+json.dumps(out,separators=(',',':')),flush=True)
