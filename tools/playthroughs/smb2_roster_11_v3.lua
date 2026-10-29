-- Controller-only: use SMB2's run button and land before the stair valley.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/smb2_roster_11_v2.lua'))
local crossed=false
local hold=0
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 then
  if c.x>450 then b.b=true end
  if not crossed and c.x>=2160 and c.x<2256 then
   b={right=c.x<2188,left=c.x>2189,b=true}
   if c.grounded and c.y<=112 and not c.lastA then
    b={right=true,a=true,b=true}
    crossed=true
    hold=35
   end
  elseif crossed and hold>0 then
   b={right=true,a=true,b=true}
   hold=hold-1
  end
 end
 return b
end
