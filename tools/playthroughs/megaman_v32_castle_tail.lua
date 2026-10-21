local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_platform_tail.lua'))
return function(c)
 local b=prior(c)
 if c.char==1 and c.world==0 and c.level==3 and c.x>=1010 and c.x<1120 and c.grounded then
  return{right=true,down=true,a=c.r('MmSliding')==0 and not c.lastA}
 end
 return b
end
