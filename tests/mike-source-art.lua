-- Ordinary cold Mike selection, then labeled arranged component arenas.
-- Physical collection, B releases, enemy defeat/drop and actual DMA are real
-- game paths. Initial actor/health arrangements are not campaign certificates.
local frame,t,entered=0,0,false
local upper=0;local chr={};local pickups,kills,drops=0,0,0
local seenStar,seenHeart,seenNova0,seenNova1=0,0,0,0
local rows=assert(io.open(TEST_DIR..'native.csv','w'))
rows:write('frame,t,health,stars,drop0,kills,drops,sfx,chr4,chr5,enemyFlag,enemyState,enemyX,enemyY,enemyHP,kind5,shotX5,shotY5,tier,attack,logic,oam\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function put(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function bank()local p=emu.convertAddress(emu.getState()['cpu.pc']);return p and p.address//8192 or -1 end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)chr[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x5127)
emu.addMemoryCallback(function(_,v)if entered and v==0x20 then pickups=pickups+1 end end,emu.callbackType.write,L.Square2SoundQueue)
emu.addMemoryCallback(function()if entered and bank()==B.ShellOrBlockDefeat then kills=kills+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function()
 if entered and bank()==B.JnEnemyDrop then
  drops=drops+1
  local slot=emu.getState()['cpu.x']
  -- Explicit source of randomness for two reproducible native drop cases.
  w('PseudoRandomBitReg',(t<450)and 1 or 0,slot+1)
 end
end,emu.callbackType.exec,L.JnEnemyDrop)
local function clear()
 for i=0,5 do w('Enemy_Flag',0,i);put(0x5c20+i,0);put(0x5c50+i,0);put(0x5c56+i,0);put(0x5c5c+i,0);put(0x5c78+i,0)end
 for i=0,3 do put(0x5c64+i,0)end
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0);put(0x5c05,0);put(0x5c06,0);put(0x5c08,0)
end
local function drop(kind)
 clear();put(0x5c64,kind);put(0x5c68,128);put(0x5c6c,0);put(0x5c70,184);put(0x5c74,0)
end
local function enemy()
 clear()
 w('Enemy_Flag',1,0);w('Enemy_ID',6,0);w('Enemy_State',0,0)
 w('Enemy_X_Position',100,0);w('Enemy_PageLoc',0,0);w('Enemy_Y_Position',184,0);w('Enemy_Y_HighPos',1,0)
 w('Enemy_X_Speed',0,0);w('Enemy_Y_Speed',0,0);w('Enemy_MovingDir',2,0);w('Enemy_BoundBoxCtrl',9,0);w('Enemy_CollisionBits',0,0)
end
emu.addEventCallback(function()
 local buttons={}
 if not entered and frame>=60 and frame%12==0 then
  if r('CrossoverMenuState')~=2 then buttons.start=true
  else
   local index=r('CrossoverMenuIndex')
   if index<12 then buttons.down=true
   elseif index~=15 then buttons.right=true else buttons.a=true end
  end
 elseif entered then
  buttons.right=(t>=45 and t<85)or(t>=135 and t<175)
  buttons.b=(t>=201 and t<208)or(t>=241 and t<248)or(t>=361 and t<368)or(t>=481 and t<488)
 end
 emu.setInput(buttons,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==16,'Actual menu selects Mike')
  entered=true;w('CrossoverBehaviorVersion',BEHAVIOR);clear()
 end
 if not entered then assert(frame<700,'Cold menu entry timeout');return end
 t=t+1
 if t==1 then put(0x5f30,4);put(0x5f31,3);put(0x5f3e,0);drop(2)end
 if t==90 then assert(read(0x5c64)==0 and read(0x5f3e)==1,'Physical star collection adds one star');drop(1);put(0x5f30,2)end
 if t==180 then
  assert(read(0x5c64)==0 and read(0x5f30)==4,'Physical small heart heals one full heart')
  clear();put(0x5f31,11);put(0x5f30,22);put(0x5f32,2)
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('Enemy_X_Position',84,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('PowerUpType',1,5);w('InvPickupOwner',16,5);w('InvPickup',0x83,5)
 end
 if t==200 then assert(read(0x5f32)==3 and read(0x5c0c)==3,'Physical Nova pickup enables its actual primary');clear()end
 if t==225 then
  local name={}
  for i=0,4 do
   local tile=emu.read(0x2030+i,emu.memType.nesPpuDebug)
   name[#name+1]=(tile>=10 and tile<=35)and string.char(65+tile-10)or' '
  end
  assert(table.concat(name)=='NOVA ','Visible HUD follows the effective Nova tier after physical collection')
 end
 if t==351 or t==471 then enemy()end
 if t==450 then assert(kills>=1 and drops>=1,'Real B projectile defeat generates a physical star')end
 if t==590 then assert(kills>=2 and drops>=2,'Second real B defeat generates a physical heart')end
 local oam={};local stars,hearts=0,0
 for i=0,63 do
  local a=i*4;local y=emu.read(a,emu.memType.nesSpriteRam);local tile=emu.read(a+1,emu.memType.nesSpriteRam)
  for k=0,3 do oam[#oam+1]=string.format('%02x',emu.read(a+k,emu.memType.nesSpriteRam))end
  if y<240 then
   if tile==109 then stars=stars+1;assert(chr[5]==711,'Star DMA uses its committed item page')end
   if tile==103 then hearts=hearts+1;assert(chr[5]==711,'Heart DMA uses its committed item page')end
   if t>210 and t<320 then
    if tile==17 then seenNova0=seenNova0+1;assert(chr[4]==710,'Nova phase0 committed page')end
    if tile==19 then seenNova1=seenNova1+1;assert(chr[4]==710,'Nova phase1 committed page')end
   end
  end
 end
 if t>=10 and t<40 then assert(stars==2,'Native star has both source halves');seenStar=seenStar+1 end
 if t>=100 and t<130 then assert(hearts==2,'Native small heart has both source halves');seenHeart=seenHeart+1 end
 rows:write(table.concat({frame,t,read(0x5f30),read(0x5f3e),read(0x5c64),kills,drops,pickups,chr[4]or-1,chr[5]or-1,r('Enemy_Flag'),r('Enemy_State'),r('Enemy_X_Position'),r('Enemy_Y_Position'),read(0x5c50),read(0x5c25),read(0x5c2b),read(0x5c37),read(0x5c0c),read(0x5c05),r('FrameCounter'),table.concat(oam)},',')..'\n')
 if t>=2 then local p=assert(io.open(TEST_DIR..'frame-'..t..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
 if t==610 then
  assert(seenStar==30 and seenHeart==30 and seenNova0>0 and seenNova1>0,'Actual DMA exposes complete food and both outbound Nova phases')
  assert(pickups>=3,'Real physical pickups queue their sound')
  local result=assert(io.open(TEST_DIR..'result.json','w'))
  result:write(string.format('{"passed":true,"behavior":%d,"star_frames":%d,"heart_frames":%d,"nova_phase0":%d,"nova_phase1":%d,"kills":%d,"drop_calls":%d,"pickup_sfx":%d}',BEHAVIOR,seenStar,seenHeart,seenNova0,seenNova1,kills,drops,pickups));result:close()
  rows:close();print('PASS Mike source-art physical collection/B-release/enemy-drop/DMA component arena');emu.stop(0)
 end
end,emu.eventType.endFrame)
