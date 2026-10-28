-- Input-only repeated-gap takeoff over the frozen Arrow/toolkit route.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_darkwing_arrow_v5.lua')
local phase='find';local edge,landing;local resumeAfter=0
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
local function supported(c,x)
 for y=math.min(c.y+40,232),232,16 do if solid(c.block(x,y))then return true end end
 return false
end
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if phase=='resume'then
  if c.x<resumeAfter then return{right=true}end
  phase='find'
 end
 assert(c.char==12 and c.r('DarkwingVariant')==1,'Actual Darkwing gap owner')
 if phase=='find'and c.grounded and c.x>450 and supported(c,c.x+8)then
  local nextTile=(c.x//16+1)*16
  for x=nextTile,nextTile+32,16 do
   if not supported(c,x)then
    local far=x
    while far<x+80 and not supported(c,far)do far=far+16 end
    if far>x and far<=x+64 and supported(c,far)then
     edge=x;landing=far;phase='runup'
     print('Darkwing gap terrain edge'..edge..' landing'..landing..' x'..c.x..' previous'..c.r('DwPrevious'))
    end
    break
   end
  end
 end
 if phase=='find'then return b end
 if phase=='runup'then
  -- Release is acknowledged by the real movement consumer, not last poll.
  -- A bounded pause prevents a lagged release from carrying us off the edge.
  b={right=c.x<edge-16 or c.r('DwPrevious')&128==0}
  if c.grounded and c.x>=edge-14 and c.r('DwPrevious')&128==0 then
   phase='press';b={right=true,a=true}
   print('Darkwing gap fresh press x'..c.x..' edge'..edge)
  end
  return b
 end
 if phase=='press'then
  b={right=true,a=true}
  if not c.grounded and c.vy>=128 then phase='cross';print('Darkwing gap actual rise x'..c.x..' y'..c.y)end
  return b
 end
 if phase=='cross'then
  if c.grounded and c.x>=landing-15 then phase='resume';resumeAfter=landing+8;print('Darkwing gap actual landing x'..c.x..' y'..c.y)end
  return{right=true,a=true}
 end
 return b
end
