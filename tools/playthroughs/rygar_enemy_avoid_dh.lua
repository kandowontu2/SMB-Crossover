-- Full old-movie pose guidance with an actual nearby-enemy jump response.
-- This supplies ordinary buttons only; no actor, power or position writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local follow=assert(dofile(root..'/build/verification/retime-movie-dg-7-0/policy.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'enemy-avoidance.csv','w'))
log:write('frame,poll,x,y,slot,enemyX,enemyY,jump\n')
return function(c)
 assert(c.r('CrossoverBehaviorVersion')==0,'This ordinary Rygar route uses actual Easy default')
 for i=0,5 do
  local flag,kind,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  if flag>0 and flag<128 and kind<7 and state<32 and(kind~=6 or state<2)then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if x>=c.x and x-c.x<=56 and math.abs(y-c.y)<=36 and c.yHigh==1 then
    local jump=not c.grounded or c.r('RgPreviousButtons')&128==0
    log:write(table.concat({c.frame,c.poll,c.x,c.y,i,x,y,jump and 1 or 0},',')..'\n');log:flush()
    return{right=true,b=c.frame%12<5,a=jump}
   end
  end
 end
 return follow(c)
end
