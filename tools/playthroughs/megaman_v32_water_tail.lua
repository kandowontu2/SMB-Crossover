-- Controller-only water route: settle on the first coral before its gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_late_overworld.lua'))
local phase,age=MM32_CORAL_READY and 'release' or 'approach',0
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.x>=990 and c.x<1190 and phase~='done' then
  if phase=='approach' then
   if c.grounded and c.x>=999 and not c.lastA then phase='climb';age=0;return{right=true,a=true}end
   return{right=true}
  elseif phase=='climb' then
   age=age+1
   if c.grounded and c.y<=96 and c.x>=1030 then phase='release';age=0;print('MM32 first coral landed '..c.poll);return{}end
   return{right=c.x<1040,left=c.x>1043,a=age<32}
  elseif phase=='release' then
   age=age+1
   if age>=8 and c.grounded then phase='cross';age=0;return{right=true,a=true}end
   return{}
  elseif phase=='cross' then
   age=age+1
   if c.grounded and c.x>=1130 then phase='done';print('MM32 first water gap landed '..c.poll);return{right=true}end
   return{right=true,a=age<32,b=c.poll%8<3}
  end
 end
 return prior(c)
end
