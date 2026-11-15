"""Genuine cold CPU callback/return acknowledgement check for native profiler."""
from collections import defaultdict,deque
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json

import replay_battletoads_idle_native_profile_1115 as P
import check_battletoads_idle_funded_1115 as Base

W,N,Frames=Base.W,Base.N,Base.Frames


def run(raw):
    seed=Base.cold(raw);runtime=P.F.Frozen.LuaRuntime(unpack_returned_tuples=True)
    callbacks=defaultdict(list);events=defaultdict(list)
    ctx=dict(cpu=None,clock=0,status=None,receipt=None);m=None;recent=deque(maxlen=32)
    class ReadBus(type(seed)):
        def __getitem__(self,at):
            if isinstance(at,int):
                for fn in tuple(callbacks.get((1,at),())):fn()
            return super().__getitem__(at)
    m=list.__new__(ReadBus);list.extend(m,list.__iter__(seed))
    for name,value in seed.__dict__.items():setattr(m,name,value if name=='bundle'else deepcopy(value))
    api=runtime.table();api.memType=runtime.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=runtime.table_from(dict(exec=0,read=1));api.eventType=runtime.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==2:return raw[16+at]
        if kind==1:return m.ram[at//8192][at%8192]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return runtime.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def state():
        c=ctx['cpu'];row={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        row['cpu.ps']=row['cpu.p'];row['cpu.cycleCount']=ctx['clock'];return runtime.table_from(row)
    def memory(fn,kind,lo,hi=None):
        assert kind in(0,1)
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[kind,at].append(fn)
    def inputs(pad,port):
        assert port==0
        m.controller_pad=sum(value for key,value in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[key])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):
            ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '));ctx['receipt_trace']=list(recent)
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=inputs
    api.addMemoryCallback=memory;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    runtime.globals().emu=api;runtime.globals().print=emit;runtime.globals().CPU_CONTROLLER_OPENING=True
    runtime.execute(P.controller(raw))
    base=N.NesMPU
    class Observed(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.epoch=ctx['clock']
        def step(self):
            ctx['cpu']=self;ctx['clock']=self.epoch+self.processorCycles
            recent.append((self.pc,self.sp,self.a,self.x,self.y,list(m.rawtags)))
            for fn in tuple(callbacks.get((0,self.pc),())):fn()
            result=super().step();ctx['clock']=self.epoch+self.processorCycles;return result
    with patch.object(N,'NesMPU',Observed):
        for tick in range(100):
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            if ctx['status']is not None:break
    receipt=ctx['receipt'];assert ctx['status']==0,(ctx['status'],receipt,ctx.get('receipt_trace',list(recent)))
    q=receipt['native_cycle_profile'];assert len(q['rows'])<=32
    assert q['mapped_guard_entries']==q['guard_returns']==160 and q['unacknowledged_getters']==0,q
    assert not q['pending_Main']and q['pending_ISR']==0,q
    for phase,count in(('idle',48),('walk',32)):
        for name in('Main','getter12','getter13'):assert q['groups'][phase+':'+name]['calls']==count,q
    return dict(ROM_SHA256=sha256(raw).hexdigest(),controller_SHA256=sha256(P.controller(raw).encode()).hexdigest(),
        actual_source_Main=tick+1,profile=q,source_only_no_physical_IRQ_or_cadence_claim=True)


def main():
    parent=P.C.load_current_image();image=P.B.candidate(parent)
    def forbid(*a,**kw):raise RuntimeError('Profiler source check attempted output/native')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(P.C.Packet.Frozen.Cold.Runner.Native,'run',forbid):rows=[run(raw)for raw in(parent,image)]
    q=dict(results=rows,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
