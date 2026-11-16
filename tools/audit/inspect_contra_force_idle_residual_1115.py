"""One real bc5 idle Main: unassigned instruction aggregates and P1 OAM witness."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import profile_contra_force_current_costs_1115 as P

C,W,N,Frames=P.C,P.W,P.N,P.Frames
PROFILE_PIN='721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94'


def inspect(raw):
    assert C.H(Path(P.__file__).read_bytes())==PROFILE_PIN
    q=P.bindings(raw);m=P.cold(raw);b=m.bundle;points=q['points']
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    # The exact current retained segment declaration binds physical RAM3,
    # not the same numerical PC in any mapped ROM/foreign family.
    late=bytes(q['carrier'][16384+0x1e53:16384+0x1eff])
    gate=bytes(q['carrier'][16384+0x1f55:16384+0x1f6b])
    packet=bytes(q['carrier'][0x1f10:0x1f8c])
    assert len(late)==172 and len(gate)==22 and len(packet)==124
    counts=Counter();cycles=Counter();pages=Counter();by_pc=Counter();closed=Counter()
    witnesses=[];instances=[];base=N.NesMPU;minimum=255
    class Probe(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.pending=[];self.oam=None;instances.append(self)
        def settle(self):
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            while self.pending and(self.pc,self.sp,tag)==self.pending[-1]['return_']:
                done=self.pending.pop();closed[done['name']]+=1
            return tag
        def step(self):
            nonlocal minimum
            tag=self.settle();pc=self.pc;point=points.get((tag,pc))
            if point:
                assert bytes(m[pc:pc+8])==bytes(point['bytes'])
                sp=self.sp;ret=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                rt=m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                self.pending.append(dict(name=point['name'],return_=(ret,(sp+2)&255,rt)))
                counts[point['name']]+=1
            if(tag,pc)==(3,0xbe80):
                assert bytes(m[0xbe53:0xbeff])==late
                assert self.oam is None
                self.oam=bytes(m[0x200:0x300])
                tags=Counter((self.oam[i]<240,self.oam[i+2]&24)for i in range(0,256,4))
                witnesses.append(dict(entry_PC=pc,entry_tag=tag,SP=self.sp,
                    OAM_SHA256_before=C.H(self.oam),tagged_rows=sum(n for(_,t),n in tags.items()if t),
                    rows=[dict(visible=v,attribute_tag=t,count=n)for(v,t),n in sorted(tags.items())]))
            if(tag,pc)==(3,0xbf55)and self.oam is not None:
                assert bytes(m[pc:pc+22])==gate
                after=bytes(m[0x200:0x300]);choice=m.ram[2][0x2fb];visible=m.ram[2][0x2fa]
                expected=bytearray(self.oam)
                for i in range(0,256,4):
                    t=expected[i+2]&24
                    if(t==8 and not choice)or(t==16 and choice):expected[i]=248
                    expected[i+2]&=231
                assert after==expected,('Actual P1 paint contract',choice,visible)
                witnesses[-1].update(gate_PC=pc,gate_tag=tag,visible=visible,choice=choice,
                    OAM_SHA256_after=C.H(after),paint_changed_OAM=after!=self.oam,
                    all64_actual_rows_equal_original_contract=True)
                self.oam=None
            active=self.pending[-1]['name']if self.pending else None
            in_main=any(s['name']=='GameLoop'for s in self.pending)
            start=self.processorCycles;minimum=min(minimum,self.sp);result=super().step();delta=self.processorCycles-start
            if in_main:
                cycles[active]+=delta
                if active=='GameLoop':pages[tag,pc&0xff00]+=delta;by_pc[tag,pc]+=delta
            return result
    with patch.object(N,'NesMPU',Probe):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    for c in instances:c.settle()
    assert not any(c.pending or c.oam for c in instances)
    assert counts==closed and counts['GameLoop']==counts['CfP1LateEntry']==1
    P.empty(m)
    tops=[]
    for(tag,pc),n in by_pc.most_common(32):
        if tag>=128:at=16+(tag&127)*8192+(pc&8191);preimage=raw[at:at+8]
        elif tag>0:at=P.CHR+935*1024+(tag-1)*8192+(pc&8191);preimage=raw[at:at+8]
        else:at=None;preimage=bytes(m[pc:pc+8])
        tops.append(dict(tag=tag,PC=pc,cycles=n,source_file=at,bytes=preimage.hex()))
    return dict(ROM_SHA256=C.H(raw),reference67_SHA256=q['reference67_SHA256'],
        exact_actual_cf_late=dict(tag=3,PC=0xbe53,length=172,SHA256=C.H(late),hex=late.hex()),
        exact_actual_cf_gate=dict(tag=3,PC=0xbf55,length=22,SHA256=C.H(gate),hex=gate.hex()),
        actual_packet=dict(tag=1,PC=0xbf10,length=124,SHA256=C.H(packet)),
        source_main_calls=1,all_named_calls=dict(counts),all_named_returns=dict(closed),
        exclusive_Main_cycles=sum(cycles.values()),exclusive_cycles_by_innermost=dict(cycles),
        residual_cycles=cycles['GameLoop'],
        residual_physical_page_cycles=[dict(tag=t,page=p,cycles=n)for(t,p),n in pages.most_common()],
        residual_top32_instructions=tops,P1_witnesses=witnesses,minimum_SP=minimum,
        actual_native_actors=0,actual_source_shots=0,no_overlay_or_gameplay_seeds=True,
        scheduler_regular_NMI_is_outside_Main=True,no_native_or_cadence_claim=True,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No second mutable Nightly read'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only source inspection attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q=inspect(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
