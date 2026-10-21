-- Explicit native-terrain unit arenas. These writes do not prove traversal.
-- Actual controller input warms native side contact and then requests a jump.
-- The reference is pinned Ryu.as pressJmpBtn / groundOnSide, not current code.
dofile(TEST_DIR..'menu-bootstrap.lua')
local cases={}
for _,kind in ipairs({'ground','water','stale','ceiling','wall-away','wall-top','neutral','neutral-water','away','away-water'})do
 for dir=1,2 do cases[#cases+1]={kind=kind,dir=dir}end
end
local frame,index,age=0,0,-1
local active,interruptDepth,firstJump= nil,0,false
local contactSeen,wallSeen,removed,launchCount=false,false,false,0
local launches,failures={},{}
local sourceLaunchVy,ceilingReceipts=nil,0
local ceilingLater
local jumpRequestAge,contactBeforeLaunch=nil,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function px()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function signed(v)return v>=0x800000 and v-0x1000000 or v end
local function vx()return signed(r('MmVX')+256*r('MmVX',1)+65536*r('MmVX',2))/65536 end
local function velocity()return signed(r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2))/65536 end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced fixture interrupt scope')end,emu.callbackType.exec,pc)
end
local out=assert(io.open(OUTPUT..ROM_NAME..'-ryu-ground-wall-updates.csv','w'))
out:write('case,kind,dir,frame,age,event,x,y,state,wall,contact,lock,fresh,raw,vy,launchVy,swimming,underwater,areaType,vx\n')
local summary=assert(io.open(OUTPUT..ROM_NAME..'-ryu-ground-wall-cases.csv','w'))
summary:write('case,kind,dir,contactSeen,wallSeen,firstJumpY,firstJumpVy,firstJumpWall,firstJumpLock,launchVy,vx,result\n')
local function row(event,launchVy)
 out:write(table.concat({index,active.kind,active.dir,frame,age,event,px(),r('Player_Y_Position'),r('Player_State'),r('XgWall'),r('XgWallContact'),r('XgWallLock'),r('XgFresh'),r('SavedJoypadBits'),velocity(),launchVy or '',r('SwimmingFlag'),r('MmUnderwater'),r('AreaType'),vx()},',')..'\n');out:flush()
