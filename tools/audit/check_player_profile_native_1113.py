"""Readonly native MM/Luigi motion regression for the proposed PLAYER compaction."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import audit_current_roster_powerups_1110 as A
from run_stdout_mesen_1110 import run

OUT = Path(__file__).resolve().parents[2]/'build/metal-flower-native-1112'
CASES = {'megaman': (1, 0, 1), 'luigi': (0, 1, 8)}


def controller(raw, case):
    slot, cycle, owner = CASES[case]
    b = dict(A.W.Symbols.bundle(), raw=raw)
    names = ('CrossoverTitleDrawn', 'DisableScreenFlag', 'CrossoverMenuState',
        'CrossoverMenuIndex', 'SelectedCharacter', 'OperMode', 'OperMode_Task',
        'GameEngineSubroutine', 'NumberofLives', 'Player_X_Position', 'Player_PageLoc',
        'Player_Y_Position', 'Player_State', 'GameLoop', 'IdleLoop', 'CrossoverJumpProfile')
    labels = {name: A.W.address(b, name) for name in names}
    text = 'local L='+json.dumps(labels, separators=(',', ':')).replace('"', '')
    # Lua's table keys use equals, rather than JSON's colons.
    text = text.replace(':', '=')+'\n'
    text += f'local SLOT,CYCLE,OWNER={slot},{cycle},{owner}\n'
    text += f'local LOOP_OFFSET={A.W.location(b,"GameLoop")-16}\n'
    text += f'local PROFILE_OFFSET={A.W.location(b,"CrossoverJumpProfile")-16}\n'
    text += r'''
local frame,updates,pad,phase,since=0,0,0,'menu',0
local game,done,pending=false,false,nil
local first,walk,jump,last=nil,nil,nil,nil
local profileCalls=0
local function r(n)return emu.read(L[n],emu.memType.nesDebug)end
local function state()return{frame=frame,update=updates,x=r('Player_PageLoc')*256+r('Player_X_Position'),y=r('Player_Y_Position'),body=r('Player_State'),engine=r('GameEngineSubroutine'),lives=r('NumberofLives')}end
local function encode(v)
 if type(v)=='table'then local out={};for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=reason,ROM_SHA256=assert(os.getenv('SMB_STDOUT_ROM_SHA')),controller_only=true,runtime_state_writes=0,physical_frames=frame,Main_updates=updates,owner=OWNER,profile_calls=profileCalls,first=first,walk=walk,jump=jump,terminal=state()}));emu.stop(ok and 0 or 1)
end
local function mapped(pc,offset)local q=emu.convertAddress(pc);return q and q.memType==emu.memType.nesPrgRom and q.address==offset end
local function tick()
 local s=state();assert(r('SelectedCharacter')==OWNER and s.lives==2 and s.engine==8,'Same living active owner')
 local age=updates-since
 if phase=='settle'then
  pad=0;if s.body==0 and s.y>=160 then first=s;phase='walk';since=updates;pad=1 end
 elseif phase=='walk'then
  pad=1;if age>=24 then walk=s;assert(s.x>first.x+8,'Actual walk displacement');phase='release';since=updates;pad=0 end
 elseif phase=='release'then
  pad=0;if age>=8 then phase='jump';since=updates;pad=128;jump={start=s,apex=s.y}end
 elseif phase=='jump'then
  jump.apex=math.min(jump.apex,s.y);pad=age<18 and 128 or 0
  if age>=24 and s.body==0 and s.y==first.y then jump.finish=s;assert(jump.apex<=first.y-16,'Actual source jump and landing');phase='fire';since=updates;pad=64 end
  assert(age<180,'Jump landing bound')
 elseif phase=='fire'then
  pad=64;if age>=24 then last=s;if OWNER==1 then assert(profileCalls==0,'MM source movement must bypass the retired native profile')end;finish(true,'Native source walk, fresh jump, landing and B input')end
 end
 assert(updates<400,'Motion update bound')
end
emu.addMemoryCallback(function()
 if not game or not mapped(L.GameLoop,LOOP_OFFSET)then return end
 local c=emu.getState();local sp=c['cpu.sp'];pending={pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535,sp=(sp+2)&255}
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if done or not pending then return end;local c=emu.getState();if c['cpu.pc']~=pending.pc or c['cpu.sp']~=pending.sp then return end
 pending=nil;updates=updates+1;local ok,why=pcall(tick);if not ok then finish(false,tostring(why))end
end,emu.callbackType.exec,L.IdleLoop+12)
emu.addMemoryCallback(function()if game and mapped(L.CrossoverJumpProfile,PROFILE_OFFSET)then profileCalls=profileCalls+1 end end,emu.callbackType.exec,L.CrossoverJumpProfile)
local function wait(fn)for _=1,1800 do if fn()then return end;coroutine.yield()end;error('Native menu/ingress bound')end
local function press(bits)pad=bits;for _=1,4 do coroutine.yield()end;pad=0;for _=1,8 do coroutine.yield()end end
local route=coroutine.create(function()
 wait(function()return frame>=100 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _=1,32 do if r('CrossoverMenuIndex')==SLOT then break end;press(2)end
 assert(r('CrossoverMenuIndex')==SLOT,'Real D-pad selects intended slot')
 for _=1,CYCLE do press(32)end;assert(r('SelectedCharacter')==OWNER,'Real Select identity')
 press(16);wait(function()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end)
 game=true;phase='settle';since=updates
end)
emu.addEventCallback(function()emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;if frame>3000 then finish(false,'Physical bound3000');return end
 if coroutine.status(route)~='dead'then local ok,why=coroutine.resume(route);if not ok then finish(false,tostring(why))end end
end,emu.eventType.endFrame)
'''
    assert not any(x in text for x in ('emu.write', 'io.open', 'loadState', 'saveState', 'takeScreenshot'))
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected', required=True)
    p.add_argument('--case', choices=CASES, required=True)
    args = p.parse_args()
    raw = args.rom.read_bytes()
    assert sha256(raw).hexdigest() == args.expected
    text = controller(raw, args.case)
    script = OUT/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    q = run(script, args.rom.resolve(), OUT/'capture', args.expected, 120)
    print(json.dumps({k:q[k] for k in ('passed', 'ROM_SHA256', 'script_SHA256', 'receipt_SHA256', 'receipt')},separators=(',', ':')), flush=True)
    assert q['passed'], 'Native motion regression failed'
