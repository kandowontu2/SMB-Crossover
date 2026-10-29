-- Read-only source-grounded controller. Never changes the game's RAM/state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/roster_samus_contra.lua'))
local attributes=assert(ROSTER_CONFIG.rogue_tile_attributes)
return function(c)
 local action=c.r('RdAction')
 local gravity=c.r('RdGravity')
 local vy=c.r('RdVY')
 local centerX=c.r('RdX')+256*c.r('RdRoomHi')
 local radiusX=c.r('RdRadiusX')
 local footY=c.r('RdY')+c.r('RdRadiusY')+1
 local function solid(x)
  local tile=c.block(x,footY)
  if tile==0x5f or tile==0x60 or tile==0xc2 or tile==0xc3 or tile==0xc5 then return false end
  -- Exact current ROM's labelled fixed-F127 EF36 table, bound at preparation.
  return(attributes[tile+1]&3)==1
 end
 local support=footY<240 and c.yHigh==1
  and(solid(centerX-radiusX)or solid(centerX)or solid(centerX+radiusX))
 -- Source stand0/aim4 admit fresh A; running1 requires zero gravity.
 local jumpReady=action==0 or action==4
  or(gravity==0 and vy<128 and action==1)
 local sourceContext=setmetatable({grounded=support and jumpReady},{__index=c})
 local b=route(sourceContext)
 b.down=false
 b.up=false
 return b
end
