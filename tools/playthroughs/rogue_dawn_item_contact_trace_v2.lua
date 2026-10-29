-- Bounded read-only item/body geometry trace; no emulated writes or cheats.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v5.lua'))
local count=0
local log=assert(io.open(ROSTER_CONFIG.out..'item-contact.csv','w'))
return function(c)
 local b=route(c)
 if count<128 and c.poll%4==0 and c.x>=320 then
  for i=0,5 do
   if c.r('Enemy_ID',i)==0x2e or c.r('InvPickupOwner',i)==2 then
    local j=(i+1)*4
    local line=table.concat({c.poll,c.x,c.y,c.camera,
     c.r('RdAction'),c.r('RdVY'),c.r('RdGravity'),c.r('RdTanks'),c.status,
     i,c.r('Enemy_Flag',i),c.r('Enemy_State',i),c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
     c.r('Enemy_Y_Position',i),c.r('Enemy_BoundBoxCtrl',i),
     c.r('InvPickupOwner',i),c.r('InvPickup',i),c.r('InvRisePhase',i),c.r('PowerUpType',i),
     c.r('BoundingBox_UL_XPos'),c.r('BoundingBox_UL_YPos'),
     c.r('BoundingBox_LR_Corner'),c.r('BoundingBox_LR_Corner',1),
     c.r('BoundingBox_UL_XPos',j),c.r('BoundingBox_UL_YPos',j),
     c.r('BoundingBox_LR_Corner',j),c.r('BoundingBox_LR_Corner',j+1)},',')
    log:write(line..'\n');log:flush()
    count=count+1;if count==128 then log:close()end;break
   end
  end
 end
 return b
end
