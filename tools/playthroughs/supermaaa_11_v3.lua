-- Input-only walking/stomp discovery; all neck and jump mechanics stay original.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/supermaaa_11_v2.lua'))
return function(c)
 local b=route(c)
 -- Avoid running through successive Goombas during this first level pilot.
 b.b=false
 return b
end
