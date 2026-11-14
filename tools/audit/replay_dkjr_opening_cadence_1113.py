"""Read-only returned-update idle/walk windows for root's sole native queue."""
from hashlib import sha256
import json
from pathlib import Path
import sys

import compose_dkjr_direct_platform_1113 as T
from check_ff_stdout_controller_source_1110 import LuaRuntime

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
import dkjr_original_cpu_1102_v1 as Donor


COMMON=r'''
local frame,phase,start,bits,done,ready=0,'setup',nil,0,false,false
local entries,returned,reads,polls,polled=0,0,0,0,false
local pending,callbacks=nil,{}
local rows,baseline={},nil
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function encode(v)
 if type(v)=='table'then local a,n=true,0;for k in pairs(v)do if type(k)~='number'then a=false end;n=n+1 end;local q={}
  if a then for i=1,n do q[#q+1]=encode(v[i])end;return '['..table.concat(q,',')..']'end
  for k,w in pairs(v)do q[#q+1]=string.format('%q',k)..':'..encode(w)end;return '{'..table.concat(q,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return 'null'else return tostring(v)end
end
@SERVICES@
local function finish(ok,why)
 if done then return end;done=true;bits=0
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=why,ROM_SHA256=ROM_SHA,rows=rows,terminal=state(),
  physical_frames=frame,source_or_native_writes=false,returned_updates_separate_from_input_polls=true,captures=0}))
 emu.stop(ok and 0 or 1)
end
local function begin(name)
 phase=name;start=frame;bits=name=='walk_right'and 1 or name=='walk_left'and 2 or 0
 baseline={entries=entries,returned=returned,reads=reads,polls=polls,state=state(),skipped=skipped()}
end
emu.addMemoryCallback(function()if phase~='setup'then reads=reads+1 end end,emu.callbackType.read,0x4016)
emu.addMemoryCallback(function()
 if phase=='setup'or not admitted()then return end
 entries=entries+1;assert(not pending,'Nested motor update in opening window')
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 pending={pc=pc,sp=(sp+2)&255}
 if not callbacks[pc]then callbacks[pc]=true;emu.addMemoryCallback(function()
  if not pending then return end;local c=emu.getState()
  if c['cpu.pc']==pending.pc and c['cpu.sp']==pending.sp then returned=returned+1;pending=nil end
 end,emu.callbackType.exec,pc)end
end,emu.callbackType.exec,ENTRY)
emu.addEventCallback(function()
 polled=true
 emu.setInput({right=bits&1~=0,left=bits&2~=0,start=bits&16~=0,select=bits&32~=0,down=bits&4~=0},0)
end,emu.eventType.inputPolled)
@SETUP@
emu.addEventCallback(function()
 if done then return end;frame=frame+1
 if polled and phase~='setup'then polls=polls+1 end;polled=false
 if frame>2400 then finish(false,'Bounded opening cadence window');return end
 if phase=='setup'then setup();if ready and active()and settled()then begin('idle')end;return end
 if not active()or not settled()then finish(false,'Opening left healthy grounded state');return end
 local limit=phase=='idle'and 120 or 32
 if frame-start>=limit then
  assert(not pending,'Measurement boundary cut an unfinished motor call')
  local s=state();local row={phase=phase,physical_frames=frame-start,update_entries=entries-baseline.entries,
   update_returns=returned-baseline.returned,controller_reads=reads-baseline.reads,input_polled_frames=polls-baseline.polls,
   skipped_NMI=SKIP_COUNTER_AVAILABLE and((skipped()-baseline.skipped)&255)or nil,
   skipped_NMI_counter_available=SKIP_COUNTER_AVAILABLE,initial=baseline.state,final=s}
  assert(row.update_entries==row.update_returns and row.update_returns>0,'Complete returned-update observation')
  if phase=='idle'then assert(s.x==baseline.state.x,'Neutral opening drift')
  elseif phase=='walk_right'then assert(s.x>baseline.state.x,'Ordinary right movement')
  else assert(s.x<baseline.state.x,'Ordinary left movement')end
  rows[#rows+1]=row
  if phase=='idle'then begin('walk_right')elseif phase=='walk_right'then begin('walk_left')else finish(true,'Returned-update idle/right/left cadence windows')end
 end
end,emu.eventType.endFrame)
'''


