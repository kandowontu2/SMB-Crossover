"""Finite bindings/compile and actual-CPU production-Lua callback qualification."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import argparse,json
import replay_sonic_hidden_life_f7c9_1116 as Factory
import check_ff_stdout_controller_source_1110 as Mock

F=Factory.F


def compile_pack(raw):
    rows=[]
    for form in F.FORMS:
        text=Factory.controller(raw,form);rt=Mock.LuaRuntime(unpack_returned_tuples=True)
        assert rt.execute('return load(...)',text) is not None
        for bad in('emu.write','io.open','emu.loadState','emu.saveState','emu.reset','require('):assert bad not in text,bad
        q=Factory.bindings(raw,form)
        assert q['sha']==F.PIN and len(q['packet_pages'])==13
        rows.append(dict(form=form,Lua_SHA256=F.H(text.encode()),bytes=len(text),hooks=len(q['hooks']),source_policy_SHA256=q['source_policy_SHA256']))
    for image in(F.C.inverse(raw),raw[:-1],raw[:100]+bytes([raw[100]^1])+raw[101:]):
        try:Factory.bindings(image,'sonic')
        except AssertionError:pass
        else:raise AssertionError('Native factory accepted unknown/dirty/parent role')
    return dict(passed=True,ROM_SHA256=F.PIN,factory_SHA256=F.H(Path(Factory.__file__).read_bytes()),rows=rows,wrong_roles_rejected=3,outputs=0)


def run(raw,form='sonic',limit=900):
    pack=compile_pack(raw);q=Factory.bindings(raw,form);m,cold=F.cold(raw,form)
    rt=Mock.LuaRuntime(unpack_returned_tuples=True);rt.execute(Mock.MOCK)
    host=rt.globals().host;host.env['SMB_STDOUT_ROM_SHA']=F.PIN
    callbacks=set();counts=Counter();cpu_now=[None]
    def read(at,kind):
        at=int(at)
        if kind==3:return m.ram[at//8192][at&8191]
        if kind==2:return raw[16+at]
        return m[at]
    def mapped(pc):
        pc=int(pc)
        if pc<0x8000:return rt.table_from(dict(address=pc,memType=99))
        tag=m.rawtags[(pc-0x8000)//8192]
        return rt.table_from(dict(address=(tag&127)*8192+(pc&8191),memType=2 if tag&128 else 3))
    # Actual callback registrations remain the production Lua's functions.
    oldadd=rt.globals().emu.addMemoryCallback
    def add(fn,kind,first,last=None):
        if kind==1:callbacks.update(range(int(first),int(first if last is None else last)+1))
        return oldadd(fn,kind,first,last)
    def getstate():
        c=cpu_now[0];assert c is not None
        return rt.table_from({'cpu.pc':c.pc,'cpu.sp':c.sp,'cpu.ps':c.p,'cpu.a':c.a,'cpu.x':c.x,'cpu.y':c.y})
    rt.globals().emu.read=read;rt.globals().emu.convertAddress=mapped;rt.globals().emu.getState=getstate;rt.globals().emu.addMemoryCallback=add
    rt.execute('function emu.setInput(p,port)assert(port==0);host.pad=p;host.input_count=(host.input_count or 0)+1 end')
    text=Factory.controller(raw,form);needle='local boot=coroutine.create(function()'
    assert text.count(needle)==1
    fixture=text.replace(needle,"SONIC_SOURCE_START=function()for n in pairs(H)do auth(n)end;headers();assert(identity());game=true end\n"+needle)
    rt.execute(fixture);rt.execute('SONIC_SOURCE_START()')
    baseCPU=F.N.NesMPU;baseWrite=type(m).__setitem__
    def write(self,at,value):
        if self is m and isinstance(at,int):
            if at==0x4016 and value&1:
                host.event(1);p=host.pad;m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if p[name])
            if at==q['ram']['Square2SoundQueue']:
                for c in list(host.callbacks.values()):
                    if c['kind']==2 and c['first']<=at<=c['last']:c['fn'](at,value)
        return baseWrite(self,at,value)
    class CPU(baseCPU):
        def step(self):
            cpu_now[0]=self
            if self.pc in callbacks:
                counts['callback_dispatches']+=1;host.exec(self.pc,self.sp)
            return super().step()
    error=None
    try:
        with patch.object(F.N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
            for _ in range(limit):
                F.Frames.frame(m,whole_pass=True)
                if host.status is not None:break
    except Exception as e:error=repr(e)
    receipt,lines=(Mock.result(rt)if host.status is not None else(None,[]))
    assert error is None and receipt and receipt['passed']and host.status==0,(error,receipt,F.state(m))
    assert receipt['pending']==0 and receipt['terminal']['lives']==3 and receipt['terminal']['rings']==5
    assert receipt['collected'][0]['boxes']and receipt['collected'][0]['item']['state']==6
    out=dict(passed=True,ROM_SHA256=F.PIN,form=form,pack=pack,cold=cold,native_body_receipt=receipt,
        counts=dict(counts),compiled_source_fixture_SHA256=F.H(fixture.encode()),production_Lua_SHA256=F.H(text.encode()),
        source_SHA256=F.H(Path(__file__).read_bytes()),scope='Production read-only observer functions and controls over actual f7 CPU after genuine compiled cold. Source-only activation exposes game=true after authentic readbacks; no native/physical timing or boot-coroutine claim.',outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compile',action='store_true');p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Source callback gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw=F.load_current_image();q=compile_pack(raw)if a.compile else run(raw,a.form)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
