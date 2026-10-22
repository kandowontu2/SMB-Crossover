-- Isolated terrain arenas. Every assertion runs after actual PlayerBGCollision;
-- no claim of ordinary-controller stage progress is made by this fixture.
local frame,ci,t=0,0,0
local c,pending,active,lastX,integrated,wallChecks,edgeChecks=nil,false,false,nil,nil,0,0
local stepArt,artChecks=nil,0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function px() return 256*r('Player_PageLoc')+r('Player_X_Position') end
local function tile(col,row,id) w(col%32<16 and 'Block_Buffer_1' or 'Block_Buffer_2',id,row*16+col%16) end
local cases={}
for _,boundary in ipairs({128,256,384}) do
 for _,direction in ipairs({1,2}) do
  for _,kind in ipairs({'brick','pipe','ledge'}) do
   cases[#cases+1]={name=kind..' '..direction..' at '..boundary,wall=boundary,dir=direction,kind=kind,power=math.floor(#cases/3)%3}
  end
 end
end
emu.addEventCallback(function()
 if frame<540 then emu.setInput({right=frame==80,start=frame==120},0);return end
 if not c or pending then ci=ci+1;c=cases[ci];t=0;pending=false;active=false end
 emu.setInput(c and {right=c.dir==1,left=c.dir==2} or {},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<540 or not c or pending or r('CurrentBank')%128~=B.MegaManMovement then return end
 t=t+1
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,415 do w('Block_Buffer_1',0,i) end
 local col=math.floor(c.wall/16)
 if c.kind=='ledge' then
  for k=0,31 do
   local supported=c.dir==1 and k<col or c.dir==2 and k>=col
   if supported then tile(k,11,0x51);tile(k,12,0x51) end
  end
 else
  for k=0,31 do tile(k,11,0x51);tile(k,12,0x51) end
  local wallcol=c.dir==1 and col or col-1
  for row=8,10 do tile(wallcol,row,c.kind=='pipe' and 0x16 or 0x51) end
 end
 if not active then
  active=true
  local start=c.kind=='ledge' and (c.dir==1 and c.wall-4 or c.wall-12)
   or (c.dir==1 and c.wall-15 or c.wall-1)
  w('Player_X_Position',start%256);w('Player_PageLoc',math.floor(start/256))
  w('ScreenLeft_X_Pos',math.max(0,start-80)%256);w('ScreenLeft_PageLoc',math.floor(math.max(0,start-80)/256))
  w('ScreenRight_X_Pos',(math.max(0,start-80)+255)%256);w('ScreenRight_PageLoc',math.floor((math.max(0,start-80)+255)/256))
  w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  w('Player_X_Speed',0);w('MmLastXSpeed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',3)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
  w('MmStepTimer',0);w('MmPreviousDir',0);w('MmSliding',0);w('MmFrictionYActive',0)
  w('SwimmingFlag',0);w('PlayerFacingDir',c.dir);w('DisableCollisionDet',0)
  w('ScrollLock',1);w('PlayerStatus',c.power);w('SsHeld',0);w('MegaManShotPose',0)
 end
 lastX=px()
end,emu.callbackType.exec,assert(L.MegaManMovement))
emu.addMemoryCallback(function()
 if frame>=540 and c and not pending and r('CurrentBank')%128==B.MegaMan202Integrated then integrated=px() end
end,emu.callbackType.exec,assert(L.MegaMan202Integrated))
emu.addMemoryCallback(function()
 if frame<540 or not c or pending or not integrated or r('CurrentBank')%128~=1 then return end
 local now=px()
 if c.kind~='ledge' then
  if c.dir==1 then assert(now+14<c.wall,c.name..' right probe remains outside solid: '..now)
  else assert(now+1>=c.wall,c.name..' left probe remains outside solid: '..now) end
  assert(r('Player_State')==0,c.name..' remains supported')
  if t==1 then assert((r('Player_CollisionBits')&c.dir)==0,c.name..' publishes contacted-side collision bits') end
  if r('MmStepTimer')>0 then
   stepArt=({L.METASPRITE_MM_HAIR_STEP,L.METASPRITE_MM_HELMET_STEP,L.METASPRITE_MM_FIRE_STEP})[c.power+1]
  end
  wallChecks=wallChecks+1
 else
  -- The startup step alone crosses the support boundary on its first update.
  -- Actual feet probes, rather than the model, must observe the missing floor.
  if t==1 then
   assert(integrated-lastX==(c.dir==1 and 2 or -2),c.name..' direct startup step')
   assert(r('Player_State')~=0,c.name..' startup step leaves unsupported edge')
  end
  edgeChecks=edgeChecks+1
 end
 integrated=nil
 if t==(c.kind=='ledge' and 3 or 18) then print('PASS actual BG '..c.name);pending=true end
 if ci==#cases and pending then
  assert(artChecks==72,'Every startup update uses its power-form artwork: '..artChecks..'/72')
  print('PASS 2.02 step collision '..wallChecks..' wall/pipe updates, '..edgeChecks..' edge updates and '..artChecks..' power-form step art checks, both directions and page seams');emu.stop(0)
 end
end,emu.callbackType.exec,assert(L.MegaMan202AfterBG))
emu.addEventCallback(function()
 frame=frame+1
 if stepArt then assert(r('ObjectMetasprite')==stepArt,'Startup timer uses the selected power-form step graphic');stepArt=nil;artChecks=artChecks+1 end
 if frame>2000 then assert(false,'Step/BG arena timed out '..ci..'/'..t) end
end,emu.eventType.endFrame)
