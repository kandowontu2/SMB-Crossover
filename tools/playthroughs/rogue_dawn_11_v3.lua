-- Source-controller successor: input polls can interrupt a running Main.
-- Do not hold one failed fresh-A edge across the opening block retries.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v2.lua'))
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 and c.status==0
  and c.x>=328 and c.x<=336 and c.y>=174 and c.y<=176 then
  -- Real button presses only. A 7-poll period varies against the source's
  -- floor acceleration cycle; missed edges release before the next try.
  b.a=c.poll%7<3
 end
 return b
end
