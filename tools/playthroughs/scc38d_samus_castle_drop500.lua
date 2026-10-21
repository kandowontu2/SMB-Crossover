-- Read-only terrain receipt places the upper used block at480..495/Y96 and
-- the lower island at464..511/Y160. Drop at500 before the second lava launch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_first_highbank.lua'))
local phase,settle,hold='drop',0,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==0 and c.level==3 and c.x>=460 and c.x<610 and phase~='done' then
  if phase=='drop' then
   if c.grounded and c.y>=128 and c.x>=500 and c.x<=501 then
    settle=settle+1
    if settle>=6 and not c.lastA then phase='jump';hold=32 end
   else settle=0 end
   if phase=='drop' then return {right=c.x<500,left=c.x>501,b=c.poll%12<5}end
  end
  if phase=='jump' then
   local a=hold>0;if a then hold=hold-1 end
   if c.grounded and c.x>=560 and c.y<=112 then phase='done' end
   return {right=true,a=a,b=c.poll%12<5}
  end
 end
 return base(c)
end
