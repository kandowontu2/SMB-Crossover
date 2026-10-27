-- Controller-only native-edge acknowledgement; real lag NMIs may miss a
-- one-poll ground tap. Retain the cast and stair controllers unchanged.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/current_roster_zelda2_11_v2.lua'))
local pressLeft,releaseLeft=0,0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.r('GuestPowerupActive')~=0 or c.r('TimerControl')~=0 then
  pressLeft,releaseLeft=0,0;b.a=false;return b
 end
 if pressLeft==0 and releaseLeft==0 and b.a and c.grounded then
  if (c.r('Z2PreviousButtons')&128)~=0 then releaseLeft=8 else pressLeft=8 end
 end
 if releaseLeft>0 then
  b.a=false;releaseLeft=releaseLeft-1
  if releaseLeft==0 then pressLeft=8 end
 elseif pressLeft>0 then b.a=true;pressLeft=pressLeft-1 end
 return b
end
