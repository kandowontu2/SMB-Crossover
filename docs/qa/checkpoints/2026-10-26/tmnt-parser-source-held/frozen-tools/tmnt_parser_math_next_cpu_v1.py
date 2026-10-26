"""Full source math/caller domains and original16song comparison for1346."""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import itertools
import json
from check_tmnt_render_oa import load,address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,OB,sha
from tmnt_native_storage_cpu import Probe
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_multiply_cpu import Linked as PriorLinked

FLAGS=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]


def outcome(c,m):
    return(c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x1a0])+bytes(m[0x200:0x5205])+bytes(m[0x5207:0x8000]),list(m.banks),
        [(k,v)for k,v in m.writes if 0x4000<=k<=0x4017 or 0x5000<=k<=0x5015])


def math_groups(events,b):
    original=address(b,'TnFastProduct');size=int(b['syms']['TnFastProduct']['size'],0)
    tempo=address(b,'TnTempoProduct')if'TnTempoProduct'in b['syms']else None
    tempo_end=tempo+int(b['syms']['TnTempoProduct']['size'],0)if tempo else None
    i=0;groups=Counter()
    while i<len(events):
        first=events[i];assert first[:2]==['W',0x5205]
        second=events[i+1];assert second[:2]==['W',0x5206]
        product=first[2]*second[2]
        if original<=first[3]<original+size:
            group=events[i:i+4];assert len(group)==4
            assert[group[j][:2]for j in range(4)]==[['W',0x5205],['W',0x5206],['R',0x5205],['R',0x5206]]
            assert all(original<=r[3]<original+size for r in group)
            assert [group[2][2],group[3][2]]==[product&255,product>>8]
            assert 2<=first[2]<=15;i+=4;groups['existing_product']+=1
        else:
            assert tempo is not None and tempo<=first[3]<tempo_end
            count=3 if product>>8 else 4;group=events[i:i+count]
            assert len(group)==count and all(tempo<=r[3]<tempo_end for r in group)
            assert group[2][:2]==['R',0x5206]and group[2][2]==product>>8
            if count==4:assert group[3][:2]==['R',0x5205]and group[3][2]==product&255
            assert first[2]>=2;i+=count;groups['tempo_checked']+=1
    return groups


class Linked(PriorLinked):
    def call(self,row,song):
        c,m=self.c,self.m;c.sp=253;m[510],m[511]=255,1
        if row['call']==-1:c.a,c.x,c.y,c.pc=song-1,0,0,address(self.b,'TnNativeInit')
        else:c.pc=address(self.b,'TnNativePlay')
        m.writes=[];m.math_events=[];start=c.processorCycles;source=[];pending=[];minimum=255
        for _ in range(50000):
            if c.pc==512:break
            minimum=min(minimum,c.sp)
            if pending and c.pc==pending[-1][0]:
                ret,before=pending.pop();assert(c.a,c.x,c.y,c.p&207,c.sp)==before,('Writer ABI',song,row['call'],hex(ret));self.writers+=1
            if c.pc in self.sites and m.banks[(c.pc-0x8000)//8192]==63:
                site=self.sites[c.pc];index=c.x if site['mode']=='abx'else c.y if site['mode']=='aby'else 0
                source.append([site['address']+index,c.a]);pending.append((c.pc+3,(c.a,c.x,c.y,c.p&207,c.sp)))
            m.executing_PC=c.pc;c.step()
        else:raise AssertionError(('Source timeout',song,row['call'],hex(c.pc)))
        assert not pending and c.sp==255 and source==row['writes']
        assert all(at in self.allowed for at,v in m.writes if at<0x8000 and not 0x4000<=at<=0x4017)
        assert all(m[i]==self.saved_zp[i]for i in range(256)if not self.zp<=i<self.zp+14)
        assert not[(at,v)for at,v in m.writes if 0x2000<=at<0x4000 or 0x5000<=at<0x6000 and at not in[0x5205,0x5206]]
        groups=math_groups(m.math_events,self.b);self.math_calls+=sum(groups.values())
        assert m.banks==[126,63,99,127]
        self.depth=min(self.depth or 255,minimum);self.HW.extend((at,v)for at,v in m.writes if 0x4000<=at<=0x4017)
        return c.processorCycles-start


def domain(a):
    old,new=load(a.baseline),load(a.candidate);machines=[]
    for b in[old,new]:
        m=MathMemory(b);m.page(1,63);m.page(2,99);machines.append((b,NesMPU(memory=m),m))
    def pair(kind,period,x,pin,channel_flag=91):
        costs=[]
        for b,c,m in machines:
            zp,ram=address(b,'TnAudioZp'),address(b,'TnAudioRam')
            for i in range(14):m[zp+i]=(i*31+37)&255
            m[zp+2]=period;m[ram+0x22+x]=37;m[ram+0x28+x]=219
            m[ram+0x16+x]=channel_flag;m[ram+4+x]=period
            m.writes=[];m.math_events=[];c.pc=0xaacc if kind=='tempo'else 0xa671
            c.a,c.x,c.y,c.p,c.sp=period,x,47,pin,253;start=c.processorCycles
            for _ in range(4000):
                if c.pc in([0xaadd]if kind=='tempo'else[0xa67f,0xa91f]):break
                m.executing_PC=c.pc;c.step()
            else:raise AssertionError(('Domain timeout',kind,period,x,pin))
            costs.append(c.processorCycles-start)
            if kind=='tempo':math_groups(m.math_events,b)
        c,m=machines[0][1:];d,n=machines[1][1:]
        assert outcome(c,m)==outcome(d,n),('Domain complete state',kind,period,x,pin,channel_flag)
        assert c.pc==d.pc
        return costs[1]-costs[0]
    costs=Counter();count=0
    for period,x,pin in itertools.product(range(129),range(1,17),FLAGS):costs[pair('tempo',period,x,pin)]+=1;count+=1
    edge=Counter();edges=0
    for period,x,pin in itertools.product([0,1,2,15,16,31,64,127,128,129,255],[0,17,31,127,128,255],FLAGS):
        edge[pair('tempo',period,x,pin)]+=1;edges+=1
    pointer=Counter();pointers=0
    for timer,x,pin in itertools.product(range(256),range(6),FLAGS):
        pointer[pair('pointer',timer,x,pin)]+=1;pointers+=1
    for flag,timer,x,pin in itertools.product(range(256),[0,1,2,255],range(6),[0x20,0xe9]):
        pointer[pair('pointer',timer,x,pin,flag)]+=1;pointers+=1
    return dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        actual_loop_cases=count,actual_loop_E2_range=[0,128],actual_source_counts=[1,16],all64physical_flags=True,
        outside_source_count_and_byte_edge_cases=edges,pointer_duration_join_cases=pointers,
        full_AXYP_SP_source_nonstackRAM_SMC_banks_APU_exact=True,original_A67F_A91F_AADD_joins_genuine=True,
        tempo_cycle_delta_histogram=dict(sorted(costs.items())),edge_cycle_delta_histogram=dict(sorted(edge.items())),
        pointer_cycle_delta_histogram=dict(sorted(pointer.items())),checker_sha256=sha(Path(__file__)),native_recovery_claim=False)


