"""Zero-output strict bindings and original-CPU ordinary image-route components.

The peripheral model has no renderer: its PNG is a marked API fixture only.
Root's actual Mesen PNGs and register writes remain the graphics witness.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch

import replay_shared_world_sprite_images_1114 as Factory
import check_bub_current_budget_1113 as Frames
import run_stdout_mesen_1110 as Native

W,N=Factory.W,Factory.N


def strict_metadata(raw,key):
    original=Path.read_bytes
    def read(p):
        assert p.resolve()!=Factory.ROM.resolve(),'Mutable nightly reread'
        return original(p)
    def forbid(*a,**kw):raise RuntimeError('Readonly checker attempted file output/Mesen')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid):
        q=Factory.metadata(raw,key);rejects=[]
        changed=bytearray(raw);changed[16+8192]^=1
        for name,wrong in(('truncated',raw[:-1]),('dirty_unowned',bytes(changed)),
            ('parent_fa66',Factory.Frozen.normalize(raw).fa66),('parent12397',Factory.Frozen.normalize(raw).postbg)):
            try:Factory.controller(wrong,key)
            except AssertionError:rejects.append(name)
            else:raise AssertionError(('Wrong input accepted',name))
        q.update(rejections=rejects,mutable_nightly_rereads=0,file_and_Mesen_traps=True)
        return q


def cold(raw,key,bus_class=None):
    c=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',bus_class or W.ControllerBus):m=W.UI.seed(b,0)
    for bits in c['navigation']:W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]==c['name']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'SelectedCharacter')==c['owner']
            assert N.get(m,'Player_X_Position')==40 and N.get(m,'Player_PageLoc')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual native constructor bound')


def mode_writers(raw,key):
    """Actual cold/menu/constructor/Main writers, with current CPU/map identity."""
    c=Factory.bindings(raw,key);base=N.NesMPU;ctx=dict(cpu=None,pc=-1,calls=[])
    modes=c['ram']['X5ChrMode'];banks=c['ram']['CurrentCHRBank'];counts=defaultdict(int);first={};recent=[]
    class CPU(base):
        def step(self):
            ctx['cpu']=self;ctx['pc']=self.pc
            if self.memory[self.pc]==0x20:
                tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                ctx['calls'].append(dict(tag=tag,PC=self.pc,target=self.memory[self.pc+1]+256*self.memory[self.pc+2]))
                if len(ctx['calls'])>8:ctx['calls'].pop(0)
            return super().step()
    class Bus(W.ControllerBus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and(modes<=at<modes+12 or banks+1<=at<banks+4):
                p=ctx['cpu'];pc=ctx['pc']
                tag=self.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                stamp=(tag,pc,at,value&255);counts[stamp]+=1
                row=dict(tag=tag,PC=pc,field='mode'if modes<=at<modes+12 else'bank',window=at-(modes if modes<=at<modes+12 else banks),value=value&255,
                    old=self[at],selected=N.get(self,'SelectedCharacter'),menu=N.get(self,'CrossoverMenuState'),
                    x=p.x if p else-1,y=p.y if p else-1,
                    instruction=bytes(self[pc+i]for i in range(3)).hex()if pc>=0 else'',
                    recent_actual_JSR=list(ctx['calls']))
                if stamp not in first:
                    assert len(first)<128,'Bounded actual writer identities';first[stamp]=row
                recent.append(row)
                if len(recent)>12:recent.pop(0)
            return super().__setitem__(at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU):
        m=cold(raw,key,Bus)
        for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    rows=[dict(**first[k],count=v)for k,v in sorted(counts.items())]
    return dict(ROM_SHA256=Factory.PIN,identity=key,actual_cold_menu_constructor_and4neutral_Main=True,
        writers=rows,recent=recent,final_modes=list(m[modes:modes+12]),
        final_banks=[N.get(m,'CurrentCHRBank',i)for i in range(12)],
        actual_latched_banks=m.chr_latches,source_CPU_only=True,renderer=False,Mesen_run=False,outputs=0)


def run(raw,key,limit=1600):
    began=time.perf_counter();meta=strict_metadata(raw,key);text=Factory.controller(raw,key);m=cold(raw,key)
    lua=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True)
    callbacks={0:defaultdict(list),1:defaultdict(list)};events=defaultdict(list)
    ctx=dict(cpu=None,status=None,receipt=None,images=0);hardware_oam=bytearray([248,0,0,0]*64)
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesSpriteRam=3,nesPpuDebug=4,nesChrRom=5))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return hardware_oam[at]
        if kind==4:return m.vram[at]
        if kind==5:return raw[1048592+at]
        assert kind==0;return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def state():
        c=ctx['cpu'];return lua.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')})
    def inputs(pad,port):
        assert port==0
        m.controller_pad=sum(v for k,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[k])
    def memory(fn,kind,lo,hi=None):
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[kind][at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
        elif line.startswith('SMB_NATIVE_IMAGE '):ctx['images']+=1
    api.read=read;api.convertAddress=mapped;api.getState=state;api.setInput=inputs
    api.addMemoryCallback=memory;api.addEventCallback=lambda fn,kind:events[kind].append(fn)
    api.stop=lambda status:ctx.update(status=status)
    # No pixels are rendered or claimed. Exercise bounded PNG/base64 plumbing.
    api.takeScreenshot=lambda:b'\x89PNG\r\n\x1a\nSOURCE-API-FIXTURE'
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text)
    # Expose the established CPU fixture's latched peripheral starting state.
    # This is explicitly not an observed console startup or art witness.
    for fn in callbacks[1][0x2000]:fn(0x2000,m.ppuctrl)
    for fn in callbacks[1][0x5101]:fn(0x5101,m[0x5101])
    for i,bank in enumerate(m.chr_latches[:8]):
        for fn in callbacks[1][0x5130]:fn(0x5130,bank>>8)
        for fn in callbacks[1][0x5120+i]:fn(0x5120+i,bank&255)
    for fn in callbacks[1][0x5130]:fn(0x5130,m.upper)
    old_bus=type(m);old_cpu=N.NesMPU
    class Bus(old_bus):
        def __setitem__(self,at,value):
            if isinstance(at,int):
                for fn in tuple(callbacks[1].get(at,())):fn(at,value)
                if at==0x4014:hardware_oam[:]=bytes(self[(value&255)*256+i]for i in range(256))
            return super().__setitem__(at,value)
    class CPU(old_cpu):
        def step(self):
            ctx['cpu']=self
            for fn in tuple(callbacks[0].get(self.pc,())):fn()
            return super().step()
    def forbid(*a,**kw):raise RuntimeError('Source route attempted file output/Mesen')
    m.__class__=Bus
    try:
        with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid),patch.object(N,'NesMPU',CPU):
            for tick in range(limit):
                for fn in tuple(events[0]):fn()
                Frames.frame(m,whole_pass=True)
                for fn in tuple(events[1]):fn()
                if ctx['status']is not None:break
                if tick%250==249:print(json.dumps(dict(progress=key,Main=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),actors=[N.get(m,'Enemy_ID',i)for i in range(6)if N.get(m,'Enemy_Flag',i)])),flush=True)
    finally:m.__class__=old_bus
    q=ctx['receipt']or{};shots=q.get('shots',[])
    return dict(passed=ctx['status']==0,identity=key,metadata=meta,source_Main_passes=tick+1,
        seconds=round(time.perf_counter()-began,2),source_receipt_SHA256=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        reason=q.get('reason'),first=q.get('first'),birth=q.get('mushroom_birth'),terminal=q.get('terminal'),
        route_events=q.get('events'),images=ctx['images'],shots=[dict(tag=s['tag'],state=s['state'],target=s['target'],
            sprite_height=s['sprite_height'],PPUCTRL=s['ppu_control'],MMC5_CHR_mode=s['MMC5_CHR_mode'],
            actual_sprite_banks=s['actual_sprite_banks'],software_CHR=s['software_CHR'],palette=s['palette'],
            actual_OAM=s['actual_OAM'])for s in shots],
        gameplay_seeds=0,outputs=0,Mesen_run=False,renderer=False,
        scope='Compiled menu/Select/Start/parser and actual CPU route only. Initial mapper peripheral values and PNG API fixture are model infrastructure, not console graphics or raster evidence.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');p.add_argument('--writers',action='store_true');p.add_argument('--limit',type=int,default=1600)
    a=p.parse_args();raw=Factory.ROM.read_bytes();q=mode_writers(raw,a.identity)if a.writers else strict_metadata(raw,a.identity)if a.metadata else run(raw,a.identity,a.limit)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata and not a.writers:assert q['passed'],'Ordinary image-route source component did not pass'
