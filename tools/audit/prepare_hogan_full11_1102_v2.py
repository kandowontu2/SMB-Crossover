"""Bounded natural 1-1 traversal attempt for the existing WWF integration."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/hogan-full11-1102-v2'
ROM = R / 'build/metal-reservation-1102-v42/candidate.nes'
PIN = '1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55'
CONTROLLER = r'''
local frame,age,phase,step=0,0,'title',1
local actions={'right','right','right','right','up'}
local done=false
local lastEpoch,initialLives=nil,nil
local updates,maxX,maxCamera,minY,jumps,defeats=0,0,0,255,0,0
local pipe=1
local starts={404,564,692,868}
local ends={484,644,772,948}
local jumping,jumpAge,cooldown=false,0,0
local stagnant,lastProgressX=0,0
local trace={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function solid(x,y)
 if y<32 or y>=240 then return false end
 local tile=r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
 return tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2
end
local function nearest()
 local result=nil
 for i=0,5 do
  local flag,id,state=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
  if flag>0 and flag<128 and id<21 and (state&32)==0 then
   local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-wx()
   if dx>0 and dx<70 and math.abs(r('Enemy_Y_Position',i)-r('Player_Y_Position'))<40 then
    if not result or dx<result then result=dx end
   end
  end
 end
 return result
end
local function finish(reason)
 if done then return end;done=true
 local passed=reason=='active-1-2' and initialLives==r('NumberofLives')
 local f=assert(io.open(OUTPUT..'endpoint.png','wb'));f:write(emu.takeScreenshot());f:close()
 local out=assert(io.open(OUTPUT..'result.json','w'))
 out:write(string.format('{"passed":%s,"reason":%q,"controller_only":true,"character":"HULK HOGAN","frames":%d,"Main_updates":%d,"initial_lives":%d,"final_lives":%d,"maximum_x":%d,"maximum_camera":%d,"minimum_native_y":%d,"current_x":%d,"current_y":%d,"pipe_index":%d,"jump_sequences":%d,"native_defeats":%d,"world":%d,"level":%d,"engine":%d,"trace":[%s]}',tostring(passed),reason,frame,updates,initialLives or -1,r('NumberofLives'),maxX,maxCamera,minY,wx(),r('Player_Y_Position'),pipe,jumps,defeats,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),table.concat(trace,',')))
 out:close();emu.stop(passed and 0 or 1)
end
emu.addMemoryCallback(function()
 if phase=='play' and active() then defeats=defeats+1 end
end,emu.callbackType.exec,assert(L.ShellOrBlockDefeat))
emu.addEventCallback(function()
 local pad={}
 if phase=='open' or phase=='start' then pad.start=age<4
 elseif phase=='select' and age<4 then pad[actions[step]]=true
 elseif phase=='play' and active() then
  pad.right=true
  local x,y=wx(),r('Player_Y_Position')
  local ground=r('Player_State')==0
  if pipe<=4 and x>=ends[pipe] and ground then pipe=pipe+1 end
  local danger=nearest()
  if not jumping and cooldown==0 and ground then
   if pipe<=4 and x>=starts[pipe] or pipe>4 and (not solid(x+24,216) or solid(x+28,y+24)) then
    jumping=true;jumpAge=0;jumps=jumps+1
   elseif danger and danger<=44 then pad.right=false;pad.b=updates%18<3 end
  end
  if jumping then pad.a=jumpAge<36 end
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  step=step+1;age=0
  if step>#actions then assert(r('CrossoverMenuIndex')==28 and r('SelectedCharacter')==29);phase='start' end
 elseif phase=='start' and age>=300 then
  assert(active() and r('SelectedCharacter')==29 and r('FmGroups')&7==0)
  initialLives=r('NumberofLives');phase='play';age=0;lastEpoch=r('FrameCounter')
 elseif phase=='play' then
  if r('NumberofLives')~=initialLives then finish('lost-life');return end
  if r('WorldNumber')==0 and r('LevelNumber')==1 and active() then finish('active-1-2');return end
  if active() then
   local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255;lastEpoch=epoch
   assert(delta<=2,'Unexpected Main epoch gap during active stage')
   if delta>0 then
    updates=updates+delta
    if jumping then
     jumpAge=jumpAge+delta
     if jumpAge>36 and r('Player_State')==0 then jumping=false;cooldown=16 end
    elseif cooldown>0 then cooldown=math.max(0,cooldown-delta)end
    local x=wx();maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera());minY=math.min(minY,r('Player_Y_Position'))
    if x>lastProgressX then lastProgressX=x;stagnant=0 else stagnant=stagnant+delta end
    if stagnant>=650 then finish('stationary-bound');return end
   end
  else lastEpoch=r('FrameCounter') end
  if age%150==0 then
   assert(#trace<80)
   trace[#trace+1]=string.format('{"frame":%d,"updates":%d,"x":%d,"y":%d,"state":%d,"engine":%d,"pipe":%d}',frame,updates,wx(),r('Player_Y_Position'),r('Player_State'),r('GameEngineSubroutine'),pipe)
  end
  if age>=10500 then finish('route-bound');return end
 end
 if frame>=11500 then finish('global-bound')end
end,emu.eventType.endFrame)
'''


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    prepare(O / 'native', ROM, CONTROLLER, [Path(__file__)], expected=PIN,
            timeout=180, allow_interactive=True,
            scope='Natural cold Hogan1-1 traversal attempt, source punch input and native block-aware jumps. '
                  'No writes/cheats/teleports, one PNG and bounded aggregate. A failed controller route '
                  'does not by itself establish an impossible jump or authorize altered physics.')


if __name__ == '__main__':
    main()
