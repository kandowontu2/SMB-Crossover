-- Independent fixed-input playback and read-only frame/event audit.
local frame,poll,finished=0,0,false
local died,nextFrames,nextX,nextControl=false,0,nil,false
local r=function(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function position(n,p,i) return r(n,i)+256*r(p,i) end
local fixed={}
if RUN_INPUT_FILE then
 for line in io.lines(RUN_INPUT_FILE) do
  local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
  if p then fixed[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)} end
 end
end
local applied=assert(io.open(RUN_OUTPUT..'applied-inputs.csv','w'));applied:write('poll,frame,mask\n')
local objects=assert(io.open(RUN_OUTPUT..'objects.csv','w'));objects:write('frame,event,serial,id,x,y,state,yHigh\n')
local registers=assert(io.open(RUN_OUTPUT..'apu.csv','w'));registers:write('frame,scanline,address,value\n')
local render=assert(io.open(RUN_OUTPUT..'render.csv','w'));render:write('frame,engine,x,y,yHigh,camera,oamMax,lag,screenDisabled,world,level,areaType,worldSfx,buttons,previousButtons,velocityX,bassStep,nativeSfxMask,backgroundFontTiles\n')
local irq=assert(io.open(RUN_OUTPUT..'scroll-writes.csv','w'));irq:write('frame,scanline,dot,address,value\n')
local animation=assert(io.open(RUN_OUTPUT..'animation.csv','w'));animation:write('frame,state,pose,crouch,attack,shoot,wall,ceiling,power,powerup,display,chr,expectedChr,mushroom1,mushroom2,mushroom3,sfx1,sfx2,sfxNoise\n')
local rawSetInput,rawStop=emu.setInput,emu.stop
local active,serial,seen,defeated,escaped={},{},0,0,0
local nextSerial=0
local function objectEvent(event,e,state)
 objects:write(table.concat({frame,event,e.serial,e.id,e.x,e.y,state or e.state,e.yHigh or -1},',')..'\n')
end
emu.addMemoryCallback(function(a,v)
 if finished or frame<500 then return end
 local slot=a-L.Enemy_State;local e=active[slot]
 if e and not e.defeated and ((v&0x20)>0 or (e.id==6 and v>=2)) then
  e.defeated=true;defeated=defeated+1
  e.x=position('Enemy_X_Position','Enemy_PageLoc',slot);e.y=r('Enemy_Y_Position',slot);e.yHigh=r('Enemy_Y_HighPos',slot)
  objectEvent('defeat',e,v)
 end
end,emu.callbackType.write,L.Enemy_State,L.Enemy_State+5)
emu.setInput=function(buttons,port)
 if finished then return end
 poll=poll+1
 local mask=0
 if RUN_INPUT_FILE then
  local input=assert(fixed[poll],'Fixed input stream ended at poll '..poll)
  assert(input.frame==frame,'Fixed replay poll/frame diverged at '..poll..': '..input.frame..' / '..frame)
  mask=input.mask
  for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}) do buttons[name]=(mask&bit)>0 end
 else
  for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}) do if buttons[name] then mask=mask+bit end end
 end
 applied:write(poll..','..frame..','..mask..'\n')
 return rawSetInput(buttons,port)
