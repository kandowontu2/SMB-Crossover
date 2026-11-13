"""Run the same readonly Ladder Lua decisions on actual Main/NMI; stdout only."""

import argparse
from collections import defaultdict
import json
from unittest.mock import patch

import replay_karnov_ladder_native_1113 as Replay
import check_roster_powerup_continuation_1110 as Frames
from check_ff_stdout_controller_source_1110 import LuaRuntime

N,W=Replay.Roster.N,Replay.Roster.W


def opening(raw):
    bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,7)
    W.UI.key(m,32);assert W.UI.menu_name(m)[0]=='KARNOV'
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    idle=W.address(bundle,'IdleLoop')
    for update in range(480):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'SelectedCharacter')==34 and N.get(m,'FmAlts')&1
            assert(N.get(m,'Player_X_Position'),N.get(m,'Player_Y_Position'))==(40,176)
            return m,update
        m.controller_pad=0;W.clear_logs(m);N.consume(m)
        cpu=N.NesMPU(memory=m,pc=idle);cpu.sp,cpu.p=255,0x31;cpu.stPushWord(0xe33b)
        for _ in range(4_000_000):
            if(cpu.pc,cpu.sp)==(idle+12,252):break
            assert m[cpu.pc],('Cold BRK',hex(cpu.pc));cpu.step()
        else:raise AssertionError(('Cold frame bound',hex(cpu.pc)))
    raise AssertionError('Native active ingress bound')


def run(*,limit=2400,return_model=False):
    raw,text,proof=Replay.factory();m,startup=opening(raw)
    lua=LuaRuntime(unpack_returned_tuples=True)
    callbacks={0:defaultdict(list),1:defaultdict(list)};events={};context=dict(cpu=None,exit=None,receipt=None)
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    emu.callbackType=lua.table_from(dict(exec=0,write=1));emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        if kind==1:return m.ram[at//8192][at%8192]
        if kind==2:return raw[16+at]
        if kind==3:return m.vram[at&0x3fff]
        assert kind==0,kind
        return m[at]
    def mapped(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def get_state():
        cpu=context['cpu']
        return lua.table_from({f'cpu.{k}':getattr(cpu,k)if cpu else 0 for k in('pc','sp','a','x','y')})
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[name])
    def add_memory(fn,kind,lo,hi=None):
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[kind][at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):context['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    emu.read,emu.convertAddress,emu.getState,emu.setInput=read,mapped,get_state,set_input
    emu.addMemoryCallback=add_memory;emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    emu.stop=lambda code:context.update(exit=code)
    lua.globals().emu=emu;lua.globals().print=emit;lua.globals().CPU_KARNOV_LADDER_OPENING=True
    lua.globals().os.getenv=lambda name:proof['fixture_SHA256']if name=='SMB_STDOUT_ROM_SHA'else None
    lua.execute(text)
    parent=N.NesMPU
    class Observed(parent):
        def step(self):
            context['cpu']=self
            for fn in tuple(callbacks[0].get(self.pc,())):fn()
            return parent.step(self)
    static=(bytes(m.ram[3]),bytes(m.ram[2][0x900:0x1000]),bytes(m.ram[2][0x1600:0x1e00]))
    with patch.object(N,'NesMPU',Observed):
        for tick in range(limit):
            events[0]();Frames.frame(m)
            # The shared frame harness stops on arrival at IdleLoop+12,
            # before executing it. Native Mesen executes that return hook;
            # dispatch it once using the actual arrived CPU/SP, without
            # executing an extra game instruction or changing any state.
            endpoint=context['cpu']
            assert(endpoint.pc,endpoint.sp)==(W.address(m.bundle,'IdleLoop')+12,252)
            for fn in tuple(callbacks[0].get(endpoint.pc,())):fn()
            events[1]()
            assert static==(bytes(m.ram[3]),bytes(m.ram[2][0x900:0x1000]),bytes(m.ram[2][0x1600:0x1e00]))
            if context['exit']is not None:break
    report=dict(proof,passed=context['exit']==0,actual_menu_startup_updates=startup,
        actual_Main_NMI_controller_updates=tick+1,receipt=context['receipt'],immutable_source_code=True,
        Mesen_run=False,CPU_menu_title_navigation_skipped_after_actual_Select_Start=True,
        no_runtime_fixture_writes_after_confirmation=True,source_ROM_and_controller_factory_frozen=True,
        fallback={n:N.get(m,n)for n in('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_State','NumberofLives')},
        source_fallback=list(m.ram[2][0x5e:0x69]))
    if context['receipt']is not None and report['passed']:
        assert len(report['receipt']['pickups'])==5
    return(report,m)if return_model else report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=2400)
    args=p.parse_args();result=run(limit=args.limit)
    print(json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],'Readonly native-controller CPU route did not finish'
