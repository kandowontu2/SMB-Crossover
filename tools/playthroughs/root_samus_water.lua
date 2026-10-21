-- Controller-only Samus discovery. Final candidates need a fresh fixed replay.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local dry=assert(dofile(root..'/tools/playthroughs/root_samus_contra.lua'))
local jumpStart=nil
local bridgePhase=0
local bridgeStart=nil
local bridgeRelease=nil
local springPhase='approach'
local springJump=nil
return function(c)
 if c.char==2 and c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach'then
   if animation>0 then springPhase='compress';return{}end
   if c.grounded and c.x>=2990 and(not springJump or c.poll-springJump>40)then springJump=c.poll end
   return {right=c.x<3008,left=c.x>3012,a=springJump~=nil and c.poll-springJump<16}
  elseif springPhase=='compress'then
   if animation==0 and c.vy>=128 then springPhase='cross';return {right=true,a=true}end
   return {a=animation>=2 and animation<=4}
  end
  return {right=true,a=not c.grounded}
 end
 if c.char~=2 or c.areaType~=0 then return dry(c)end
 local shot=c.poll%12<5
 local solid=function(x,y)
  local t=c.block(x,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 if c.grounded and not c.lastA then jumpStart=nil end
 local obstacle=solid(c.x+24,c.y+8)or solid(c.x+24,c.y+24)
 local gap=not solid(c.x+28,math.min(c.y+40,232))
 if c.grounded and not c.lastA and(c.r('PreviousA_B_Buttons')&128)==0 and(obstacle or gap)then jumpStart=c.poll end
 local jump=jumpStart~=nil and c.poll-jumpStart<85
 if c.world==1 and c.level==1 and c.x>=2040 and c.x<2240 then
  local sy=c.y+(c.yHigh==0 and -256 or 0)
  if bridgePhase==0 then
   if c.grounded and c.y<=112 and c.x>=2058 then
    bridgePhase=1;bridgeStart=nil;bridgeRelease=c.poll
    return {b=shot}
   end
   return {right=c.x<2064,left=c.x>2067,b=shot,a=jump}
  elseif bridgePhase==1 then
   if bridgeStart==nil and c.grounded and not c.lastA and c.poll-bridgeRelease>=8 and(c.r('PreviousA_B_Buttons')&128)==0 then bridgeStart=c.poll end
   if c.x>=2100 then bridgePhase=2;return {right=true,b=shot}end
   return {right=sy<=0,b=shot,a=bridgeStart~=nil and c.poll-bridgeStart<85}
  end
  return {right=true,b=shot}
 end
 if c.x>3000 then jump=false end
 return {right=true,b=shot,a=jump,up=c.r('SmBall')~=0}
end
