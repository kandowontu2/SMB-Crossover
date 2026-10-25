-- Source-guided route except for a physical retreat below the1-2 pipe lip.
-- Only ordinary buttons and read-only telemetry; no emulated state mutation.
local guide=assert(dofile('C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/retime-movie-dg-9-0/policy.lua'))
local start,phase=nil,0
local log=assert(io.open(ROSTER_CONFIG.out..'pipe-approach.csv','w'))
log:write('frame,poll,x,y,state,engine,phase,face,tileUpper,tileLower,changeTimer\n')
return function(c)
 if c.world==0 and c.level==1 and c.x>=2500 then
  if not start then start=c.poll end
  local age=c.poll-start
  phase=age<64 and 1 or 2
  log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,c.engine,phase,c.r('PlayerFacingDir'),c.block(c.x+16,c.y+8),c.block(c.x+16,c.y+24),c.r('ChangeAreaTimer')},',')..'\n');log:flush()
  assert(age<400,'Bounded physical pipe approach must enter or expose its first obstruction')
  return phase==1 and{left=true}or{right=true}
 end
 return guide(c)
end
