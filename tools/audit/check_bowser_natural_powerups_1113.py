"""Actual menu/controller/Main/NMI Bowser item route; zero generated files.

The established native-menu CPU arena is the only fixture. After Start no
gameplay fields, actors, gear, coordinates, tiles or cartridge bytes are seeded.
Logical Main/NMI scheduling does not establish physical Mesen cadence.
"""
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
import time
from unittest.mock import patch

import replay_bowser_natural_powerups_1113 as Replay
import check_bub_current_budget_1113 as Frames

W=Replay.Base.W
N=W.N


def cold(raw,identity):
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):
        m=W.UI.seed(b,0)
    for bits in(4,4,4,1,1):W.UI.key(m,bits)
    assert N.get(m,'CrossoverMenuIndex')==26 and N.get(m,'SelectedCharacter')==27
    if identity:W.UI.key(m,32)
    assert bool(N.get(m,'FmAlts')&8)==bool(identity)
    menu=W.UI.menu_name(m)[0]
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for epoch in range(700):
        assert N.get(m,'SelectedCharacter')==27 and N.get(m,'NumberofLives')==2
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.ram[3][0x1e26]==183
            return m,dict(menu=menu,identity=identity,epoch=epoch,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                y=N.get(m,'Player_Y_Position'),tier=m.ram[3][0x1e28],health=m.ram[3][0x1e29],
                actual_grid=[4,4,4,1,1],Select_presses=identity)
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual native Bowser menu/constructor bound')


def run(raw,identity,limit=5000):
    assert sha256(raw).hexdigest()==Replay.PIN
    began=time.perf_counter();m,opening=cold(raw,identity)
    text=Replay.controller(raw,identity);lua=Replay.Base.LuaRuntime(unpack_returned_tuples=True)
    callbacks=defaultdict(list);events={};context=dict(cpu=None,exit=None,receipt=None);counts=Counter()
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return m.vram[at&0x3fff]
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def get_state():
        c=context['cpu'];return lua.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in('pc','sp','a','x','y','p')})
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[name])
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):context['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    def memory(fn,kind,lo,hi=None):
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    emu.read,emu.convertAddress,emu.getState,emu.setInput=read,mapped,get_state,set_input
    emu.addMemoryCallback=memory;emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    emu.stop=lambda code:context.update(exit=code)
    lua.globals().emu=emu;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text+'\nBOWSER_CPU_REPORT=function()return{natural=natural,s=state(),updates=updates}end\n')
    points={(3 if name.startswith('Bw')else 128|(W.location(m.bundle,name)-16)//8192,
        W.address(m.bundle,name)):name for name in('BwMovement','BwPickup','BwPowerupTick','PowerUpObjHandler',
        'NrPickupCollision','HandlePowerUpCollision','NativeRarePlayerHeadCollisionCore')}
    parent=N.NesMPU
    class Observed(parent):
        def step(self):
            context['cpu']=self
            if self.pc>=0x8000:
                point=(m.rawtags[(self.pc-0x8000)//8192],self.pc)
                if point in points:counts[points[point]]+=1
            for fn in tuple(callbacks.get(self.pc,())):fn()
            return parent.step(self)
    with patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            events[0]();Frames.frame(m)
            c=context['cpu'];assert(c.pc,c.sp)==(W.address(m.bundle,'IdleLoop')+12,252)
            for fn in tuple(callbacks.get(c.pc,())):fn()
            events[1]()
            if context['exit']is not None:break
            if(tick+1)%500==0:
                print('BOWSER_ITEMS_CPU_PROGRESS '+json.dumps(dict(identity=identity,Main=tick+1,
                    x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
                    tier=m.ram[3][0x1e28],health=m.ram[3][0x1e29])),flush=True)
    def plain(value):
        if hasattr(value,'items'):
            values=dict(value.items())
            if values and all(type(k)is int for k in values):return[plain(values[i])for i in range(1,len(values)+1)]
            return{k:plain(v)for k,v in values.items()}
        return value
    report=plain(lua.globals().BOWSER_CPU_REPORT())
    return dict(passed=context['exit']==0,seconds=round(time.perf_counter()-began,2),identity=identity,
        opening=opening,actual_Main_NMI_updates=tick+1,controller_SHA256=sha256(text.encode()).hexdigest(),
        ROM_SHA256=Replay.PIN,CPU=report,receipt=context['receipt'],native_leaf_counts=dict(counts),
        runtime_field_grants_or_seeds=0,ROM_edits=0,output_files=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',type=int,choices=(0,1),default=0)
    p.add_argument('--limit',type=int,default=5000);p.add_argument('--summary',action='store_true');args=p.parse_args()
    q=run(Replay.Base.ROM.read_bytes(),args.identity,args.limit)
    if args.summary and q['receipt']:
        q['receipt']={key:q['receipt'][key]for key in('passed','reason','return_counts')}
    print(json.dumps(q,separators=(',',':')),flush=True);assert q['passed'],'Natural Bowser item CPU route must qualify'
