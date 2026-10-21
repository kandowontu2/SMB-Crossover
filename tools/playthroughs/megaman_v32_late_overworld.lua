-- Controller-only continuation from the late 2-1 brick pillar.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_pipe_gap_tail.lua'))
local pillarDone,age,quiet=false,0,0
local springPhase,jumpAt,crossAge='approach',nil,0
return function(c)
 if c.char==1 and c.world==1 and c.level==0 then
  if c.x>=2560 and c.x<2610 and not pillarDone then
   local foe=false
   for i=0,5 do
    local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if f>0 and f<128 and id<0x15 and id~=13 and st<32 and not(id==6 and st>=2)
     and x>c.x-32 and x<c.x+220 then foe=true end
   end
   age=age+1;quiet=foe and 0 or quiet+1
   if quiet>=16 then pillarDone=true;print('MM32 late pillar clear '..c.poll)
   else return{right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3,a=age>120 and age%100<40}end
  end
  if c.x>=2944 and c.x<3090 then
   local animation=c.r('JumpspringAnimCtrl')
   if springPhase=='approach' then
    if animation>0 then springPhase='compress';return{}end
    if c.grounded and c.x>=2990 and(not jumpAt or c.poll-jumpAt>60)then jumpAt=c.poll end
    return{right=c.x<3008,left=c.x>3012,a=jumpAt and c.poll-jumpAt<24}
   elseif springPhase=='compress' then
    if animation==0 and c.vy>=128 then springPhase='cross';crossAge=0;return{right=true,a=true}end
    return{a=animation>=2 and animation<=4}
   end
   crossAge=crossAge+1
   return{right=true,a=crossAge<64}
  end
 end
 return prior(c)
end
