"""Exact421 natural empty CF idle/walk CPU attribution; zero outputs.

Actual native30Hz is a separate root receipt. These instruction costs do not
simulate hardware frame timing and grant no cache, bypass or code placement.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import json
import re
from unittest.mock import patch

import replay_contra_force_clock_1114 as C
import check_contra_force_full11_1114 as Cold
import check_bub_current_budget_1113 as Frames

W,N=C.W,C.N


def profile(raw,key='burns'):
    assert sha256(raw).hexdigest()==C.PIN
    with patch.object(Cold,'Factory',C):m=Cold.cold(raw,key)
    labels={name:int(at,16)for at,name in re.findall(r'^al ([0-9a-fA-F]+) \.(\w+)$',
        (C.Previous.Previous.KERNEL/'runtime.lbl').read_text(),re.M)}
    b=m.bundle;points={}
    for name in('GameLoop','CfOrBtCheck','CfLoaderProposal','CfLoaderCoreProposal'):
        try:points[((W.location(b,name)-16)//8192)|128,W.address(b,name)]=name
        except (KeyError,AssertionError):pass
    bank=raw[16+65*8192:16+66*8192]
    sites=[0xa000+i for i in range(0xe00,0xf27)if bank[i:i+8]==bytes.fromhex('ad026038e925c907')]
    assert len(sites)==1
    points[193,sites[0]]='CoCheckCode_actual'
    private={'CfA2Router':2,'CfCallA':2,'CfNativeClear':2,'CfHostMovement':3,
        'CfHostAfterBG':3,'CfHostEnsure':3,'CfHostConstruct':3,'CfNativeInput':3,
        'CfNativeBody':3,'CfHostGraphics':3,'CfHostDraw':3,'CfHostShots':3,
        'CfHostScrollPublish':3}
    points.update({(tag,labels[name]):name for name,tag in private.items()})
    for _ in range(2):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    rows=[];base=N.NesMPU
    for phase,pad,count in(('idle',0,32),('right',1,32),('left',2,32)):
        calls=Counter();inclusive=Counter();exclusive=Counter();banks=Counter();pcs=Counter()
        returned=Counter();outer_auth_rows=Counter();router_rows=Counter();header_hits=0
        totals=[];cpu_objects=[];minimum=255
        initial=dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'))
        class Probe(base):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs);self.pending=[];cpu_objects.append(self)
            def step(self):
                nonlocal header_hits,minimum
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.pending and(self.pc,self.sp)==self.pending[-1]['return']:
                    done=self.pending.pop();elapsed=self.processorCycles-done['cycles']
                    inclusive[done['name']]+=elapsed;returned[done['name']]+=1
                name=points.get((tag,self.pc))
                if name:
                    pc=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    self.pending.append(dict(name=name,return_ignored=False,
                        **{'return':(pc,(self.sp+2)&255)},cycles=self.processorCycles))
                    calls[name]+=1
                    if name=='CfOrBtCheck':outer_auth_rows[m[0x16c]]+=1
                    elif name=='CfA2Router':router_rows[m[0x16c]]+=1
                if(tag,self.pc)==(193,0xaf27):header_hits+=1
                pc=self.pc;before=self.processorCycles;minimum=min(minimum,self.sp)
                result=super().step();delta=self.processorCycles-before
                banks[tag]+=delta;pcs[tag,pc]+=delta
                if self.pending:exclusive[self.pending[-1]['name']]+=delta
                return result
        with patch.object(N,'NesMPU',Probe):
            for _ in range(count):
                m.controller_pad=pad;totals.append(Frames.frame(m,whole_pass=True))
                assert N.get(m,'SelectedCharacter')==31 and N.get(m,'NumberofLives')==2
                assert N.get(m,'PlayerStatus')==N.get(m,'StarInvincibleTimer')==0
                assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
                assert not any(m.ram[2][0x382+i]for i in range(10,22))
                assert m.ram[2][0x4d2]==1 and m.ram[2][0x4b4]==0
        unclosed=[dict(name=p['name'],PC=c.pc,SP=c.sp,return_target=p['return'])for c in cpu_objects for p in c.pending]
        # Some published aliases are branch seams rather than standalone
        # functions. Report every unclosed scope instead of inventing a cost.
        rows.append(dict(phase=phase,scheduled_full_Main=count,initial=initial,
            final=dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position')),
            mean_Main_only_cycles=sum(totals)/count,all_observed_CPU_cycles_per_Main=sum(banks.values())/count,
            mapped_bank_cycles_per_Main={str(k):v/count for k,v in sorted(banks.items())},
            function_calls=dict(calls),function_returns=dict(returned),
            inclusive_cycles_per_Main={k:v/count for k,v in sorted(inclusive.items())},
            innermost_scope_cycles_per_Main={k:v/count for k,v in sorted(exclusive.items())},
            external_auth_target_low_counts=dict(outer_auth_rows),router_target_low_counts=dict(router_rows),
            CoCheckCode_full_header_entries=header_hits,unclosed_scopes=unclosed,
            minimum_SP=minimum,hottest_instructions=[dict(bank=tag,PC=pc,cycles_per_Main=value/count)
                for(tag,pc),value in pcs.most_common(24)]))
        print(json.dumps(dict(progress=phase,Main=count,mean_cycles=sum(totals)/count)),flush=True)
    return dict(passed=True,ROM_SHA256=C.PIN,identity=key,source_CPU_only=True,
        actor_and_shot_slots_naturally_zero=True,source_only_no_physical_cadence_claim=True,
        actual_native_bare_clock_30Hz_is_separate=True,
        traced_points=[dict(bank=tag,PC=pc,name=name)for(tag,pc),name in sorted(points.items())],
        phases=rows,cache_or_bypass_or_ROM_changes=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    print(json.dumps(profile(C.ROM.read_bytes()),separators=(',',':')),flush=True)
