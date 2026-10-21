-- Pit/Rygar/Sophia route discovery. Read-only telemetry and ordinary inputs.
-- A candidate is evidence only after the complete CSV independently replays.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
local launchHold=0
local pillarLanded=false
local stairsMounted=false
local stairHold=0
local exitPhase='back'
return function(c)
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.areaType
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0;launchHold=0;pillarLanded=false;stairsMounted=false;stairHold=0;exitPhase='back' end
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
 if still==60 then local e=c.enemy();print('STALL char='..c.char..' x='..c.x..' y='..c.y..' enemy='..(e and(e.id..'/'..e.dx..'/'..e.y)or'none'))end
 if c.areaType==0 then
  -- Pit/Rygar retain source jump/gravity; Sophia can steer vertically.
  if c.char==11 then
   b.up=c.y>112;b.down=c.y<88
   if solid(c.x+24,c.y+24)then b.up=true;b.down=false end
  else
   local obstacle=solid(c.x+24,c.y+24) or solid(c.x+24,c.y+8)
   local gap=not solid(c.x+28,math.min(c.y+40,232))
   b.a=c.grounded and not c.lastA and (obstacle or gap or still>20)
   if not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
  end
  b.b=c.poll%8<4
  if c.x>3000 then b.a=false;b.up=false;b.down=c.char==11 and c.y<160 end
  return b
 end
 local e=c.enemy()
 b.b=c.poll%8<4
 -- Keep firing through Bowser's jump instead of approaching when his Y changes.
 if (c.char==6 or c.char==7) and c.level==3 and c.areaType==3 and c.x>2080 then
  for slot=0,5 do
   if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_ID',slot)==0x2d then
    local bx=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
    if bx-c.x>32 and bx-c.x<160 then return {b=b.b,down=true}end
   end
  end
 end
 if c.world==0 and c.level==1 and c.areaType==2 then
  if c.char==7 and c.x>=2350 and c.x<2580 then return {right=true,b=b.b}end
  if c.x>=2580 then
   launchHold=0
   if exitPhase=='back' then
    local target=math.max(2616,c.camera+1)
    if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter' end
    return {right=c.x<target,left=c.x>target+3,b=b.b}
   end
   return {right=true,b=b.b}
  end
  if not stairsMounted and c.x>=2144 and c.x<2208 then
   if c.grounded and c.y<=112 then stairsMounted=true;launchHold=0;stairHold=0;return {right=true,b=b.b}end
   if c.grounded and not c.lastA and stairHold==0 then stairHold=32 end
   local a=stairHold>0;if a then stairHold=stairHold-1 end
   return {right=c.x<2180,left=c.x>2184,a=a,b=b.b}
  end
  if c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then
   launchHold=0;return {right=true,b=b.b}
  end
 end
 if c.world==0 and c.level==1 and c.areaType==2 and not pillarLanded and c.x>=1944 and c.x<1984 then
  if c.grounded then pillarLanded=true;launchHold=0;b.a=not c.lastA;return b end
  return {right=c.x<1958,left=c.x>1962,b=b.b}
 end
 if e and e.dx>32 and e.dx<112 and math.abs(e.y-c.y)<24 and c.grounded and launchHold==0 then
  b.right=false;b.down=c.char==6 or c.char==7
  return b
 end
 if e and e.dx>12 and e.dx<96 and math.abs(e.y-c.y)<48 and not c.grounded and c.vy<128 then
  for y=math.min(feet+8,232),232,16 do if solid(c.x+8,y)then b.right=false;break end end
 end
 local obstacle=solid(c.x+24,c.y+height-8)or solid(c.x+24,c.y+8)
 local mount=c.areaType==2 and(solid(c.x+40,c.y-24)or solid(c.x+40,c.y-8))and not solid(c.x+24,c.y+16)
 if c.char==7 and c.world==0 and c.level==1 and c.areaType==2 and c.x>=800 and c.x<1120 then mount=false end
 local gap=not solid(c.x+28,math.min(feet+8,232))
 local enemy=e and e.dx>0 and e.dx<45 and math.abs(e.y-c.y)<48
 if c.grounded and not c.lastA and(obstacle or mount or gap or enemy or still>20)then b.a=true;jumpAge=0;launchHold=6
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<34 end
 if launchHold>0 then
  if c.grounded then b.a=true;launchHold=launchHold-1 else launchHold=0 end
 end
 return b
end
