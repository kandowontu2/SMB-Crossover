-- Controller-only unreachable-aim correction; v1 mechanics/first-block/pipe
-- policy remains intact. Every enemy continues its real update/collision.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/current_roster_bass_11_v1.lua'))
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
return function(c)
 local b=prior(c)
 if c.char~=9 or c.world~=0 or c.level~=0 or not c.grounded or not b.b or b.a then return b end
 local e=c.enemy()
 if not e or math.abs(e.y-c.y)>=32 then return b end
 -- The old wait also turns toward the foe for a poll. Include that turn or
 -- it would alternate Left/Right forever after ignoring only stationary B.
 local blocked=e.x<c.camera
 if not blocked then
  local first,last=math.min(c.x+8,e.x+8),math.max(c.x+8,e.x+8)
  for x=first,last,8 do
   if solid(c,x,c.y+16)then blocked=true;break end
  end
 end
 if blocked then return{right=true}end
 return b
end
