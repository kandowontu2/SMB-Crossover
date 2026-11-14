-- Toad's own ordinary-input mount. Earn every position from the cold route.
local phase,held='mount',-1
return function(c)
 if c.world~=0 or c.level~=0 or c.x<2360 or c.x>=2580 or phase=='done'then return choose(c)end
 if phase=='mount'then
  if c.grounded and c.x>=2428 and c.y<=112 then phase='release';return{}end
  local velocity=c.vx<128 and c.vx or c.vx-256
  local stopping=c.x+velocity*math.abs(velocity)/32
  local b={right=stopping<2432,left=stopping>2434,b=false}
  if c.grounded then
   if c.lastA then held=-1;b.a=false
   else held=0;b.a=true end
  elseif held>=0 then held=held+1;b.a=held<=40 end
  return b
 end
 if phase=='release'then
  if c.lastA then return{}end
  phase='cross';held=0
 end
 if phase=='cross'then
  if c.grounded and c.x>=2480 then phase='done';return choose(c)end
  held=held+1;return {right=true,b=true,a=held<=40}
 end
end
