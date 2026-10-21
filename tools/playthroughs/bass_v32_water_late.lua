-- Controller-only low route under the final hanging coral; reserve a fresh
-- primary jump for actual steps/gaps rather than climbing onto the roof.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_water_exit.lua'))
local age,offAge=-1,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==9 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2380 and c.x<3000 then
  local function solid(x,y)
   local t=c.block(x,math.min(232,math.max(32,y)))
   return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  local b={right=true}
  if c.grounded then
   age=-1
   local wall=solid(c.x+16,c.y+8)or solid(c.x+16,c.y+24)
   local gap=not solid(c.x+16,c.y+40)
   if offAge>=5 and(wall or gap)then age=0;b.a=true end
  elseif age>=0 then age=age+1;b.a=age<32 end
  return b
 end
 return prior(c)
end
