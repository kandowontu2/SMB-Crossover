-- Real Celeste mushroom/grip + later flower/dash acquisition discovery.
-- Controller hints only; actual raw0/variant4 and original kernel remain.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local navigate=assert(dofile(root..'/tools/playthroughs/sunny_upgrades_11_v4.lua'))
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==4,'Genuine Celeste identity')
 local view={}
 for key,value in pairs(c)do view[key]=value end
 view.char=23
 local b=navigate(view)
 if c.status>0 and not c.grounded and c.r('CmWallGrace')>0 and c.r('CmWallKick')==0 then
  b.up=true
  b.a=c.r('CmPreviousAB')&128==0
 end
 return b
end
