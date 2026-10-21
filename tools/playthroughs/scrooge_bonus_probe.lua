-- Bounded read-only room-map probe over an ordinary controller prefix.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=dofile(root..'/tools/playthroughs/scrooge_native_policy.lua')
local logged=false
return function(c)
 if c.areaType==2 and c.area==64 and c.poll>=5900 and not logged then
  logged=true
  local f=assert(io.open(ROSTER_CONFIG.out..'bonus-map.csv','w'))
  f:write('y');for x=c.camera,c.camera+255,16 do f:write(','..x)end;f:write('\n')
  for y=32,224,16 do
   f:write(y);for x=c.camera,c.camera+255,16 do f:write(','..c.block(x,y))end;f:write('\n')
  end
  f:close()
  local q=assert(io.open(ROSTER_CONFIG.out..'bonus-actor.txt','w'))
  q:write(string.format('poll=%d x=%d y=%d camera=%d state=%d pogo=%d\n',c.poll,c.x,c.y,c.camera,c.state,c.r('ScPogo')));q:close()
  local shot=assert(io.open(ROSTER_CONFIG.out..'bonus.png','wb'));shot:write(emu.takeScreenshot());shot:close()
  local ppu=assert(io.open(ROSTER_CONFIG.out..'bonus-ppu.bin','wb'))
  for a=0x2000,0x2fff do ppu:write(string.char(emu.read(a,emu.memType.nesPpuDebug)))end;ppu:close()
  emu.stop(0)
 end
 return normal(c)
end
