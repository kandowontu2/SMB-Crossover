-- First real Celeste route discovery. Inputs only, genuine raw0/variant4.
-- Reuse read-only pickup/obstacle decisions; do not substitute Mario physics.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local navigate=assert(dofile(root..'/tools/playthroughs/sunny_11_v3.lua'))
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==4,'Genuine Celeste identity')
 local view={}
 for key,value in pairs(c)do view[key]=value end
 view.char=23
 return navigate(view)
end
