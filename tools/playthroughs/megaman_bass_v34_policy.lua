-- Controller retiming only. The34b camera hold and faster foreground path
-- change which short button edges are consumed. A release spans at least five
-- real controller polls before this policy asks for another jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_water_exit.lua'))
local offAge=0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 local b=prior(c)
 if b.a and not c.lastA and offAge<5 then b.a=false end
 return b
end
