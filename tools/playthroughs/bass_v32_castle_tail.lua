-- Controller-only castle continuation from the verified first firebar branch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_platform_end.lua'))
local axeAge=-1
return function(c)
 if c.char==9 and c.world==0 and c.level==3 and c.x>=2200 and c.x<2260 then
  if c.grounded and c.x>=2230 and not c.lastA and c.r('XgDash')==0 then axeAge=0 end
  if axeAge>=0 then axeAge=axeAge+1 end
  return{right=true,a=axeAge>=0 and axeAge<32}
 end
 local b=prior(c)
 if c.char==9 and c.world==0 and c.level==3 and c.x>=1010 and c.x<1120 and c.grounded then
  return{right=true,down=true,a=c.r('XgDash')==0 and not c.lastA}
 end
 return b
end
