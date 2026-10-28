-- Controller decisions only. The selected ROM identity remains raw23 Sunny.
-- Sunny's requested foundation is native Mario gameplay, so reuse the mature
-- Mario route with a local view for its family-specific navigation decisions.
-- The driver independently asserts actual selected identity and Easy/Hard.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local mario=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
return function(c)
 assert(c.char==23,'Sunny controller used with another identity')
 local navigation={}
 for key,value in pairs(c)do navigation[key]=value end
 navigation.char=0
 return mario(navigation)
end
