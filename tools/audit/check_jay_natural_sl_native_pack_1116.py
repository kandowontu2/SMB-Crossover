"""Strict current packaging and16 genuine-source-update callback smoke."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import json
import replay_jay_natural_sl_7c0f_1116 as F
from check_ff_stdout_controller_source_1110 import LuaRuntime

J=F.J


def run(raw):
    q=J.bindings(raw);scripts={kind:F.controller(raw,kind)for kind in('life','star')}
    rejects=[]
    dirty=bytearray(raw);dirty[123]^=1
    for name,image,kind in(('dirty',bytes(dirty),'life'),('historical91dc',J.reference(raw),'star'),('unknown-kind',raw,'flower')):
        try:F.controller(image,kind)
        except AssertionError:rejects.append(name)
        else:raise AssertionError('Native factory accepted '+name)
    compiled=[]
    for kind,text in scripts.items():
        lua=LuaRuntime();assert lua.execute('return function()\n'+text+'\nend')
        assert 'emu.write'not in text and 'io.open'not in text
        compiled.append(dict(kind=kind,bytes=len(text.encode()),SHA256=J.H(text.encode())))
    # Observer setup only: actual game/cookies/position come exclusively from
    # genuine compiled menu+constructor. No game state is supplied here.
    m=J.cold(raw);lua=LuaRuntime();callbacks=defaultdict(list);events=defaultdict(list);instances=[];current=[None];receipts=[];stopped=[]
    mem=dict(nesDebug=0,nesPrgRom=1,nesWorkRam=2);types=dict(exec=0,write=1)
    def read(at,kind):
        if kind==mem['nesPrgRom']:return raw[16+at]
        if kind==mem['nesWorkRam']:return m.ram[at//8192][at&8191]
        return m[at]
    def convert(pc):
        if pc<0x8000:return lua.table_from(dict(memType=mem['nesDebug'],address=pc))
        tag=m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=mem['nesPrgRom']if tag>=128 else mem['nesWorkRam'],address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        c=current[0];assert c is not None
        return lua.table_from({'cpu.pc':c.pc,'cpu.sp':c.sp,'cpu.a':c.a,'cpu.x':c.x,'cpu.y':c.y,'cpu.ps':c.p})
    def add(fn,kind,at):callbacks[kind,at].append(fn)
    def event(fn,kind):events[kind].append(fn)
    def input_pad(v,port):
        assert port==0
        m.controller_pad=sum(bit for key,bit in dict(right=1,left=2,down=4,up=8,start=16,select=32,b=64,a=128).items()if v[key])
    emu=lua.table_from(dict(memType=lua.table_from(mem),callbackType=lua.table_from(types),eventType=lua.table_from(dict(inputPolled=0,endFrame=1)),
        read=read,convertAddress=convert,getState=cpu_state,addMemoryCallback=add,addEventCallback=event,setInput=input_pad,stop=lambda code:stopped.append(code)))
    lua.globals().emu=emu;lua.globals().print=lambda *a:receipts.append(' '.join(map(str,a)))
    lua.execute('os.getenv=function(name)assert(name=="SMB_STDOUT_ROM_SHA");return "'+J.PIN+'"end')
    witness=lua.execute(scripts['life']+'\nreturn {start=function()for name in pairs(H)do auth(name)end;game=true;pad=0 end,settle=settle,counts=counts,pending=pending,get=function()return{Main=main,updates=updates,motor=motor,state=state()}end}')
    witness.start();base=J.N.NesMPU;old_write=type(m).__setitem__
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);instances.append(self)
        def step(self):
            current[0]=self
            for fn in tuple(callbacks[types['exec'],self.pc]):fn()
            return super().step()
    def write(bus,at,value):
        if bus is m and current[0]is not None:
            for fn in tuple(callbacks[types['write'],at]):fn(at,value)
        return old_write(bus,at,value)
    with patch.object(J.N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
        for _ in range(16):
            for fn in events[0]:fn()
            J.Frames.frame(m,whole_pass=True)
            # Source Frames can stop at an acknowledged return before its next
            # instruction. Invoke only the observer's settle at those real
            # PC/SP endpoints, not entry callbacks or synthetic return PCs.
            for c in instances:current[0]=c;witness.settle()
            instances.clear();assert not stopped,(stopped,receipts)
    result=witness.get();counts=dict(witness.counts.items())
    assert len(witness.pending)==0 and result['Main']==result['updates']==result['motor']==16
    for name in('GameLoop','JayIntegrate'):assert counts[name+'_entries']==counts[name+'_returns']==16
    out=dict(passed=True,owning_SHA256=J.PIN,wrong_inputs_rejected=rejects,compiled=compiled,
        actual_cold_and16_update_callback_smoke=True,counts=counts,Main=result['Main'],motor=result['motor'],
        terminal={k:v for k,v in result['state'].items()},pending=0,
        cold_UI_boot_native_unrun=True,natural_collector_observer_native_unrun=True,
        factory_SHA256=J.H(Path(F.__file__).read_bytes()),checker_SHA256=J.H(Path(__file__).read_bytes()),
        generated_files=0,native=False,no_gameplay_or_health_or_actor_seeds=True)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Native package smoke attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
