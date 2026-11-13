"""Passive short-stall observation over the frozen d6 Karnov controller."""
import argparse
from hashlib import sha256
import json

import replay_karnov_ladder_native_suffix_1113 as Frozen

BASE='d6d0f47e1d7cf1d6544073c0937835d7b520a80bb6b2aa56614e406b9cf09a44'
SOURCE=Frozen.SOURCE.with_name('karnov_ladder_suffix_diagnostic_1113.lua')


def controller(raw):
    text=Frozen.controller(raw);assert sha256(text.encode()).hexdigest()==BASE
    b=dict(Frozen.Frozen.Late.Native.W.Symbols.bundle(),raw=raw)
    prefix='local DIAG_PAD1='+str(Frozen.Frozen.Late.Native.W.address(b,'SavedJoypad1Bits'))+'\n'
    point='local function mapped(pc,physical)'
    assert text.count(point)==1
    text=text.replace(point,SOURCE.read_text()+'\n'+point)
    point='native_blast_contacts=blastCalls,fifth=stockFifth'
    assert text.count(point)==1
    text=text.replace(point,point+',native_suffix=stockFifth.native_suffix,native_suffix_diagnostic=stockFifth.native_suffix_diagnostic')
    text=prefix+text
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    Frozen.Frozen.Late.LuaRuntime().compile(text)
    return text


def observer_check():
    """Synthetic observer-only gate/return tests, not seeded gameplay tests."""
    prefix=r'''
local game,done,frame,epoch=true,false,0,0
local pickups={1,2,3,4};local armed,undergroundReady=true,true
local routePhase,routeAge='travel',17;local early={stage='head'}
local stockFifth={stage='travel'};local L={GameLoop=0};local FORCE_SETTLE=false;local DIAG_PAD1=100
local registers={WorldNumber=0,LevelNumber=1,AreaType=2,Player_State=0,Player_Y_Position=176,Player_X_Position=353,Player_PageLoc=0}
local work={};local callbacks={};local stopped=nil
local function r(name)return registers[name]or 0 end
local function kr(at)return work[at]or 0 end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function actor(i)return{slot=i,flag=0,id=0,x=0,y=0,state=0,kind=0}end
local function state()return{x=wx(),y=r('Player_Y_Position'),frame=frame}end
local function tile(x,y)return 0 end
local function finish(ok,why)stopped={ok=ok,why=why};done=true end
local emu={memType={nesDebug=0,nesWorkRam=1,nesPrgRom=2},callbackType={exec=0},eventType={endFrame=1}}
emu.read=function()return 0 end;emu.addMemoryCallback=function()end
emu.addEventCallback=function(fn,kind)callbacks[kind]=fn end
'''
    tail=r'''
return function(count,world,level,area,isarmed,bomb,x,y,ground,wasdone)
 pickups={};for i=1,count do pickups[i]=i end
 registers.WorldNumber=world;registers.LevelNumber=level;registers.AreaType=area
 registers.Player_X_Position=x;registers.Player_PageLoc=0;registers.Player_Y_Position=y
 registers.Player_State=ground and 0 or 2;armed=isarmed;work[0xc0]=bomb
 nav.done=wasdone;nav.stage='unstarted';nav.returns=0;nav.since=0;nav.bypassed=nil
 local handled,pad=nativeSuffixControl(x,y,ground,nil)
 return handled,pad,nav.done,nav.stage,control()
end
'''
    native=Frozen.SOURCE.read_text()
    stub='\nlocal function control()return 73 end\n'
    old=Frozen.Frozen.Late.LuaRuntime(unpack_returned_tuples=True).execute(prefix+native+stub+tail)
    runtime=Frozen.Frozen.Late.LuaRuntime(unpack_returned_tuples=True)
    new=runtime.execute(prefix+native+stub+SOURCE.read_text()+tail)
    cases=[(4,0,1,2,True,0,353,176,True,False)]
    for index,value in((0,3),(1,1),(2,0),(3,1),(4,False),(5,128),(6,350),(6,417),(7,96),(8,False),(9,True)):
        case=list(cases[0]);case[index]=value;cases.append(tuple(case))
    for case in cases:assert old(*case)==new(*case),case
    # Separate VM: the only terminal change must be the requested180-frame bound.
    probe=r'''
for i=1,200 do frame=i;callbacks[1]()end
assert(stopped and not stopped.ok and stopped.why=='passive-diagnostic-wall-stall180')
assert(navDiagnostic.stall_frames==180 and #navDiagnostic.samples==12)
assert(#navDiagnostic.wall_last.actors==6)
assert(control()==73)
return true
'''
    assert runtime.execute(prefix+native+stub+SOURCE.read_text()+probe)
    return dict(synthetic_observer_only=True,gate_return_parity=len(cases),control_pad_unchanged=True,
        stop_after_physical_frames=180,max_samples=12,wall_actor_slots=6,runtime_or_input_writes=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-check',action='store_true');args=p.parse_args()
    raw=Frozen.Frozen.Late.Feature.Owner.NIGHTLY.read_bytes();text=controller(raw)
    print(json.dumps(dict(ROM_SHA256=Frozen.PIN,base_SHA256=BASE,controller_SHA256=sha256(text.encode()).hexdigest(),
        bytes=len(text),Lua_compile=True,input_changes=0,runtime_writes=0,outputs=0,Mesen_run=False,
        observer_check=observer_check()if args.self_check else None)),flush=True)
