"""Existing-code C-window borrower ownership; no proposed scope or opcodes."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import inspect_contra_force_main_cwindow_current_1116 as Previous

M,N,W,Frames=Previous.M,Previous.N,Previous.W,Previous.Frames
PREVIOUS_SHA='5f84a8430062ad5e5b8d01cc0a51c1821f9e9a44dd72d299b85b19caf4c14b42'


def run(raw):
    assert M.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    q=M.bindings(raw);b=q['bundle'];base=N.NesMPU
    ctx={'CPU':None,'instruction':False,'measurement':False,'after_cold':False,'frames':0}
    mapwrites=Counter();p1=Counter();sfc=Counter();headers=Counter();main=[]
    original_cold,original_frame=M.cold,Frames.frame
    bus_type=W.ControllerBus;reader,writer=bus_type.__getitem__,bus_type.__setitem__
    def tag(m,pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def ret(c,m):
        pc=(reader(m,256+((c.sp+1)&255))+256*reader(m,256+((c.sp+2)&255))+1)&65535
        return pc,(c.sp+2)&255,tag(m,pc)
    class CPU(base):
        def step(self):
            m=self.memory;active=ctx['measurement']and getattr(self,'main',None)is not None and not getattr(self,'isrs',())
            ctx.update(CPU=self,instruction=active,PC=self.pc,tag=tag(m,self.pc),SP=self.sp)
            if active:
                if not main:main.append(dict(entry_SP=self.sp,first_observed_PC=self.pc,tag=tag(m,self.pc)))
                if self.pc in(0x15a,0x15d):
                    bank=self.a if self.pc==0x15a else reader(m,0x162)
                    target=reader(m,0x16c)+256*reader(m,0x16d)
                    sfc[bank,target,self.sp,ret(self,m)]+=1
            try:return super().step()
            finally:ctx['instruction']=False
    def observed_write(bus,at,value):
        if ctx['instruction']and isinstance(at,int):
            if at in(0x7da1,0x5116):
                before=tag(bus,0xc000)if at==0x5116 else reader(bus,at)
                mapwrites[ctx['tag'],ctx['PC'],ctx['SP'],at,before,value&255]+=1
            if at>=0x8000 and tag(bus,at)==2 and(at&8191)==0x1dd1:
                p1['write',ctx['tag'],ctx['PC'],ctx['SP'],value&255]+=1
            if at>=0x8000 and tag(bus,at)in(2,3)and 0x1fe0<=at&8191<0x1ff0:
                headers[tag(bus,at),ctx['tag'],ctx['PC'],at&8191,value&255]+=1
        return writer(bus,at,value)
    def observed_read(bus,at):
        value=reader(bus,at)
        if ctx['instruction']and isinstance(at,int)and at>=0x8000 and tag(bus,at)==2 and(at&8191)==0x1dd1:
            p1['read',ctx['tag'],ctx['PC'],ctx['SP'],value]+=1
        return value
    def cold(image):
        m=original_cold(image);ctx.update(after_cold=True,frames=0);return m
    def frame(m,*a,**kw):
        if ctx['after_cold']:ctx['frames']+=1;ctx['measurement']=ctx['frames']==5
        return original_frame(m,*a,**kw)
    with patch.object(M,'cold',cold),patch.object(Frames,'frame',frame),patch.object(N,'NesMPU',CPU),patch.object(bus_type,'__getitem__',observed_read),patch.object(bus_type,'__setitem__',observed_write):old=Previous.run(raw)
    assert old['passed']and old['Main']['Main_entries']==old['Main']['Main_returns']==1
    assert ctx['frames']==5 and main,(ctx['frames'],main)
    assert len(mapwrites)<=256,('Aggregate map writer bound',len(mapwrites))
    # Authenticated source/code addresses, not nearest-name claims for data.
    points=[]
    for t,pc in sorted({(k[0],k[1])for k in mapwrites}|{(k[1],k[2])for k in p1}):
        if t>=128:at=16+(t&127)*8192+(pc&8191);data=raw[at:at+12]
        else:data=q['carrier'][(t-1)*8192+(pc&8191):(t-1)*8192+(pc&8191)+12]
        points.append(dict(tag=t,PC=pc,next12=data.hex()))
    mapgroups={}
    for(t,pc,sp,at,before,after),n in mapwrites.items():
        row=mapgroups.setdefault((t,pc,at,before,after),dict(SPs=set(),writes=0));row['SPs'].add(sp);row['writes']+=n
    out=dict(passed=True,owning_SHA256=M.H(raw),source_observer_SHA256=PREVIOUS_SHA,
        Main=old['Main'],previous_Cwindow_receipt=old['receipt_SHA256'],
        map_writers=[dict(writer_tag=t,PC=pc,actual_SPs=sorted(row['SPs']),address=at,before=before,after=after,writes=row['writes'])for(t,pc,at,before,after),row in sorted(mapgroups.items())],
        all_map_writer_SP_contexts=len(mapwrites),
        P1NativeC_accesses=[dict(kind=kind,tag=t,PC=pc,SP=sp,value=v,accesses=n)for(kind,t,pc,sp,v),n in sorted(p1.items())],
        header_writes=[dict(physical_tag=physical,writer_tag=t,PC=pc,offset=at,value=v,writes=n)for(physical,t,pc,at,v),n in sorted(headers.items())],
        SFC_raw_entry_points_top24=[dict(bank_tag=t,PC=pc,SP=sp,actual_return=returned,entries=n)for(t,pc,sp,returned),n in sfc.most_common(24)],
        SFC_raw_entry_points_all_contexts=len(sfc),SFC_raw_entry_points_SHA256=M.H(json.dumps(sorted((list(k),v)for k,v in sfc.items()),separators=(',',':')).encode()),
        exact_current_map_writer_preimages=points,
        scope='One genuine ordinary current Main; no mapping/state intervention. Bank2/RAM3 loader and foreign/IRQ domains are not closed by absence here.',
        no_new_game_code_or_scope_allocation_or_native=True,outputs=0)
    out['receipt_SHA256']=M.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=M.load_current_image();original=Path.read_bytes
    def read(path):
        assert path.resolve()!=M.ROM.resolve(),'No second mutable Nightly read'
        return original(path)
    def deny(*a,**kw):raise AssertionError('Borrower audit attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
