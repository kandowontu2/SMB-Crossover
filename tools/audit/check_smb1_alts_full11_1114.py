"""Zero-output genuine compiled Select/Start and full routes on strict421."""
import argparse
from collections import defaultdict,deque
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch

import replay_smb1_alts_full11_1114 as Factory
import check_bub_current_budget_1113 as Frames
import run_stdout_mesen_1110 as Native
from check_ff_stdout_controller_source_1110 import LuaRuntime

W,N=Factory.W,Factory.N


def strict_metadata(raw,key):
    original=Path.read_bytes
    def read(path):
        assert path.resolve()!=Factory.ROM.resolve(),'Mutable nightly reread after initial input load'
        return original(path)
    def forbid(*a,**kw):raise RuntimeError('Readonly metadata attempted file output/Mesen')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid):
        q=Factory.metadata(raw,key);rejects=[]
        changed=bytearray(raw);changed[16+8192]^=1
        for label,wrong in(('truncated',raw[:-1]),('unowned_physics_byte',bytes(changed)),
            ('parent_fa66',Factory.normalize(raw).fa66),('parent12397',Factory.normalize(raw).postbg)):
            try:Factory.controller(wrong,key)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong ROM accepted',label))
        q.update(strict_rejections=rejects,mutable_nightly_rereads=0,file_and_Mesen_traps=True)
        return q


def cold(raw,key):
    config=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(config['cycle']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==config['name']
    assert N.get(m,'SelectedCharacter')==0 and N.get(m,'MarioVariant')==config['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'MarioVariant')==config['variant']
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Native constructor bound')


def run(raw,key,limit=8500):
    began=time.perf_counter();info=strict_metadata(raw,key);text=Factory.controller(raw,key);m=cold(raw,key)
    runtime=LuaRuntime(unpack_returned_tuples=True);callbacks=defaultdict(list);events=defaultdict(list)
    ctx=dict(cpu=None,pc=0,cycles=0,status=None,receipt=None);pads=set();recent=deque(maxlen=48)
    api=runtime.table();api.memType=runtime.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=runtime.table_from(dict(exec=0));api.eventType=runtime.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==2:return raw[16+at]
        if kind==1:return m.ram[at//8192][at%8192]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return runtime.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def state():
        c=ctx['cpu'];q={f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')}
        q['cpu.pc']=ctx['pc'];q['cpu.ps']=q['cpu.p'];q['cpu.cycleCount']=ctx['cycles']
        return runtime.table_from(q)
    def input(pad,port):
        assert port==0
        m.controller_pad=sum(v for k,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[k])
        pads.add(m.controller_pad)
    def memory(fn,kind,lo,hi=None):
        assert kind==0
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=input
    api.addMemoryCallback=memory;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    runtime.globals().emu=api;runtime.globals().print=emit;runtime.globals().CPU_CONTROLLER_OPENING=True
    runtime.execute(text)
    base=N.NesMPU
    class Observed(base):
        def step(self):
            ctx['cpu']=self;ctx['pc']=self.pc
            for fn in tuple(callbacks.get(self.pc,())):fn()
            before=self.processorCycles;q=super().step();ctx['cycles']+=self.processorCycles-before
            return q
    def forbid(*a,**kw):raise RuntimeError('Readonly source route attempted file output/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid),patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            for fn in tuple(events[0]):fn()
            Frames.frame(m,whole_pass=True)
            for fn in tuple(events[1]):fn()
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            if x>=2360 and tick%8==0:
                recent.append(dict(Main=tick+1,x=x,y=N.get(m,'Player_Y_Position'),state=N.get(m,'Player_State'),
                    vx=N.get(m,'Player_X_Speed'),vy=N.get(m,'Player_Y_Speed'),pad=m.controller_pad,
                    size=N.get(m,'PlayerSize')))
            if ctx['status']is not None:break
            if tick%500==499:print(json.dumps(dict(progress_identity=key,Main=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),engine=N.get(m,'GameEngineSubroutine'),power=N.get(m,'PlayerStatus'))),flush=True)
    q=ctx['receipt']or{}
    return dict(passed=ctx['status']==0,identity=key,metadata=info,source_scheduler_passes=tick+1,
        source_receipt_SHA256=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        seconds=round(time.perf_counter()-began,2),controller_pad_values=sorted(pads),receipt=q,
        diagnostic_final_stair=list(recent)if ctx['status']!=0 else[],
        frontend='Compiled menu arena/Select/Start/parser/constructor; bus lacks real vblank, native title/roster authority pending',
        gameplay_seeds=0,physical_APU_video_timing_claim=False,Mesen_run=False,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');args=p.parse_args();raw=Factory.ROM.read_bytes()
    q=strict_metadata(raw,args.identity)if args.metadata else run(raw,args.identity)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Exact stated full route did not pass'
