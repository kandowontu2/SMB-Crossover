-- Descend over genuine floor before engaging the enemy below the next pipe.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_movement_receipts.lua'))
return function(c)
 if c.world==1 and c.level==0 and c.x>=1744 and c.x<1840 and c.yHigh==1 and not c.grounded and c.vy<128 then
  local tile=c.block(c.x+8,216)
  local e=c.enemy()
  if tile~=0 and tile~=0x23 and e and e.id~=13 and e.dx>=0 and e.dx<120 and e.y>c.y+24 then
   if c.r('PlayerFacingDir')~=1 then return{right=true,b=true}end
   return {b=c.poll%8<3}
  end
 end
 return base(c)
end
