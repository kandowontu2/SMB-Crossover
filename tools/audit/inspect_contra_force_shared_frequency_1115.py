"""One unchanged current Burns Main: exact helper frequencies and P1 marker writes."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import profile_contra_force_current_costs_1115 as P

C,W,N,Frames=P.C,P.W,P.N,P.Frames


def run(raw):
    q=P.bindings(raw);m=P.cold(raw);b=m.bundle
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    base=N.NesMPU;counts=Counter();private=Counter();marker=Counter();ctx={};writer=type(m).__setitem__
    class Observe(base):
        def step(self):
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            ctx.update(PC=self.pc,tag=tag,SP=self.sp)
            if(tag,self.pc)==(224,0xb799):
                word=m[0x101+self.sp]+256*m[0x102+self.sp]
                assert word==0x16d and m[0x103+self.sp]==215
                counts[self.a,self.x,self.y,self.p&1,self.sp]+=1
            if(tag,self.pc)==(2,0xbe6e):private[m[0x16c]]+=1
            return super().step()
    def write(bus,at,value):
        if isinstance(at,int)and at>=0x8000:
            tag=bus.rawtags[(at-0x8000)//8192]
            if tag==2 and(at&8191)==0x2df:
                marker[ctx['tag'],ctx['PC'],ctx['SP'],value]+=1
        return writer(bus,at,value)
    with patch.object(N,'NesMPU',Observe),patch.object(type(m),'__setitem__',write):
        m.controller_pad=0;Frames.frame(m,whole_pass=True)
    P.empty(m)
    masks=[]
    for name in('Bitmasks','CfRetire'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        masks.append(dict(name=name,PC=pc,file=at,physical_PRG=bank,bytes=raw[at:at+(8 if name=='Bitmasks'else 36)].hex(),
            fixed_CPU_window=pc<0xa000 or pc>=0xe000))
    return dict(owning_ROM_SHA256=C.CANDIDATE,one_actual_unchanged_Main=True,
        helper_frequencies=[dict(command_offset=a,query_X=x,cohort_Y=y,incoming_C=c,SP=sp,calls=n)for(a,x,y,c,sp),n in sorted(counts.items())],
        private_service_frequencies=[dict(offset=a,calls=n)for a,n in sorted(private.items())],
        all_helper_entries_real_SFC_return016D_oldbankD7=True,
        marker_writes=[dict(physical_code_tag=t,PC=pc,SP=sp,value=v,count=n)for(t,pc,sp,v),n in sorted(marker.items())],
        fixed_mask_and_retire_bindings=masks,
        zero_native_actors_source_shots_no_A_B_gameplay_or_state_seeds=True,
        no_modified_opcode_or_ROM_or_native=True,outputs=0)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No second mutable Nightly read'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only frequency inspection attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
