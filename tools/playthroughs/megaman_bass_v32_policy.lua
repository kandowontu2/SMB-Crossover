-- Controller-only32 discovery. No emulated memory/register changes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_bass_route_v2.lua'))
local lastX,stuck,held=-1,0,0
local lipJump=false
local bassPitJump=false
local highPhase,highSaw,highQuiet=MM32_HIGH_CLEARED and'approach'or'spawn',false,0
local highAge=0
return function(c)
 local b=prior(c)
 if c.x==lastX then stuck=stuck+1 else stuck=0 end;lastX=c.x
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then held=0;return b end
 if c.char==1 and c.world==0 and c.level==2 and c.x>=544 and c.x<672 and highPhase~='done' then
  local foe=false
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<0x15 and st<32 and x>=520 and x<820 then foe=true end
  end
  held=0
  if highPhase=='spawn'then
   if foe then highSaw=true;highPhase='back';print('MM32 high-cap foe spawned at '..c.poll)end
   return {right=not highSaw and c.x<614,left=highSaw and c.x>581}
  elseif highPhase=='back'then
   if c.x<=581 then highPhase='wait' end
   return {left=c.x>581}
  elseif highPhase=='wait'then
   highQuiet=foe and 0 or highQuiet+1
   if highQuiet>=16 then highPhase='approach';print('MM32 high-cap foe cleared at '..c.poll)end
   return {right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3}
  elseif highPhase=='approach'then
   if c.grounded and c.x>=612 and not c.lastA then highPhase='climb';highAge=0;return{right=true,a=true}end
   return{right=true}
  elseif highPhase=='climb'then
   highAge=highAge+1
   if c.grounded and c.y<=32 and c.x>=656 then highPhase='done';print('MM32 high-cap landed at '..c.poll)end
   return{right=true,a=highAge<40}
  end
 end
 -- The2.02 high jump can land on the first block row before the historic
 -- mushroom alignment. Leave that platform rather than repeatedly jumping
 -- on top of the already-missed underside target.
 if c.char==1 and c.world==0 and c.level==0 and c.status==0 and c.x>=280 and c.x<352 and c.y<=112 then
  return {right=true,b=c.poll%8<3}
 end
 if stuck==60 then
  local e=c.enemy();print('MM32-STILL '..c.world..'-'..c.level..' x'..c.x..' y'..c.y..' enemy'..(e and(e.id..'/'..e.dx..'/'..e.y)or'none'))
 end
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 local wall=solid(c.x+24,c.y+24)or solid(c.x+24,c.y+8)
 if c.areaType~=0 and c.grounded and(stuck>45 or wall)then
  b.right=true;b.left=false;b.b=wall and c.poll%8<3;b.a=not c.lastA
  if b.a then held=32;stuck=0 end
 end
 if held>0 then held=held-1;b.right=true;b.left=false;b.a=true end
 if wall then b.b=c.poll%8<3 end
 local e=c.enemy()
 if e and e.dx>0 and e.dx<56 and c.y+28>=e.y and c.y<e.y+24 then
  -- Guest bodies do not stomp. Gain vertical clearance before advancing into
  -- a near enemy; otherwise a held travel jump closes the gap while rising.
  b.right=false;b.left=false;b.b=c.poll%8<3
 end
 if c.char==9 and e and e.dx> -16 and e.dx<96 and not c.grounded then
  b.down=e.y>c.y+24;b.up=e.y<c.y-24;b.b=c.poll%8<3
  if e.dx<56 and c.y+40>=e.y and c.vy<128 and c.r('XgJumpUsed')==0 then
   b.a=not c.lastA;held=b.a and 32 or 0;b.down=false
  end
 end
 if c.char==1 and c.world==0 and c.level==1 and c.areaType==2 and c.x>=1840 and c.x<1888 then
  -- This64px pit needs the source70px jump from the near lip. The older
  --22px lookahead launches before the small approach platform's right edge.
  b.right=true;b.left=false;b.a=lipJump and held>0
  if c.grounded and c.x>=1877 and not c.lastA then held=32;lipJump=true;b.a=true end
 end
 if c.char==9 and c.world==0 and c.level==1 and c.areaType==2 and c.x>=1232 and c.x<1280 then
  -- Leave the overhang before launching across the first underground pit.
  b.right=true;b.left=false;b.b=false;b.down=false;b.a=bassPitJump and held>0
  if c.grounded and c.x>=1274 and not c.lastA then held=32;bassPitJump=true;b.a=true end
 end
 if c.char==9 and c.grounded and e and math.abs(e.dx)<140 and math.abs(e.y-c.y)<24 and e.id~=2 and e.id~=13 then
  -- Bass needs five normal hits on a Goomba. Do not let a generic stuck-wall
  -- timeout force a jump into a group before the actual targets are defeated.
  held=0;b.a=false;b.down=false;b.up=false;b.b=true;b.right=false;b.left=false
  local face=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=face then b.right=face==1;b.left=face==2 end
 end
 return b
end
