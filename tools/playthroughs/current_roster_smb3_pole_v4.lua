-- Fresh ground jump at the actual pole base; never spend its A edge in air.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_smb3_stair_v2.lua')
local holding=false
return function(c)
 if c.char~=17 or c.world~=0 or c.level~=0 or c.r('GameEngineSubroutine')~=8 or c.x<3104 or c.x>=3184 then return base(c)end
 if c.block(3176,184)~=0x25 or c.block(3176,201)~=0x61 then return base(c)end
 local previous=c.r('M3Previous')
 if c.x<3120 then holding=false;return{right=true,b=true}end
 if holding then
  if c.grounded and(previous&128)~=0 then holding=false;return{right=true,b=true}end
  return{right=true,b=true,a=true}
 end
 if c.grounded and(previous&128)==0 then
  holding=true;print('SMB3 pole grounded freshA x'..c.x..' y'..c.y..' form'..c.r('M3Form')..' previous'..previous)
  return{right=true,b=true,a=true}
 end
 return{right=true,b=true}
end
