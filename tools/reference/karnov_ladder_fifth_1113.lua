-- Extension after the frozen four-pickup gameplay prefix. No RAM/file writes.
stockFifth={main=0,movement_updates=0,stage='await-bomb',start=0,recent={},heads={},progress={},pipes={},GameLoop_entries=0,GameLoop_returns=0}
local fifthReturn=nil
local fifthJumpUntil=0
local fifthLastPulse=-100
local fifthBrickStable=0
local fifthGap=nil
local function fifthGapControl(x,y,ground)
 if not fifthGap and x>=2110 and x<2368 then fifthGap={phase='setup',start=stockFifth.main};stockFifth.gap=fifthGap end
 if not fifthGap or fifthGap.phase=='complete'then return nil end
 local p=fifthGap;local age=stockFifth.main-p.start
 if p.phase=='setup'then
  if not ground then return 0 end
  if x<2192 then return 1 elseif x>2192 then return 2 end
  p.phase='request';p.start=stockFifth.main;p.initial_left=x+24;return 36
 elseif p.phase=='request'then
  for i=0,5 do local a=actor(i)
   if a.flag==1 and a.id==40 and a.state==66 and math.abs(a.x-p.initial_left)<5 then
    p.slot=i;p.phase='wait-return';p.start=stockFifth.main;p.birth=state();return 0
   end
  end
  assert(age<45,'Existing Down+Select native horizontal girder request');return age<3 and 36 or 0
 end
 local a=actor(p.slot);assert(a.flag==1 and a.id==40 and a.state==66,'Native horizontal gap helper retained')
 p.minimum_left=math.min(p.minimum_left or a.x,a.x);p.maximum_left=math.max(p.maximum_left or a.x,a.x)
 if p.phase=='wait-return'then
  if age>=150 and a.x<=p.initial_left+24 then p.phase='board';p.start=stockFifth.main;p.takeoff=state()end
  assert(age<260,'Original horizontal helper returns for boarding');return 0
 elseif p.phase=='board'then
  if r('PlatformCollisionFlag',p.slot)==p.slot and ground then p.phase='ride';p.start=stockFifth.main;p.boarded=state();return 0 end
  assert(age<100,'Ordinary jump boards horizontal girder');return 1|(age<36 and 128 or 0)
 elseif p.phase=='ride'then
  p.carries=(p.carries or 0)+1
  if a.x>=p.initial_left+104 then p.phase='exit';p.start=stockFifth.main;p.departure=state()end
  assert(age<260,'Native horizontal girder reaches far edge');return 0
 end
 if x>=2368 and ground then p.phase='complete';p.finish=state();jumpAge=0;release=8;return 1 end
 assert(age<140,'Original jump from horizontal helper reaches stock right bank')
 return 1|(age<36 and 128 or 0)
