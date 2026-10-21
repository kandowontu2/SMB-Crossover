-- Genuine floor to late high coral bank, using only the controller.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_water_bank_vertical.lua'))
local phase,start=0,nil
return function(c)
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2470 and c.x<2660 then
  local sy=c.y+(c.yHigh==0 and -256 or 0)
  local shot=c.poll%8<3
  if phase==0 then
   if c.grounded and c.y>=160 and(c.r('PreviousA_B_Buttons')&128)==0 then phase=1;start=c.poll end
   return {a=phase==1,b=shot,up=true}
  elseif phase==1 then
   if sy<=40 then phase=2 end
   return {a=true,b=shot,up=true,right=phase==2 and c.x<2508,left=c.x>2510}
  elseif phase==2 then
   if c.grounded and c.y<=48 then phase=3 end
   return {b=shot,right=c.x<2508,left=c.x>2510}
  elseif phase==3 then
   if c.x>=2524 and c.grounded and(c.r('PreviousA_B_Buttons')&128)==0 then phase=4;start=c.poll end
   return {right=true,b=shot,a=phase==4}
  elseif phase==4 then
   if c.x>=2608 then phase=5 end
   return {right=c.x<2608,b=shot,a=c.poll-start<85}
  end
  if not c.grounded then return {b=shot}end
 end
 return base(c)
end
