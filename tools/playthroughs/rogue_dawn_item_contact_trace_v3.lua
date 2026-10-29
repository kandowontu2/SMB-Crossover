-- Read-only geometry packets go to the harness's existing bounded event log.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v5.lua'))
local count=0
return function(c)
 local b=route(c)
 if count>=128 or c.poll%8~=0 or c.x<320 then return b end
 count=count+1
 local actors={}
 for i=0,5 do
  local j=(i+1)*4
  actors[#actors+1]={slot=i,flag=c.r('Enemy_Flag',i),id=c.r('Enemy_ID',i),state=c.r('Enemy_State',i),
   x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
   ctrl=c.r('Enemy_BoundBoxCtrl',i),owner=c.r('InvPickupOwner',i),pickup=c.r('InvPickup',i),
   rise=c.r('InvRisePhase',i),raw=c.r('PowerUpType',i),
   box={c.r('BoundingBox_UL_XPos',j),c.r('BoundingBox_UL_YPos',j),
    c.r('BoundingBox_LR_Corner',j),c.r('BoundingBox_LR_Corner',j+1)}}
 end
 return b,{x=c.x,y=c.y,camera=c.camera,power=c.status,tanks=c.r('RdTanks'),
  source={c.r('RdX')+256*c.r('RdRoomHi'),c.r('RdY'),c.r('RdRadiusX'),c.r('RdRadiusY'),
   c.r('RdAction'),c.r('RdVY'),c.r('RdGravity')},
  box={c.r('BoundingBox_UL_XPos'),c.r('BoundingBox_UL_YPos'),
   c.r('BoundingBox_LR_Corner'),c.r('BoundingBox_LR_Corner',1)},actors=actors}
end
