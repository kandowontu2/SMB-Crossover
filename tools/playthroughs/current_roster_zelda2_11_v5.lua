-- Controller-only second-gap run-up, matched to the live 1-1 floor cells.
-- Retain the real earned Jump/cast, first-pit and last-stair controllers.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/current_roster_zelda2_11_v4.lua'))
local phase='land'
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<1296 or c.x>=1472 or phase=='done' then return b end
 -- Both the floor support and the actual empty span must match. No jump
 -- outcome or position is forced; a different scene keeps the old policy.
 if c.block(1360,216)~=0x54 or c.block(1376,216)~=0
  or c.block(1408,216)~=0 or c.block(1424,216)~=0x54 then return b end
 if c.r('GuestPowerupActive')~=0 or c.r('TimerControl')~=0 then return b end
 if phase=='land' then
  if c.grounded and c.y==176 then phase='runup'
  else return{right=c.x<1344,left=c.x>=1344} end
 end
 if phase=='runup' then
  -- A grounded sword slash stops native VX. Suppress B in this run-up,
  -- acknowledge a real A release, and launch 16px before the floor edge.
  if c.grounded and c.y==176 and c.x>=1360 and c.x<=1366
   and c.vx>0 and c.vx<128 and(c.r('Z2PreviousButtons')&128)==0 then
   phase='cross';return{right=true,a=true}
  end
  return{right=c.x<=1366,left=c.x>1366}
 end
 if phase=='cross' then
  if c.grounded and c.x>=1424 then phase='done';return b end
  return{right=true,a=true}
 end
 return b
end
