dofile("C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mmc3-static-call-v37/full-roster-v1/native-guard.lua")
local original=(function()
local general=(function()
local normal=(function()
local normal=(function()
local normal=(function()
-- Controller-only discovery. No emulated memory, equipment or physics writes.
local baseline=(function()
-- Frozen existing controllers only. No game state grants or writes.
local base=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()
local mike=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=not not near and c.poll%24<2
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  local target=100
  if c.x<400 then target=145 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-clock>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 local feet=c.y+32
 local obstacle=solid(c.x+22,feet-8)or solid(c.x+22,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+12,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end





end)()
local vic=(function()
-- Controller discovery only. No game state writes; a fixed replay is required.
return function(c)
 local b={a=c.poll%6<3,b=c.poll%24<2}
 if c.world~=0 or c.level~=0 then b.right=true;return b end
 local target=48
 b.up=c.y>target+2;b.down=c.y<target-2
 -- Rise before advancing into the first low question block. Native camera
 -- motion continues while the player deliberately holds horizontal position.
 b.right=c.y<74 and(c.x-c.camera<112 or c.r('ScrollLock')~=0)
 return b
end

end)()
local meta=(function()
-- Native grounded Meta discovery; no Up-flight or constant dash attacks.
-- Base policy SHA256 d9b37780f3a5cfdaaaa9d2fbafa5fe4628a2eeaeaaee393eba3d4d7d417c51dc
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if name=='meta'then b.b=e and e.dx>-16 and e.dx<48 and math.abs(e.y-c.y)<42 and c.poll%24<2 or false end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-clock>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end

 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()
return function(c)
 if ROSTER_CONFIG.name=='mike' then return mike(c)end
 if ROSTER_CONFIG.name=='vic' then return vic(c)end
 if ROSTER_CONFIG.name=='meta' then return meta(c)end
 return base(c)
end

end)()
local scrooge=(function()
-- Existing controller-only policies, frozen without workspace-path assumptions.
local scrooge=(function()
-- Controller discovery using Scrooge's native stronger pogo; no state grants.
local normal=(function()
-- Samus/Bill/Lance candidate discovery. No emulated memory writes.
local travel=(function()
-- Pit/Rygar/Sophia route discovery. Read-only telemetry and ordinary inputs.
-- A candidate is evidence only after the complete CSV independently replays.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
local launchHold=0
local waterExit='back'
return function(c)
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.areaType
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0;launchHold=0 end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 local height=32
 local feet=c.y+height
 local solid=function(wx,y)local t=c.block(wx,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if still==60 and c.world==0 and c.level==1 and c.x>2950 then
  local cells={}
  for y=128,208,16 do cells[#cells+1]=y..':'..c.block(c.x+15,y)..'/'..c.block(c.x+16,y)end
  print('PIPE diagnostic x='..c.x..' y='..c.y..' state='..c.state..' facing='..c.r('PlayerFacingDir')..' attr='..c.r('Player_SprAttrib')..' cells='..table.concat(cells,','))
 end
 if c.areaType==0 then
  if c.char==8 and c.world==1 and c.level==1 and c.x>=2984 then
   if waterExit=='back' then
    if c.y>=100 and c.y<=112 and c.x>=2990 and c.x<=3018 then waterExit='enter' end
    return {right=c.x<3006,left=c.x>3010,b=true,a=c.y>110 and not c.lastA}
   end
   return {right=true,b=true}
  end
  -- Pit/Rygar retain source jump/gravity; Sophia can steer vertically.
  if c.char==0 or c.char==8 then
   -- Travel below pursuing Bloopers, rising only for the real coral columns.
   local target=164
   local probe
   if solid(c.x+24,c.y+8)then probe=c.y+8
   elseif solid(c.x+24,c.y+24)then probe=c.y+24 end
   if probe then
    local top=32+math.floor((probe-32)/16)*16
    local bottom=top+16
    while top>32 and solid(c.x+24,top-1)do top=top-16 end
    while bottom<224 and solid(c.x+24,bottom)do bottom=bottom+16 end
    if top==32 then target=math.min(176,bottom+4)
    else target=math.min(target,top-34)end
   end
   b.a=c.y>target and not c.lastA
  elseif c.char==11 then
   b.up=c.y>112;b.down=c.y<88
   if solid(c.x+24,c.y+24)then b.up=true;b.down=false end
  elseif c.char==12 then
   local obstacle=solid(c.x+40,c.y+8)or solid(c.x+40,c.y+24)
   local gap=not solid(c.x+32,math.min(c.y+40,232))
   b.a=c.grounded and not c.lastA and(obstacle or gap)
   if not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
  else
   b.a=c.grounded and not c.lastA
   if not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
  end
  b.b=(c.char==0 or c.char==8)or(c.char==12 and c.poll%16<4)or(c.char~=12 and c.poll%8==0)
  if c.x>3000 then b.a=false;b.up=false;b.down=c.y<160 end
  return b
 end
 local e=c.enemy()
 b.b=(c.char==0 or c.char==8)or c.poll%8==0
 if c.char~=0 and c.char~=8 and c.char~=12 and e and e.dx>32 and e.dx<112 and math.abs(e.y-c.y)<24 and c.grounded and launchHold==0 then
  b.right=false;b.down=c.char==6 or c.char==7
  return b
 end
 if c.char~=0 and c.char~=8 and c.char~=12 and e and e.dx>12 and e.dx<96 and math.abs(e.y-c.y)<48 and not c.grounded and c.vy<128 then
  for y=math.min(feet+8,232),232,16 do if solid(c.x+8,y)then b.right=false;break end end
 end
 local obstacle=solid(c.x+40,c.y+height-8)or solid(c.x+40,c.y+8)
 local mount=c.areaType==2 and(solid(c.x+40,c.y-24)or solid(c.x+40,c.y-8))and not solid(c.x+24,c.y+16)
 local gapRange=(c.char==12 and c.areaType==3)and 16 or 32
 local gap=not solid(c.x+gapRange,math.min(feet+8,232))
 local enemy=e and e.dx>0 and e.dx<45 and math.abs(e.y-c.y)<48
 if c.grounded and not c.lastA and(obstacle or mount or gap or enemy or still>20)then b.a=true;jumpAge=0;launchHold=6
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
 if launchHold>0 then
  if c.grounded then b.a=true;launchHold=launchHold-1 else launchHold=0 end
 end
 -- Underground exit: walking into its vertical pipe enters normally.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2140 then
  if c.x<2380 or c.x>=2420 then launchHold=0 end
  b.a=c.x>=2380 and c.x<2420 and c.grounded and not c.lastA
  if b.a then launchHold=6;jumpAge=0 end
  if launchHold>0 then b.a=true;launchHold=launchHold-1 end
  if c.x>=2490 and c.x<2570 and(c.yHigh==0 or c.y<48)then b.right=false end
 end
 return b
end

end)()
local initialUpgrade=false
local phase='approach'
local jumpAge=0
local mount
local pillarLanded=false
local lowMount='back'
local lowMounted=false
local stairsMounted=false
local exitPhase='back'
local plantX,plantReady=nil,false
local holdA,cooldown=0,0
local function finish(b,c)
 if cooldown>0 then cooldown=cooldown-1 end
 if b.a and holdA==0 and cooldown==0 then holdA=32 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end end
 return b
end
return function(c)
 local b=travel(c)
 if c.areaType==0 then holdA=0;cooldown=0;return b end
 if c.world==0 and c.level==0 and c.x>420 then initialUpgrade=true end
 b.b=(c.char==0 or c.char==8)or c.poll%12<5
 if(c.char==0 or c.char==8)and c.world==0 and c.level==2 and c.x<760 then b.b=false end
 local e=c.enemy()
 -- Land at the near edge of 1-3's high platform before firing at its Goombas.
 -- Bill and Lance cannot use Mario's stomp to resolve a descending overlap.
 if c.char==3 and c.world==0 and c.level==2 and c.x>=600 and c.x<640 and e and e.id==6 and e.y<80 and e.dx>16 and e.dx<128 then
  return finish({right=c.x<614,left=c.x>618,down=c.grounded,b=c.poll%12<5},c)
 end
 if c.char==3 and e and e.id~=13 and not c.grounded then
  b.up=e.y<c.y-8;b.down=e.y>c.y+8
 end
 -- Drop to the ordinary side entrance before walking into the exit pipe.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then
  holdA=0;cooldown=0
  if exitPhase=='back' then
   local target=math.max(2616,c.camera+1)
   if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter' end
   return {right=c.x<target,left=c.x>target+3,b=c.poll%12<5}
  end
  return {right=true,b=c.poll%12<5}
 end
 -- Land on the final stair before crossing to the descending lift.
 -- A single jump from the lower stair reaches only its bottom copy.
 if c.world==0 and c.level==1 and not stairsMounted and c.x>=2144 and c.x<2208 then
  if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return {right=true,b=true}end
  return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- Walk across the descending lift before jumping toward the next bank.
 -- Its second platform sits overhead, so a jump from the left edge is short.
 if c.world==0 and c.level==1 and c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then
  holdA=0;cooldown=0;return {right=true,b=c.poll%12<5}
 end
 -- Samus can clear a live plant by launching near its pipe, keeping the
 -- apex over the plant rather than using the generic early enemy jump.
 if c.char==2 and e and e.id==13 and e.dx>0 and e.dx<80 then
  if c.grounded and e.dx>42 then holdA=0;return {right=true,b=c.poll%12<5}end
  return finish({right=true,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- A Piranha is above the floor muzzle. Jump vertically and fire before
 -- crossing its pipe, rather than shooting below it or landing on its head.
 if c.char==3 and e and e.id==13 and e.dx> -16 and e.dx<68 then
  if plantX~=e.x then plantX=e.x;plantReady=false end
  if not plantReady then
   if e.dx<56 then holdA=0;return {left=true,b=false}end
   plantReady=true
  elseif e.dx<32 then plantReady=false;holdA=0;return {left=true}end
  if c.r('PlayerFacingDir')~=1 then return {right=true}end
  return finish({a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 if c.world==0 and c.level==1 and c.areaType==2 and not lowMounted and c.x>=1170 and c.x<1290 then
  if c.y<=112 and c.grounded then lowMounted=true
  elseif c.block(1224,152)~=0 and c.block(1224,152)~=0x23 then
   if lowMount=='back'then
    holdA=0
    local target=math.max(1196,c.camera+1)
    if c.x>=target and c.x<=target+2 and c.grounded then lowMount='rise';return finish({a=true},c)end
    return {right=c.x<target,left=c.x>target+2}
   elseif lowMount=='rise'then
    if c.y<=112 then lowMount='onto' end
    return finish({a=c.grounded and not c.lastA},c)
   else
    if c.grounded and c.y>112 then lowMount='back';holdA=0;cooldown=4;return {left=true}end
    return finish({right=c.x<1250,left=c.x>1252},c)
   end
  else lowMounted=true end
 end
 -- The underground pair of gaps contains a narrow intermediate column.
 -- Land on its real top instead of carrying one jump past both gaps.
 if c.world==0 and c.level==1 and c.areaType==2 and not pillarLanded and c.x>=1944 and c.x<1984 then
  if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c)end
  return finish({right=c.x<1960,left=c.x>1964},c)
 end
 if c.char==2 and c.r('SmBall')~=0 then
  -- Never strand a controller candidate in Morph Ball at a pipe.
  b.up=c.poll%2==0;b.down=false;b.a=false
 end
 -- The first ordinary mushroom is a real native pickup, collected through
 -- head contact and pursuit. Other upgrade coverage uses separate arenas.
 if c.world~=0 or c.level~=0 or initialUpgrade then return finish(b,c)end
 if c.status>0 or(c.char==3 and(c.r('InvOwnedLo',3)+256*c.r('InvOwnedHi',3))>1)then initialUpgrade=true;return finish(b,c)end
 if phase=='approach' and c.x<320 then return finish(b,c)end
 if (phase=='approach' or phase=='bump') and c.grounded and c.y<=128 then phase='drop' end
 b={}
 if phase=='drop' then
  b.right=c.x<392;b.left=false;b.a=false
  if c.y>=150 then phase='approach' end
 elseif phase=='approach' then
  b.right=c.x<330;b.left=c.x>334
  if c.x>=330 and c.x<=334 and c.grounded then phase='bump';jumpAge=0 end
 elseif phase=='bump' then
  b.a=jumpAge<30;jumpAge=jumpAge+1
  b.right=c.x<330;b.left=c.x>334
  if jumpAge>65 and c.grounded then jumpAge=0 end
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then phase='collect' end end
 elseif phase=='collect' then
  local px,py
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)
  end end
  if not px then phase='bump';jumpAge=0;return finish(b,c)end
  b.right=c.x<px-5;b.left=c.x>px+5
  if not mount and py<c.y-10 and c.grounded and c.y>144 then mount='back';holdA=0 end
  if mount then
   local target=math.max(284,c.camera+1)
   if mount=='back'then
    b.right=c.x<target;b.left=c.x>target+1;b.a=false
    if c.x>=target and c.x<=target+1 and c.grounded then mount='rise';b.a=true end
   elseif mount=='rise'then
    b.right=false;b.left=false
    if c.y<=112 then mount='onto' end
    if c.grounded and not c.lastA then b.a=true end
   else
    b.right=c.x<px-4;b.left=c.x>px+4
    if c.grounded and c.y>144 then mount='back' end
   end
  elseif py<c.y-10 and c.grounded then b.a=not c.lastA end
 end
 if e and math.abs(e.dx)<90 then
  b.b=c.poll%7==0
  if c.char==3 then b.down=c.grounded end
  if math.abs(e.dx)<24 and c.grounded then b.a=not c.lastA;b.down=false end
 end
 return finish(b,c)
end


end)()
local airborne=0
local drillStart
local lastCap='edge'
local lastCapArm
local secondWorldCap='land'
local secondWorldArm
local lateGap='land'
local lateGapLaunch
local springPhase='approach'
local springJumpAt
local waterFirst='land'
local waterFirstLaunch
local waterBridge='land'
local waterBridgeJump
local waterBridgeRise
local waterExitPhase='land'
local waterExitJump
local undergroundExit='land'
local undergroundExitLaunch
local firstHighCap='land'
local firstHighCapArm
local bonusPhase='back'
local undergroundGaps='edge'
local gapLaunch,gapArm
local castleFireJump
return function(c)
 local b=normal(c)
 if c.char~=12 then return b end
 if c.areaType==2 and c.area==64 then
  -- The exit's raised brick tread sits above its low side entrance. Settle
  -- in the entrance well left of that tread, then walk along the lower floor.
  if bonusPhase=='back' then
   local target=c.camera+24
   if c.x>=target and c.x<=target+3 and c.grounded and c.y>=176 then bonusPhase='exit'
   else return {right=c.x<target,left=c.x>target+3}end
  end
  return {right=true}
 end
 bonusPhase='back'
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=1840 and c.x<2064 then
  if undergroundGaps=='edge' then
   if c.grounded and c.x>=1908 and c.y>=176 then undergroundGaps='first';gapLaunch=c.poll
   else return {right=c.x<1908}end
  end
  if undergroundGaps=='first' then
   if c.grounded and c.x>=1940 then undergroundGaps='island'
   else return {right=c.x<1960,left=c.x>1964,a=c.poll-gapLaunch<32}end
  end
  if undergroundGaps=='island' then
   if c.grounded and c.x>=1970 and c.x<=1974 then undergroundGaps='arm';gapArm=c.poll
   else return {right=c.x<1972,left=c.x>1974}end
  end
  if undergroundGaps=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then undergroundGaps='cross'
   else return {a=c.poll-gapArm<16,down=c.poll-gapArm>=3,b=c.poll-gapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.areaType==0 then
  if c.world==1 and c.level==1 and c.x>=2960 then
   if waterExitPhase=='land' then
    if c.grounded and c.y<=112 and c.x>=3004 and c.x<=3012 then waterExitPhase='enter'
    else
     if c.grounded and c.y>112 and(not waterExitJump or c.poll-waterExitJump>60)then waterExitJump=c.poll end
     return {right=c.x<3008,left=c.x>3012,a=waterExitJump and c.poll-waterExitJump<16,b=c.poll%16<4}
    end
   end
   return {right=true}
  end
  if c.world==1 and c.level==1 and c.x>=2020 and c.x<2256 then
   if waterBridge=='land' then
    if c.grounded and c.y<=112 and c.x>=2062 and c.x<=2068 then waterBridge='rise';waterBridgeRise=c.poll
    else
     if c.grounded and c.y>112 and(not waterBridgeJump or c.poll-waterBridgeJump>60)then waterBridgeJump=c.poll end
     return {right=c.x<2064,left=c.x>2068,a=waterBridgeJump and c.poll-waterBridgeJump<16,b=c.poll%16<4}
    end
   end
   if waterBridge=='rise' then
    -- Water controls are disabled outside YHigh=1. Reach the stem's left
    -- edge before the brief top wrap so rightward control resumes on landing.
    if c.yHigh==0 or c.y<=64 then waterBridge='cross'
    else return {a=c.poll-waterBridgeRise<34,b=c.poll%16<4}end
   end
   return {right=true,b=c.poll%16<4}
  end
  if c.world==1 and c.level==1 and c.x>=980 and c.x<1160 then
   if waterFirst=='land' then
    if c.grounded and c.y<=96 and c.x>=1022 and c.x<=1028 then waterFirst='edge'
    else return {right=c.x<1024,left=c.x>1028,b=c.poll%16<4}end
   end
   if waterFirst=='edge' then
    if c.grounded and c.x>=1030 then waterFirst='cross';waterFirstLaunch=c.poll
    else return {right=true,b=c.poll%16<4}end
   end
   return {right=true,a=c.poll-waterFirstLaunch<34,b=c.poll%16<4}
  end
  return b
 end
 if c.areaType==3 then
  -- Bowser flames are native actor $15, outside the generic nearest-enemy
  -- helper's ordinary-enemy filter. Respond with real jump inputs.
  if c.grounded and not c.lastA then
   for slot=0,5 do
    if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_Flag',slot)<128 and c.r('Enemy_ID',slot)==0x15 then
     local fx=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
     local fy=c.r('Enemy_Y_Position',slot)
     if fx>c.x and fx<c.x+64 and math.abs(fy-c.y)<56 then castleFireJump=c.poll end
    end
   end
  end
  if castleFireJump and c.poll-castleFireJump<32 then return {right=true,a=true}end
  return b -- Release pogo to descend below castle overhangs.
 end
 if c.world==0 and c.level==2 and c.x>=580 and c.x<656 then
  -- The first tall cap rises64px, beyond the ordinary58px jump. Use the
  -- actual84px pogo rebound rather than entering its lower side corner.
  if firstHighCap=='land' then
   if c.grounded and c.y==96 and c.x>=598 and c.x<=604 then firstHighCap='arm';firstHighCapArm=c.poll
   else return {right=c.x<600,left=c.x>604}end
  end
  if firstHighCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then firstHighCap='cross'
   else return {a=c.poll-firstHighCapArm<16,down=c.poll-firstHighCapArm>=3,b=c.poll-firstHighCapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach' then
   if animation>0 then springPhase='compress';return {}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   return {right=c.x<3008,left=c.x>3012,a=springJumpAt and c.poll-springJumpAt<16}
  elseif springPhase=='compress' then
   if animation==0 and c.vy>=128 then springPhase='cross';return {right=true}end
   return {a=animation>=2 and animation<=4}
  end
  return {right=true}
 end
 if c.world==1 and c.level==0 and c.x>=2080 and c.x<2280 then
  if lateGap=='land' then
   if c.grounded and c.y>=176 and c.x>=2172 and c.x<=2180 then lateGap='approach'
   else return {right=c.x<2176,left=c.x>2180}end
  end
  if lateGap=='approach' then
   if c.x>=2208 and c.grounded then lateGap='cross';lateGapLaunch=c.poll
   else return {right=true}end
  end
  return {right=true,a=c.poll-lateGapLaunch<32}
 end
 if c.world==1 and c.level==0 and c.x>=1352 and c.x<1440 then
  if secondWorldCap=='land' then
   if c.grounded and c.y<=112 and c.x>=1394 and c.x<=1400 then secondWorldCap='arm';secondWorldArm=c.poll
   else return {right=c.x<1396,left=c.x>1400}end
  end
  if secondWorldCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then secondWorldCap='cross'
   else return {a=c.poll-secondWorldArm<16,down=c.poll-secondWorldArm>=3,b=c.poll-secondWorldArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==1 and c.level==0 and c.x>=1312 and c.x<1552 then
  b.b=false;b.down=false -- Climb the brick stairs without smashing their treads.
  return b
 end
 -- The last 1-3 cap rises64px. Engage pogo on the preceding safe ledge,
 -- then cross on its real84px rebound rather than the ordinary58px jump.
 if c.world==0 and c.level==2 and c.x>=1576 and c.x<1648 then
  if lastCap=='edge' then
   if c.grounded and c.x>=1590 and c.x<=1596 then lastCap='arm';lastCapArm=c.poll
   else return {right=c.x<1592,left=c.x>1596}end
  end
  if lastCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then lastCap='cross'
   else return {a=c.poll-lastCapArm<16,down=c.poll-lastCapArm>=3,b=c.poll-lastCapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2420 and c.x<2580 then
  -- Release pogo and use the second real lift below the exit roof.
  if undergroundExit=='land' then
   if c.grounded and c.yHigh==1 and c.y>=112 and c.y<=128 and c.x>=2514 and c.x<=2520 then
    undergroundExit='cross';undergroundExitLaunch=c.poll
   else return {right=c.x<2516,left=c.x>2520}end
  end
  return {right=true,a=c.poll-undergroundExitLaunch<32}
 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then return b end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=820 and c.x<928 then
  drillStart=drillStart or c.poll
  local age=(c.poll-drillStart)%80
  return {right=true,a=age<20,b=c.poll%16<4}
 end
 if c.grounded then airborne=0 else airborne=airborne+1 end
 if not c.grounded and airborne>=3 then
  b.down=true;b.b=true
 elseif c.r('ScPogo')~=0 then
  local function solid(x,y)
   local t=c.block(x,y)
   return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  local wall=solid(c.x+40,c.y+8)or solid(c.x+40,c.y+24)
  local mount=solid(c.x+40,c.y-24)or solid(c.x+40,c.y-8)
  local gap=not solid(c.x+32,math.min(c.y+40,232))
  if wall or mount or gap then b.down=true;b.b=true;b.a=false end
 end
 return b
end

end)()
local simon=(function()
-- Link/Simon/Ryu discovery. This is not a verified route.
-- Return function(context); the harness owns menu input, logging and replay.
-- Each agent may copy this file into its own uniquely named character policy.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
local firstPowerDone,powerStage,powerAge,powerMount=false,'approach',0,nil
local holdA,cooldown=0,0
local allowDouble=true
local lowMount,lowMounted,stairsMounted,pillarLanded,exitPhase='back',false,false,false,'back'
local outdoorStairReady=false
local liftLaunch=0
local springPhase,springJumpAt='approach',nil
local waterExitJumpAt
local function finish(b,c)
 if c.char==10 and b.up and c.r('XgWall')~=0 then
  -- Wall-top jumps consume a fresh A edge. A ground-jump hold must not
  -- replace the release requested by the wall controller below.
  holdA=0;cooldown=0;return b
 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end
 elseif cooldown>0 then b.a=false;cooldown=cooldown-1
 elseif b.a then holdA=(c.char==5 and 23 or 31)
 elseif allowDouble and c.char==5 and not c.grounded and c.r('RgDoubleJump')~=0 and not c.lastA and c.y>40 then
  b.a=true;holdA=23
 end
 return b
end
return function(c)
 allowDouble=true
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.areaType
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0;holdA=0;cooldown=0 end
 if c.grounded then jumpAge=-1 elseif jumpAge>=0 then jumpAge=jumpAge+1 end
 local small=(c.char==0 or c.char==8)and c.status==0
 local height=small and 16 or 32
 local feet=c.y+height
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local solid=function(wx,y)local t=c.block(wx,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if c.char==10 and c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  -- Native spring compression needs a new A edge after the landing input.
  -- Align over its actual X3008 support before committing to the tall wall.
  holdA=0;cooldown=0
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach'then
   if animation>0 then springPhase='compress';return{}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   local wall=c.r('XgWall')~=0
   local jump=springJumpAt and c.poll-springJumpAt<16
   if wall then
    local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
    jump=not c.lastA and not solid(probe,c.y+3)
   end
   return{right=c.x<3008,left=c.x>3012,a=jump,up=wall}
  elseif springPhase=='compress'then
   if animation==0 and c.vy>=128 then springPhase='cross';return{right=true}end
   return{a=animation>=2 and animation<=4}
  end
  if c.r('XgWall')~=0 then
   -- The boost can reach the tall wall before clearing its top. Ryu's
   -- source grab needs Up and a new top-jump edge to finish the crossing.
   local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
   return{right=true,up=true,a=not c.lastA and not solid(probe,c.y+3)}
  end
  return{right=true}
 end
 if c.areaType==3 and c.x>=2240 and c.x<2290 then
  -- Settle over the axe. Ryu must release wall-climb Up at the right wall;
  -- otherwise he repeatedly climbs into the roof instead of falling onto it.
  holdA=0;cooldown=0
  return{right=c.x<2248,left=c.x>2251}
 end
 if c.world==0 and c.level==0 and not firstPowerDone then
  if c.status>0 or c.x>480 then firstPowerDone=true
  elseif c.x>=320 or powerStage~='approach' then
   local px,py
   for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)end end
   if powerStage=='approach'and c.y<160 then powerStage='settle'end
   if powerStage=='settle'then
    holdA=0;cooldown=0
    if c.grounded and c.y>=160 then powerStage='approach'end
    local target=math.max(300,c.camera+1)
    return{right=c.x<target,left=c.x>target+2}
   end
   if powerStage=='approach'then
    holdA=0;cooldown=0
    if c.x>=330 and c.x<=334 and c.grounded then powerStage='bump';powerAge=0 end
    return{right=c.x<330,left=c.x>334}
   elseif powerStage=='bump'then
    powerAge=powerAge+1
    if px then powerStage='chase'
    else
     if powerAge>65 and c.grounded then powerAge=0;holdA=0;cooldown=4 end
     return finish({a=powerAge<30,right=c.x<330,left=c.x>334},c)
    end
   end
   if px then
    local item={right=c.x<px-5,left=c.x>px+5}
    if not powerMount and py<c.y-10 and c.grounded and c.y>144 then powerMount='back';holdA=0;cooldown=0 end
    if powerMount then
     local target=math.max(284,c.camera+1)
     if powerMount=='back'then
      item={right=c.x<target,left=c.x>target+1}
      if c.x>=target and c.x<=target+1 and c.grounded then powerMount='rise';item.a=true end
     elseif powerMount=='rise'then
      item={a=c.grounded and not c.lastA}
      if c.y<=112 then powerMount='onto'end
     else
      item={right=c.x<px-5,left=c.x>px+5}
      if c.grounded and c.y>144 then powerMount=nil end
     end
    end
    return finish(item,c)
   end
   if c.status==0 then powerStage='bump';powerAge=0;holdA=0;cooldown=4;return{}end
  end
 end
 if c.areaType==0 then
  if c.char==10 and c.world==1 and c.level==1 and c.x>=2900 then
   -- The native side pipe admits the body at Y112. Ryu's Right wall grab
   -- stops gravity, so use his real Down climb to leave the high approach
   -- and then hold Right through the opening, without another jump edge.
   holdA=0;cooldown=0
   if c.x<2935 then return{right=true}end
   if c.r('XgWall')~=0 then return{right=true,down=c.yHigh==0 or c.y<112}end
   if c.x>=2990 then return{right=true}end
   if c.grounded and not c.lastA then waterExitJumpAt=c.poll end
   return{right=true,a=waterExitJumpAt and c.poll-waterExitJumpAt<24}
  end
  -- Swim around mid-height and hold Right into the underwater exit pipe.
  if c.char==0 or c.char==8 then b.a=c.y>100 and not c.lastA
  else b.a=c.grounded and not c.lastA end
  b.b=c.poll%8==0
  if solid(c.x+20,c.y+8)then b.a=not c.lastA end
  if c.char==10 and c.r('XgWall')~=0 then
   b.up=true
   local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
   b.a=not solid(probe,c.y+3)and not c.lastA
  end
  return finish(b,c)
 end
 local e
 for slot=0,5 do
  local id,st=c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
  local dx=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)-c.x
  if c.r('Enemy_Flag',slot)>0 and id<0x15 and st<0x20 and not(id==6 and st>=2)and dx> -12 and dx<120 then
   if not e or math.abs(dx)<math.abs(e.dx)then e={dx=dx,y=c.r('Enemy_Y_Position',slot),id=id}end
  end
 end
 b.b=e and math.abs(e.dx)<48 and math.abs(e.y-c.y)<44 and c.poll%12==0
 local obstacle=solid(c.x+24,c.y+height-8)or solid(c.x+24,c.y+8)
 if c.char==5 and not c.grounded then
  local supportBelow=false
  for y=math.max(32,feet+4),232,8 do if solid(c.x+8,y)then supportBelow=true;break end end
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   if c.r('Enemy_Flag',i)>0 and id>=0x24 and id<=0x2c then
    local left=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local top=c.r('Enemy_Y_Position',i)
    local ctrl=c.r('Enemy_BoundBoxCtrl',i)
    local width=ctrl==6 and 48 or ctrl==5 and 32 or 24
    if c.x+8>=left and c.x+8<left+width and top>=feet-4 then supportBelow=true end
   end
  end
  allowDouble=not supportBelow or obstacle
 end
 -- A floor far beneath a pipe/platform is not support for its current ledge.
 local ledgeProbe=c.char==5 and 12 or 20
 local supportAhead=solid(c.x+ledgeProbe,math.min(feet+8,232))
 local gap=not supportAhead
 if c.grounded and not solid(c.x+8,math.min(feet+2,232))then
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   if c.r('Enemy_Flag',i)>0 and id>=0x24 and id<=0x2c then
    local left=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local top=c.r('Enemy_Y_Position',i)
    local ctrl=c.r('Enemy_BoundBoxCtrl',i)
    local width=ctrl==6 and 48 or ctrl==5 and 32 or 24
    local vertical=math.abs(feet-top)<8 or(id>=0x2b and math.abs(feet-(top+128)%256)<8)
    if vertical and c.x+14>=left and c.x+2<left+width then
     -- Native platforms are not in the metatile buffer. Cross their actual
     -- width before launching, rather than jumping from their near edge.
     gap=c.x+ledgeProbe>=left+width
     break
    end
   end
  end
 end
 if c.grounded and not c.lastA and(obstacle or gap or still>20)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<30 end
 if allowDouble and c.char==5 and not c.grounded and jumpAge>=31 and c.r('RgDoubleJump')~=0
  and(gap or obstacle)and c.y>60 then b.a=not c.lastA end
 if e and math.abs(e.dx)<(c.char==5 and 43 or 31)and math.abs(e.y-c.y)<32 and c.grounded then
  b.right=false;b.left=false;b.b=c.r('RgAttack')==0;b.a=false
  holdA=0;cooldown=4
  local facing=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=facing then return{left=facing==2,right=facing==1}end
  -- Ryu's crouch blade is seven pixels lower. Keep the standing blade for
  -- a hopping Koopa whose body is above him instead of slashing under it.
  if c.char==10 and e.y>=c.y or c.char==5 and e.id==6 then b.down=true end
 end
 if c.char==4 and e and e.dx>35 and e.dx<90 and math.abs(e.y-c.y)<80 and c.r('RgAttack')==0 then
  b.select=true;b.up=e.y<c.y-28
 end
 if c.char==4 and c.grounded and c.r('RgAttack')>0 and(gap or obstacle)then
  -- Link's source forbids a ground jump during his sword/throw sequence.
  -- Let that attack finish on the support before pressing a fresh A.
  holdA=0;cooldown=4;b.a=false;b.right=false;b.left=false
  return b
 end
 if c.areaType==3 and c.grounded then
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   local dx=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)-c.x
   local dy=c.r('Enemy_Y_Position',i)-c.y
   -- Bowser flames use bbox Y+4..8. A high flame can safely pass over a
   -- standing guest; jumping merely because its origin is nearby hits it.
   -- Include its remaining vertical travel toward the native target row.
   local flameTop,flameBottom=c.y+dy+4,c.y+dy+8
   if id==0x15 and c.r('Enemy_Y_MoveForce',i)~=0 then
    local target=({144,128,112,144})[c.r('BowserFlamePRandomOfs',i)%4+1]
    flameTop=math.min(c.y+dy,target)+4
    flameBottom=math.max(c.y+dy,target)+8
   end
   local head=c.y+(c.char==4 and 18 or 1)
   local flameThreat=flameBottom>=head and flameTop<=c.y+32
   if c.r('Enemy_Flag',i)>0 and((id==0x15 and dx>0 and dx<80 and flameThreat)
      or(id==0x2d and dx>0 and dx<55 and math.abs(dy)<40))then
    b.b=false;b.select=false
    if c.char==4 and c.r('RgAttack')>0 then holdA=0;cooldown=0;return{left=true}end
    if not c.lastA then b.a=true;jumpAge=0 end
   end
  end
 end
 if c.char==10 and c.r('XgWall')~=0 then
  b.up=true;b.a=not solid(c.x+21,c.y+3)and not c.lastA
 end
 if c.char==10 and obstacle and c.grounded and still>10 and solid(c.x+8,c.y-8)then
  holdA=0;cooldown=4;b.a=false;b.down=true;b.b=c.r('RgAttack')==0
 end
 if c.char==5 and obstacle and c.grounded and still>8 and solid(c.x+8,c.y-8)then
  -- His standing whip reaches the low wall's bottom brick; crouching passes
  -- underneath that row. Release B between source whip sequences.
  holdA=0;cooldown=4
  return{b=c.poll%28<6}
 end
 if c.world==0 and c.level==0 and c.x>=2390 and c.x<2480 and not outdoorStairReady then
  if c.grounded and c.x>=2430 and c.x<=2437 and c.y<=112 then
   outdoorStairReady=true;holdA=0;cooldown=4;return{right=true}
  end
  return finish({right=c.x<2433,left=c.x>2435,a=c.grounded and c.x<2430 and not c.lastA},c)
 end
 if c.world==0 and c.level==1 and c.areaType==2 then
  if c.x>=2580 then
   holdA=0;cooldown=0
   if exitPhase=='back'then
    local target=math.max(2616,c.camera+1)
    if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter'end
    return{right=c.x<target,left=c.x>target+3}
   end
   return{right=true}
  end
  if not stairsMounted and c.x>=2144 and c.x<2208 then
   if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return{right=true}end
   return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA},c)
  end
  if c.x>=2208 then
   -- Step across the descending lift. A ground launch near the next bank
   -- reaches the rising lift; repeated Simon double jumps reach the roof.
   holdA=0;cooldown=0
   local tail={right=b.right,left=b.left,up=b.up,down=b.down,b=b.b}
   if c.char==10 and c.r('XgWall')~=0 then tail.a=b.a end
   if c.x<2380 and c.grounded and obstacle and not c.lastA then tail.a=true end
   if c.x>=2380 and c.x<2420 then
    if c.grounded and not c.lastA and liftLaunch==0 then liftLaunch=6 end
    if liftLaunch>0 then tail.a=true;liftLaunch=liftLaunch-1 end
   else liftLaunch=0 end
   if c.x>=2490 and c.x<2570 and(c.yHigh==0 or c.y<48)then tail.right=false end
   return tail
  end
  if c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then holdA=0;cooldown=0;return{right=true}end
  if c.char==4 and not lowMounted and c.x>=1170 and c.x<1290 then
   if c.y<=112 and c.grounded then lowMounted=true
   elseif solid(1224,152)then
    if lowMount=='back'then
     holdA=0;local target=math.max(1196,c.camera+1)
     if c.x>=target and c.x<=target+2 and c.grounded then lowMount='rise';return finish({a=true},c)end
     return{right=c.x<target,left=c.x>target+2}
    elseif lowMount=='rise'then
     if c.y<=112 then lowMount='onto'end
     return finish({a=c.grounded and not c.lastA},c)
    else
     if c.grounded and c.y>112 then lowMount='back';holdA=0;cooldown=4;return{left=true}end
     return finish({right=c.x<1250,left=c.x>1252},c)
    end
   else lowMounted=true end
  end
  if not pillarLanded and c.x>=1944 and c.x<1984 then
   if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c)end
   return finish({right=c.x<1960,left=c.x>1964},c)
  end
 end
 -- Underground exit: walking into its vertical pipe enters normally.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2800 then b.a=false end
 return finish(b,c)
end



end)()
local other=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()
return function(c)
 if c.char==12 and c.r("DarkwingVariant")==0 then return scrooge(c)end
 if c.char==5 and c.r("Cv3Variant")==0 then return simon(c)end
 return other(c)
end

end)()
local simon=(function()
-- Controller inputs only: stop on support and use the actual whip.
local base=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()
return function(c)
 local b=base(c)
 if c.char~=5 or c.r('Cv3Variant')~=0 or c.r('CrossoverBehaviorVersion')~=1 or c.x<420 then return b end
 local e=c.enemy()
 if c.grounded and e and math.abs(e.dx)<60 and math.abs(e.y-c.y)<48 then
  local face=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=face then return {left=face==2,right=face==1}end
  return {down=e.id==6,b=c.r('RgAttack')==0}
 end
 return b
end

end)()
local native=(function()
-- Metadata aliases only; no writes to emulated state.
L.CdHeld=23570
L.CdThrowAge=23572
L.CdBoxKind=23584
L.CdBoxMode=23638
L.CdBoxX=23590
L.CdBoxPage=23596
L.CdBoxY=23602
L.DwHealth=29679
L.DwAdaptor=29681
L.DwMode=29682
L.DwGas=29680
L.DwHang=29687
L.FrameCounter=14
L.RgShotType=27755
L.DarkwingVariant=29663
L.Z2Variant=29688
L.XgWall=28345
local base=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()

local lastArrowPipe=0
local arrowStage='align';local arrowShot=false
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
local observation
if ROSTER_CONFIG.name=='darkwing'then
 observation=assert(io.open(ROSTER_CONFIG.out..'native-controls.csv','w'))
 observation:write('frame,x,y,hp,adaptor,mode,gas,hang,pipeStage,arrows\n')
end
return function(c)
 local b=base(c)
 if observation then
  local arrows=0;for i=0,9 do if c.r('RgShotType',i)==6 then arrows=arrows+1 end end
  observation:write(table.concat({c.frame,c.x,c.y,c.r('DwHealth'),c.r('DwAdaptor'),c.r('DwMode'),c.r('DwGas'),c.r('DwHang'),arrowStage,arrows},',')..'\n');observation:flush()
 end
 -- Actual shooter combat before attempting a ground jump into an enemy.
 if c.char==2 or c.char==3 or c.char==9 or(c.char==12 and c.r('DarkwingVariant')~=0)then
  local e=c.enemy()
  if c.grounded and e and e.dx>0 and e.dx<120 and math.abs(e.y-c.y)<42 then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{b=c.r('FrameCounter')%12<2}
  end
 end
 if c.char==4 and c.r('Z2Variant')==0 and c.grounded and b.a then
  b.b=false
  if c.r('RgAttack')~=0 then b.a=false;b.right=false;b.left=false end
 end
 if c.char==10 and c.r('XgWall')~=0 then
  local face=c.r('PlayerFacingDir');local probe=c.x+(face==1 and 21 or-5)
  return{right=face==1,left=face==2,up=true,a=not c.lastA and not solid(c,probe,c.y+3)}
 end
 if c.char==14 then
  b.b=false
  local held=c.r('CdHeld');local e=c.enemy()
  local close=e and e.dx> -16 and e.dx<56 and math.abs(e.y-c.y)<46
  if held~=0 then
   if close and c.grounded then
    if c.r('PlayerFacingDir')~=1 then return{right=true}end
    if e.dx<22 then return{down=true}end
    return{b=c.r('CdThrowAge')==0 and(c.r('SavedJoypadBits')&64)==0}
   end
  else
   local nearby=false
   for i=0,5 do
    if c.r('CdBoxKind',i)~=0 and c.r('CdBoxMode',i)==0 then
     local wx=c.r('CdBoxX',i)+256*c.r('CdBoxPage',i)
     if math.abs(wx-c.x)<=20 and math.abs(c.r('CdBoxY',i)-c.y)<40 then nearby=true end
    end
   end
   local x=c.x+(c.r('PlayerFacingDir')==1 and 20 or-4)
   local t=c.block(x,c.y+20)
   if nearby or t==0x51 or t==0x52 then b.b=(c.r('SavedJoypadBits')&64)==0 end
   if close and c.grounded and not c.lastA then b.a=true;b.b=false end
  end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 -- Darkwing's real Arrow adaptor creates a native climbable wall actor.
 -- Use it for the tall pipes; no ability/equipment is granted by the script.
 if c.char==12 and c.r('DarkwingVariant')~=0 then
  local pipe
  if c.x>=660 and c.x<778 then pipe=736 elseif c.x>=836 and c.x<954 then pipe=912 end
  if pipe and c.r('DwAdaptor')==2 then
   if lastArrowPipe~=pipe then lastArrowPipe=pipe;arrowStage='align';arrowShot=false end
   if c.r('DwMode')==0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
   if c.r('DwHang')>=128 then
    arrowStage='cross';return{right=true,a=not c.lastA}
   end
   if arrowStage=='align'then
    local target=pipe-34
    if c.grounded and c.x>=target and c.x<=target+2 then arrowStage='rise'
    else return{right=c.x<target,left=c.x>target+2}end
   end
   if arrowStage=='rise'then
    local shoot=not arrowShot and not c.grounded and c.y<=128
    if shoot then arrowShot=true end
    if arrowShot and c.grounded then arrowStage='rise';arrowShot=false end
    return{a=c.grounded and not c.lastA or c.vy>=128,b=shoot}
   end
   return{right=true,a=c.vy>=128}
  end
  if not pipe and c.r('DwMode')~=0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 return b
end

end)()
local darkwing=(function()
local normal=(function()
-- Metadata aliases only; no writes to emulated state.
L.CdHeld=23570
L.CdThrowAge=23572
L.CdBoxKind=23584
L.CdBoxMode=23638
L.CdBoxX=23590
L.CdBoxPage=23596
L.CdBoxY=23602
L.DwHealth=29679
L.DwAdaptor=29681
L.DwMode=29682
L.DwGas=29680
L.DwHang=29687
L.FrameCounter=14
L.RgShotType=27755
L.DarkwingVariant=29663
L.Z2Variant=29688
L.XgWall=28345
local base=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()

local lastArrowPipe=0
local arrowStage='align';local arrowShot=false
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
local observation
if ROSTER_CONFIG.name=='darkwing'then
 observation=assert(io.open(ROSTER_CONFIG.out..'native-controls.csv','w'))
 observation:write('frame,x,y,hp,adaptor,mode,gas,hang,pipeStage,arrows\n')
end
return function(c)
 local b=base(c)
 if observation then
  local arrows=0;for i=0,9 do if c.r('RgShotType',i)==6 then arrows=arrows+1 end end
  observation:write(table.concat({c.frame,c.x,c.y,c.r('DwHealth'),c.r('DwAdaptor'),c.r('DwMode'),c.r('DwGas'),c.r('DwHang'),arrowStage,arrows},',')..'\n');observation:flush()
 end
 -- Actual shooter combat before attempting a ground jump into an enemy.
 if c.char==2 or c.char==3 or c.char==9 or(c.char==12 and c.r('DarkwingVariant')~=0)then
  local e=c.enemy()
  if c.grounded and e and e.dx>0 and e.dx<120 and math.abs(e.y-c.y)<42 then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{b=c.r('FrameCounter')%12<2}
  end
 end
 if c.char==4 and c.r('Z2Variant')==0 and c.grounded and b.a then
  b.b=false
  if c.r('RgAttack')~=0 then b.a=false;b.right=false;b.left=false end
 end
 if c.char==10 and c.r('XgWall')~=0 then
  local face=c.r('PlayerFacingDir');local probe=c.x+(face==1 and 21 or-5)
  return{right=face==1,left=face==2,up=true,a=not c.lastA and not solid(c,probe,c.y+3)}
 end
 if c.char==14 then
  b.b=false
  local held=c.r('CdHeld');local e=c.enemy()
  local close=e and e.dx> -16 and e.dx<56 and math.abs(e.y-c.y)<46
  if held~=0 then
   if close and c.grounded then
    if c.r('PlayerFacingDir')~=1 then return{right=true}end
    if e.dx<22 then return{down=true}end
    return{b=c.r('CdThrowAge')==0 and(c.r('SavedJoypadBits')&64)==0}
   end
  else
   local nearby=false
   for i=0,5 do
    if c.r('CdBoxKind',i)~=0 and c.r('CdBoxMode',i)==0 then
     local wx=c.r('CdBoxX',i)+256*c.r('CdBoxPage',i)
     if math.abs(wx-c.x)<=20 and math.abs(c.r('CdBoxY',i)-c.y)<40 then nearby=true end
    end
   end
   local x=c.x+(c.r('PlayerFacingDir')==1 and 20 or-4)
   local t=c.block(x,c.y+20)
   if nearby or t==0x51 or t==0x52 then b.b=(c.r('SavedJoypadBits')&64)==0 end
   if close and c.grounded and not c.lastA then b.a=true;b.b=false end
  end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 -- Darkwing's real Arrow adaptor creates a native climbable wall actor.
 -- Use it for the tall pipes; no ability/equipment is granted by the script.
 if c.char==12 and c.r('DarkwingVariant')~=0 then
  local pipe
  if c.x>=660 and c.x<778 then pipe=736 elseif c.x>=836 and c.x<954 then pipe=912 end
  if pipe and c.r('DwAdaptor')==2 then
   if lastArrowPipe~=pipe then lastArrowPipe=pipe;arrowStage='align';arrowShot=false end
   if c.r('DwMode')==0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
   if c.r('DwHang')>=128 then
    arrowStage='cross';return{right=true,a=not c.lastA}
   end
   if arrowStage=='align'then
    local target=pipe-34
    if c.grounded and c.x>=target and c.x<=target+2 then
     if c.r('PlayerFacingDir')~=1 then return{right=true}end
     arrowStage='rise'
    else return{right=c.x<target,left=c.x>target+2}end
   end
   if arrowStage=='rise'then
    local shoot=not arrowShot and not c.grounded and c.y<=128
    if shoot then arrowShot=true end
    if arrowShot and c.grounded then arrowStage='rise';arrowShot=false end
    return{a=c.grounded and not c.lastA or c.vy>=128,b=shoot}
   end
   return{right=true,a=c.vy>=128}
  end
  if not pipe and c.r('DwMode')~=0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 return b
end

end)()
local log
local launchHold=0
local ledges={{start=2160,target=2197,top=112,finish=2258,phase='approach',wait=0},{start=2390,target=2440,top=112,finish=2516,phase='approach',wait=0}}
if ROSTER_CONFIG.name=='darkwing'then
 log=assert(io.open(ROSTER_CONFIG.out..'recovery-controls.csv','w'))
 log:write('frame,x,y,hp,adaptor,gas,mode,state,cache,stage\n')
end
return function(c)
 if c.char~=12 or c.r('DarkwingVariant')==0 or c.world~=0 or c.level~=0 then return normal(c)end
 if log then
  log:write(table.concat({c.frame,c.x,c.y,c.r('DwHealth'),c.r('DwAdaptor'),c.r('DwGas'),c.r('DwMode'),c.state,c.peek(0x5e84),'native'},',')..'\n');log:flush()
 end
 -- Keep ordinary enemies from consuming the limited pipe-traversal ammo.
 local e=c.enemy()
 if c.grounded and e and e.id~=13 and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
  if c.r('DwMode')~=0 then return{select=(c.r('SavedJoypadBits')&32)==0}end
  local face=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
  return{b=c.r('FrameCounter')%12<2}
 end
 local pipe
 if c.x>=660 and c.x<778 then pipe=736 elseif c.x>=836 and c.x<954 then pipe=912 end
 if pipe and(c.r('DwAdaptor')~=2 or c.r('DwGas')<3)then
  -- The native recovery offers an actual Arrow actor behind a grounded
  -- player pressing into a tall typed pipe. Wait on support to request it.
  local cache
  for i=0,5 do
   if c.r('Enemy_Flag',i)~=0 and c.r('Enemy_ID',i)==0x2e and c.r('InvPickupOwner',i)==12 and c.r('InvPickup',i)==0x26 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if math.abs(x-c.x)<80 and c.r('Enemy_Y_Position',i)>=160 then cache=x end
   end
  end
  if cache then return{left=c.x>cache+3,right=c.x<cache-3}end
  return{right=true}
 end
 local b=normal(c)
 -- The gun's native ground pose stops walking. Only actual combat above
 -- fires it; a navigation controller must not repeatedly stop on empty floor.
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 if not pipe then
  b.b=false
  local foot=math.min(c.y+40,232)
  if c.grounded then
   local obstacle=solid(c.x+32,c.y+24)or solid(c.x+32,c.y+8)
   local gap=not solid(c.x+8,foot)
   b.a=not c.lastA and(obstacle or gap)
   if b.a then launchHold=6 end
   if launchHold>0 then b.a=true;launchHold=launchHold-1 end
  else
   launchHold=0;b.a=c.vy>=128
  end
  for _,ledge in ipairs(ledges)do
   if c.x>=ledge.start and c.x<ledge.finish and ledge.phase~='done'then
    if ledge.phase=='approach'then
     b.right=c.x<ledge.target;b.left=c.x>ledge.target+2
     if c.x>=ledge.target-1 and c.x<=ledge.target+2 and c.y<=ledge.top then ledge.phase='land' end
    end
    if ledge.phase=='land'then
     b={right=c.x<ledge.target,left=c.x>ledge.target+2}
     if c.grounded then
      if c.y<=ledge.top then ledge.wait=ledge.wait+1
       if ledge.wait>=6 then ledge.phase='cross';launchHold=6;b={right=true,a=true}end
      else ledge.phase='approach';ledge.wait=0 end
     end
    elseif ledge.phase=='cross'then
     b={right=true,a=launchHold>0 or c.vy>=128}
     if launchHold>0 then launchHold=launchHold-1 end
    end
    return b
   elseif c.x>=ledge.finish then ledge.phase='done'end
  end
 end
 return b
end

end)()
local mario=(function()
-- Samus/Bill/Lance candidate discovery. No emulated memory writes.
local travel=(function()
-- Pit/Rygar/Sophia route discovery. Read-only telemetry and ordinary inputs.
-- A candidate is evidence only after the complete CSV independently replays.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
local launchHold=0
local waterExit='back'
return function(c)
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.areaType
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0;launchHold=0 end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 local height=32
 local feet=c.y+height
 local solid=function(wx,y)local t=c.block(wx,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if still==60 and c.world==0 and c.level==1 and c.x>2950 then
  local cells={}
  for y=128,208,16 do cells[#cells+1]=y..':'..c.block(c.x+15,y)..'/'..c.block(c.x+16,y)end
  print('PIPE diagnostic x='..c.x..' y='..c.y..' state='..c.state..' facing='..c.r('PlayerFacingDir')..' attr='..c.r('Player_SprAttrib')..' cells='..table.concat(cells,','))
 end
 if c.areaType==0 then
  if c.char==8 and c.world==1 and c.level==1 and c.x>=2984 then
   if waterExit=='back' then
    if c.y>=100 and c.y<=112 and c.x>=2990 and c.x<=3018 then waterExit='enter' end
    return {right=c.x<3006,left=c.x>3010,b=true,a=c.y>110 and not c.lastA}
   end
   return {right=true,b=true}
  end
  -- Pit/Rygar retain source jump/gravity; Sophia can steer vertically.
  if c.char==0 or c.char==8 then
   -- Travel below pursuing Bloopers, rising only for the real coral columns.
   local target=164
   local probe
   if solid(c.x+24,c.y+8)then probe=c.y+8
   elseif solid(c.x+24,c.y+24)then probe=c.y+24 end
   if probe then
    local top=32+math.floor((probe-32)/16)*16
    local bottom=top+16
    while top>32 and solid(c.x+24,top-1)do top=top-16 end
    while bottom<224 and solid(c.x+24,bottom)do bottom=bottom+16 end
    if top==32 then target=math.min(176,bottom+4)
    else target=math.min(target,top-34)end
   end
   b.a=c.y>target and not c.lastA
  elseif c.char==11 then
   b.up=c.y>112;b.down=c.y<88
   if solid(c.x+24,c.y+24)then b.up=true;b.down=false end
  elseif c.char==12 then
   local obstacle=solid(c.x+40,c.y+8)or solid(c.x+40,c.y+24)
   local gap=not solid(c.x+32,math.min(c.y+40,232))
   b.a=c.grounded and not c.lastA and(obstacle or gap)
   if not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
  else
   b.a=c.grounded and not c.lastA
   if not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
  end
  b.b=(c.char==0 or c.char==8)or(c.char==12 and c.poll%16<4)or(c.char~=12 and c.poll%8==0)
  if c.x>3000 then b.a=false;b.up=false;b.down=c.y<160 end
  return b
 end
 local e=c.enemy()
 b.b=(c.char==0 or c.char==8)or c.poll%8==0
 if c.char~=0 and c.char~=8 and c.char~=12 and e and e.dx>32 and e.dx<112 and math.abs(e.y-c.y)<24 and c.grounded and launchHold==0 then
  b.right=false;b.down=c.char==6 or c.char==7
  return b
 end
 if c.char~=0 and c.char~=8 and c.char~=12 and e and e.dx>12 and e.dx<96 and math.abs(e.y-c.y)<48 and not c.grounded and c.vy<128 then
  for y=math.min(feet+8,232),232,16 do if solid(c.x+8,y)then b.right=false;break end end
 end
 local obstacle=solid(c.x+40,c.y+height-8)or solid(c.x+40,c.y+8)
 local mount=c.areaType==2 and(solid(c.x+40,c.y-24)or solid(c.x+40,c.y-8))and not solid(c.x+24,c.y+16)
 local gapRange=(c.char==12 and c.areaType==3)and 16 or 32
 local gap=not solid(c.x+gapRange,math.min(feet+8,232))
 local enemy=e and e.dx>0 and e.dx<45 and math.abs(e.y-c.y)<48
 if c.grounded and not c.lastA and(obstacle or mount or gap or enemy or still>20)then b.a=true;jumpAge=0;launchHold=6
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
 if launchHold>0 then
  if c.grounded then b.a=true;launchHold=launchHold-1 else launchHold=0 end
 end
 -- Underground exit: walking into its vertical pipe enters normally.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2140 then
  if c.x<2380 or c.x>=2420 then launchHold=0 end
  b.a=c.x>=2380 and c.x<2420 and c.grounded and not c.lastA
  if b.a then launchHold=6;jumpAge=0 end
  if launchHold>0 then b.a=true;launchHold=launchHold-1 end
  if c.x>=2490 and c.x<2570 and(c.yHigh==0 or c.y<48)then b.right=false end
 end
 return b
end

end)()
local initialUpgrade=false
local phase='approach'
local jumpAge=0
local mount
local pillarLanded=false
local lowMount='back'
local lowMounted=false
local stairsMounted=false
local exitPhase='back'
local plantX,plantReady=nil,false
local holdA,cooldown=0,0
local function finish(b,c)
 if cooldown>0 then cooldown=cooldown-1 end
 if b.a and holdA==0 and cooldown==0 then holdA=32 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end end
 return b
end
return function(c)
 local b=travel(c)
 if c.areaType==0 then holdA=0;cooldown=0;return b end
 if c.world==0 and c.level==0 and c.x>420 then initialUpgrade=true end
 b.b=(c.char==0 or c.char==8)or c.poll%12<5
 if(c.char==0 or c.char==8)and c.world==0 and c.level==2 and c.x<760 then b.b=false end
 local e=c.enemy()
 -- Land at the near edge of 1-3's high platform before firing at its Goombas.
 -- Bill and Lance cannot use Mario's stomp to resolve a descending overlap.
 if c.char==3 and c.world==0 and c.level==2 and c.x>=600 and c.x<640 and e and e.id==6 and e.y<80 and e.dx>16 and e.dx<128 then
  return finish({right=c.x<614,left=c.x>618,down=c.grounded,b=c.poll%12<5},c)
 end
 if c.char==3 and e and e.id~=13 and not c.grounded then
  b.up=e.y<c.y-8;b.down=e.y>c.y+8
 end
 -- Drop to the ordinary side entrance before walking into the exit pipe.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then
  holdA=0;cooldown=0
  if exitPhase=='back' then
   local target=math.max(2616,c.camera+1)
   if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter' end
   return {right=c.x<target,left=c.x>target+3,b=c.poll%12<5}
  end
  return {right=true,b=c.poll%12<5}
 end
 -- Land on the final stair before crossing to the descending lift.
 -- A single jump from the lower stair reaches only its bottom copy.
 if c.world==0 and c.level==1 and not stairsMounted and c.x>=2144 and c.x<2208 then
  if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return {right=true,b=true}end
  return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- Walk across the descending lift before jumping toward the next bank.
 -- Its second platform sits overhead, so a jump from the left edge is short.
 if c.world==0 and c.level==1 and c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then
  holdA=0;cooldown=0;return {right=true,b=c.poll%12<5}
 end
 -- Samus can clear a live plant by launching near its pipe, keeping the
 -- apex over the plant rather than using the generic early enemy jump.
 if c.char==2 and e and e.id==13 and e.dx>0 and e.dx<80 then
  if c.grounded and e.dx>42 then holdA=0;return {right=true,b=c.poll%12<5}end
  return finish({right=true,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- A Piranha is above the floor muzzle. Jump vertically and fire before
 -- crossing its pipe, rather than shooting below it or landing on its head.
 if c.char==3 and e and e.id==13 and e.dx> -16 and e.dx<68 then
  if plantX~=e.x then plantX=e.x;plantReady=false end
  if not plantReady then
   if e.dx<56 then holdA=0;return {left=true,b=false}end
   plantReady=true
  elseif e.dx<32 then plantReady=false;holdA=0;return {left=true}end
  if c.r('PlayerFacingDir')~=1 then return {right=true}end
  return finish({a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 if c.world==0 and c.level==1 and c.areaType==2 and not lowMounted and c.x>=1170 and c.x<1290 then
  if c.y<=112 and c.grounded then lowMounted=true
  elseif c.block(1224,152)~=0 and c.block(1224,152)~=0x23 then
   if lowMount=='back'then
    holdA=0
    local target=math.max(1196,c.camera+1)
    if c.x>=target and c.x<=target+2 and c.grounded then lowMount='rise';return finish({a=true},c)end
    return {right=c.x<target,left=c.x>target+2}
   elseif lowMount=='rise'then
    if c.y<=112 then lowMount='onto' end
    return finish({a=c.grounded and not c.lastA},c)
   else
    if c.grounded and c.y>112 then lowMount='back';holdA=0;cooldown=4;return {left=true}end
    return finish({right=c.x<1250,left=c.x>1252},c)
   end
  else lowMounted=true end
 end
 -- The underground pair of gaps contains a narrow intermediate column.
 -- Land on its real top instead of carrying one jump past both gaps.
 if c.world==0 and c.level==1 and c.areaType==2 and not pillarLanded and c.x>=1944 and c.x<1984 then
  if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c)end
  return finish({right=c.x<1960,left=c.x>1964},c)
 end
 if c.char==2 and c.r('SmBall')~=0 then
  -- Never strand a controller candidate in Morph Ball at a pipe.
  b.up=c.poll%2==0;b.down=false;b.a=false
 end
 -- The first ordinary mushroom is a real native pickup, collected through
 -- head contact and pursuit. Other upgrade coverage uses separate arenas.
 if c.world~=0 or c.level~=0 or initialUpgrade then return finish(b,c)end
 if c.status>0 or(c.char==3 and(c.r('InvOwnedLo',3)+256*c.r('InvOwnedHi',3))>1)then initialUpgrade=true;return finish(b,c)end
 if phase=='approach' and c.x<320 then return finish(b,c)end
 if (phase=='approach' or phase=='bump') and c.grounded and c.y<=128 then phase='drop' end
 b={}
 if phase=='drop' then
  b.right=c.x<392;b.left=false;b.a=false
  if c.y>=150 then phase='approach' end
 elseif phase=='approach' then
  b.right=c.x<330;b.left=c.x>334
  if c.x>=330 and c.x<=334 and c.grounded then phase='bump';jumpAge=0 end
 elseif phase=='bump' then
  b.a=jumpAge<30;jumpAge=jumpAge+1
  b.right=c.x<330;b.left=c.x>334
  if jumpAge>65 and c.grounded then jumpAge=0 end
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then phase='collect' end end
 elseif phase=='collect' then
  local px,py
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)
  end end
  if not px then phase='bump';jumpAge=0;return finish(b,c)end
  b.right=c.x<px-5;b.left=c.x>px+5
  if not mount and py<c.y-10 and c.grounded and c.y>144 then mount='back';holdA=0 end
  if mount then
   local target=math.max(284,c.camera+1)
   if mount=='back'then
    b.right=c.x<target;b.left=c.x>target+1;b.a=false
    if c.x>=target and c.x<=target+1 and c.grounded then mount='rise';b.a=true end
   elseif mount=='rise'then
    b.right=false;b.left=false
    if c.y<=112 then mount='onto' end
    if c.grounded and not c.lastA then b.a=true end
   else
    b.right=c.x<px-4;b.left=c.x>px+4
    if c.grounded and c.y>144 then mount='back' end
   end
  elseif py<c.y-10 and c.grounded then b.a=not c.lastA end
 end
 if e and math.abs(e.dx)<90 then
  b.b=c.poll%7==0
  if c.char==3 then b.down=c.grounded end
  if math.abs(e.dx)<24 and c.grounded then b.a=not c.lastA;b.down=false end
 end
 return finish(b,c)
end


end)()

local lateGap='approach';local holdA=0
return function(c)
 if c.char==12 and c.r('DarkwingVariant')~=0 then return darkwing(c)end
 if c.char==0 or c.char==2 then return mario(c)end
 if c.char==8 then return baseline(c)end
 if c.char==12 and c.r('DarkwingVariant')==0 then return scrooge(c)end
 if c.char==5 and c.r('Cv3Variant')==0 then return simon(c)end
 if c.char==2 or c.char==3 or c.char==10 or c.char==14 or(c.char==4 and c.r('Z2Variant')==0)or(c.char==9 and c.r('RlVariant')==0)then
  local b=native(c)
  local e=c.enemy()
  if c.char==3 and c.grounded and e and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
   local face=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
   return{down=true,b=c.r('FrameCounter')%12<2}
  end
  return b
 end
 local b=baseline(c)
 if c.world==0 and c.level==0 and(c.char==17 or(c.char==5 and c.r('Cv3Variant')==3))and c.x>=2380 and c.x<2512 then
  if lateGap=='approach'and c.x>=2410 and c.y<=100 then lateGap='land'end
  if lateGap=='land'then
   b={right=c.x<2412,left=c.x>2420}
   if c.grounded and c.y<=112 then lateGap='jump';holdA=6;b={right=true,a=true}end
   return b
  elseif lateGap=='jump'then
   b.right=true;b.left=false;b.b=c.char==17;b.a=holdA>0 or c.vy>=128
   if holdA>0 then holdA=holdA-1 end
  end
 end
 if c.char==5 and c.r('Cv3Variant')>0 and c.grounded and b.a then
  b.b=false
  if c.r('Cv3AttackAge')~=0 then b.a=false;b.right=false;b.left=false end
 end
 return b
end

end)()
local groundHold=0;local bassHold=0
local ledges={{start=2160,target=2197,top=112,finish=2258,phase='approach',wait=0},{start=2390,target=2440,top=112,finish=2516,phase='approach',wait=0}}
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 local e=c.enemy()
 if c.char==2 and c.r('CrossoverBehaviorVersion')==1 then
  if c.grounded and e and e.id~=13 and math.abs(e.dx)<120 and math.abs(e.y-c.y)<42 then
   if c.r('SmBall')~=0 then return{up=true}end
   if c.r('SmCrouch')==0 then return{down=true}end
   local face=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=face then return{down=true,left=face==2,right=face==1}end
   return{down=true,b=c.r('FrameCounter')%12<2}
  elseif c.r('SmCrouch')~=0 then return{up=true}end
 end
 if c.char==9 and c.r('RlVariant')==0 and not c.grounded and c.r('XgJumpUsed')==0 and c.vy<128 and c.y>48 then
  -- Bass owns a real unused double jump. Release, then hold its new A edge.
  if not c.lastA then bassHold=4 end
  b.a=bassHold>0
 end
 if bassHold>0 then b.a=true;bassHold=bassHold-1 end
 local useLedges=c.char==0 or c.char==4 or c.char==7 or c.char==10 or(c.char==5 and c.r('Cv3Variant')~=0)
 if c.char==0 then for _,ledge in ipairs(ledges)do ledge.top=112+(c.r('PlayerSize')~=0 and 16 or 0)end end
 if useLedges then
  for _,ledge in ipairs(ledges)do
   if c.x>=ledge.start and c.x<ledge.finish and ledge.phase~='done'then
    if ledge.phase=='approach'then
     b.right=c.x<ledge.target;b.left=c.x>ledge.target+2
     if c.x>=ledge.target-1 and c.x<=ledge.target+2 and c.y<=ledge.top then ledge.phase='land'end
    end
    if ledge.phase=='land'then
     b={right=c.x<ledge.target,left=c.x>ledge.target+2}
     if c.grounded then
      if c.y<=ledge.top then
       ledge.wait=ledge.wait+1
       if ledge.wait>=6 then ledge.phase='cross';groundHold=6;b={right=true,a=true}end
      else ledge.phase='approach';ledge.wait=0 end
     end
    elseif ledge.phase=='cross'then b={right=true,a=groundHold>0 or c.vy>=128}end
   elseif c.x>=ledge.finish then ledge.phase='done'end
  end
 end
 -- Deliver a grounded edge through at least two updates of a lagging scene.
 if c.grounded and b.a and not c.lastA then groundHold=6 end
 if groundHold>0 then b.a=true;groundHold=groundHold-1 end
 return b
end

end)()
local flagHold=0
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==17 and c.x>3115 and c.x<3184 then
  -- The ordinary solid pole base must be jumped; walking into it is no clear.
  if c.grounded and not c.lastA then flagHold=8 end
  b={right=true,b=true,a=flagHold>0 or(not c.grounded and c.vy>=128)}
  if flagHold>0 then flagHold=flagHold-1 end
 end
 if c.char==10 then
  local e=c.enemy()
  if c.grounded and e and e.id~=13 and e.dx>0 and e.dx<88 and math.abs(e.y-c.y)<44 then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{down=true,b=c.poll%20<10}
  end
 end
 return b
end

end)()
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==10 or(c.char==5 and c.r('Cv3Variant')>0)then
  -- Their source attacks stop grounded walking. Do not spam B on empty floor.
  b.b=false
  local e=c.enemy()
  if e and e.id~=13 and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<46 then
   if c.grounded then
    if c.r('PlayerFacingDir')~=1 then return{right=true}end
    if e.dx<48 then return{down=true,b=c.poll%24<12}end
    return{}
   else
    b.b=e.dx<52 and math.abs(e.y-c.y)<30 and c.poll%24<12
   end
  end
 end
 return b
end

end)()
local sophia=(function()
-- Frozen existing controllers only. No game state grants or writes.
local base=(function()
-- Bounded controller discovery; no game-state writes or clear claim.
local base=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local pickupStart=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame;pickupStart=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-pickupStart>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='meta'and not c.grounded and obstacle and c.y>72 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()

return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==5 and c.r('Cv3Variant')==0 and not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 and c.y>32 then
  -- The actual Simon source grants an unused air jump; release and repress A.
  b.a=not c.lastA
 elseif c.char==12 and c.r('DarkwingVariant')==0 and c.x>450 then
  -- Use the native stronger pogo rather than forcing a58px ordinary jump
  -- over a64px pipe. The game, not this controller, owns the rebound.
  b.down=true;b.b=true
 end
 return b
end

end)()
local mike=(function()
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=not not near and c.poll%24<2
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  local target=100
  if c.x<400 then target=145 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-clock>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 local feet=c.y+32
 local obstacle=solid(c.x+22,feet-8)or solid(c.x+22,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+12,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end





end)()
local vic=(function()
-- Controller discovery only. No game state writes; a fixed replay is required.
return function(c)
 local b={a=c.poll%6<3,b=c.poll%24<2}
 if c.world~=0 or c.level~=0 then b.right=true;return b end
 local target=48
 b.up=c.y>target+2;b.down=c.y<target-2
 -- Rise before advancing into the first low question block. Native camera
 -- motion continues while the player deliberately holds horizontal position.
 b.right=c.y<74 and(c.x-c.camera<112 or c.r('ScrollLock')~=0)
 return b
end

end)()
local meta=(function()
-- Native grounded Meta discovery; no Up-flight or constant dash attacks.
-- Base policy SHA256 d9b37780f3a5cfdaaaa9d2fbafa5fe4628a2eeaeaaee393eba3d4d7d417c51dc
-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
local rollGap='approach'
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=c.poll%8<2
 if name=='roll'then b.b=c.poll%24<2 end
 if name=='kirby'then b.b=not not near end
 if name=='meta'then b.b=e and e.dx>-16 and e.dx<48 and math.abs(e.y-c.y)<42 and c.poll%24<2 or false end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  if name~='vic' then
   -- Leave visible reaction space ahead of a source shooter. Holding Right
   -- forever pins its tiny core to the far edge while enemies enter there.
   b.right=c.x-c.camera<128 or c.r('ScrollLock')~=0
   b.a=c.poll%8<3
   b.b=c.poll%16<4
  end
  local target=100
  if c.x<400 and name=='vic' then target=145 end
  if name~='vic' and c.x>2700 then target=55 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-clock>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 if name=='roll'and c.x>=2380 and c.x<2512 then
  -- Land on the last stair before crossing its pit. Jumping immediately
  -- from the lower step wastes the approach height and strikes the far wall.
  if rollGap=='approach'and c.x>=2410 and c.y<=100 then rollGap='land'end
  if rollGap=='land'then
   b.right=c.x<2412;b.left=c.x>2420;b.a=false;b.b=false
   if c.grounded and c.y<=112 then rollGap='jump';b.right=true;b.left=false;b.a=true end
   return b
  elseif rollGap=='jump'then b.right=true;b.a=true;return b end
 end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+32,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end

 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end

end)()
return function(c)
 if ROSTER_CONFIG.name=='mike' then return mike(c)end
 if ROSTER_CONFIG.name=='vic' then return vic(c)end
 if ROSTER_CONFIG.name=='meta' then return meta(c)end
 return base(c)
end

end)()
return function(c)if c.char==11 then return sophia(c)end;return general(c)end

end)()

local ledges={{start=2160,target=2197,top=112,finish=2258},{start=2390,target=2440,top=112,finish=2516}}
local hold=0
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 then return b end
 for _,s in ipairs(ledges)do
  if c.x>=s.finish then s.phase='done'end
  if c.x>=s.start and c.x<s.finish and s.phase~='done'then
   if not s.phase then s.phase='approach';s.wait=0 end
   b.b=false
   if s.phase=='approach'then
    b.right=c.x<s.target;b.left=c.x>s.target+2
    if c.grounded and not c.lastA and c.y>s.top then b.a=true end
    if c.x>=s.target-1 and c.x<=s.target+2 and c.y<=s.top then s.phase='land'end
   end
   if s.phase=='land'then
    b={right=c.x<s.target,left=c.x>s.target+2}
    if c.grounded then
     if c.y<=s.top then
      s.wait=s.wait+1
      if s.wait>=6 and not c.lastA then s.phase='cross';hold=34;b={right=true,a=true}end
     else s.phase='approach';s.wait=0 end
    end
   elseif s.phase=='cross'then b={right=true,a=hold>0}end
  end
 end
 if hold>0 then b.a=true;hold=hold-1 end
 
 return b
end
