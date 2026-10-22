-- Brick debris origins need suit0/1 head breaking, the original-source EASY
-- rule; pinned2.02 HARD bumps in every suit. Wall/ceiling controls are shared.
SelectEasyRules()
-- Explicit collision arenas, not a controller-only clear. Inputs after the
-- first contact are ordinary controls. Expectations come from pinned 2.02
-- Character.groundAbove/groundOnSide and the authored 16px terrain cells.
-- In particular, groundOnSide separates zero/away contacts too; it cancels
-- velocity only when that velocity points into the contacted wall.
local frame,index,age,depth=0,0,0,0
local cases,current={},nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)return r(n)+256*r(n,1)+65536*r(n,2)end
local function setq(n,v)for i=0,2 do w(n,(v//256^i)%256,i)end end
local function wx(n,p,i)return r(n,i)+256*r(p,i)end
local function px()return wx('Player_X_Position','Player_PageLoc')end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
-- Foreground code at a label's actual physical PRG bank (fixed banks included).
local function actual(n)
 if depth~=0 then return false end
 local p=emu.convertAddress(assert(L[n],n))
 return p and p.memType==emu.memType.nesPrgRom and p.address//8192==assert(B[n],n)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced collision interrupt scope')end,emu.callbackType.exec,pc)
end
local log=assert(io.open(OUTPUT..ROM_NAME..'-samus-zero-wall-contact.csv','w'))
log:write('case,kind,age,form,side,motion,power,tile,x,y,vx,vy,heads,walls\n')
local totals={head=0,wall=0,brick=0,reward=0,rise=0}

-- The first case reproduces the real replay: origin nibble3, 0x51 becomes
-- 0x23, and the following head pass used to skip native ceiling separation.
cases[#cases+1]={kind='head',base=1232,x=1235,roof=144,power=0,tile=0x51,dir=0,jumped=true,form='air',limit=20,wide=true}
for _,power in ipairs({0,1,2})do for _,base in ipairs({112,256})do
 for _,offset in ipairs({-12,2,3,4,12,13})do for _,dir in ipairs({0,1,2})do
  cases[#cases+1]={kind='head',base=base,x=base+offset,roof=144,power=power,tile=0x51,dir=dir,jumped=true,form='air',limit=20,wide=false}
 end end
end end
for _,tile in ipairs({0xc1,0xc0})do for _,power in ipairs({0,1,2})do
 for _,base in ipairs({112,256})do for _,offset in ipairs({-12,3,13})do
  cases[#cases+1]={kind='head',base=base,x=base+offset,roof=96,power=power,tile=tile,dir=0,jumped=true,form='air',limit=20,wide=false}
 end end
end end
-- Source jumped=false preserves velocity; Morph Ball removes only the
-- ceiling bump cue. Neither condition permits horizontal ceiling snaps.
for _,form in ipairs({'air','ball'})do for _,jumped in ipairs({false,true})do
 cases[#cases+1]={kind='head',base=256,x=259,roof=144,power=0,tile=0x54,dir=0,jumped=jumped,form=form,limit=1,wide=false}
end end
cases[#cases+1]={kind='head',base=256,x=259,roof=144,power=0,tile=0xc1,dir=0,jumped=true,form='air',limit=90,wide=false,rise=true}
-- Integer and subpixel velocities include a native X-speed mirror of zero.
for _,boundary in ipairs({128,256,512})do for _,side in ipairs({1,2})do
 for _,form in ipairs({'ground','air','ball','crouch'})do
  for _,motion in ipairs({'zero','toward','away','towardSub','awaySub'})do
   for _,depth in ipairs({1,3})do
    cases[#cases+1]={kind='wall',boundary=boundary,side=side,form=form,motion=motion,depth=depth,power=1,tile=0x54,limit=1}
   end
  end
 end
end end

local function setup(c)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('EnemyMetasprite',0,i)end
 for i=0,1 do
  w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)
  w('MmXFraction',0,i);w('MmYFraction',0,i)
 end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i)end
 setq('MmVX',0);setq('MmVY',0)
 w('SelectedCharacter',2);w('PlayerStatus',c.power);w('PlayerSize',0)
 w('AreaType',2);w('SwimmingFlag',0);w('GameEngineSubroutine',8);w('TimerControl',0)
 w('GuestPowerupActive',0);w('GuestHurtTicks',0);w('DisableCollisionDet',0)
 w('SmCrouch',c.form=='crouch' and 1 or 0);w('SmBall',c.form=='ball' and 1 or 0)
 w('SmPreviousDirections',0);w('SmFlip',0);w('CrouchingFlag',c.form=='crouch' and 4 or 0)
 if L.SmCeilingHit then w('SmCeilingHit',0);w('SmSourceJumped',c.jumped and 1 or 0)end
 w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0);w('MmBlockAttack',0)
 w('Square1SoundQueue',0);w('Square2SoundQueue',0);w('NoiseSoundQueue',0)
 c.heads,c.walls,c.origin,c.debris,c.pickup=0,0,nil,0,nil
 local x,y,state,vx=0,0,1,0
 if c.kind=='head' then
  x=c.x;c.headOffset=c.form=='ball' and 19 or 7
  c.expectedY=c.roof+16-c.headOffset
  y=c.expectedY-4
  if c.wide then for dx=-16,32,16 do w('Block_Buffer_1',c.tile,cell(c.base+dx,c.roof))end
  else w('Block_Buffer_1',c.tile,cell(c.base,c.roof))end
  setq('MmVY',-4*65536);w('Player_Y_Speed',252)
 else
  local sign=c.side==1 and 1 or -1
  local direction=c.motion:find('away',1,true) and -sign or sign
  if c.motion~='zero' then vx=direction*(c.motion:find('Sub',1,true) and 16384 or 98304)end
  c.expectedX=c.side==1 and c.boundary-15 or c.boundary-1
  x=c.expectedX+sign*c.depth
  y=(c.form=='ground' or c.form=='crouch') and 176 or 90
  state=(c.form=='ground' or c.form=='crouch') and 0 or 1
  local wallX=c.side==1 and c.boundary or c.boundary-16
  for yy=64,192,16 do w('Block_Buffer_1',c.tile,cell(wallX,yy))end
  setq('MmVX',vx);w('Player_X_Speed',math.floor(vx/65536));w('Player_Y_Speed',0)
  c.expectedVX=(direction==sign and c.motion~='zero') and 0 or vx%16777216
  c.expectedNativeVX=c.expectedVX==0 and 0 or math.floor(vx/65536)%256
  -- Source assigns an integer boundary, discarding old position remainder.
  w('MmXFraction',0x65);w('MmXFraction',0x43,1);w('Player_X_Scroll',1)
 end
 w('Player_X_Position',x);w('Player_PageLoc',x//256)
 w('Player_Y_Position',y);w('Player_Y_HighPos',1);w('Player_State',state)
 if c.kind=='head' then w('Player_X_Speed',0)end
 w('Player_MovingDir',c.dir==2 and 2 or 1);w('PlayerFacingDir',c.dir==2 and 2 or 1)
 local camera=math.max(0,x-112)
 w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256)
 w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256)
 c.lastX,c.lastY=x,y
end

local function finish(c)
 if c.kind=='wall' then
  assert(c.walls>0,'Every wall arena must exercise actual native StopPlayerMove, case '..index)
  totals.wall=totals.wall+1
 else
  if c.tile~=0x54 then
   assert(c.heads>0,'Every effect arena exercises actual PlayerHeadCollision, case '..index)
   assert(c.origin and c.origin.xWritten and c.origin.yWritten,'Actual effect cell/page and row were observed')
   if c.tile==0x51 and c.power<2 then assert(c.debris>0,'Breakable brick exercises real debris creation')end
   if c.tile==0xc1 then assert(c.pickup,'Mushroom/question block creates a real world pickup')end
  end
  if c.rise then
   assert(c.pickup.steps>=16,'Mushroom completes its sixteen-pixel rise in the world')
   assert(c.pickup.mature,'Mushroom becomes available after its real rise')
   totals.rise=totals.rise+1
  end
  totals.head=totals.head+1
 end
end

emu.addMemoryCallback(function()
 if frame<550 or not actual('PlayerBGCollision')then return end
 if not current then
  index=index+1;current=cases[index];age=0
  if not current then
   log:close()
   assert(totals.head>140 and totals.wall==240 and totals.brick>0 and totals.reward>0 and totals.rise==1,'Entire independent matrix completed')
   print('PASS Samus source ceiling separation and zero/away/toward wall controls: '..totals.head..' head arenas, '..totals.wall..' wall arenas, '..totals.brick..' debris origins, '..totals.reward..' question pickups, real mushroom rise')
   emu.stop(0);return
  end
  setup(current)
 end
 -- Actual gameplay updates may be separated by several hardware frames.
 -- Advance/check only at this native collision invocation.
 -- These are authored arenas: discard background streaming work from the
 -- boot level, which must not insert its pipes into the test's empty cells.
 w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 current.enterX,current.enterY=px(),r('Player_Y_Position')
end,emu.callbackType.exec,L.PlayerBGCollision)

emu.addMemoryCallback(function()
 if not current or not actual('PlayerHeadCollision')or current.kind~='head' then return end
 local c=current;c.heads=c.heads+1
 local x=px();local expected
 for _,offset in ipairs({8,2,13})do
  local probe=x+offset
  if r('Block_Buffer_1',cell(probe,c.roof))~=0 then expected=(probe//16)*16;break end
 end
 assert(expected,'Actual head effect resolves against an authored cell before erasure')
 c.origin={x=expected,y=c.roof,slot=r('SprDataOffset_Ctrl')}
end,emu.callbackType.exec,L.PlayerHeadCollision)

emu.addMemoryCallback(function()
 if current and actual('SamusStopAtWall')then current.walls=current.walls+1 end
end,emu.callbackType.exec,L.SamusStopAtWall)

emu.addMemoryCallback(function(address,value)
 local o=current and current.origin
 if not o then return end
 if address==L.Block_PageLoc2+o.slot then
  assert(r('Block_X_Position',o.slot)+256*value==o.x,'Block origin stays in the independently struck cell/page')
  o.xWritten=true
 end
end,emu.callbackType.write,L.Block_PageLoc2,L.Block_PageLoc2+1)
emu.addMemoryCallback(function(address,value)
 local o=current and current.origin
 if o and not o.yWritten and address==L.Block_Y_Position+o.slot then
  assert(value==o.y,'Pre-effect ceiling separation must preserve the authored block row')
  o.yWritten=true
 end
 if o and o.awaitChunk and address==L.Block_Y_Position+o.slot+2 then
  assert(value==o.y+8,'Lower brick debris starts eight pixels below the actual cell')
  assert(wx('Block_X_Position','Block_PageLoc',o.slot+2)==o.x,'Mirrored brick debris keeps the actual world cell/page')
  o.awaitChunk=false
 end
end,emu.callbackType.write,L.Block_Y_Position,L.Block_Y_Position+3)
emu.addMemoryCallback(function()
 local c=current;local o=c and c.origin
 if not o or not actual('SpawnBrickChunks')then return end
 assert(wx('Block_X_Position','Block_PageLoc',o.slot)==o.x and r('Block_Y_Position',o.slot)==o.y,'Brick debris uses original authored effect origin')
 o.awaitChunk=true;c.debris=c.debris+1;totals.brick=totals.brick+1
end,emu.callbackType.exec,L.SpawnBrickChunks)
emu.addMemoryCallback(function()
 local c=current;local o=c and c.origin
 if not o or not actual('SetupPowerUp')then return end
 local slot=emu.getState()['cpu.x']
 assert(wx('Block_X_Position','Block_PageLoc',o.slot)==o.x and r('Block_Y_Position',o.slot)==o.y,'Question reward uses actual struck cell before emergence')
 c.pickup={slot=slot,x=o.x,y=o.y-8,steps=0,initial=false,mature=false}
 totals.reward=totals.reward+1
end,emu.callbackType.exec,L.SetupPowerUp)
emu.addMemoryCallback(function(address,value)
 local p=current and current.pickup
 if p and not p.initial and address==L.Enemy_Y_Position+p.slot then
  assert(value==p.y,'Pickup first appears eight pixels above the authored block origin')
  assert(wx('Enemy_X_Position','Enemy_PageLoc',p.slot)==p.x,'Pickup starts in its real block cell/page')
  p.initial=true
 end
end,emu.callbackType.write,L.Enemy_Y_Position,L.Enemy_Y_Position+5)

emu.addMemoryCallback(function()
 if not current or not actual('MegaMan202AfterBG')then return end
 local c=current;age=age+1
 if c.kind=='wall' then
  assert(px()==c.expectedX,'Source separates a real '..c.form..' wall contact even with '..c.motion..' motion, case '..index..': '..px()..' vs '..c.expectedX)
  assert(q('MmVX')==c.expectedVX,'Only toward-wall Q8.16 velocity is cancelled, case '..index)
  assert(r('Player_X_Speed')==c.expectedNativeVX,'Away/zero native velocity mirror is preserved')
  assert(r('MmXFraction')==0 and r('MmXFraction',1)==0 and r('Player_X_Scroll')==0,'Real wall boundary clears old position and scroll remainders')
 else
  assert(math.abs(px()-c.lastX)<=2,'Ceiling must not misclassify as a sixteen-pixel side step, case '..index..': '..c.lastX..' -> '..px())
  if age==1 then
   assert(r('Player_Y_Position')==c.expectedY,'Ascending head is separated to source groundAbove height before side checks, case '..index)
   assert(q('MmVY')==(c.jumped and 0xd555 or (-4*65536)%16777216),'groundAbove uses source jumped flag for CIELING_DISPLACE=100/120')
   assert(r('MmYFraction')==0 and r('MmYFraction',1)==0,'Ceiling boundary discards old fractional Y')
   assert((r('Square1SoundQueue')&2)==(c.form=='ball' and 0 or 2),'Only Morph Ball suppresses the stored ceiling cue')
  end
  local p=c.pickup
  if p and p.initial and not p.mature then
   assert(r('Enemy_Flag',p.slot)~=0,'Emerging pickup remains a world object instead of automatic collection')
   assert(wx('Enemy_X_Position','Enemy_PageLoc',p.slot)==p.x,'Emerging pickup does not jump horizontally')
   local y=r('Enemy_Y_Position',p.slot)
   assert(y==p.y or y==p.y-1,'Pickup rises at most one real pixel per gameplay update')
   p.steps=p.steps+p.y-y;p.y=y
   if r('Enemy_State',p.slot)>=128 then p.mature=true end
  end
 end
 log:write(table.concat({index,c.kind,age,c.form,c.side or 0,c.motion or c.dir,c.power,c.tile,px(),r('Player_Y_Position'),q('MmVX'),q('MmVY'),c.heads,c.walls},',')..'\n')
 c.lastX,c.lastY=px(),r('Player_Y_Position')
 if age>=c.limit then finish(c);current=nil;log:flush()end
end,emu.callbackType.exec,L.MegaMan202AfterBG)

emu.addEventCallback(function()
 local c=current
 emu.setInput({right=frame==80 or frame==100 or(c and c.kind=='head' and c.dir==1),
  left=c and c.kind=='head' and c.dir==2,start=frame==200,a=c and c.kind=='head' and age<10},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 assert(frame<22000,'Bounded collision matrix must finish')
end,emu.eventType.endFrame)
