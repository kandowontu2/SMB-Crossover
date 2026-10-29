-- Real native Mario navigation; skin identity and CHR publication checked.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==3,'Actual Kamikaze menu alternate')
 assert(c.r('X5ChrMode')==0x84,'Published skin owner retained in gameplay')
 return route(c)
end
