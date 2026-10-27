-- Controller only: use Alucard's native Down+freshA transform over the last gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local crossing='approach'
return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='alucard'or ROSTER_CONFIG.mode_value~=0
    or c.char~=5 or c.variant~=3 or c.world~=0 or c.level~=0
    or c.areaType~=1 or c.x<2336 or c.x>=2592 or crossing=='done'then return b end
 -- Stop starting new attacks before the airborne transformation window.
 b.b=false
 if crossing=='approach'and c.x>=2380 and c.y<=128 then crossing='release'end
 if crossing=='approach'then return b end
 local bat=c.r('Cv3Bat')
 if crossing=='release'then
  if bat~=0 then crossing='cross'
  elseif c.r('Cv3Previous')&128==0 and c.r('Cv3AttackAge')==0
     and c.r('Cv3HurtAge')==0 and c.r('Cv3Hearts',2)>0 then
   return{down=true,a=true,b=false}
  else return{a=false,b=false}end
 end
 if crossing=='cross'then
  if bat==1 then return{a=false,b=false}end
  if bat==2 then
   -- The far descending stair supplies a real landing; do not transform
   -- back while over the gap, inside a block, or without support below.
   local floor=false
   for y=math.max(96,c.y+40),224,8 do local t=c.block(c.x+8,y);if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 then floor=true;break end end
   if c.x>=2512 and c.y<=80 and floor and c.block(c.x+3,c.y)==0 and c.block(c.x+13,c.y)==0 then
    if c.r('Cv3Previous')&128==0 then crossing='land';return{down=true,a=true,b=false}end
    return{a=false,b=false}
   end
   return{right=true,up=c.y>64,down=c.y<56,a=false,b=false}
  end
 end
 if crossing=='land'then
  if bat~=0 or not c.grounded then return{a=false,b=false}end
  crossing='done';return b
 end
 return{a=false,b=false}
end