end
local fifthPipe=nil
local function fifthPipeControl(x,y,ground)
 if not fifthPipe then
  for i=0,5 do local a=actor(i)
   if a.flag==1 and a.id==13 and a.x>x and a.x-x<128 and(not fifthPipe or a.x<fifthPipe.x)then
    fifthPipe={slot=i,x=a.x,phase='approach',start=stockFifth.main};stockFifth.pipe=fifthPipe
   end
  end
 end
 if not fifthPipe then return nil end
 local p=fifthPipe;local a=actor(p.slot)
 if a.flag~=1 or a.id~=13 or a.x~=p.x then fifthPipe=nil;return nil end
 if p.phase=='approach'then
  if not ground then return 1 end
  if x<p.x-31 then return 1 elseif x>p.x-30 then return 2 end
  p.phase='wait';p.start=stockFifth.main;stockFifth.pipes[#stockFifth.pipes+1]={event='wait',plant=a,s=state()};return 0
 elseif p.phase=='wait'then
  -- Original MovePiranhaPlant does not re-emerge within 33 horizontal pixels.
  -- Wait at that ordinary safe approach until its actual fully-down pivot.
  if a.y>=r('PiranhaPlantDownYPos',p.slot)then
   p.phase=p.x==1752 and 'girder-request'or 'release';p.start=stockFifth.main
   stockFifth.pipes[#stockFifth.pipes+1]={event='down',plant=a,s=state()}
  end
  assert(stockFifth.main-p.start<250,'Stock pipe Piranha must finish retracting');return 0
 elseif p.phase=='girder-request'then
  for i=0,5 do local h=actor(i)
   if h.flag==1 and h.id==37 and h.state==65 and math.abs(h.x-(x-8))<=1 then p.phase='girder-ride';p.start=stockFifth.main;return 0 end
  end
  assert(stockFifth.main-p.start<40,'Existing native girder at stock tall pipe')
  return stockFifth.main-p.start<3 and 40 or 0
 elseif p.phase=='girder-ride'then
  if y<=80 then p.phase='release';p.start=stockFifth.main;stockFifth.pipes[#stockFifth.pipes+1]={event='carried',s=state()}end
  assert(stockFifth.main-p.start<220,'Existing native tall-pipe girder carry');return 0
 elseif p.phase=='release'then
  if stockFifth.main-p.start>=3 then p.phase='jump';p.start=stockFifth.main end
  return 0
 end
 local age=stockFifth.main-p.start
 if x>p.x+32 then stockFifth.pipes[#stockFifth.pipes+1]={event='crossed',plant=a,s=state()};fifthPipe=nil;jumpAge=0;release=8;return 1 end
 assert(age<140,'Ordinary stock timed pipe crossing')
 return 1|(age<36 and 128 or 0)
end
local function fifthClearEnemy(x,y)
 for i=0,5 do local a=actor(i)
  -- A Piranha at the top of a pipe is not a ground-level crouch-shot target.
  -- Let the ordinary wall/jump control handle the pipe and its native timing.
  if a.flag>0 and a.flag<128 and a.id<21 and a.id~=13 and a.state&32==0 and math.abs(a.x-x)<100 and math.abs(a.y-y)<24 then
   return 4+(a.x<x and 2 or 1)+(epoch%12<6 and 64 or 0)
  end
 end
 return nil
end
local function fifthEnemyNear(x,d)
 for i=0,5 do local a=actor(i)
  if a.flag>0 and a.flag<128 and a.id<21 and a.id~=13 and a.state&32==0 and a.x>x and a.x-x<d and math.abs(a.y-r('Player_Y_Position'))<24 then return true end
 end
 return false
end
local function fifthOrdinary(x,y,ground)
 -- Preserve the exact original movement policy while applying the new
 -- Piranha classification to its final enemyNear crouch-shot override too.
 local original=enemyNear;enemyNear=fifthEnemyNear
 local pad=ordinary(x,y,ground);enemyNear=original;return pad
end
local function fifthOpenSite(x,y)
 local column=((x+8)//16)*16;local bottom=((y+24)//16)*16
 if bottom<144 or bottom>=208 then return false end
 for n=0,7 do local t=tile(column,bottom-16*n)
  if emu.read(MTILE_ATTRIBUTES_OFFSET+t,emu.memType.nesPrgRom)&3~=0 then return false end
 end
 return true
end
local fifthCells,fifthAttrs={},{}
local function fifthRememberPPU()
 local col=kr(0x625);local page=(kr(0x626)&0xf0)|((col>>4)&15)
 local bottom=(kr(0x626)&15)*16;local column=col&15
 for i=0,7 do local y=bottom-16*i;local at=0x2000+(page&1)*0x400+(y//8)*32+2*column
  for _,offset in ipairs({0,1,32,33})do fifthCells[#fifthCells+1]={at+offset,emu.read(at+offset,emu.memType.nesPpuDebug)}end
  local attr=0x23c0+(page&1)*0x400+(y//32)*8+(column//2);fifthAttrs[attr]=emu.read(attr,emu.memType.nesPpuDebug)
 end
end
local function fifthArtPPU()
 local col=kr(0x625);local page=(kr(0x626)&0xf0)|((col>>4)&15)
 local bottom=(kr(0x626)&15)*16;local column=col&15;local ppu=emu.memType.nesPpuDebug
 for i=0,7 do local y=bottom-16*i;local at=0x2000+(page&1)*0x400+(y//8)*32+2*column
  assert(emu.read(at,ppu)==44 and emu.read(at+1,ppu)==45 and emu.read(at+32,ppu)==44 and emu.read(at+33,ppu)==45,'Stock Ladder native quad reaches physical PPU')
  local attr=emu.read(0x23c0+(page&1)*0x400+(y//32)*8+(column//2),ppu)
  local shift=((y//16)&1)*4+(column&1)*2;assert((attr>>shift)&3==2,'Stock Ladder owned palette quadrant')
 end
 return{page=page,column=column,bottom=bottom,cells=32,palette=2,colors={emu.read(0x3f0a,ppu),emu.read(0x3f0b,ppu)}}
end
local function fifthRestoredPPU()
 local ppu=emu.memType.nesPpuDebug
 for _,cell in ipairs(fifthCells)do if emu.read(cell[1],ppu)~=cell[2]then return false end end
 for at,value in pairs(fifthAttrs)do if emu.read(at,ppu)~=value then return false end end
 return true
end
local function fifthTo(name)
 stockFifth.stage=name;stockFifth.start=stockFifth.main;stockFifth.progress[#stockFifth.progress+1]={stage=name,s=state()}
end
local function fifthControl(x,y,ground,item)
 local age=stockFifth.main-stockFifth.start
 if #pickups<5 then
  if not armed then return routeAge%8<2 and 68 or 0 end
  if kr(0xc0)~=0 then return 0 end
  if stockFifth.stage=='await-bomb'then fifthTo('travel');age=0 end
  if item then
   if item.state<128 then return 0 end
   if stockFifth.stage~='collect-setup'and stockFifth.stage~='lift-request'and stockFifth.stage~='lift-ride'and stockFifth.stage~='collect-jump'then fifthTo('collect-setup');age=0 end
   if stockFifth.stage=='collect-setup'then
    if not ground then return 0 end
    local clear=fifthClearEnemy(x,y);if clear then return clear end
    local target=item.x+32
    if x<target-1 then return 1 elseif x>target+1 then return 2 end
    fifthTo('lift-request');return 40
   elseif stockFifth.stage=='lift-request'then
    for i=0,5 do local a=actor(i);if a.flag==1 and a.id==37 and a.state==65 and math.abs(a.x-(x-8))<=1 then fifthTo('lift-ride');return 0 end end
    assert(age<40,'Existing native manual girder request');return age<3 and 40 or 0
   elseif stockFifth.stage=='lift-ride'then
    if y<=112 then fifthTo('collect-jump')end
    assert(age<220,'Native fifth-flower girder carry');return 0
   end
   if age>=110 and ground then fifthTo('collect-setup');return 0 end
   return(x>item.x+2 and 2 or 0)|(age<36 and 128 or 0)
  end
  if x<2320 then assert(age<3200,'Fifth route ordinary traversal Main bound')end
  if ground then local clear=fifthClearEnemy(x,y);if clear then return clear end end
  local gap=fifthGapControl(x,y,ground);if gap then return gap end
  if x<2320 then
   local pipe=fifthPipeControl(x,y,ground);if pipe then return pipe end
   return fifthOrdinary(x,y,ground)
  end
  if stockFifth.stage~='bump'then fifthTo('bump');age=0;jumpAge=0;release=0 end
  if ground then
   local clear=fifthClearEnemy(x,y);if clear then return clear end
   -- Retain the already-qualified fourth-brick controller's source shot
   -- approach, translated to the next authored powerup column.
   local anchor=fifthBrickStable>=8 and 2393 or 2377
   if x<anchor then return 1 elseif x>anchor+2 then return 2 end
   if r('PlayerFacingDir')~=1 then return 1 end
  end
  local pad=epoch%8<4 and 64 or 0
  if ground and stockFifth.main-fifthLastPulse>35 then fifthLastPulse=stockFifth.main;fifthJumpUntil=stockFifth.main+8 end
  if stockFifth.main<fifthJumpUntil then pad=pad|128 end
  assert(age<700,'Fifth authored2400 brick head bound')
  return pad
 end
 if stockFifth.stage~='clear-floor'and stockFifth.stage~='select'and stockFifth.stage~='activate'and stockFifth.stage~='grow'and stockFifth.stage~='grown-visible'and stockFifth.stage~='climb'and stockFifth.stage~='down'and stockFifth.stage~='restore'and stockFifth.stage~='restored-visible'and stockFifth.stage~='complete'then
  assert(kr(0x860)==3 and kr(0x8f)&4~=0,'Fifth natural item earned original Ladder');fifthTo('clear-floor')
 end
 if stockFifth.stage=='clear-floor'then
  if not ground then return 0 end
  local clear=fifthClearEnemy(x,y);if clear then return clear end
  stockFifth.site=stockFifth.site or 2464
  if x<stockFifth.site-1 then return 1 elseif x>stockFifth.site+1 then return 2 end
  if not fifthOpenSite(x,y)then stockFifth.site=stockFifth.site+16;assert(stockFifth.site<=2544,'Native stock Ladder column needs eight clear cells');return 1 end
  fifthTo('select');return 0
 elseif stockFifth.stage=='select'then
  if kr(0x8e)==2 then fifthTo('activate');return 0 end
  return age%8<2 and 32 or 0
 elseif stockFifth.stage=='activate'then
  if kr(0x5e)==1 then stockFifth.activation=state();fifthRememberPPU();fifthTo('grow');return 0 end
  assert(age<60,'Earned stock Ladder Down+B activation')
  return age%8<2 and 68 or 0
 elseif stockFifth.stage=='grow'then
  if kr(0x5e)==0 then assert(kr(0x624)&15==8,'Stock Ladder has eight legal terrain cells');fifthTo('grown-visible')end
  assert(age<80,'Stock native Ladder growth Main bound');return 0
 elseif stockFifth.stage=='grown-visible'then
  if age>=4 then stockFifth.art=fifthArtPPU();stockFifth.grown=state();fifthTo('climb')end
  return 0
 elseif stockFifth.stage=='climb'then
  if age>=24 then stockFifth.climbed=state();assert(y<stockFifth.grown.y,'Stock original Up climbs');fifthTo('down');return 4 end
  return 8
 elseif stockFifth.stage=='down'then
  if kr(0x5e)==2 then fifthTo('restore');return 0 end
  assert(age<140,'Stock original heldDown retraction');return 4
 elseif stockFifth.stage=='restore'then
  if kr(0x5e)==0 and kr(0x624)&15==0 and kr(0x627)==0 then
   assert(kr(0x8f)&4~=0 and kr(0x8e)==2,'Stock Ladder ownership returns');fifthTo('restored-visible')
  end
  assert(age<80,'Stock Ladder original restoration');return 0
 elseif stockFifth.stage=='restored-visible'then
  if age>=4 and r('VRAM_Buffer1_Offset')==0 and fifthRestoredPPU()then
   stockFifth.restored_cells=#fifthCells;local n=0;for _ in pairs(fifthAttrs)do n=n+1 end;stockFifth.restored_attributes=n
   stockFifth.complete=state();fifthTo('complete')
  end
  assert(age<30,'Stock last native restoration reaches physical PPU');return 0
 end
 return 0
end
-- COUNTER_HOOKS
emu.addMemoryCallback(function()
 local q=emu.convertAddress(L.KrMovement)
 if game and q and q.memType==emu.memType.nesWorkRam and q.address==3*8192+(L.KrMovement&8191)then stockFifth.movement_updates=stockFifth.movement_updates+1 end
end,emu.callbackType.exec,L.KrMovement)
emu.addMemoryCallback(function()
 if #pickups~=4 or not mapped(L.NativeRarePlayerHeadCollisionCore,HEAD_OFFSET)then return end
 local c=emu.getState();stockFifth.heads[#stockFifth.heads+1]={s=state(),tile=c['cpu.a'],row=r('R2')+32}
 if #stockFifth.heads>12 then table.remove(stockFifth.heads,1)end
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
emu.addMemoryCallback(function()
 if not game or not mapped(L.GameLoop,GAMELOOP_OFFSET)then return end
 stockFifth.GameLoop_entries=stockFifth.GameLoop_entries+1
 local c=emu.getState();local sp=c['cpu.sp'];fifthReturn={pc=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535,sp=(sp+2)&255}
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if not fifthReturn then return end;local c=emu.getState()
 if c['cpu.pc']==fifthReturn.pc and c['cpu.sp']==fifthReturn.sp then
  stockFifth.GameLoop_returns=stockFifth.GameLoop_returns+1;stockFifth.main=stockFifth.GameLoop_returns;fifthReturn=nil
  if #pickups==4 and wx()>=2320 then
   if tile(2400,144)==0 then fifthBrickStable=fifthBrickStable+1 else fifthBrickStable=0 end
   stockFifth.brick_stable=fifthBrickStable;stockFifth.target_tiles={tile(2400,128),tile(2400,144)}
  end
 end
end,emu.callbackType.exec,L.IdleLoop+12)
