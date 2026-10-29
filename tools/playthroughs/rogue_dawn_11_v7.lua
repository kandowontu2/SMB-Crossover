-- Keep v6's earned physical first pickup. After that, use direct source
-- grounded jumps; the Samus route's crouch-and-fire loop cannot be reused
-- for Dawn, whose Down input is Morph Ball rather than an ordinary crouch.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local opening=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v6.lua'))
local travel=assert(dofile(root..'/tools/playthroughs/roster_samus_contra_nav.lua'))
local attributes=assert(ROSTER_CONFIG.rogue_tile_attributes)
local earned=false
return function(c)
 if c.status>0 then earned=true end
 if not earned then return opening(c) end
 local action,gravity,vy=c.r('RdAction'),c.r('RdGravity'),c.r('RdVY')
 local cx=c.r('RdX')+256*c.r('RdRoomHi')
 local rx=c.r('RdRadiusX')
 local footY=c.r('RdY')+c.r('RdRadiusY')+1
 local function solid(x)
  local tile=c.block(x,footY)
  if tile==0x5f or tile==0x60 or tile==0xc2 or tile==0xc3 or tile==0xc5 then return false end
  return(attributes[tile+1]&3)==1
 end
 local support=footY<240 and c.yHigh==1
  and(solid(cx-rx)or solid(cx)or solid(cx+rx))
 local ready=action==0 or action==4 or(gravity==0 and vy<128 and action==1)
 local b=travel(setmetatable({grounded=support and ready},{__index=c}))
 if(action==1 or action==2 or action==6)and vy>=128 then b.a=true end
 b.down=false;b.up=false
 return b
end
