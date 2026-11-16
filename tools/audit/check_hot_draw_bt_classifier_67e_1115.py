"""Flat detached classifier proof only; no NesBus/ROM overlay or gameplay."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import plan_hot_draw_bt_67e_1115 as P


def run(raw):
    old=P.old_code(raw);new,labels,_=P.new_code(raw);memories=[]
    class Memory(list):
        def __init__(self,code):
            super().__init__([0]*65536);self[P.BASE:P.BASE+118]=code
            self.watch=False;self.reads=set();self.writes=set()
        def __getitem__(self,at):
            if self.watch and isinstance(at,int):self.reads.add(at)
            return super().__getitem__(at)
        def __setitem__(self,at,v):
            if getattr(self,'watch',False)and isinstance(at,int):self.writes.add(at)
            super().__setitem__(at,v)
    for code in(old,new):memories.append(Memory(code))
    minimum=255;cases=0;costs=Counter();owner_costs=Counter();destinations=set()
    def one(owner,alt,roll,a,p,x=71,y=37,weight=False):
        nonlocal minimum,cases
        results=[]
        for m in memories:
            m.watch=False;m[0x6002]=owner;m[0x5fe5]=alt;m[0x5feb]=roll
            c=P.N.NesMPU(memory=m,pc=P.BASE);c.a=a;c.x=x;c.y=y;c.p=p;c.sp=224;m.watch=True
            for _ in range(120):
                if c.pc==0x15d:break
                assert P.BASE<=c.pc<P.BASE+91,('Classifier escaped code',c.pc)
                minimum=min(minimum,c.sp);c.step()
            else:raise AssertionError(('Classifier instruction bound',owner,alt,roll,p,c.pc))
            assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,y,p|0x30,224),(owner,alt,roll,a,p,x,y,c.a,c.x,c.y,c.p,c.sp)
            m.watch=False
            results.append(dict(target=(m[0x162],m[0x16c]+256*m[0x16d]),A=m[0x16a],cycles=c.processorCycles))
        assert results[0]['A']==results[1]['A']==a
        if owner==33:assert results[0]['target']==(252,0xa1a2)and results[1]['target']==(215,0xb026)
        else:assert results[0]['target']==results[1]['target'],('Foreign destination',owner,alt,roll,results)
        assert memories[0][0x1dd:0x1e1]==memories[1][0x1dd:0x1e1]
        delta=results[0]['cycles']-results[1]['cycles'];costs['raw33'if owner==33 else'foreign',delta]+=1
        if weight:owner_costs[owner,delta]+=1
        destinations.add(results[1]['target']);cases+=1
    for owner in range(256):
        for alt in range(256):
            for roll in(0,1):one(owner,alt,roll,85,0x31,weight=True)
        if owner%64==63:print('PROGRESS '+json.dumps(dict(selector_owners=owner+1,cases=cases)),flush=True)
    selector=cases
    for owner in range(256):
        for p in range(256):
            if p&32:one(owner,(owner*73)&255,owner&1,85,p)
    statuses=cases-selector
    for owner in range(256):
        for a in range(256):one(owner,(owner*17)&255,owner&1,a,0xe5)
    arguments=cases-selector-statuses
    for owner in range(256):
        for p in(0x20,0x31,0x69,0xe5):
            for x,y in((0,0),(0,255),(71,109),(255,255)):one(owner,(owner*31)&255,owner&1,85,p,x,y)
    allowed_reads=set(range(P.BASE,P.BASE+118))|{0x6002,0x5fe5,0x5feb}|set(range(0x1dd,0x1e1))
    allowed_writes={0x162,0x16a,0x16c,0x16d}|set(range(0x1dd,0x1e1))
    for m in memories:
        assert m.reads<=allowed_reads,('Unexpected classifier data reads',sorted(m.reads-allowed_reads))
        assert m.writes<=allowed_writes,('Private/global state written',sorted(m.writes-allowed_writes))
    assert minimum==220
    return dict(descriptor=P.descriptor(raw),cases=cases,all256_selected_all256_FmAlts_both_Roll_states=selector,
        all256_selected_all128_hardware_status= statuses,all256_selected_all256_input_A=arguments,
        register_corners=cases-selector-statuses-arguments,minimum_SP=minimum,
        exact_AXYP_SP_SafeA_stack_and_CVID=True,only_raw33_destination_changed=True,
        all_input_fields_and_private_state_unchanged=True,
        read_addresses_union=[sorted(m.reads-set(range(P.BASE,P.BASE+118)))for m in memories],
        written_addresses_union=[sorted(m.writes)for m in memories],
        cycle_savings=[dict(kind=k,cycles=d,cases=n)for(k,d),n in sorted(costs.items())],
        selector_cycle_savings_by_owner=[dict(owner=o,cycles=d,cases=n)for(o,d),n in sorted(owner_costs.items())],
        new_destination_count=len(destinations),no_actual_public_target_handler_executed=True,
        no_NesBus_ROM_mount_or_image=True,no_IRQ_or_gameplay_claim=True,outputs=0)


def main():
    raw=P.load_current()
    def deny(*a,**kw):raise AssertionError('Detached classifier attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(P.Reference.C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(raw)
    q['receipt_SHA256']=P.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
