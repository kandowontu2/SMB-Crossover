"""Finite currentbc5 observer binding and ordinary CPU callback checks, zero files."""
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_contra_force_current_idle_1115 as F

C,W,N,P=F.C,F.W,F.N,F.P


def strict(raw):
    q=F.metadata(raw);rejects=[]
    for name,image in(('parent67',C.inverse(raw)),('truncated',raw[:-1]),('unknown',bytes(len(raw)))):
        try:F.controller(image)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Non-current image accepted',name))
    for name,at in(('hot118',C.FILE),('live108',C.FILE+118),('CFcookie',W.location(P.bindings(raw)['bundle'],'CfExternalCookie')),
        ('CFcarrier',P.CHR+935*1024),('Prince',535471),('unowned',100)):
        image=bytearray(raw);image[at]^=1
        try:F.controller(bytes(image))
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Dirty image accepted',name))
    try:F.controller(raw,'smith')
    except AssertionError:rejects.append('ungranted_identity_smith')
    else:raise AssertionError('Observer widened to another class')
    q.update(strict_rejections=rejects,compiled_Lua=True,source_callback_gate_pending=True)
    return q


def callbacks(raw,complete=False):
    info=strict(raw);m=P.cold(raw);rt=F.Clock.Frozen.LuaRuntime(unpack_returned_tuples=True)
    memory=defaultdict(list);events=defaultdict(list);ctx=dict(cpu=None,status=None,receipt=None)
    api=rt.table();api.memType=rt.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=rt.table_from(dict(exec=0,read=1));api.eventType=rt.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at&8191]
        if kind==2:return raw[16+at]
        return m[at]
    def mapped(pc):
        if pc<0x8000:return None
        tag=m.rawtags[(pc-0x8000)//8192]
        return rt.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(pc&8191)))
    def state():
        c=ctx['cpu'];return rt.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')})
    def add(fn,kind,lo,hi=None):
        assert kind in(0,1)
        for pc in range(lo,(hi if hi is not None else lo)+1):memory[kind,pc].append(fn)
    def pad(buttons,port):
        assert port==0
        m.controller_pad=sum(v for n,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if buttons[n])
        assert m.controller_pad in(0,1),'Only idle or ordinary Right in source gate'
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line[19:])
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=pad
    api.addMemoryCallback=add;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    rt.globals().emu=api;rt.globals().print=emit;rt.globals().CPU_CONTROLLER_OPENING=True
    # This source-only export exposes observer counters; the native text is
    # byte-identical up to this appended read-only test export.
    rt.execute(F.controller(raw)+"\nCF_SOURCE_VIEW=function()return{Main_entries=mainEntries,Main_returns=mainReturns,worker_entries=workerEntries,worker_returns=workerReturns,services=nativeServices,pendingMain=not not pendingMain,pendingWorker=not not pendingWorker,pendingNative=not not nativePending,phase=phaseIndex}end")
    base=N.NesMPU;bus_read=type(m).__getitem__;port_reads=0
    class Observed(base):
        def step(self):
            ctx['cpu']=self
            for fn in tuple(memory[0,self.pc]):fn()
            ctx['CPU_read']=True
            try:return super().step()
            finally:ctx['CPU_read']=False
    def observe_read(bus,at):
        nonlocal port_reads
        if isinstance(at,int)and at in(0x4016,0x4017)and ctx.get('CPU_read'):
            port_reads+=1
            for fn in tuple(memory[1,at]):fn()
        return bus_read(bus,at)
    with patch.object(N,'NesMPU',Observed),patch.object(type(m),'__getitem__',observe_read):
        for tick in range(80 if complete else 6):
            for fn in tuple(events[0]):fn()
            P.Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            P.empty(m)
            if ctx['status']is not None:
                assert complete and ctx['status']==0,ctx
                break
        else:assert not complete,'Source observer completion bound'
    view=rt.globals().CF_SOURCE_VIEW();services={name:{k:int(view['services'][name][k])for k in('entries','returns')}for name in('CfNativeInput','CfNativeBody')}
    expected=66 if complete else 6
    assert view['Main_entries']==view['Main_returns']==expected
    assert view['worker_entries']==view['worker_returns']==expected-1
    assert all(q['entries']==q['returns']==expected-1 for q in services.values()),services
    assert not any(view[n]for n in('pendingMain','pendingWorker','pendingNative'))
    assert view['phase']==(3 if complete else 1)and port_reads>0
    if complete:
        assert ctx['receipt']['passed']and[len(ctx['receipt']['phases'])]==[2]
        assert[q['Main_returns']for q in ctx['receipt']['phases']]==[48,16]
    info['source_callback_gate_pending']=False
    return dict(metadata=info,source_scheduler_iterations=tick+1,actual_Main_entries_returns=expected,
        actual_CF_movement_entries_returns=expected-1,actual_RAM1_services=services,actual_CPU_port_reads=port_reads,
        native_observer_text_unchanged_before_test_export=True,actual_mapped_PC_SP_returns_all_acknowledged=True,
        bounded_callback_gate=True,whole64update_observer_completed_in_source=complete,
        source_observer_receipt=ctx['receipt']if complete else None,
        no_physical_cadence_or_literal_miss_result_claimed=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','callbacks','complete'));a=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==F.PIN
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No mutable Nightly reread after capture'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Source observer checker attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q=strict(raw)if a.mode=='strict'else callbacks(raw,a.mode=='complete')
    q.update(mode=a.mode,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
