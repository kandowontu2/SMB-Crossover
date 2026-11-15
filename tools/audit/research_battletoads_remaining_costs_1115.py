"""Read-only attribution/funding research on existing exact a90c; no new bytes."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

import compose_battletoads_idle_funded_1115 as C
import check_battletoads_idle_funded_1115 as Base
import profile_battletoads_current_idle_1114 as Profile

R=C.Packet
W,N,Frames=Base.W,Base.N,Base.Frames


def load():
    parent=C.load_current_image();image,info=C.proposal(parent)
    assert C.inverse(image)==parent
    return parent,image,info


def inspect(parent,image):
    q=R.inspect(parent)
    for row in q['resolver_spans']:
        lo,hi=row['file'];assert parent[lo:hi]==image[lo:hi]
    q['executed_reference_SHA256']=C.CANDIDATE
    q['resolver_bytes_identical_on_a90c']=True
    b=Base.symbols(image);extra=[]
    for name in('BtCheck','CfOrBtCheck','BtRouter','BtActive','BtSave','BtRestore','KbDrawDispatch','ThSharedDrawHot','NrDraw'):
        if name not in b['syms']:continue
        at=W.location(b,name);pc=W.address(b,name);sym=b['syms'][name];segment=b['segs'][sym['seg']]
        tag=3 if segment.get('name','').startswith('"BT_CACHE')else((at-16)//8192)|128
        size=96 if name in('BtCheck','CfOrBtCheck')else 40
        code=image[at:at+size];memory=[0]*65536;memory[pc:pc+size]=code;d=Disassembler(MPU(memory=memory));listing=[];cursor=pc
        while cursor<pc+size:
            n,text=d.instruction_at(cursor);listing.append(dict(PC=cursor,hex=bytes(memory[cursor:cursor+n]).hex(),instruction=text));cursor+=n
        extra.append(dict(name=name,tag=tag,PC=pc,file=at,bytes=code.hex(),listing=listing))
    q['actual_validator_and_wrapper_bindings']=extra
    return q


def profile(parent,image,count=4):
    m=Base.cold(image);b=m.bundle;base=N.NesMPU;idle=W.address(b,'IdleLoop')
    points=Profile.points(image,b)
    names=('WfResolve','BwBtResolve','HuFullBox','HuMovement','HuDraw','HuVisible',
        'GameCoreRoutine','DrawAllMetasprites','EnemiesAndLoopsCore','AreaParserTaskHandler','MetaspriteRenderLoop')
    for name in names:
        if name in b['syms']:
            at=W.location(b,name);key=(((at-16)//8192)|128,W.address(b,name))
            if name not in points.setdefault(key,[]):points[key].append(name)
    for slot in range(36):points[215,0xb020+3*slot]=['public_slot'+str(slot)]
    macros=Profile.save_blocks(image,b)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    phases=[];minimum=255
    for phase,pad in(('idle',0),('right',1)):
        calls=Counter();inclusive=Counter();exclusive=Counter();banks=Counter();pcs=Counter()
        jsr_cost=Counter();jsr_calls=Counter();unwinds=Counter();cpus=[];rows=[];mac_cost=Counter();mac_calls=Counter();returns=Counter();resolver_entries=Counter()
        class Probe(base):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.kind='Main'if self.pc==idle else'NMI';self.pending=[];self.jsrs=[];cpus.append(self)
            def step(self):
                nonlocal minimum
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.jsrs:
                    p=self.jsrs[-1]
                    if(self.pc,self.sp)==p['return']:
                        self.jsrs.pop();jsr_cost[p['key']]+=self.processorCycles-p['cycle'];jsr_calls[p['key']]+=1
                    elif self.sp>p['return'][1]:self.jsrs.pop();unwinds[p['key']]+=1
                    else:break
                while self.pending and(self.pc,self.sp)==self.pending[-1]['return']:
                    p=self.pending.pop();inclusive[self.kind,p['name']]+=self.processorCycles-p['cycle'];returns[self.kind,p['name']]+=1
                for name in points.get((tag,self.pc),()):
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    self.pending.append(dict(name=name,cycle=self.processorCycles,**{'return':(ret,(self.sp+2)&255)}));calls[self.kind,name]+=1
                    if name in('WfResolve','BwBtResolve','BtRouter','CfOrBtCheck','BtCheck'):
                        resolver_entries[self.kind,name,self.a,self.x,self.y]+=1
                pc=self.pc;before=self.processorCycles;minimum=min(minimum,self.sp)
                if m[pc]==0x20:
                    target=m[pc+1]+256*m[pc+2];target_tag=m.rawtags[(target-0x8000)//8192]if target>=0x8000 else-1
                    self.jsrs.append(dict(key=(self.kind,tag,pc,target_tag,target),cycle=before,**{'return':((pc+3)&65535,self.sp)}))
                result=super().step();cost=self.processorCycles-before;banks[self.kind,tag]+=cost;pcs[self.kind,tag,pc]+=cost
                if self.pending:exclusive[self.kind,self.pending[-1]['name']]+=cost
                if tag==3:
                    for name,spans in macros.items():
                        for lo,hi in spans:
                            if lo<=pc<hi:
                                mac_cost[self.kind,name]+=cost
                                if pc==lo:mac_calls[self.kind,name]+=1
                return result
        with patch.object(N,'NesMPU',Probe):
            for tick in range(count):
                before=calls['Main','GameLoop'];returned=returns['Main','GameLoop'];start=len(cpus)
                m.controller_pad=pad;cost=Frames.frame(m,whole_pass=True)
                assert calls['Main','GameLoop']-before==returns['Main','GameLoop']-returned==1
                state=Profile.state(m);assert(state['HP'],state['lives'],state['power'],state['star'])==(47,2,0,0)and not state['actors']
                rows.append(dict(Main=tick+1,normal_draw=True,Main_cycles=cost,
                    scheduled_NMI_cycles=sum(c.processorCycles for c in cpus[start:]if c.kind=='NMI')))
        hot=[]
        for(kind,tag,caller,target_tag,target),cost in jsr_cost.most_common(24):
            target_names=[]
            if target_tag&128:
                pos=16+(target_tag&127)*8192+(target&8191)
                for name in b['syms']:
                    try:where=W.location(b,name)
                    except(KeyError,AssertionError):continue
                    if where==pos:target_names.append(name)
            hot.append(dict(kind=kind,caller_tag=tag,caller_PC=caller,target_tag=target_tag,target_PC=target,
                names=target_names[:4],cycles_per_Main=cost/count,calls_per_Main=jsr_calls[kind,tag,caller,target_tag,target]/count))
        unreturned=Counter(p['name']for c in cpus for p in c.pending)
        assert all(returns[k,n]==v for(k,n),v in calls.items()if n in('GameLoop','WfResolve','BwBtResolve','BtRouter','CfOrBtCheck','BtCheck')),(dict(calls),dict(returns),dict(unreturned))
        row=dict(phase=phase,Main=count,per_Main=rows,mean_Main=sum(x['Main_cycles']for x in rows)/count,
            mean_scheduled_NMI=sum(x['scheduled_NMI_cycles']for x in rows)/count,
            inclusive=[dict(kind=k,name=n,calls_per_Main=calls[k,n]/count,cycles_per_Main=v/count)for(k,n),v in inclusive.most_common()],
            innermost=[dict(kind=k,name=n,cycles_per_Main=v/count)for(k,n),v in exclusive.most_common()],
            banks=[dict(kind=k,tag=t,cycles_per_Main=v/count)for(k,t),v in banks.most_common(16)],
            hot_PCs=[dict(kind=k,tag=t,PC=pc,cycles_per_Main=v/count)for(k,t,pc),v in pcs.most_common(20)],
            actual_JSR=hot,resolver_entries=[dict(kind=k,name=n,A=a,X=x,Y=y,count=v)for(k,n,a,x,y),v in sorted(resolver_entries.items())],
            nonlocal_JSR_unwinds=[dict(kind=k,tag=t,PC=pc,target_tag=tt,target=target,count=v)for(k,t,pc,tt,target),v in sorted(unwinds.items())],
            unreturned_named_scopes=dict(unreturned),
            private_save_restore=[dict(kind=k,name=n,cycles_per_Main=v/count,calls_per_Main=mac_calls[k,n]/count)for(k,n),v in mac_cost.items()],
            final=Profile.state(m))
        phases.append(row);print('PROGRESS '+json.dumps(dict(phase=phase,Main=row['mean_Main'],NMI=row['mean_scheduled_NMI'])),flush=True)
    return dict(ROM_SHA256=C.CANDIDATE,phases=phases,minimum_SP=minimum,
        normal_source_Main_not_native_catchup_mean=True,inclusive_spans_overlap=True,
        cache_check_audio_timers_inputs_unchanged=True,no_new_opcode_or_image=True,physical_cadence_claim=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inspect',action='store_true');args=ap.parse_args()
    parent,image,info=load()
    def forbid(*a,**kw):raise RuntimeError('Cost research attempted output/native')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',forbid):q=inspect(parent,image)if args.inspect else profile(parent,image)
    q.update(actual_reference_SHA256=C.CANDIDATE,source_parent_SHA256=C.PIN,outputs=0,Mesen_run=False,new_code_mount=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