end
local function cell(x,y,value)
 local off=(x//256)%2*208+((y-32)//16)*16+(x%256)//16
 w('Block_Buffer_1',value,off);w('MmSolidTerrain',value==0 and 0 or 1,off)
end
local function wall(value)
 local wx=active.wallX
 for y=active.wallY,192,16 do cell(wx,y,value)end
end
local function setup(q)
 assert(r('SelectedCharacter')==10,'Real menu selects Ryu before isolated unit arenas')
 active=q;ceilingLater=nil;firstJump=false;contactSeen=false;wallSeen=false;removed=false;launchCount=0;launches={};sourceLaunchVy=nil;ceilingReceipts=0;jumpRequestAge=nil;contactBeforeLaunch=false
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do cell(p*256+col*16,208,0x54)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 local air=q.kind:sub(1,4)=='wall'
 q.noWall=q.kind=='neutral'or q.kind=='neutral-water'or q.kind=='away'or q.kind=='away-water'
 q.wallX=q.dir==1 and(air and 112 or 256)or(air and 128 or 128)
 q.wallY=air and 160 or 144
 q.startX=q.noWall and 176 or q.dir==1 and(air and 97 or 232)or(air and 145 or 154)
 q.startY=air and 150 or 176
 if not q.noWall then wall(0x61)end
 if q.kind=='ceiling'then for wx=q.startX-16,q.startX+32,16 do cell((wx//16)*16,160,0x61)end end
 w('Player_X_Position',q.startX%256);w('Player_PageLoc',q.startX//256)
 w('Player_Y_Position',q.startY);w('Player_Y_HighPos',1);w('Player_State',air and 1 or 0)
 w('PlayerStatus',0);w('PlayerSize',0);w('PlayerFacingDir',q.dir);w('Player_MovingDir',q.dir)
 w('Player_Y_Speed',0);w('Player_X_Speed',0);w('Player_CollisionBits',255);w('SideCollisionTimer',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestPowerupActive',0)
 w('PlayerChangeSizeFlag',0);w('DisableCollisionDet',0);w('InjuryTimer',0);w('StarInvincibleTimer',0)
 for _,n in ipairs({'GuestHurtKind','GuestHurtTicks','GuestInvulTimer','GuestFlickerPhase','GuestVisible','LsrHurtFlags','RgCrouch','RgAttack','RgCooldown','RgPreviousButtons','A_B_Buttons','PreviousA_B_Buttons','XgWall','XgWallLock','XgWallContact','XgCeiling','XgDash','XgJumpUsed','XgHoverActive','MmJumpReleased','MmFrictionYActive'})do
  if L[n]then w(n,0)end
 end
 -- V3-MIGRATION-GROUND-BEGIN: reset the complete new persistent wall state
 -- only inside this explicitly teleported component arena. Old48 has no fields.
 for _,n in ipairs({'RyWallEdge','RyWallPage','RyWallSide','RyWallResolved','RyWallBlocked','RyWallSupported','RyWallWasGround','RyWallOldHeight','RyWallOldX','RyWallOldPage','RyWallOldXFine','RyWallOldXFrac','RyWallOldY','RyWallOldYFine','RyWallOldYFrac','RyWallScanY','RyWallScanLast'})do
  if L[n]then w(n,0)end
 end
 -- V3-MIGRATION-GROUND-END
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local water=q.kind:find('water',1,true)~=nil
 w('SwimmingFlag',water and 1 or 0);w('AreaType',water and 0 or 1);w('MmUnderwater',water and 1 or 0)
 local camera=air and 0 or 96
 w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',(camera+255)%256);w('ScreenRight_PageLoc',(camera+255)//256)
 row('setup')
end
-- Remove a previously contacted wall exactly before the real launch update.
-- This tests stale contact admission; no player state/contact bit is injected.
emu.addMemoryCallback(function()
 if not active or interruptDepth~=0 or r('CurrentBank')%128~=30 then return end
 if active.kind=='stale'and age>=16 and not removed and r('SavedJoypadBits')&128~=0 then
  assert(contactSeen,'Stale control first acquired an actual native wall contact')
  wall(0);removed=true;row('remove-previous-wall')
 end
end,emu.callbackType.exec,assert(L.ExpandedMovement))
emu.addMemoryCallback(function(_,value)
 if not active or interruptDepth~=0 or r('CurrentBank')%128~=30 then return end
 if age>=16 and value&128~=0 then
  launchCount=launchCount+1
  if launchCount==1 then contactBeforeLaunch=r('Player_State')==0 and r('XgWallContact')&active.dir~=0 end
  row('fresh-A')
 end
end,emu.callbackType.write,assert(L.XgFresh))
emu.addMemoryCallback(function(_,value)
 if not active or interruptDepth~=0 or age<16 or age>22 then return end
 local v=signed(value*65536+256*r('MmVY',1)+r('MmVY'))/65536
 if v<0 then
  launches[#launches+1]=v
  local expected=active.kind:find('water',1,true)and -400/120 or active.kind=='wall-away'and -300/120 or active.kind=='wall-top'and -430/120 or -540/120
  if math.abs(v-expected)<1/65536 then sourceLaunchVy=v end
  row('negative-vy-write',v)
 end
end,emu.callbackType.write,assert(L.MmVY)+2)
emu.addMemoryCallback(function()
 if not active or interruptDepth~=0 or r('CurrentBank')%128~=0 then return end
 if age<16 then
  if r('XgWallContact')&active.dir~=0 and r('Player_State')==0 then contactSeen=true end
  if r('XgWall')~=0 then wallSeen=true end
 end
 row('completed-collision',launches[1])
 if active.kind=='ceiling'and firstJump and r('Player_Y_Speed')<128 and velocity()>=0 then ceilingLater={age=age,vy=velocity()}end
 if age>=16 and launchCount>0 and not firstJump then
  firstJump={age=age,yFraction=r('MmYFraction')+256*r('MmYFraction',1),y=r('Player_Y_Position'),vy=velocity(),wall=r('XgWall'),lock=r('XgWallLock'),state=r('Player_State'),yspeed=r('Player_Y_Speed'),vx=vx(),launchVy=sourceLaunchVy}
 end
end,emu.callbackType.exec,assert(L.GuestPostEnemyCollision))
emu.addMemoryCallback(function(_,value)
 if active and active.kind=='water'and age<23 then
  local st=emu.getState();row('underwater-write-'..value..'-pc'..st['cpu.pc']..'-bank'..r('CurrentBank'))
 end
end,emu.callbackType.write,assert(L.MmUnderwater))
emu.addMemoryCallback(function()
 if active and age>=16 and interruptDepth==0 and r('CurrentBank')%128==1 then ceilingReceipts=ceilingReceipts+1;row('actual-native-ceiling-stop')end
end,emu.callbackType.exec,assert(L.NYSpd))
local function finish()
 local q,j=active,firstJump
 local errors={}
 local function check(v,message)if not v then errors[#errors+1]=message end end
 check(j,'actual fresh-A update was completed')
 if q.kind:sub(1,4)=='wall'then
  check(wallSeen,'ordinary input acquired real wall attachment')
  if j then
   local expected=q.kind=='wall-top'and -430/120 or -300/120
   check(j.launchVy and math.abs(j.launchVy-expected)<1/65536,'genuine wall launch retains source speed')
   check(j.vy<0 and j.wall==0 and j.lock>1,'genuine wall launch retains detach lock and rises')
  end
 else
  if not q.noWall then check(contactSeen and contactBeforeLaunch,'ordinary input acquired actual grounded side contact, still present at actual fresh-A launch')end
  if j then
   local expected=q.kind:find('water',1,true)and -400/120 or -540/120
   check(j.launchVy and math.abs(j.launchVy-expected)<1/65536,'normal jump uses source launch speed')
   if q.kind=='ceiling'then
    -- SOURCE-CEILING-V: Ryu's largest unrotated HRect is27 NES pixels;
    -- foot=PY+32, roof bottom176. First launch -540/120 plus gravity
    -- 1400/7200 yields qVY=-282169 and top176.69444, strictly disjoint.
    -- A genuine head collision follows on a later update, not this first one.
    -- Original native-stop-at-first-update failures remain in the private run.
    local expectedVy=-294912+12743
    local actualYQ=j.y*65536+j.yFraction
    check(actualYQ==176*65536+expectedVy and math.abs(j.vy-expectedVy/65536)<1/131072,'source-disjoint first launch preserves exact integrated Y and VY')
    check(actualYQ+5*65536>176*65536 and j.yspeed>=128,'largest27px source envelope is disjoint and continues rising')
    check(ceilingReceipts>0 and ceilingLater and ceilingLater.age>j.age,'actual later overhead collision still reaches native stop and stops rising motion')
   else check(j.y<q.startY and j.vy<0 and j.wall==0,'first ground-launch update rises before wall attachment')end
  end
 end
 if q.noWall and j then
  local expected=q.kind:sub(1,4)=='away'and(q.dir==1 and -185/120 or 185/120)or 0
  check(math.abs(j.vx-expected)<1/65536,'source neutral/away horizontal velocity '..j.vx..' expected '..expected)
 end
 local result=#errors==0 and 'PASS'or table.concat(errors,'; ')
 summary:write(table.concat({index,q.kind,q.dir,tostring(contactSeen),tostring(wallSeen),j and j.y or '',j and j.vy or '',j and j.wall or '',j and j.lock or '',j and j.launchVy or '',j and j.vx or '',result},',')..'\n');summary:flush()
 if #errors>0 then failures[#failures+1]=q.kind..'/'..q.dir..': '..result end
 active=nil
end
emu.addEventCallback(function()
 local air=active and active.kind:sub(1,4)=='wall'
 if active and age>=16 and not jumpRequestAge then
  local ready=air and r('XgWall')~=0 or not air and r('Player_State')==0 and(active.noWall or r('XgWallContact')&active.dir~=0)
  if ready then jumpRequestAge=age end
 end
 local away=active and active.kind=='wall-away'and jumpRequestAge~=nil
 local dir=active and(away and 3-active.dir or active.dir)
 if active and active.noWall then
  dir=jumpRequestAge and active.kind:sub(1,4)=='away'and 3-active.dir or nil
 end
 emu.setInput({down=frame==80,right=frame>=100 and frame<180 and(frame-100)%20==0 or(dir==1),left=dir==2,
  start=frame==240,a=jumpRequestAge and age-jumpRequestAge<6,up=air and not jumpRequestAge},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<640 then return end
 age=age+1
 if age%80==0 then
  age=0;index=index+1
  if not cases[index]then
   out:close();summary:close()
   for _,message in ipairs(failures)do print('DIAGNOSTIC '..message)end
   assert(#failures==0,'Pinned Ryu ground/previous-ground wall admission controls: '..#failures..' failing arenas')
   print('PASS Ryu grounded launch, genuine wall jump, stale contact, real ceiling, underwater and neutral/away VX source controls: '..#cases..' actual-input arenas');emu.stop(0);return
  end
  setup(cases[index])
 elseif age==70 then finish()end
end,emu.eventType.endFrame)
