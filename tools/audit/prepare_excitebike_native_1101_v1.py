"""Prepare root-owned, controller-only cold ingress and motor smoke packet."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
O=R/'build/excitebike-pose-1101-v3'

CONTROLLER=r'''
local frame,age,phase,done=0,0,'title',false
local menu=0
local phases={{'idle',90,0},{'right',30,1},{'coast',180,0},{'reverse',30,2},{'rest',180,0},{'prepare',90,1},{'jump',36,9},{'land',120,0}}
local part,steps,lastEpoch,initialLives=1,0,nil,nil
local results,trace={},{}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function finish(reason)
 if done then return end
 done=true;shot('final')
 local passed=reason=='completed' and #results==8 and results[1].minX==results[1].maxX and results[2].lastX>results[2].firstX and results[3].lateMinX==results[3].lateMaxX and results[4].lastX<results[4].firstX and results[7].minY<results[7].firstY-30 and r('NumberofLives')==initialLives and r('Player_State')==0 and r('Player_Y_HighPos')==1
 local rows={}
 for _,q in ipairs(results)do rows[#rows+1]=string.format('{"phase":"%s","updates":%d,"physical_frames":%d,"first_x":%d,"last_x":%d,"min_x":%d,"max_x":%d,"first_y":%d,"minimum_y":%d,"last_y":%d,"late_min_x":%d,"late_max_x":%d}',q.name,q.updates,q.frames,q.firstX,q.lastX,q.minX,q.maxX,q.firstY,q.minY,q.lastY,q.lateMinX,q.lateMaxX)end
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":%s,"reason":"%s","frames":%d,"selected":%d,"initial_lives":%d,"final_lives":%d,"world_x":%d,"y":%d,"engine":%d,"phases":[%s],"trace":[%s]}\n',tostring(passed),reason,frame,r('SelectedCharacter'),initialLives or -1,r('NumberofLives'),wx(),r('Player_Y_Position'),r('GameEngineSubroutine'),table.concat(rows,','),table.concat(trace,',')))
 f:close();emu.stop(passed and 0 or 1)
end
emu.addEventCallback(function()
 local pad={}
 if phase=='open' or phase=='start' then pad.start=age<4
 elseif phase=='select' and age<4 then if menu<5 then pad.right=true else pad.down=true end
 elseif phase=='play' then
  local bits=phases[part][3]
  pad.right=(bits&1)~=0;pad.left=(bits&2)~=0;pad.up=(bits&8)~=0
  pad.a=part==7 and steps<1
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  menu=menu+1;age=0
  if menu==8 then assert(r('CrossoverMenuIndex')==29 and r('SelectedCharacter')==37);phase='start' end
 elseif phase=='start' and age>=300 then
  assert(r('SelectedCharacter')==37 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8)
  initialLives=r('NumberofLives');phase='play';age=0;lastEpoch=r('FrameCounter');shot('cold-spawn')
 elseif phase=='play' then
  local cfg=phases[part];local q=results[part]
  if not q then q={name=cfg[1],updates=0,frames=0,firstX=wx(),lastX=wx(),minX=wx(),maxX=wx(),firstY=r('Player_Y_Position'),minY=r('Player_Y_Position'),lastY=r('Player_Y_Position'),lateMinX=65536,lateMaxX=-1};results[part]=q end
  q.frames=q.frames+1;q.lastX=wx();q.minX=math.min(q.minX,wx());q.maxX=math.max(q.maxX,wx());q.lastY=r('Player_Y_Position');q.minY=math.min(q.minY,q.lastY)
  local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255;lastEpoch=epoch
  assert(delta<=2,'unexpected Main epoch gap')
  steps=steps+delta;q.updates=q.updates+delta
  if steps>=cfg[2]-20 then q.lateMinX=math.min(q.lateMinX,wx());q.lateMaxX=math.max(q.lateMaxX,wx())end
  if age%60==0 then trace[#trace+1]=string.format('{"frame":%d,"phase":"%s","steps":%d,"x":%d,"y":%d,"state":%d,"engine":%d}',frame,cfg[1],steps,wx(),q.lastY,r('Player_State'),r('GameEngineSubroutine'))end
  if r('NumberofLives')~=initialLives then finish('lost-life')
  elseif r('SelectedCharacter')~=37 then finish('lost-owner')
  elseif steps>=cfg[2] then
   if part==7 then shot('source-lean-jump')end
   part=part+1;steps=0;age=0
   if part>#phases then finish('completed')end
  elseif age>1000 then finish('phase-bound')end
 end
 if frame>5000 and not done then finish('global-bound')end
end,emu.eventType.endFrame)
'''


def main():
    composition=json.loads((O/'current-composition.json').read_text());assert composition['passed']
    prepare(O/'native',O/'current.nes',CONTROLLER,
            [Path(__file__),O/'current-composition.json',O/'current-CPU.json',O/'cold-CPU.json',O/'terrain-CPU.json'],
            expected=composition['ROM_SHA256'],timeout=150,allow_interactive=True,
            scope='Controller-only raw37 cold menu ingress, idle/no-drift, throttle/coast/reverse, original backlean jump and native landing. Three PNGs, compact phase/60-frame trace; no emulated writes, full1-1 or helper claim.')

if __name__=='__main__':main()
