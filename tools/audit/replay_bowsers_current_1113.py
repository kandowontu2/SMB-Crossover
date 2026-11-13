"""Current ordinary-input Bowser 1-1 replay; no state, ROM or capture writes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT=W.R/'build/metal-flower-native-1112'


def controller(raw, identity=0):
    assert identity in (0,1) and sha256(raw).hexdigest()==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState',
        'CrossoverMenuIndex','SelectedCharacter','FmAlts','OperMode','OperMode_Task',
        'GameEngineSubroutine','NumberofLives','Player_X_Position','Player_PageLoc',
        'Player_Y_Position','Player_State','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
        'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
        'Block_Buffer_1','MTILE_SOLID','GameLoop','IdleLoop','WorldNumber','LevelNumber',
        'GameTimerDisplay','AreaType')
    fields={name:W.address(b,name) for name in names}
    attr=W.location(b,'MTileAttribute')-16
    game=W.location(b,'GameLoop')-16
    idle=W.location(b,'IdleLoop')-16
    text='local F={'+','.join(f'{name}={value}' for name,value in fields.items())+'}\n'
    text+=f'local identity,expectedRom,gameOffset,attrs={identity},"{PIN}",{game},{attr}\n'
    text+='local hooks={'+','.join('{offset='+str(at)+',hex="'+raw[16+at:16+at+size].hex()+'"}'
        for at,size in ((game,8),(idle,39),(attr,256)))+'}\n'
    text+=r'''
local frames,updates,pad=0,0,0
local game,done=false,false
local pending,returnHooks,returns={},{},{}
local lastX,still,hold,lastA=-1,0,0,false
local flag,castle,entrance,nextUpdates=false,false,false,0
local phase='menu';local records={};local pipes={};local seenPipes={}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(name)return read(F[name])end
local function work(at)return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()
 return{frame=frames,updates=updates,x=x(),y=r('Player_Y_Position'),native_state=r('Player_State'),engine=r('GameEngineSubroutine'),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaType'),health=work(0xbe29),ready=work(0xbe26),lives=r('NumberofLives'),timer=100*read(F.GameTimerDisplay)+10*read(F.GameTimerDisplay+1)+read(F.GameTimerDisplay+2)}
end
local function encode(v)
 if type(v)=='table'then local a={};for k,q in pairs(v)do a[#a+1]=string.format('%q',k)..':'..encode(q)end;return'{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function finish(ok,why)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=why,ROM_SHA256=expectedRom,identity=identity==0 and 'SMB3 BOWSER'or'SMB1 BOWSER',controller_only=true,physical_frames=frames,all_returned_Main=updates,terminal=state(),flag=flag,castle=castle,entrance=entrance,next_area_updates=nextUpdates,return_counts=returns,pipes=pipes,recent=records,new_helpers=0,capture_files=0,runtime_state_writes=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function tile(wx,y)
 if y<32 or y>=240 then return 0 end
 return read(F.Block_Buffer_1+(wx//256%2)*208+((y-32)//16)*16+(wx%256)//16)
end
local function solid(wx,y)return emu.read(attrs+tile(wx,y),emu.memType.nesPrgRom)&F.MTILE_SOLID~=0 end
local function drive()
 local s=state()
 assert(r('SelectedCharacter')==27 and r('FmAlts')&8==identity*8,'Retain selected Bowser identity')
 assert(s.lives==2 and s.health>0 and s.engine~=6 and s.engine~=11,'No Bowser death or life loss')
 assert(s.ready==183,'Original Bowser runtime remains live')
 assert(updates<7000,'Finite complete stage and entrance controller bound')
 if updates%120==0 then
  records[tostring(updates)]=s
  if updates>=1440 then records[tostring(updates-1440)]=nil end
 end
 if s.world==0 and s.level==0 and s.engine==4 and s.x>=3140 then flag=true end
 if s.world==0 and s.level==0 and s.engine==5 and s.x>=3160 then castle=true end
 if s.world==0 and s.level==1 and s.engine==7 then entrance=true end
 if s.world==0 and s.level==1 and s.area==2 and active()then
  nextUpdates=s.y==176 and nextUpdates+1 or 0
  if nextUpdates>=25 then
   assert(flag and castle and entrance,'Real native flagpole/castle/next-area chain')
   finish(true,'Bowser clears non-shortcut1-1 then25 grounded quiet underground1-2 updates');return
  end
  pad=0;return
 end
 if not active()then pad=0;return end
 assert(s.world==0 and s.level==0,'Expected ordinary1-1 before flagpole')
 still=s.x==lastX and still+1 or 0;lastX=s.x
 assert(still<240,'No240-update active horizontal softlock')
 local pipe=nil
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 for wx=s.x//16*16,math.min(camera+255,s.x+111),16 do
  local top=nil
  for yy=32,192,16 do local t=tile(wx,yy);if t>=16 and t<=21 then top=yy;break end end
  if top then
   if wx>=s.x+8 and not pipe then pipe={left=wx,top=top}end
   local key=tostring(wx)..':'..top
   if not seenPipes[key]then seenPipes[key]=true;pipes[key]={left=wx,top=top,updates=updates}end
  end
 end
 local grounded=r('Player_State')==0
 local a=false
 if hold>0 then hold=hold-1;a=true
 elseif grounded and not lastA then
  local jump=pipe and pipe.left-s.x<52 or still>15 or solid(s.x+24,s.y+8)or solid(s.x+24,s.y+24)
  local ahead=tile(s.x+24,math.min(232,s.y+40))
  jump=jump or ahead==0 or ahead==35 or ahead==38 or ahead==194 or ahead==195
  for slot=0,5 do
   if read(F.Enemy_Flag+slot)==1 and read(F.Enemy_ID+slot)<21 and read(F.Enemy_State+slot)<32 then
    local gap=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot)-s.x
    if gap>0 and gap<72 then jump=true end
   end
  end
  if jump then hold=7;a=true end
 end
 lastA=a;pad=1|(a and 128 or 0)|(updates%32==0 and 64 or 0)
 assert(updates<7000,'Finite ordinary full-stage controller bound')
end
-- Observe every actual GameLoop return, including the native catch-up caller.
-- The source CPU's one-call frame model does not predict physical cadence.
emu.addMemoryCallback(guard(function()
 if not game then return end
 local at=emu.convertAddress(F.GameLoop)
 if not at or at.memType~=emu.memType.nesPrgRom or at.address~=gameOffset then return end
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 pending[#pending+1]={pc=pc,sp=(sp+2)&255}
 assert(#pending<=4,'Bounded actual GameLoop return stack')
 if not returnHooks[pc]then
  returnHooks[pc]=true
  emu.addMemoryCallback(guard(function()
   local p=pending[#pending];if not p then return end
   local q=emu.getState();if q['cpu.pc']~=p.pc or q['cpu.sp']~=p.sp then return end
   pending[#pending]=nil;updates=updates+1
   local key=string.format('%04x',p.pc);returns[key]=(returns[key]or 0)+1
   drive()
  end),emu.callbackType.exec,pc)
 end
end),emu.callbackType.exec,F.GameLoop)
local function wait(fn)for _=1,1800 do if fn()then return end;coroutine.yield()end;error('Native title/menu/ingress bound')end
local function press(bits)pad=bits;for _=1,4 do coroutine.yield()end;pad=0;for _=1,8 do coroutine.yield()end end
local task=coroutine.create(function()
 wait(function()return frames>=100 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Initial Mario roster position')
 for _=1,3 do press(4)end
 for _=1,2 do press(1)end
 assert(r('CrossoverMenuIndex')==26 and r('SelectedCharacter')==27,'Actual grid reaches Bowser')
 if identity==1 then press(32)end
 assert(r('FmAlts')&8==identity*8,'Actual Select resolves Bowser alternate')
 press(16);wait(active);game=true;phase='game';pad=1
end)
assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,'Exact current public ROM')
for _,h in ipairs(hooks)do for i=1,#h.hex,2 do assert(emu.read(h.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(h.hex:sub(i,i+1),16),'Exact native current observer preimage')end end
emu.addEventCallback(guard(function()emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frames=frames+1;if frames>22000 then finish(false,'Physical replay bound22000');return end
 if coroutine.status(task)~='dead'then local ok,why=coroutine.resume(task);assert(ok,why)end
end),emu.eventType.endFrame)
'''
    assert not any(word in text for word in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity',type=int,choices=(0,1),default=0)
    parser.add_argument('--metadata',action='store_true')
    args=parser.parse_args()
    assert check(ROM)['ROM_sha256']==PIN
    text=controller(ROM.read_bytes(),args.identity)
    if args.metadata:
        print(json.dumps(dict(ROM_SHA256=PIN,script_SHA256=sha256(text.encode()).hexdigest(),native_run=False,output_files=0)),flush=True)
    else:
        script=OUT/'controller.lua';script.write_text(text,encoding='utf-8',newline='\n')
        q=run(script,ROM,OUT/'capture',PIN,240)
        print(json.dumps(dict(passed=q['passed'],ROM_SHA256=PIN,script_SHA256=q['script_SHA256'],receipt_SHA256=q['receipt_SHA256'],receipt=q['receipt'],outputs_written=q['outputs_written']),separators=(',',':')),flush=True)
        assert check(ROM)['ROM_sha256']==PIN
        assert q['passed'],'Current Bowser full-stage replay must pass'
