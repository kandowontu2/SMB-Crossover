-- Controller-only second-gap approach for Grant's native short jump.
local root=assert(ROSTER_CONFIG.root)
local base=assert(dofile(root..'/tools/playthroughs/current_roster_grant_11_v1.lua'))
return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name=='grant' and ROSTER_CONFIG.mode_value==1
  and c.char==5 and c.variant==1 and c.world==0 and c.level==0
  and c.x>=1328 and c.x<1440 then
  -- The floor gap starts at1376; the ordinary32px probe jumps too early.
  -- Start near its lip so the native49-update arc reaches the far shore.
  b.right=true;b.left=false;b.b=false;b.a=c.x>=1368
 end
 return b
end
