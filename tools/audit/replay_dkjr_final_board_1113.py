"""Separate final-girder boarding controls; frozen universal stairs unchanged."""
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
import sys

import replay_dkjr_stair_geometry_turn_1113 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

T,Gate=Previous.T,Previous.Gate
LUA_PIN='34390aca9d1965190782de6aac1369c2346ea85653910e4cbf872da76f6d32e3'
EARLY_LUA_PIN='34bdb799a4bc9c28833997a22e7c94e8454dc5f36969f23159f92a2358eefc2b'


def controller(raw):
    text=Previous.controller(raw)
    assert sha256(text.encode()).hexdigest()==Previous.LUA_PIN
    at=16+71*8192+0xc18
    assert raw[at:at+2]==bytes.fromhex('85bd')
    marker='local function drive()\n'
    capture='''local finalNativePassenger
emu.addMemoryCallback(guarded('actual final girder passenger',function()
 if not active()or not mapped(0xac18,'nesPrgRom',71*8192+0xc18)then return end
 local cpu=emu.getState();local slot=cpu['cpu.x'];local birth=births['3040']
 if not birth or slot~=birth.slot or pos(0x76,0x5d,slot)~=3040 then return end
 assert(read(0x10+slot)==1 and read(0x17+slot)==0x25 and read(0x646+slot)==5,
  'Original final vertical helper at native Y position')
 assert(read(0x566+slot)==slot and cpu['cpu.a']+32==read(0xbe+slot),
  'Actual final native passenger selection and pending Y store')
 finalNativePassenger={Main=updates,slot=slot,top=read(0xbe+slot),pending_y=cpu['cpu.a'],x=x()}
end),emu.callbackType.exec,0xac18)
local function finalSupport(top)
 local p=finalNativePassenger;local birth=births['3040']
 if not p or not birth or p.slot~=birth.slot or p.Main~=updates or p.top~=top then return false end
 if read(0x566+p.slot)~=p.slot or read(0xbd)~=p.pending_y or ram(2,0x6b)~=1 or ram(2,0x210)~=read(0xbd)+15 then return false end
 local a=0x65c+4*p.slot
 local playerLeft,playerRight=read(0x658),read(0x65a)
 local left,right=read(a),read(a+2)
 assert(right-left==32,'Original32px final helper collision width')
 return playerLeft>=left and playerRight<=right
end
'''
    text=T.P.once(text,marker,capture+marker)
    start=text.index(" if phase=='final-cap'then\n")
    end=text.index(" if phase=='final-depart'then\n",start)
    old=text[start:end]
    assert "right=player<stairDown+27"in old and "if onStairDown then setPhase('final-lower',stairTop)end"in old
    new=''' if phase=='final-cap'then
  right=player<stairDown-2
  if player>=stairDown-2 and stairTop and priorTop[stairDown]and
   stairTop>=80 and stairTop<=92 and stairTop>=priorTop[stairDown]and
   ram(2,0x6b)==1 and ram(2,0x6c)==1 then
   hold=0;setPhase('final-board',stairTop)
  end
 end
 if phase=='final-board'and stairTop then
  local centerSafe=stairDown+8
  right,left=player<centerSafe,player>centerSafe+1
  if player>=centerSafe and player<=centerSafe+1 and finalSupport(stairTop)then
   right,left=false,false;setPhase('final-lower',stairTop)
   events[#events].native_passenger=finalNativePassenger
  end
 end
 if phase=='final-lower'and stairTop then
  local centerSafe=stairDown+8
  right,left=player<centerSafe,player>centerSafe+1
  if finalSupport(stairTop)and stairTop>=192 and stairTop<=208 and
   priorTop[stairDown]and stairTop>=priorTop[stairDown]then
   right,left=true,false;setPhase('final-depart',stairTop)
  end
 end
'''
    text=text[:start]+new+text[end:]
    LuaRuntime().compile(text)
    if LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def early_controller(raw):
    """Keep ordinary Right through the actual early passenger event."""
    text=controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA_PIN
    body=T.P.T.payload(raw)
    assert body[0xb005-0xa000:0xb009-0xa000]==bytes((7,0,24,15))
    W=Gate.W;b=W.Symbols.bundle();b['raw']=raw
    buffers=[W.address(b,name)for name in('Block_Buffer_1','Block_Buffer_2')]
    at=W.location(b,'MTileAttribute');attrs=raw[at:at+256]
    solids=''.join('1'if v&3==1 else'0'for v in attrs)
    text=T.P.once(text,'local finalNativePassenger','local finalCapCleared\nlocal finalNativePassenger')
    start=text.index(" if phase=='final-cap'then\n");end=text.index(" if phase=='final-board'and stairTop then\n",start)
    new=''' if phase=='final-cap'then
  right=player<stairDown+8
  local p=finalNativePassenger;local birth=births[tostring(stairDown)]
  if p and birth and p.slot==birth.slot and p.Main==updates and p.top==stairTop and
   read(0x566+p.slot)==p.slot and y==p.pending_y and ram(2,0x6b)==1 and ram(2,0x210)==y+15 then
   hold=0;setPhase('final-board',stairTop);events[#events].native_passenger=p
  end
 end
'''
    text=text[:start]+new+text[end:]
    marker=" if phase=='final-board'and stairTop then\n"
    safety=f''' if (phase=='final-cap'or phase=='final-board')and not finalCapCleared then
  local solidKinds='{solids}'
  local column=math.floor((stairDown-1)/16)*16
  local base=((column>>8)&1)==1 and {buffers[1]} or {buffers[0]}
  local capTop
  for top=32,224,16 do
   local tile=read(base+((top-32)&240)+((column>>4)&15))
   if solidKinds:sub(tile+1,tile+1)=='1'then capTop=top;break end
  end
  assert(capTop,'Missing actual final cap column')
  local capRight=column+15
  local bodyLeft=camera()+ram(2,0x213)+7
  local bodyBottom=ram(2,0x210)+15
  if bodyLeft>capRight then
   assert(bodyBottom<capTop,'Cap edge cleared after original body reached solid height')
   finalCapCleared={{Main=updates,left=bodyLeft,bottom=bodyBottom,cap_right=capRight,cap_top=capTop}}
   remember('final-cap-body-clear',stairTop);events[#events].clearance=finalCapCleared
  else assert(bodyBottom<capTop,'Original body entered the old cap before lateral clearance')end
 end
'''
    text=T.P.once(text,marker,safety+marker)
    text=T.P.once(text,"if player>=centerSafe and player<=centerSafe+1 and finalSupport(stairTop)then",
        "if player>=centerSafe and player<=centerSafe+1 and finalSupport(stairTop)and finalCapCleared then")
    LuaRuntime().compile(text)
    if EARLY_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==EARLY_LUA_PIN
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',action='store_true');ap.add_argument('--early',action='store_true');args=ap.parse_args()
    parent,raw=T.load_inputs();text=early_controller(raw)if args.early else controller(raw)
    info=dict(candidate_SHA256=T.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),
        frozen_prefix_Lua_SHA256=Previous.LUA_PIN,compiled=True,
        actual_native_passenger_and_complete_X_overlap=True,lowering_target_worldX=3048,
        source_or_native_writes=False,outputs_written=0,native_qualified=False,early_actual_passenger=args.early)
    if args.route:
        Q,P,H=Gate.Q,Gate.P,Gate.H;e73=T.Old.reverse(parent)
        _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
        updates=0;output=sys.stdout
        def after(mem):
            nonlocal updates
            updates+=1
            if updates%1500==0:print('DKJR_FINAL_BOARD_PROGRESS '+json.dumps(dict(Main=updates,final=P.B.state(mem)),separators=(',',':')),file=output,flush=True)
        with redirect_stdout(io.StringIO()):result=P.B.route(m,raw,12000,controller_text=text,after_frame=after)
        receipt=result.get('receipt')or{}
        info.update(passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
            reason=receipt.get('reason'),last_events=receipt.get('events',[])[-18:],
            receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            physical_cadence_claim=False)
    print('DKJR_FINAL_BOARD '+json.dumps(info,separators=(',',':')),flush=True)
    if args.route:assert info['passed'],info


if __name__=='__main__':main()