end
emu.addMemoryCallback(function(a,v)
 if finished or frame<500 then return end
 local s=emu.getState();registers:write(table.concat({frame,s['ppu.scanline'],a,v},',')..'\n')
end,emu.callbackType.write,0x4000,0x4015)
emu.addMemoryCallback(function(a,v)
 if finished or frame<500 then return end
 local s=emu.getState();registers:write(table.concat({frame,s['ppu.scanline'],a,v},',')..'\n')
end,emu.callbackType.write,0x5000,0x5015)
emu.addMemoryCallback(function(a,v)
 if finished or frame<500 then return end
 local s=emu.getState()
 if s['ppu.scanline']>=30 and s['ppu.scanline']<=38 then irq:write(table.concat({frame,s['ppu.scanline'],s['ppu.cycle'],a,v},',')..'\n') end
end,emu.callbackType.write,0x2005,0x2006)
emu.addEventCallback(function()
 if finished then return end
 frame=frame+1
 if frame<500 then return end
 local x=position('Player_X_Position','Player_PageLoc')
 local camera=position('ScreenLeft_X_Pos','ScreenLeft_PageLoc')
 local maxSprites,count=0,0;local edges={}
 for i=0,63 do
  local y=emu.read(0x200+4*i,emu.memType.nesDebug)+1
  local first,last=math.max(32,y),math.min(240,y+16)
  if first<last then edges[first]=(edges[first] or 0)+1;edges[last]=(edges[last] or 0)-1 end
 end
 for scanline=32,239 do count=count+(edges[scanline] or 0);maxSprites=math.max(maxSprites,count) end
 -- 1-1's visible terrain uses tiles >=$24. HUD glyphs/VRAM command bytes
 -- appearing below the split expose column-buffer corruption that a floor
 -- motion comparison cannot detect. Ignore loading screens and clipped edges.
 local badBackground=0
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('DisableScreenFlag')==0 and r('WorldNumber')==0 and r('LevelNumber')==0 then
  for sx=16,232,8 do
   local wx=camera+sx
   local base=0x2000+math.floor(wx/256)%2*0x400+math.floor(wx%256/8)
   for row=5,29 do if emu.read(base+row*32,emu.memType.nesPpuDebug)<0x24 then badBackground=badBackground+1 end end
  end
 end
 render:write(table.concat({frame,r('GameEngineSubroutine'),x,r('Player_Y_Position'),r('Player_Y_HighPos'),camera,maxSprites,r('NmiSkipped'),r('DisableScreenFlag'),r('WorldNumber'),r('LevelNumber'),r('AreaType'),r('GuestMixMask'),r('SavedJoypadBits'),r('RgPreviousButtons'),r('MmVX')+256*r('MmVX',1)+65536*r('MmVX',2),r('XgBassStep'),RUN_CHARACTER==9 and r('BassAudioPreviousMask') or 0,badBackground},',')..'\n')
 if RUN_CHARACTER>=6 then
  local role=({'PIT','RYGAR','LUIGI','BASS','RYU','SOPHIA'})[RUN_CHARACTER-5]
  local display=r('GuestPowerupActive')~=0 and r('GuestPowerupDisplay') or r('PlayerStatus')
  local index=r('RgPose')+assert(L.XG_POSE_COUNT)*display
  local expected=emu.read((0x1f+RUN_CHARACTER-6)*0x2000+(L['Xg'..role..'Banks']+index)%0x2000,emu.memType.nesPrgRom)
  animation:write(table.concat({frame,r('Player_State'),r('RgPose'),r('RgCrouch'),r('RgAttack'),r('RgShootPose'),r('XgWall'),r('XgCeiling'),r('PlayerStatus'),r('GuestPowerupActive'),display,r('PlayerChrBank'),expected,emu.read(0x3f19,emu.memType.nesPpuDebug),emu.read(0x3f1a,emu.memType.nesPpuDebug),emu.read(0x3f1b,emu.memType.nesPpuDebug),r('Square1SoundBuffer'),r('Square2SoundBuffer'),r('NoiseSoundBuffer')},',')..'\n')
 end
 if frame>540 and (r('GameEngineSubroutine')==11 or (r('Player_Y_HighPos')>=2 and r('OperMode')==1 and r('OperMode_Task')==3)) then died=true end
 if r('WorldNumber')==0 and r('LevelNumber')==1 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('AreaType')==2 then
  nextFrames=nextFrames+1;if not nextX then nextX=x end
  nextControl=nextFrames>=25 and x>nextX+5
 end
 if r('WorldNumber')~=0 or r('LevelNumber')~=0 or r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 for slot=0,5 do
  local id,flag=r('Enemy_ID',slot),r('Enemy_Flag',slot)
  local e=active[slot]
  if flag>0 and flag<128 and id<0x15 then
   if not e or e.id~=id then
    nextSerial=nextSerial+1;e={serial=nextSerial,id=id,x=position('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),yHigh=r('Enemy_Y_HighPos',slot),state=r('Enemy_State',slot)}
    active[slot]=e;seen=seen+1;objectEvent('spawn',e)
   end
   e.x=position('Enemy_X_Position','Enemy_PageLoc',slot);e.y=r('Enemy_Y_Position',slot);e.yHigh=r('Enemy_Y_HighPos',slot);e.state=r('Enemy_State',slot)
   if not e.defeated and ((e.state&0x20)>0 or (id==6 and e.state>=2)) then e.defeated=true;defeated=defeated+1;objectEvent('defeat',e) end
  elseif e then
   if not e.defeated then
    if e.yHigh==2 or e.yHigh==1 and e.y>=220 then e.defeated=true;defeated=defeated+1;objectEvent('fell',e)
    else escaped=escaped+1;objectEvent('despawn-unconfirmed',e) end
   end
   active[slot]=nil
  end
 end
end,emu.eventType.endFrame)
emu.stop=function(code)
 if not finished then
  finished=true
  local f=assert(io.open(RUN_OUTPUT..'audit.json','w'))
  f:write('{"frames":'..frame..',"polls":'..poll..',"fixed_inputs":'..tostring(RUN_INPUT_FILE~=nil)..',"enemies_seen":'..seen..',"enemies_defeated":'..defeated..',"unconfirmed_despawns":'..escaped..',"died":'..tostring(died)..',"next_level_control":'..tostring(nextControl)..'}\n');f:close()
  for _,f in ipairs({applied,objects,registers,render,irq,animation}) do f:close() end
 end
 return rawStop(code)
end
