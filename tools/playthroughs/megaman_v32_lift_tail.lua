-- Ordinary controller tail from the independently verified first lift cap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_high_tail.lua'))
local phase,age,quiet='fight',0,0
return function(c)
 if c.world==0 and c.level==2 and c.x>=1120 and c.x<1230 and phase~='done'then
  local foe=false
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<0x15 and st<32 and x>c.x and x<c.x+180 then foe=true end
  end
  age=age+1
  if phase=='fight'then
   quiet=foe and 0 or quiet+1
   if quiet>=16 then phase='release';age=0;print('MM32 first lift foe clear '..c.poll)end
   return{right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3,a=age>240 and age%80<40}
  elseif phase=='release'then
   if age>=8 then phase='jump';age=0 end
   return{}
  elseif phase=='jump'then
   if c.x>=1220 and c.grounded and c.y<=80 then phase='done';print('MM32 next lift cap landed '..c.poll)end
   return{right=true,a=age<40,b=c.poll%8<3}
  end
 end
 return prior(c)
end
