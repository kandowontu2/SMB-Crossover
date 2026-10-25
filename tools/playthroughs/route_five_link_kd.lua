-- Brake before the stair lip; the prior controller steered left only after
-- passing its target and drifted off the last supported foot column.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/link_simon_ryu_policy.lua'))
local phase,age='land',0
local best,stage,lastProgress=0,'',0
return function(c)
 assert(c.r('SelectedCharacter')==4 and c.r('CrossoverBehaviorVersion')==0,'Actual Easy Link')
 local key=c.world..'-'..c.level..'-'..c.area
 if key~=stage then stage=key;best=c.x;lastProgress=c.poll end
 if c.x>best+8 then best=c.x;lastProgress=c.poll end
 assert(c.poll-lastProgress<1000,'Bounded Link navigation stall at '..key..' X'..c.x..' Y'..c.y)
 if c.world==0 and c.level==0 and c.x>=2390 and c.x<2512 and phase~='done' then
  if phase=='land' then
   local vx=(c.vx>=128 and c.vx-256 or c.vx)/16
   local e=2426-c.x-8*vx
   if c.grounded and c.y<=112 then phase='release';age=0 end
   return {right=e>1,left=e< -1}
  elseif phase=='release' then
   age=age+1
   if age>8 then phase='jump';age=0 end
   return{}
  elseif phase=='jump' then
   age=age+1
   if c.x>=2508 then phase='done' end
   return{right=true,a=age<33}
  end
 end
 return prior(c)
end
