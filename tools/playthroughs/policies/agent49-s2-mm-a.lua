-- Ordinary controller discovery on immutable S2. No emulated-state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
return assert(dofile(root..'/tools/playthroughs/megaman_v34_water_late_wall.lua'))
