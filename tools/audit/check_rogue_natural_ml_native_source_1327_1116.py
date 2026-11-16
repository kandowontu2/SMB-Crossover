"""Execute native ML callbacks, including real life-writer token; no files."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_rogue_natural_ml_1327_1116 as F
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,N,Frames=F.J,F.N,F.Frames


def run(raw,limit=3000):
    text=F.controller(raw);m=J.cold(raw);lua=LuaRuntime(unpack_returned_tuples=True)
    callbacks={0:defaultdict(list),1:defaultdict(list)};events=defaultdict(list);ctx=dict(cpu=None,pc=0,status=None,receipt=None)
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        assert kind==0;return m[at]
    def mapped(pc):
        if pc<0x8000:return None
        tag=m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(pc&8191)))
    def state():
        c=ctx['cpu'];d={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        d['cpu.pc']=ctx['pc'];d['cpu.ps']=d['cpu.p'];return lua.table_from(d)
    def memory(fn,kind,lo,hi=None):
        assert kind in(0,1)
        for at in range(lo,(hi if hi is not None else lo)+1):callbacks[kind][at].append(fn)
    def pad(p,port):
        assert port==0;m.controller_pad=sum(v for n,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if p[n])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=pad;api.addMemoryCallback=memory
    api.addEventCallback=lambda fn,kind:events[kind].append(fn);api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text)
    registration=dict(exec_addresses=len(callbacks[0]),write_addresses=len(callbacks[1]),event_counts={k:len(v)for k,v in events.items()})
    assert registration['exec_addresses']==17 and registration['write_addresses']==19 and registration['event_counts']=={0:1,1:1},registration
    base=N.NesMPU;old_write=type(m).__setitem__
    class CPU(base):
        def step(self):
            ctx.update(cpu=self,pc=self.pc)
            for fn in tuple(callbacks[0].get(self.pc,())):fn()
            return super().step()
    def write(bus,at,value):
        if bus is m and isinstance(at,int):
            for fn in tuple(callbacks[1].get(at,())):fn(at,value)
        return old_write(bus,at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
        for tick in range(limit):
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            if ctx['status']is not None:break
    q=ctx['receipt']or{}
    result=dict(passed=ctx['status']==0 and q.get('passed')is True,metadata=F.metadata(raw),
        executed_top_level_registration=registration,source_passes=tick+1,receipt=q,
        native_receipt_SHA256=F.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),
        actual_owning_CPU=True,actual_renderer_or_Mesen=False,outputs=0)
    result['receipt_SHA256']=F.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=3000);a=p.parse_args();assert 2801<=a.limit<=3500
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Callback source gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)




