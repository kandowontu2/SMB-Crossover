-- Ordinary controller-only late-water bridge approach from the verified floor.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_lastwinged.lua'))
local phase=0
local start=nil
return function(c)
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2040 and c.x<2240 then
  local sy=c.y+(c.yHigh==0 and -256 or 0)
  local shot=c.poll%8<3
  if phase==0 then
   if c.grounded and c.y>=160 and(c.r('PreviousA_B_Buttons')&128)==0 then phase=1;start=c.poll end
   return {a=phase==1,b=shot,up=true}
  elseif phase==1 then
   if sy<=100 then phase=2 end
   return {a=true,b=shot,up=true,right=phase==2 and c.x<2068,left=c.x>2070}
  elseif phase==2 then
   if c.grounded and c.y<=112 then phase=3;start=nil end
   return {b=shot,right=c.x<2068,left=c.x>2070}
  elseif phase==3 then
   if start==nil and(c.r('PreviousA_B_Buttons')&128)==0 then start=c.poll end
   if c.x>=2100 then phase=4 end
   return {a=start~=nil and c.poll-start<100,b=shot,up=true,right=sy<=0}
  end
  return {right=true,b=shot}
 end
 return base(c)
end
