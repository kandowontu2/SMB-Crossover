"""Separate full route requiring25 returned healthy grounded1-2 updates."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_oneway_support_1114 as S
from check_ff_stdout_controller_source_1110 import LuaRuntime

PRIVATE_LUA_PIN='7cd0d37d0988bd5695bea00783a5d2a62bbcc56032bca411c862a8fda56ab547'
CURRENT_LUA_PIN='168fe6b3bc0cda81062a470d58872c72bb864c23201454b0797082380fd52f5f'


def strengthen(original):
    once=S.P.once
    declarations='''local undergroundPending
local undergroundCallbacks={}
local undergroundGrounded,undergroundReturned=0,0
local undergroundStart,undergroundFirst,undergroundLast
'''
    text=declarations+original
    old="   setPhase('active-underground-1-2')\n   finish(true,'Donkey Kong Jr. cleared 1-1 and entered active 1-2')\n   return"
    new="   setPhase('settle-underground-1-2')\n   undergroundStart=updates;bits=0\n   return"
    text=once(text,old,new)
    wait=''' if phase=='settle-underground-1-2'then
  bits=0
  assert(read(0x75f)==2 and read(0x0f)~=11 and ram(2,0x6b)~=5,
   'Original fall or native injury during1-2 settling '..json(snapshot()))
  assert(updates-undergroundStart<240,'Bounded1-2 grounding after entrance')
  if undergroundGrounded>=25 then
   assert(active()and read(0x764)==0 and read(0x761)==1 and read(0x753)==2 and
    x()==40 and read(0xbd)==176 and read(0xa4)==1 and read(0x1e)==0 and
    ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==191 and not undergroundPending,
    'Twenty-five actual returned living grounded1-2 updates')
   setPhase('grounded-underground-1-2')
   finish(true,'Donkey Kong Jr. cleared1-1 and survived25 returned grounded1-2 updates')
  end
  return
 end
'''
    text=once(text,'local function drive()\n','local function drive()\n'+wait)
    observer='''emu.addMemoryCallback(guarded('grounded1-2 motor entry',function()
 if phase~='settle-underground-1-2'or not active()or
  not mapped(0xd65e,'nesWorkRam',2*8192+0x165e)then return end
 assert(not undergroundPending,'Nested1-2 source motor')
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 undergroundPending={pc=pc,sp=(sp+2)&255}
 if not undergroundCallbacks[pc]then
  undergroundCallbacks[pc]=true
  emu.addMemoryCallback(guarded('grounded1-2 motor return',function()
   if not undergroundPending then return end
   local q=emu.getState()
   if q['cpu.pc']~=undergroundPending.pc or q['cpu.sp']~=undergroundPending.sp then return end
   undergroundPending=nil;undergroundReturned=undergroundReturned+1
   assert(read(0x75f)==2 and read(0x0f)~=11 and ram(2,0x6b)~=5,
    'Living original1-2 motor return '..json(snapshot()))
   local healthy=active()and read(0x764)==0 and read(0x761)==1 and read(0x753)==2 and
    x()==40 and read(0xbd)==176 and read(0xa4)==1 and read(0x1e)==0 and
    ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==191
   undergroundGrounded=healthy and undergroundGrounded+1 or 0
   if healthy then
    local row=snapshot();row.prior_source=ram(2,0x6c);row.source_y=ram(2,0x210)
    row.native_high=read(0xa4);row.actual_return=undergroundReturned
    row.return_pc=q['cpu.pc'];row.return_sp=q['cpu.sp']
    if undergroundGrounded==1 then undergroundFirst=row end
    undergroundLast=row
   end
  end),emu.callbackType.exec,pc)
 end
end),emu.callbackType.exec,0xd65e)
'''
    text=once(text,"emu.addMemoryCallback(guarded('main',function()",observer+"emu.addMemoryCallback(guarded('main',function()")
    receipt='events=events,grounded_12_return_count=undergroundGrounded,actual_12_returns=undergroundReturned,first_grounded_12_return=undergroundFirst,last_grounded_12_return=undergroundLast,'
    text=once(text,'events=events,',receipt)
    LuaRuntime().compile(text)
    restored=text[len(declarations):]
    restored=once(restored,new,old)
    restored=once(restored,'local function drive()\n'+wait,'local function drive()\n')
    restored=once(restored,observer+"emu.addMemoryCallback(guarded('main',function()","emu.addMemoryCallback(guarded('main',function()")
    restored=once(restored,receipt,'events=events,')
    assert restored==original,'Strengthened controller changed earlier controls/assertions'
    return text


def private_controller(raw):
    b=S.Replay.Gate.W.Symbols.bundle();b['raw']=raw
    assert S.Replay.Gate.W.address(b,'Player_Y_HighPos')==0xa4
    text=strengthen(S.controller(raw))
    if PRIVATE_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==PRIVATE_LUA_PIN
    return text


def current_controller(raw):
    import compose_dkjr_oneway_current_1114 as Current
    b=S.Replay.Gate.W.Symbols.bundle();b['raw']=raw
    assert S.Replay.Gate.W.address(b,'Player_Y_HighPos')==0xa4
    text=strengthen(Current.controller(raw))
    if CURRENT_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==CURRENT_LUA_PIN
    return text


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--current-421',action='store_true');args=ap.parse_args()
    if args.current_421:
        import compose_dkjr_oneway_current_1114 as Current
        raw,_=Current.proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
        text=current_controller(raw)
    else:
        _,parent=S.Replay.load_inputs();raw,_=S.proposal(parent);text=private_controller(raw)
    import compose_dkjr_oneway_current_1114 as Current
    current_adapter=text if args.current_421 else text.replace(S.PIN,Current.PIN,1)
    LuaRuntime().compile(current_adapter)
    print('DKJR_GROUNDED12_CONTROLLER '+json.dumps(dict(ROM_SHA256=sha256(raw).hexdigest(),
        controller_SHA256=sha256(text.encode()).hexdigest(),compiled=True,required_actual_grounded_returns=25,
        current_ROM_identity_adapter_SHA256=sha256(current_adapter.encode()).hexdigest(),
        maximum_settling_Main_updates=240,all_prior_assertions_preserved=True,source_or_native_writes=False,
        outputs_written=0),separators=(',',':')),flush=True)
