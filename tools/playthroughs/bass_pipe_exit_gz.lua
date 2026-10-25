-- Ordinary retreat below the1-2 pipe lip, confined to its underground room.
local guide=assert(dofile('C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/retime-movie-dg-9-0/policy.lua'))
local start
local log=assert(io.open(ROSTER_CONFIG.out..'pipe-approach.csv','w'))
log:write('frame,poll,x,y,state,engine,phase,area,areaType,changeTimer\n')
return function(c)
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2500 then
  if not start then start=c.poll end
  local age=c.poll-start
  local phase=age<64 and 1 or 2
  log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.engine,phase,c.area,c.areaType,c.r('ChangeAreaTimer')},',')..'\n');log:flush()
  assert(age<400,'Bounded underground pipe approach')
  return phase==1 and{left=true}or{right=true}
 end
 return guide(c)
end
