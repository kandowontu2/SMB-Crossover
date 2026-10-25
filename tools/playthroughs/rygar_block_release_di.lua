-- Release/repress B while an actual elevated brick wall stops the guided run.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local follow=assert(dofile(root..'/tools/playthroughs/rygar_enemy_avoid_dh.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'brick-response.csv','w'))
log:write('frame,poll,x,y,frontTop,frontBottom,a,b\n')
return function(c)
 local top=c.block(c.x+16,c.y+8);local bottom=c.block(c.x+16,c.y+24)
 if c.world==0 and c.level==1 and c.y<176 and c.vx==0 and(top==0x52 or bottom==0x52)then
  local a=c.frame%24>=12;local b=c.frame%12<5
  log:write(table.concat({c.frame,c.poll,c.x,c.y,top,bottom,a and 1 or 0,b and 1 or 0},',')..'\n');log:flush()
  return{right=true,a=a,b=b}
 end
 return follow(c)
end