def songs(a):
    coverage=json.loads((OB/'probe-v2/coverage.json').read_text());calls=stores=writers=0;rows=[];deltas=Counter();regressions=[]
    for song,meta in coverage['songs'].items():
        capture=OB/f'probe-v2/song-{int(song):02d}.json.gz';assert sha(capture)==meta['capture_sha256'];gold=json.loads(gzip.decompress(capture.read_bytes()))
        original,parent,child=Probe(a.raw_original,True),Linked(a.baseline,True),Linked(a.candidate,True);costs=[[],[],[]]
        for row in gold:
            for i,runner in enumerate([original,parent,child]):costs[i].append(runner.call(row,int(song)))
            assert original.registers()==parent.registers()==child.registers(),('Source AXYP',song,row['call'])
            positions=list(range(0xe0,0xee))+list(range(0x7000,0x70ae))
            expected=bytes((original.m[at]-(27 if original.origin.get(at)in original.changed_high else 0))&255 for at in positions)
            assert parent.state()==child.state()==expected,('Source state',song,row['call'])
            delta=costs[2][-1]-costs[1][-1];deltas[delta]+=1
            if delta>0:regressions.append(dict(song=int(song),call=row['call'],delta=delta))
            calls+=1;stores+=len(row['writes'])
        q=dict(song=int(song),calls=len(gold),requests=sum(len(r['writes'])for r in gold),
            parent_total=sum(costs[1]),candidate_total=sum(costs[2]),parent_peak=max(costs[1][1:]),candidate_peak=max(costs[2][1:]),
            parent_mean=sum(costs[1][1:])/12000,candidate_mean=sum(costs[2][1:])/12000)
        rows.append(q);writers+=parent.writers+child.writers;print(q,flush=True)
        (a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        original_calls=calls,original_ordered_APU_requests=stores,checked_writer_returns=writers,
        full_source_AXYP_SP_188byte_state_foreground_ZP_SMC_banks_exact=True,
        exact_helper_owned_products_with_explicit_new_high_first_guard=True,
        cycle_delta_histogram=dict(sorted(deltas.items())),regressions=regressions,songs=rows,
        checker_sha256=sha(Path(__file__)),native_recovery_claim=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--test',choices=['domain','songs'],required=True);p.add_argument('--raw-original',type=Path);a=p.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    proof=domain(a)if a.test=='domain'else songs(a)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in['songs','regressions']}))
