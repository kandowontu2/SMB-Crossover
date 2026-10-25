-- Jump from native foot support when the underground route has a real pit.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local follow=assert(dofile(root..'/tools/playthroughs/rygar_ceiling_wall_dj.lua'))
local flight=nil
local log=assert(io.open(ROSTER_CONFIG.out..'gap-response.csv','w'))
log:write('frame,poll,event,x,y,frontX,airborne\n')
local function floorBelow(c,x)
 for y=c.y+32,239,16 do if c.block(x,y)~=0 then return true end end
 return false
end
return function(c)
 if c.world~=0 or c.level~=1 then flight=nil;return follow(c)end
 if flight then
  if not c.grounded then flight.air=true end
  if(flight.air and c.grounded)or c.frame-flight.frame>90 then
   log:write(table.concat({c.frame,c.poll,'finish',c.x,c.y,flight.front,flight.air and 1 or 0},',')..'\n');log:flush();flight=nil
  end
 end
 if not flight and c.grounded and(c.block(c.x+2,c.y+32)~=0 or c.block(c.x+13,c.y+32)~=0)and not floorBelow(c,c.x+20)and not floorBelow(c,c.x+36)then
  flight={frame=c.frame,front=c.x+20,air=false}
  log:write(table.concat({c.frame,c.poll,'launch',c.x,c.y,flight.front,0},',')..'\n');log:flush()
 end
 if flight then return{right=true,a=not c.grounded or c.r('RgPreviousButtons')&128==0,b=c.frame%12<5}end
 return follow(c)
end
