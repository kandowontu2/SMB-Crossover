-- Controller-only Goku route. Original air attack cancels the jump ascent;
-- the generic roster policy's repeated B pulses are inappropriate for him.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
return function(c)
 assert(c.char==24,'Actual Goku menu identity')
 local b=route(c)
 if c.world==0 and c.level==0 then
  local e=c.enemy()
  b.b=c.grounded and not b.a and e and e.dx>0 and e.dx<30 and math.abs(e.y-c.y)<40 or false
 end
 return b
end
