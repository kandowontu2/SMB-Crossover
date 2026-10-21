-- Bill uses source-style floor jumps underwater; first settle from entry.
-- Controller-only discovery, no synthesized contacts or state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_late_koopa_walk.lua'))
local settled=false
return function(c)
 if c.char==3 and c.world==1 and c.level==1 and c.areaType==0 then
  local prev=(c.r('PreviousA_B_Buttons')&128)~=0
  local shot=c.poll%8<3
  if not settled then
   if c.grounded then settled=true else return {up=true,b=shot}end
  end
  local b={right=true,b=shot,a=c.x>=228 and c.grounded and not prev}
  local e=c.enemy()
  if e and e.dx>=-24 and e.dx<112 then
   b.up=e.y<c.y-8
   b.down=not c.grounded and e.y>c.y+12
  end
  return b
 end
 return base(c)
end
