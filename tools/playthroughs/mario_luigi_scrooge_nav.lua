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
