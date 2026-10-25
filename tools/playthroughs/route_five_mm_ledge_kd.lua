local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/route_five_mm_highcap_kd.lua'))
return function(c)
 local b=prior(c)
 if c.char==1 and c.world==0 and c.level==2 and c.x>=820 and c.grounded then
  local function solid(x,y)
   local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  local fy=math.min(c.y+34,232)
  local wall=solid(c.x+24,c.y+8)or solid(c.x+24,c.y+24)
  if solid(c.x+8,fy) and not wall then
   if solid(c.x+12,fy)and not solid(c.x+24,fy)then b.a=false
   elseif not solid(c.x+12,fy)then b.a=not c.lastA end
  end
 end
 return b
end
