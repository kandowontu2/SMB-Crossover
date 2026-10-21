-- Read actual currently parsed floor cells, then stop. Controller prefix only.
return function(c)
 local f=assert(io.open(ROSTER_CONFIG.out..'gap-map.csv','w'))
 f:write('y');for x=1792,2048,16 do f:write(','..x)end;f:write('\n')
 for y=96,224,16 do f:write(y);for x=1792,2048,16 do f:write(','..c.block(x,y))end;f:write('\n')end
 f:close()
 local q=assert(io.open(ROSTER_CONFIG.out..'gap-actor.txt','w'))
 q:write(string.format('poll=%d x=%d y=%d camera=%d state=%d\n',c.poll,c.x,c.y,c.camera,c.state));q:close()
 local p=assert(io.open(ROSTER_CONFIG.out..'gap.png','wb'));p:write(emu.takeScreenshot());p:close()
 emu.stop(0);return{}
end
