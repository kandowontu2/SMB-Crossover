-- This candidate's fixed prefix already waited for and killed the high-cap foe.
MM32_HIGH_CLEARED=true
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
return assert(dofile(root..'/tools/playthroughs/megaman_bass_v32_policy.lua'))
