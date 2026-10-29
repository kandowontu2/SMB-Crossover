-- Controller-only standing-beam discovery; Rogue Down is morph, not crouch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/roster_samus_contra.lua'))
return function(c)
 local b=route(c)
 -- This route exercises ordinary jumps/beam and physically earned items.
 -- Morph/Spring-Ball receive their own earned-ability route later.
 b.down=false
 b.up=false
 return b
end
