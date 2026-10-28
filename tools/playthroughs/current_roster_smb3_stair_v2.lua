-- Input-only final stair landing/runup, retaining the generic120-wait route.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_chip_pickup_v2.lua')
local phase='approach'
local function change(c,p)
 if phase~=p then phase=p;print('SMB3 last-stair '..p..' x'..c.x..' y'..c.y..' vx'..c.vx..' form'..c.r('M3Form')..' previous'..c.r('M3Previous'))end
end
return function(c)
 if c.char~=17 or c.world~=0 or c.level~=0 or c.x<2380 or c.x>=2544 then return base(c)end
 local form=c.r('M3Form');if form~=0 and form~=4 then return base(c)end
 if c.block(2424,145)~=0x61 or c.block(2440,145)~=0x61 or c.block(2488,145)~=0x61 or c.block(2456,145)~=0 then return base(c)end
 if phase=='approach'and c.x>=2406 and c.y<=112 then change(c,'land')end
 if phase=='approach'then return base(c)end
 if phase=='land'then
  -- Real SMB3 inertia needs opposite direction to brake; neutral input alone
  -- can carry the native Frog beyond the last support before it lands.
  local b={}
  if c.x>2424 then b.left=true
  elseif c.x<2418 then b.right=true
  elseif c.vx>0 and c.vx<128 then b.left=true
  elseif c.vx>=128 then b.right=true end
  if c.grounded and c.y+32<=144 and(c.r('M3Previous')&128)==0 then change(c,'runup');return{right=true,b=true}end
  return b
 end
 if phase=='runup'then
  if c.grounded and c.x>=2430 and(c.r('M3Previous')&128)==0 then change(c,'cross');return{right=true,b=true,a=true}end
  return{right=true,b=true}
 end
 if phase=='cross'then
  if c.grounded and c.x>=2472 then change(c,'out')end
  return{right=true,b=true,a=true}
 end
 return{right=true,b=true}
end
