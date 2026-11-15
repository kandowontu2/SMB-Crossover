-- Ordinary classic-DK inputs, driven only by completed native movement/Main.
local jumpAge=-1
local lastX,still=0,0
return function(c)
 if c.world~=0 or c.level~=0 then return{}end
 if c.x==lastX then still=still+1 else still=0 end
 lastX=c.x
 local solid=function(x,y)
  local tile=c.block(x,y)
  return tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2 and tile~=0xc3
 end
 local e=c.enemy()
 -- Use the existing ordinary horizontal barrel against a nearby Goomba.
 if c.grounded and e and e.id==6 and e.dx>40 and e.dx<=108 and math.abs(e.y-c.y)<40 then
  jumpAge=-1
  return{b=c.poll%28<2}
 end
 local b={right=true,b=c.x<3104}
 if c.grounded then
  jumpAge=-1
  -- A released on a real early landing permits another ordinary jump.
  -- A held through an overhead brick bump must not suppress every retry.
  if c.lastA then return b end
  local obstacle=solid(c.x+48,c.y+8)or solid(c.x+48,c.y+24)
  local gap=not solid(c.x+48,math.min(c.y+40,232))
  local enemy=e and e.dx>0 and e.dx<72 and math.abs(e.y-c.y)<48
  if obstacle or gap or enemy or still>20 then b.a=true;jumpAge=0 end
 elseif jumpAge>=0 then
  jumpAge=jumpAge+1;b.a=jumpAge<40
 end
 return b
end
