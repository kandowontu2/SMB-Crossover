-- Explicit initialized arenas, not a level-clear proof. A real descending
-- controller pogo activates each authored block. A separate initialized drop
-- then checks that the same live bouncing placeholder still supports a body.
local frame,index,current=0,0,nil
local cases={}
for _,tile in ipairs({0x5f,0x60,0xc1,0x58,0x51,0xc4,0x61})do
 for _,x in ipairs({96,103,0x4fc,0x500})do
  for _,speed in ipairs({2,4,6})do cases[#cases+1]={tile=tile,x=x,speed=speed}end
 end
end
-- Occupy the preferred native slot: a valid receipt must follow the actual
-- allocator, even when its final preferred-slot bit equals the pre-hit bit.
cases[#cases+1]={tile=0x5f,x=96,speed=4,busyPreferred=true}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function cell(x,y)return(x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local csv=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-pogo-bump-support.csv','w'))
csv:write('case,tile,startX,speed,age,phase,x,y,state,pogo,vy,bumpCalls,shatterCalls,mapTile\n')
local function resetMotion(y,speed,pogo)
 w('Player_X_Position',current.x%256);w('Player_PageLoc',current.x//256)
 w('Player_Y_Position',y);w('Player_Y_HighPos',1)
 w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',speed)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',0x10,1);w('MmVY',speed,2)
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScPogo',pogo and 1 or 0);w('ScAttack',0)
 w('ScPrevious',pogo and 68 or 0);w('RgPreviousButtons',pogo and 68 or 0)
 w('RgCrouch',0);w('CrouchingFlag',0);w('XgRise',0);w('XgWallContact',0)
 for i=0,5 do w('Enemy_Flag',0,i)end
end
local function setup(c)
 c.age=0;c.bump=0;c.shatter=0;c.bounced=false;c.phase='pogo';c.supported=false
 c.bumpExpected=c.tile==0x5f or c.tile==0x60 or c.tile==0xc1 or c.tile==0x58
 c.map=cell(((c.x+8)//16)*16,144)
 for i=0,415 do
  w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i);w('RgMeleeBlocks',0,i)
 end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x61,page*208+176+col)end end
 w('Block_Buffer_1',c.tile,c.map)
 w('MmSolidTerrain',c.tile==0x61 and 1 or 0,c.map)
 w('SelectedCharacter',12);w('PlayerStatus',0);w('PlayerSize',0)
 w('PlayerFacingDir',1);w('Player_MovingDir',1)
 w('ScreenLeft_X_Pos',(c.x-96)%256);w('ScreenLeft_PageLoc',(c.x-96)//256)
 w('ScreenRight_X_Pos',(c.x+159)%256);w('ScreenRight_PageLoc',(c.x+159)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 w('TimerControl',0);w('InjuryTimer',0);w('GuestPowerupActive',0)
 for i=0,2 do w('GameTimerDisplay',9,i)end
 w('GameTimerCtrlTimer',24);w('GameEngineSubroutine',8);w('DisableCollisionDet',0)
 w('SwimmingFlag',0);w('AreaType',1);w('Hidden1UpFlag',1)
 w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)end
 if c.busyPreferred then
  local oldX=c.x+64
  w('Block_State',1);w('Block_Metatile',0xc4)
  w('Block_BBuf_Low',(oldX//256)%2*208+(oldX%256)//16)
  w('Block_Orig_YPos',48);w('Block_Orig_XPos',oldX%256)
  w('Block_X_Position',oldX%256);w('Block_PageLoc',oldX//256);w('Block_PageLoc2',oldX//256)
  w('Block_Y_Position',80);w('Block_Y_HighPos',1);w('Block_Y_Speed',0)
 end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 resetMotion(113-c.speed,c.speed,true)
end
-- The shared bump/shatter routines live in a fixed bank; count only real
-- execution at their physical PRG location, whatever the caller mapped.
local function actual(n)
 local p=emu.convertAddress(assert(L[n],n))
 return p and p.memType==emu.memType.nesPrgRom and p.address//8192==assert(B[n],n)
end
emu.addMemoryCallback(function()
 if current and current.phase=='pogo'and actual('BumpBlock') then current.bump=current.bump+1 end
end,emu.callbackType.exec,L.BumpBlock)
emu.addMemoryCallback(function()
 if current and current.phase=='pogo'and actual('BrickShatter') then current.shatter=current.shatter+1 end
end,emu.callbackType.exec,L.BrickShatter)
emu.addEventCallback(function()
 if frame<620 then
  emu.setInput({down=frame==80,right=frame==100 or frame==120,start=frame==200},0);return
 end
 if not current then
  index=index+1
  if not cases[index]then
   csv:close();print('PASS Scrooge85 real pogo bump/shatter/protected cases and live bouncing-block support controls, including world-page seams and occupied preferred slot');emu.stop(0);return
  end
  current=cases[index];setup(current)
 end
 if current.age==8 and current.bumpExpected and current.phase=='pogo'then
  assert(r('Block_Buffer_1',current.map)==0x23,'Support control uses the actual live bouncing placeholder')
  current.phase='support'
  -- Independent initialized drop onto the still-live real bump transaction.
  -- This actor reset is confined to the explicitly labelled support arena.
  resetMotion(110,2,false)
 end
 emu.setInput({down=current.phase=='pogo',b=current.phase=='pogo'},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not current then assert(frame<4000,'Bounded pogo support arena');return end
 local c=current;local x,y=wx(),r('Player_Y_Position')
 csv:write(table.concat({index,c.tile,c.x,c.speed,c.age,c.phase,x,y,r('Player_State'),r('ScPogo'),r('MmVY',2),c.bump,c.shatter,r('Block_Buffer_1',c.map)},',')..'\n');csv:flush()
 assert(x==c.x,'A stationary pogo/block contact cannot eject the player:case '..index..' age '..c.age..' X '..x..' expected '..c.x)
 assert(r('GameEngineSubroutine')==8 and r('InjuryTimer')==0,'Block interaction remains playable without injury')
 if c.phase=='pogo'and r('MmVY',2)>=128 then c.bounced=true end
 if c.phase=='support'and y==112 and r('Player_State')==0 then c.supported=true end
 if c.age==7 then
  if c.bumpExpected then
   assert(c.bump==1 and c.shatter==0,'A bumpable block must perform exactly one actual native bump transaction')
   assert(c.bounced,'A descending pogo must rebound from the newly solid bumpable block')
  elseif c.tile==0x51 then
   assert(c.shatter==1 and c.bump==0,'Ordinary brick performs its real shatter transaction')
   assert(r('Block_Buffer_1',c.map)==0,'Shattered ordinary brick stays empty')
  else
   assert(c.bump==0 and c.shatter==0 and r('Block_Buffer_1',c.map)==c.tile,'Used/protected support cannot be activated or destroyed')
  end
 end
 if c.age==14 then
  if c.bumpExpected then assert(c.supported,'An ordinary nonpogo body must land on the live bumped block; pending23 cannot be ignored globally')end
  print('PASS Scrooge pogo support case '..index..' tile='..c.tile..' x='..c.x..' speed='..c.speed)
  current=nil
 else c.age=c.age+1 end
 assert(frame<4000,'Bounded pogo support matrix')
end,emu.eventType.endFrame)
