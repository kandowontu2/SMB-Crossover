-- Ordinary controller discovery: step off coral when real floor lies below.
-- Jump across true floor gaps and onto obstacles; no memory/state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/scc34_samus_water_tail.lua'))
return function(c)
 local b=choose(c)
 if c.areaType==0 and c.grounded and c.y<176 and not(c.world==1 and c.level==1 and c.x>=2040 and c.x<2240)then
  local function solid(x,y)
   local t=c.block(x,y)
   return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  if solid(c.x+24,216)and not solid(c.x+24,c.y+8)and not solid(c.x+24,c.y+24)then b.a=false end
 end
 return b
end
