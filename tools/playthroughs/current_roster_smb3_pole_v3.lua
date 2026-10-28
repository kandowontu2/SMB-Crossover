-- Input-only pole-base approach; retain the qualified final-stair controller.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_smb3_stair_v2.lua')
local jumped=false
return function(c)
 if c.char~=17 or c.world~=0 or c.level~=0 or c.r('GameEngineSubroutine')~=8 or c.x<3104 or c.x>=3184 then return base(c)end
 -- Genuine compiled1-1 pole shaft37 and raised base97 at column198.
 if c.block(3176,184)~=0x25 or c.block(3176,201)~=0x61 then return base(c)end
 if c.x<3120 then return{right=true,b=true}end -- Real consumed A release.
 if not jumped and(c.r('M3Previous')&128)==0 then
  jumped=true;print('SMB3 pole freshA x'..c.x..' y'..c.y..' form'..c.r('M3Form')..' previous'..c.r('M3Previous'))
 end
 return{right=true,b=true,a=jumped}
end
