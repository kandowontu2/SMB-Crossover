-- Controller-only native Luigi navigation. Resolve the underground enemies
-- at the open left edge before entering the low tunnel.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local pipes=assert(dofile(root..'/tools/playthroughs/luigi_native_pipes.lua'))
local cleared,quiet,hold=false,0,0
local springPhase,springJumpAt='approach',nil
local highCapPhase,highCapJump='land',nil
local wallHold=0
return function(c)
 if c.world==0 and c.level==2 and c.x>=640 and c.x<960 and highCapPhase~='done' then
  if highCapPhase=='land' then
   if c.grounded and c.y<=32 then highCapPhase='release';return{}end
   return{left=c.x>680,right=c.x<672,a=c.vy>=128}
  elseif highCapPhase=='release' then
   if c.lastA then return{}end
   highCapPhase='launch';highCapJump=c.poll
  end
  if highCapPhase=='launch' then
   if c.poll-highCapJump>=36 then highCapPhase='lowerland' end
   return{right=true,b=true,a=c.poll-highCapJump<32}
  elseif highCapPhase=='lowerland' then
   if c.grounded and c.y>=160 then highCapPhase='lowerrelease';return{}end
   return{left=c.x>810,right=c.x<804}
  elseif highCapPhase=='lowerrelease' then
   if c.lastA then return{}end
   highCapPhase='lowerlaunch';highCapJump=c.poll
  end
  if highCapPhase=='lowerlaunch' then
   if c.poll-highCapJump>=48 then highCapPhase='done' end
   return{right=true,b=true,a=c.poll-highCapJump<32}
  end
 end
 if c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  -- Ordinary controller press during the real spring's compression; the
  -- boost comes from native JumpspringHandler, with no granted velocity.
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach' then
   if animation>0 then springPhase='compress';return{}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   return{right=c.x<3008,left=c.x>3012,b=true,a=springJumpAt and c.poll-springJumpAt<16}
  elseif springPhase=='compress' then
   if animation==0 and c.vy>=128 then springPhase='cross';return{right=true,b=true}end
   return{a=animation>=2 and animation<=4}
  end
  return{right=true,b=true}
 end
 local pipe=pipes(c);if pipe then return pipe end
 if c.world==0 and c.level==1 and cleared and c.x>=820 and c.x<1160 then
  -- The native small body walks beneath this ceiling. Generic guest mounting
  -- jumps land on its shelf and trap the player against the next upper wall.
  return{right=true,b=true}
 end
 if c.world==0 and c.level==1 and c.x>=770 and c.x<1040 and not cleared then
  local b={left=c.x>832,right=c.x<828}
  local e=c.enemy()
  if e and e.id<=2 and e.state==4 then
   if e.dx>=0 and e.dx<40 and c.grounded then return{right=true,b=true}end
   e=nil
  end
  if e and math.abs(e.dx)<40 then
   quiet=0
   if c.grounded and not c.lastA and hold==0 then hold=28 end
  elseif c.grounded and c.x>=824 and c.x<=840 then
   quiet=quiet+1
   if quiet>=100 then cleared=true;return{right=true,b=true}end
  end
  if hold>0 then b.a=true;hold=hold-1 end
  return b
 end
 local b=travel(c)
 if c.areaType~=0 then
  local function solid(y)local t=c.block(c.x+16,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
  -- A far lookahead can skip an isolated16px stair or pillar completely.
  if c.grounded and not c.lastA and(solid(c.y+8)or solid(c.y+24))then wallHold=32 end
  if wallHold>0 then b.a=true;wallHold=wallHold-1 end
 end
 return b
end
