-- Genuine controller discovery with the actual selected neck-Mario identity.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==2,'Actual SuperMaaa menu alternate')
 assert(c.r('MaaaLength')<=160,'Original maximum neck length')
 return route(c)
end
