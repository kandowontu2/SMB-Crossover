-- Explicit underground brick/question-block arenas. The player starts just
-- below a ceiling with an authored upward velocity; ordinary A/direction
-- controls drive the following updates. This is a collision fixture, not a
-- controller-only level clear.
local frame,index,age,depth=0,0,0,0
local cases,current={},nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function worldX()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
-- Per-update fixture isolation of native terrain streaming. Boot-level parser
-- work must not insert unrelated pipes into an authored ceiling arena. This
-- guard changes no player, terrain or collision-result value after setup.
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced head-arena interrupt scope')end,emu.callbackType.exec,pc)end
emu.addMemoryCallback(function()
 if frame>=550 and depth==0 and r('CurrentBank')%128==1 then w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)end
end,emu.callbackType.exec,L.PlayerBGCollision)
for _,power in ipairs({0,1,2})do for _,x in ipairs({56,120,248,256})do
 for _,roof in ipairs({32,96,144})do for _,dir in ipairs({0,1,2})do
  for _,tile in ipairs({0x52,0xc1})do for _,wide in ipairs({false,true})do cases[#cases+1]={power=power,x=x,roof=roof,dir=dir,tile=tile,wide=wide}end end
 end end
end end
local log=assert(io.open(OUTPUT..ROM_NAME..'-samus-head-displacement.csv','w'))
log:write('case,age,power,tile,roof,dir,x,y,vx,vy\n')
local contacts,pendingBlock=0,nil
emu.addMemoryCallback(function()
 if current then
  current.contacts=current.contacts+1;contacts=contacts+1
  -- Independent full-width probe order. Resolve against the authored tile
  -- cells before the routine erases its target; never use SmHeadX/Page as
  -- the expected value.
  local x=worldX()
  for _,offset in ipairs({8,2,13})do
   local probe=x+offset
   if r('Block_Buffer_1',cell(probe,current.roof))~=0 then pendingBlock={x=(probe//16)*16,slot=r('SprDataOffset_Ctrl')};break end
  end
  assert(pendingBlock,'Actual head hit belongs to an authored ceiling cell')
 end
end,emu.callbackType.exec,L.PlayerHeadCollision)
emu.addMemoryCallback(function(address,value)
 if pendingBlock and address==L.Block_PageLoc2+pendingBlock.slot then
  local actual=r('Block_X_Position',pendingBlock.slot)+256*value
  assert(actual==pendingBlock.x,'Head-triggered brick/reward origin must remain in the struck cell/page: '..actual..' vs '..pendingBlock.x)
  pendingBlock=nil
 end
end,emu.callbackType.write,L.Block_PageLoc2,L.Block_PageLoc2+1)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or(current and current.dir==1),
  left=current and current.dir==2,start=frame==200,a=current and age<10},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if current then
  age=age+1
  local x,y=worldX(),r('Player_Y_Position')
  local dy=y-current.lastY
  if dy>128 then dy=dy-256 elseif dy< -128 then dy=dy+256 end
  log:write(table.concat({index,age,current.power,current.tile,current.roof,current.dir,x,y,r('Player_X_Speed'),r('Player_Y_Speed')},',')..'\n');log:flush()
  assert(math.abs(x-current.lastX)<=2,'Samus head collision displaces X in case '..index..': '..current.lastX..' -> '..x)
  assert(math.abs(dy)<=5,'Samus head collision displaces Y in case '..index..': '..current.lastY..' -> '..y)
  assert(r('GameEngineSubroutine')==8 or r('GameEngineSubroutine')==9,'Head contact remains playable')
  current.lastX,current.lastY=x,y
 end
 if not current or age>=20 then
  if current then assert(current.contacts>0,'Every arena must exercise an actual head/block contact');assert(not pendingBlock,'Head block origin must be completed')end
  index=index+1;current=cases[index];age=0
  if not current then log:close();assert(contacts>=432,'Actual head/brick routine must be exercised in every arena');print('PASS Samus underground head contacts:432 brick/question-block, power-state, direction, ceiling-height, edge and page-seam cases without sudden displacement; '..contacts..' actual contacts');emu.stop(0);return end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  local first,last=current.wide and -32 or 0,current.wide and 32 or 0
  for dx=first,last,16 do w('Block_Buffer_1',current.tile,cell(current.x+dx,current.roof))end
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
  w('MmVY',252,2)
  w('SelectedCharacter',2);w('PlayerStatus',current.power);w('PlayerSize',0)
  w('AreaType',2);w('SwimmingFlag',0);w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestPowerupActive',0)
  w('SmCrouch',0);w('SmBall',0);w('SmPreviousDirections',0);w('SmFlip',0);w('CrouchingFlag',0)
  w('Player_X_Position',current.x);w('Player_PageLoc',current.x//256);w('Player_Y_Position',current.roof+12);w('Player_Y_HighPos',1)
  w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',252);w('Player_MovingDir',current.dir==1 and 2 or 1);w('PlayerFacingDir',current.dir==2 and 2 or 1)
  local camera=math.max(0,current.x-112)
  w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256);w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256)
  w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
  -- This authored upward airborne jump needs the same source jumped flag as
  -- an actual A launch. Character.groundAbove (pinned2.02, lines1717..1731)
  -- applies CIELING_DISPLACE only when jumped=true; separate zero-wall tests
  -- retain the jumped=false velocity-preservation controls.
  w('SmSourceJumped',1);w('SmCeilingHit',0)
  current.lastX,current.lastY=current.x,current.roof+12;current.contacts=0
 end
end,emu.eventType.endFrame)
