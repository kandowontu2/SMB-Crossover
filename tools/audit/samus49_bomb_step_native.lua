-- Initial arenas are seeded; the actual weapons loop, boost and cache run.
-- Six additional arenas create their bomb with genuine fresh controller B.
local C=assert(BOMB_STEP);local A,H=C.ram,C.hooks
local frame,index,depth=0,0,0
local current,pending,done=nil,false,false
local completed,failed,easyFailed,hardFailed,created=0,0,0,0,0
local log=assert(io.open(C.out..'events.jsonl','w'))
local function r(n,i)return emu.read(assert(A[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(A[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='boolean'then return v and'true'or'false'elseif v==nil then return'null'else return tostring(v)end
end
local function emit(v)log:write(json(v)..'\n');log:flush()end
local function hook(n,fn,interrupt)
 local h=assert(H[n],n)
 emu.addMemoryCallback(function()
  local address=emu.convertAddress(h.address)
  if not address or address.memType~=emu.memType.nesPrgRom or address.address//8192~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact physical bomb hook '..n)end
  if interrupt or depth==0 then fn()end
 end,emu.callbackType.exec,h.address)
end
for _,n in ipairs({'NMI','IRQ'})do hook(n,function()depth=depth+1 end,true)end
for _,n in ipairs({'NMIEnd','IRQEnd'})do hook(n,function()depth=depth-1;assert(depth>=0)end,true)end
local function put3(n,value)
 value=value&0xffffff;for i=0,2 do w(n,value>>(i*8),i)end
end
local function vector(n)local value=r(n)+256*r(n,1)+65536*r(n,2);return value>=0x800000 and value-0x1000000 or value end
local function position(n,page,fraction)return (r(n)+256*r(page))*65536+r(fraction)+256*r(fraction,1)end
local function snapshot()
 local s={x=position('Player_X_Position','Player_PageLoc','MmXFraction'),y=position('Player_Y_Position','Player_Y_HighPos','MmYFraction'),vx=vector('MmVX'),vy=vector('MmVY'),jumped=r('SmSourceJumped'),state=r('Player_State'),
  camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),right=r('ScreenRight_X_Pos')+256*r('ScreenRight_PageLoc'),horizontal=r('HorizontalScroll'),ppu=r('Mirror_PPUCTRL'),scroll=r('ScrollAmount'),parser=r('ScrollThirtyTwo'),dx=r('Player_X_Scroll'),speed=r('Player_X_Speed'),absolute=r('Player_XSpeedAbsolute'),last=r('MmLastXSpeed'),
  body=r('Player_BoundBoxCtrl'),relx=r('Player_Rel_XPos'),rely=r('Player_Rel_YPos'),boosted=r('SmBombBoosted',current.case.slot),slot=r('SmSlot'),bbox={}}
 for i=0,3 do s.bbox[i+1]=r('BoundingBox_UL_Corner',i)end
 return s
end
local function seed(c)
 current={case=c,age=0,helper=0,birth=false,errors={}};pending=false
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('RgEnemyStun',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('SmBombHits',0,i);w('SmBombBoosted',0,i);w('SmBombBlocksDone',1,i)end
 for _,n in ipairs({'TimerControl','InjuryTimer','DisableCollisionDet','GuestHurtTicks','GuestInvulTicks','GuestPowerupActive','GuestLegacyHurt','MmDeathFlag','MmDeathAge','SmCrouch','SmFlip','SmShootPose','SmPreviousDirections','MmJumpReleased','MmFrictionYActive','SwimmingFlag','Player_X_MoveForce','Player_Y_MoveForce','Player_YMoveForceFractional','EnemyFrenzyBuffer','EnemyFrenzyQueue','AreaParserTaskNum','GamePauseStatus','Platform_X_Scroll','A_B_Buttons','PreviousA_B_Buttons','SavedJoypadBits'})do w(n,0)end
 w('StarInvincibleTimer',255);w('SelectedCharacter',2);w('PlayerStatus',1);w('PlayerSize',0);w('CrossoverBehaviorVersion',c.mode);w('GameEngineSubroutine',8);w('AreaType',1)
 w('SmBall',c.ball);w('SmSourceJumped',c.jumped);w('Player_State',2);w('PlayerFacingDir',c.vx<0 and 2 or 1);w('Player_CollisionBits',3)
 w('Player_X_Position',c.world);w('Player_PageLoc',c.world//256);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('MmXFraction',c.fraction);w('MmXFraction',c.fraction>>8,1);w('MmYFraction',c.fraction);w('MmYFraction',c.fraction>>8,1)
 put3('MmVX',c.vx);put3('MmVY',0);w('Player_X_Speed',c.vx//4096);w('MmLastXSpeed',c.vx//4096);w('Player_XSpeedAbsolute',math.abs(c.vx//4096));w('Player_Y_Speed',0)
 local camera=c.world-112
 w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256);w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256);w('HorizontalScroll',camera)
 w('Mirror_PPUCTRL',0x90|((camera//256)&1));w('ScrollLock',c.camera==0 and 1 or 0);w('SideCollisionTimer',c.camera==2 and 7 or 0)
 w('ScrollAmount',1);w('ScrollThirtyTwo',7);w('Player_X_Scroll',1);w('Player_Pos_ForScroll',112)
 local body=c.ball==1 and 17 or 16;local offsets=C.bbox[tostring(body)]
 w('Player_BoundBoxCtrl',body);w('Player_Rel_XPos',112);w('Player_Rel_YPos',176)
 w('BoundingBox_UL_Corner',112+offsets[1]);w('BoundingBox_UL_Corner',176+offsets[2],1);w('BoundingBox_UL_Corner',112+offsets[3],2);w('BoundingBox_UL_Corner',176+offsets[4],3)
 w('InvOwnedLo',255,2);w('InvOwnedHi',255,2);w('InvSelected',0,2);w('InvRefill',0)
 if c.created then
  for i=c.slot+1,2 do w('SmBombAge',1,i);w('SmBombBoosted',1,i);w('SmBombX',0,i);w('SmBombPage',15,i);w('SmBombY',0,i)end
 else
  w('SmBombAge',57,c.slot);w('SmBombX',c.world+8,c.slot);w('SmBombPage',(c.world+8)//256,c.slot);w('SmBombY',201,c.slot)
 end
 emit({event='seed',case=index,fixture=c,frame=frame})
end
local function check(ok,message)if not ok then current.errors[#current.errors+1]=message end end
hook('Weapons',function()
 if done or frame<600 or r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not current then
  index=index+1
  if C.cases[index]then seed(C.cases[index])
  else
   done=true;log:close();local result={completed=completed,expected=#C.cases,failed_cases=failed,easy_failed=easyFailed,hard_failed=hardFailed,controller_created=created,frames=frame,route_proof=false}
   local f=assert(io.open(C.out..'result.json','w'));f:write(json(result));f:close();print('BOMB STEP cases='..completed..' failed='..failed..' created='..created);emu.stop(failed==0 and 0 or 1)
  end
 end
end)
hook('Drop',function()
 if not current or not current.case.created then return end
 assert(not current.birth,'One actual B-created bomb')
 assert(r('SmBall')==1 and r('A_B_Buttons')&0x40~=0 and r('PreviousA_B_Buttons')&0x40==0,'Genuine fresh controllerB Morph bomb')
 current.birth=true
end)
if H.Helper then hook('Helper',function()
 if current and current.before then current.helper=current.helper+1 end
end)end
hook('Boost',function()
 if not current or pending or r('SmSlot')~=current.case.slot or r('SmBombBoosted',current.case.slot)~=0 then return end
 if current.case.created then assert(current.birth,'Actual created bomb before boost')end
 assert(emu.getState()['cpu.x']==current.case.slot,'Actual bomb slot at boost entry')
 current.before=snapshot()
end)
hook('Post',function()
 if not current or pending or not current.before or r('SmSlot')~=current.case.slot then return end
 local c,b=current.case,current.before;local after=snapshot();local boost=math.floor(-230/120*65536+0.5)
 local vx=c.mode==0 and math.max(-81920,math.min(81920,b.vx))or b.vx
 local expectedX=b.x+(c.mode==0 and vx or 0);local expectedY=b.y+(c.mode==0 and boost or 0)
 check(after.x==expectedX,'Source immediate worldX/fraction');check(after.y==expectedY,'Source immediate worldY/fraction')
 check(after.vx==vx and after.vy==boost,'Source horizontal cap and230 boost')
 check(after.jumped==(c.mode==0 and b.jumped or 1),'Easy preserves jumped history; Hard explicitly sets it')
 check(after.boosted==1 and after.state==1 and after.slot==c.slot and emu.getState()['cpu.x']==c.slot,'One boost and preserved native bomb index')
 check(current.helper==(c.mode==0 and 1 or 0),'Only Easy enters additional update helper')
 local camera=b.camera
 if c.mode==0 then
  local dx=(expectedX//65536)-(b.x//65536);local advance=0
  if c.camera==1 and dx>0 then advance=math.min(dx,math.max(0,expectedX//65536-camera-112))end
  camera=camera+advance
  check(after.dx==(b.dx+dx)&255,'Total native displacement receipt')
  check(after.speed==(vx//4096)&255 and after.last==after.speed and after.absolute==math.abs(vx//4096),'Native velocity mirrors')
  check(after.scroll==(b.scroll+advance)&255 and after.parser==(b.parser+advance)&255,'Coherent accumulated scroll/parser receipts')
  check(after.relx==((expectedX//65536-camera)&255)and after.rely==((expectedY//65536)&255),'Fresh native relative hitpoint position')
  local body=c.ball==1 and 17 or 16;local offsets=C.bbox[tostring(body)]
  check(after.body==body,'Native postboost shape selection')
  for i=1,4 do local value=(i%2==1 and after.relx or after.rely)+offsets[i];check(after.bbox[i]==(value&255),'Fresh native hitpoint endpoint'..i)end
 else
  check(after.dx==b.dx and after.scroll==b.scroll and after.parser==b.parser and after.body==b.body,'Hard native receipts remain unchanged')
  for i=1,4 do check(after.bbox[i]==b.bbox[i],'Hard keeps existing native cache'..i)end
 end
 check(after.camera==camera and after.right==camera+255 and after.horizontal==(camera&255),'Camera/page coordinates')
 check(after.ppu==(0x90|((camera//256)&1)),'Nametable mirror preserves existing bits')
 if c.created then created=created+1 end
 if #current.errors>0 then failed=failed+1;if c.mode==0 then easyFailed=easyFailed+1 else hardFailed=hardFailed+1 end end
 completed=completed+1;emit({event='result',case=index,fixture=c,before=b,after=after,errors=current.errors,helper=current.helper,frame=frame});pending=true
end)
emu.addEventCallback(function()
 local b={}
 if frame<550 then b.start=frame==60 or frame==240;b.right=frame==80 or frame==100
 elseif current and current.case.created and not current.birth then b.b=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if pending then current=nil;pending=false elseif current then current.age=current.age+1;assert(current.age<150,'Actual bomb reaches source boost in bounded time')end
 assert(frame<15000,'Bounded native bomb matrix')
end,emu.eventType.endFrame)
