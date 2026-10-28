-- Input-only ship flight path above the first coin block and final pyramid.
-- Vic v1 physically hit the solid first block at PlayerY148/queryY156.
-- No game-state writes; native flight, terrain contact and pole rules remain.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_chip_pickup_v2.lua')
return function(c)
 local b=base(c)
 if c.char~=18 or c.world~=0 or c.level~=0 then return b end
 local target=c.x>2700 and 55 or 100
 b.up=c.y>target+3;b.down=c.y<target-3
 return b
end
