MM32_CORAL_READY=true
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
return assert(dofile(root..'/tools/playthroughs/megaman_v32_water_tail.lua'))