def controller(raw):
    assert sha256(raw).hexdigest()==T.PIN
    W=T.P.B.W;b=W.Symbols.bundle();b['raw']=raw
    names=('SelectedCharacter','GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position',
        'Player_State','NumberofLives','Enemy_Flag','WorldNumber','LevelNumber','GamePauseStatus',
        'CrossoverMenuState','CrossoverMenuIndex','CheatInvincible','CheatStartLevel','NmiSkipped')
    labels={n:W.address(b,n)for n in names}
    prefix='local L={'+','.join(f'{n}={v}'for n,v in labels.items())+'}\n'
    prefix+=f'local ROM_SHA="{T.PIN}"\nlocal ENTRY=0xd65e\nlocal SKIP_COUNTER_AVAILABLE=true\n'
    services=r'''
local function r(n,i)return read(L[n]+(i or 0))end
local function ram(a)return emu.read(16384+a,emu.memType.nesWorkRam)end
local function active()return r('SelectedCharacter')==40 and r('GameEngineSubroutine')==8 and ram(0x8fe)==2 end
local function state()return {x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),source=ram(0x6b),lives=r('NumberofLives')}end
local function settled()
 local s=state();if s.lives~=2 or s.y~=176 or s.source~=1 then return false end
 for i=0,5 do if r('Enemy_Flag',i)~=0 then return false end end
 return r('WorldNumber')==0 and r('LevelNumber')==0 and r('Player_State')==0
end
local function admitted()local m=emu.convertAddress(ENTRY);return active()and m and m.memType==emu.memType.nesWorkRam and m.address==2*8192+(ENTRY&8191)end
local function skipped()return r('NmiSkipped')end
'''
    setup=r'''
local function wait(pred)for _=1,1000 do if pred()then return end;coroutine.yield()end;error('Native readiness bound')end
local function press(pad)bits=pad;for _=1,4 do coroutine.yield()end;bits=0;for _=1,8 do coroutine.yield()end end
local title=coroutine.create(function()
 wait(function()return frame>=70 and read(0x6004)==1 and r('GamePauseStatus')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 end);assert(r('CrossoverMenuIndex')==0)
 for _,pad in ipairs({4,4,1,1,1,4})do press(pad)end
 assert(r('CrossoverMenuIndex')==27 and r('SelectedCharacter')==28)
 press(32);assert(r('SelectedCharacter')==40);press(16);wait(active)
 assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0);bits=0;ready=true
end)
local function setup()
 if CPU_CONTROLLER_OPENING then bits=0;ready=true;return end
 if coroutine.status(title)~='dead'then local ok,why=coroutine.resume(title);assert(ok,why)end
end
'''
    text=prefix+COMMON.replace('@SERVICES@',services).replace('@SETUP@',setup)
    LuaRuntime().compile(text);return text


def original_controller(raw):
    assert sha256(raw).hexdigest()==Donor.SHA
    prefix=f'local ROM_SHA="{Donor.SHA}"\nlocal ENTRY=0xd412\nlocal SKIP_COUNTER_AVAILABLE=false\n'
    services=r'''
local function active()return read(0x46)==1 and read(0x6b)==1 end
local function state()return {x=read(0x213),y=read(0x210),source=read(0x6b)}end
local function settled()return active()and read(0x210)==199 end
local function admitted()local m=emu.convertAddress(ENTRY);return active()and m and m.memType==emu.memType.nesPrgRom and m.address==(ENTRY&16383)end
local function skipped()return 0 end
'''
    setup="local function setup()if CPU_CONTROLLER_OPENING then bits=0;ready=true;return end;bits=frame>=70 and frame<74 and 16 or 0;if frame>=74 then ready=true end end\n"
    text=prefix+COMMON.replace('@SERVICES@',services).replace('@SETUP@',setup)
    LuaRuntime().compile(text);return text


def donor_ground_controller(raw):
    """Separate current factory admitting acknowledged donor-ground edge state2.

    Preserve controller() byte-for-byte: root's7307 native idle row remains
    bound to that frozen text. Original current donor state/prior1 and its
    native-Y projection remain required through both ordinary walk windows.
    """
    text=controller(raw)
    old="return r('WorldNumber')==0 and r('LevelNumber')==0 and r('Player_State')==0"
    new="""local native=r('Player_State')
 return r('WorldNumber')==0 and r('LevelNumber')==0 and
  (native==0 or native==2)and ram(0x6c)==1 and ram(0x210)==s.y+15"""
    assert text.count(old)==1
    text=text.replace(old,new)
    old="source=ram(0x6b),lives=r('NumberofLives')"
    new="source=ram(0x6b),prior_source=ram(0x6c),native_state=r('Player_State'),source_y=ram(0x210),lives=r('NumberofLives')"
    assert text.count(old)==1
    text=text.replace(old,new)
    LuaRuntime().compile(text);return text


if __name__=='__main__':
    _,raw=T.load_inputs();texts=dict(current=controller(raw),original=original_controller(Donor.donor()))
    print('DKJR_OPENING_CADENCE_METADATA '+json.dumps(dict(
        Lua_SHA256={name:sha256(text.encode()).hexdigest()for name,text in texts.items()},
        physical_windows=[120,32,32],source_or_native_writes=False,captures=0,
        native_results_pending=True,outputs_written=0),separators=(',',':')),flush=True)
