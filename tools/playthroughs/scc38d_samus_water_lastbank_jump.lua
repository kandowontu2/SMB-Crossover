-- Real upper bank jump over the late water actors.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_lastwinged.lua'))
local launched,start=false,nil
return function(c)
 if c.char==2 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2590 and c.x<2790 then
  if not launched and c.grounded and c.x>=2630 and(c.r('PreviousA_B_Buttons')&128)==0 then launched=true;start=c.poll end
  return {right=true,b=c.poll%8<3,a=launched and c.poll-start<85}
 end
 return base(c)
end
