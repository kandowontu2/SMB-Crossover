-- Native 4-1 ending, with a deliberately full actor pool when the flag loads.
-- This is a native-room fixture, not a complete controller-only 4-1 clear.
local frame=0
local character=FLAGPOLE_CHARACTER or 3
local menu=character==12 and 8 or character
local poolFilled=false
local poleX
local touched=false
local nextStart
local flagAllocated=false
local lastCompleted,poleUpdates=nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function position(lo,hi)return r(lo)+256*r(hi)end
local interruptDepth=0
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced flagpole-fixture interrupt scope')end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function()
 -- InitializeArea is resident CODE at $8000; do not inject in interrupts.
 if interruptDepth==0 and frame>200 and not poolFilled then w('HalfwayPage',13)end
end,emu.callbackType.exec,L.InitializeArea)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or r('CurrentBank')%128~=2 or poolFilled then return end
 poleX=r('CurrentPageLoc')*256+r('CurrentColumnPos')*16
 for i=0,5 do w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i)end
 poolFilled=true
end,emu.callbackType.exec,L.FlagpoleObject)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<=550 or r('WorldNumber')~=3 or r('LevelNumber')~=0 or r('GameEngineSubroutine')~=8 then return end
 assert(emu.read(L.FlagpoleCollision,emu.memType.nesDebug)==0xa5 and emu.read(L.FlagpoleCollision+1,emu.memType.nesDebug)==L.GameEngineSubroutine,'Resident native pole-contact opcode')
 -- A low contact can set engine4 and advance to5 within one update, before
 -- endFrame sees it. Observe the actual shaft/ball collision, not its duration.
 touched=true
end,emu.callbackType.exec,L.FlagpoleCollision)
-- Consecutive foreground update starts observe completed gameplay updates.
-- The native pole detach moves14px; ordinary movement must not wrap to the
-- left screen edge. The old offscreen fixture could falsely pass that way.
emu.addMemoryCallback(function()
 if interruptDepth~=0 then return end
 assert(emu.read(L.NoDecTimers,emu.memType.nesDebug)==0xe6 and emu.read(L.NoDecTimers+1,emu.memType.nesDebug)==L.FrameCounter,'Native foreground update counter opcode')
 local engine=r('GameEngineSubroutine')
 if frame<=550 or r('WorldNumber')~=3 or r('LevelNumber')~=0 or r('AreaNumber')~=0 or r('OperMode_Task')~=3 or(engine~=8 and engine~=4 and engine~=5)then lastCompleted=nil;return end
 local x=position('Player_X_Position','Player_PageLoc')
 if lastCompleted then
  assert(math.abs(x-lastCompleted)<=16,'Bounded completed-update flag approach/auto-walk: '..lastCompleted..' -> '..x)
 end
 if engine==4 or engine==5 then
  assert(x>=poleX-16,'Pole/auto-walk never wraps to the left screen edge: '..x..' pole '..poleX)
  poleUpdates=poleUpdates+1
 end
 lastCompleted=x
end,emu.callbackType.exec,L.NoDecTimers)
emu.addEventCallback(function()
 emu.setInput({down=character~=8 and character>=6 and frame==80,
  right=(character<6 and frame>=80 and frame<80+20*character and (frame-80)%20==0)
   or(character~=8 and character>=6 and frame>=100 and frame<100+20*(menu-6) and (frame-100)%20==0)or frame>=550,
  select=(FLAGPOLE_LANCE or character==8) and frame==180,start=frame==200,
  -- Scrooge's source release cuts a one-poll hop to only a few pixels. Hold
  -- ordinary A through his ascent so he can clear the native flag base.
  a=frame>=550 and not touched and(r('Player_State')==0 or character==12 and r('Player_Y_Speed')>=128)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',3);w('AreaNumber',0);w('LevelNumber',0)end
 if frame==550 then
  assert(r('SelectedCharacter')==character and r('WorldNumber')==3 and r('LevelNumber')==0,'Native 4-1 with character '..character)
  if FLAGPOLE_LANCE then assert(r('BillVariant')==1,'Lance selected from the menu')end
  assert(poolFilled and poleX,'Native parser reached the flagpole with all six actor slots occupied')
  for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x30 then flagAllocated=true end end
  -- Keep the native camera, edges, scroll mirrors and already-parsed terrain.
  -- Approach by controller from its visible follow point. Placing the actor
  -- only25px before the pole left it at screenX247, ahead of the camera lock.
  local camera=position('ScreenLeft_X_Pos','ScreenLeft_PageLoc')
  local right=position('ScreenRight_X_Pos','ScreenRight_PageLoc')
  local x=poleX-160
  assert(right==camera+255 and r('HorizontalScroll')==camera%256,'Native camera, edges and scroll mirror agree')
  assert(x>=camera+16 and x+16<=right,'Approach begins entirely on screen')
  for _,sx in ipairs({x+2,x+13})do for _,sy in ipairs({48,64,79})do
   local offset=math.floor(sx/256)%2*208+math.floor((sy-32)/16)*16+math.floor(sx%256/16)
   assert(r('Block_Buffer_1',offset)==0,'Native parsed terrain leaves the full approach body clear')
  end end
  w('Player_X_Position',x%256);w('Player_PageLoc',math.floor(x/256));w('Player_Y_Position',48);w('Player_Y_HighPos',1)
  w('Player_State',2);w('Player_Y_Speed',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==850 then assert(flagAllocated,'Full actor pool drops the native flag and leaves the level stuck: engine '..r('GameEngineSubroutine')..' y '..r('Player_Y_Position')..' pole touched '..tostring(touched)..' id5 '..r('Enemy_ID',5)..' flag5 '..r('Enemy_Flag',5))end
 if frame>550 and r('WorldNumber')==3 and r('LevelNumber')==1 and r('AreaNumber')==2 and r('GameEngineSubroutine')==8 then
  -- Simon retains his incoming horizontal velocity in the air; the native
  -- pipe drop starts at zero. Check walking after landing in the new room.
  if not nextStart and r('Player_State')==0 then nextStart={frame=frame,x=r('Player_X_Position')+256*r('Player_PageLoc')}
  elseif nextStart and frame>=nextStart.frame+20 then
   assert(touched,'Native pole contact occurred before level completion')
   assert(poleUpdates>10,'Completed pole/auto-walk updates were displacement-audited')
   assert(r('Player_X_Position')+256*r('Player_PageLoc')>nextStart.x,'Controller moves the character in the native 4-2 underground room: start '..nextStart.x..' now '..(r('Player_X_Position')+256*r('Player_PageLoc'))..' y '..r('Player_Y_Position')..' state '..r('Player_State')..' speed '..r('Player_X_Speed')..' input '..r('SavedJoypadBits'))
   print('PASS character '..character..(FLAGPOLE_LANCE and ' Lance' or '')..' native 4-1 full-pool flags, slide, castle/time conversion, 4-2 pipe intro and underground control')
   emu.stop(0)
  end
 end
 if frame==2200 then assert(false,'Native 4-1 ending watchdog: level '..r('LevelNumber')..' area '..r('AreaNumber')..' engine '..r('GameEngineSubroutine')..' flag task '..r('StarFlagTaskControl')..' y '..r('Player_Y_Position'))end
end,emu.eventType.endFrame)
