-- Same bounded read-only telemetry as v3, with the grounded opening route.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v6.lua'))
local count=0
return function(c)
 local b=route(c)
 if count>=128 or c.poll%8~=0 or c.x<320 then return b end
 count=count+1
 local actors={}
 for i=0,5 do
  actors[#actors+1]={slot=i,flag=c.r('Enemy_Flag',i),id=c.r('Enemy_ID',i),
   x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
   owner=c.r('InvPickupOwner',i),pickup=c.r('InvPickup',i),rise=c.r('InvRisePhase',i)}
 end
 return b,{x=c.x,y=c.y,camera=c.camera,power=c.status,tanks=c.r('RdTanks'),
  source={c.r('RdX')+256*c.r('RdRoomHi'),c.r('RdY'),c.r('RdAction'),c.r('RdVY'),c.r('RdGravity')},
  actors=actors}
end
