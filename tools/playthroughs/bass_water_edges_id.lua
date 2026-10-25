-- Preserve the proven water route, releasing Jump after landing before a
-- fresh obstacle jump. Controller input only; no emulated state changes.
local choose=assert(dofile('C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/playthroughs/bass_water_floor_hx.lua'))
return function(c)
 local b=choose(c)
 if c.world==1 and c.level==1 and c.areaType==0 and c.grounded and b.a then
  b.a=c.r('RgPreviousButtons')&128==0
 end
 return b
end
