-- Preserve v1's negative: plain ~51px jumps cannot clear the tall1-1 pipe.
-- Use the genuinely acquired wall move with a fresh A edge, no physics edits.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local navigate=assert(dofile(root..'/tools/playthroughs/celeste_11_v1.lua'))
return function(c)
 local b=navigate(c)
 if c.status>0 and not c.grounded and c.r('CmWallGrace')>0 and c.r('CmWallKick')==0 then
  b.up=true
  b.a=c.r('CmPreviousAB')&128==0
 end
 return b
end
