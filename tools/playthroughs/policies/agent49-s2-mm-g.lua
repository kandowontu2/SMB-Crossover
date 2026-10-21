-- Ordinary castle timing from native firebar angle, not a forced hazard state.
-- Short ceiling bars have five8px parts. Their own source spin is32 steps;
-- enter while the counterclockwise bar is in its upper-right quadrant.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-f.lua'))
local cleared,cross={},nil
local f=assert(io.open(ROSTER_CONFIG.out..'mm-firebar-control.csv','w'))
f:write('poll,x,y,power,center,angle,fraction,direction,action\n')
return function(c)
 local b=prior(c)
 if c.world==0 and c.level==3 and c.areaType==3 then
  local bars={}
  for i=0,5 do
   local id,flag=c.r('Enemy_ID',i),c.r('Enemy_Flag',i)
   if flag>0 and flag<128 and id>=27 and id<=30 and c.r('Enemy_Y_Position',i)==100 then
    bars[#bars+1]={slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),angle=c.r('FirebarSpinState_High',i),low=c.r('FirebarSpinState_Low',i),dir=c.r('FirebarSpinDirection',i)}
   end
  end
  table.sort(bars,function(a,z)return a.x<z.x end)
  if cross and c.x>=cross+46 then cleared[cross]=true;cross=nil end
  local target
  for _,p in ipairs(bars)do if p.x>=c.x-46 and not cleared[p.x]then target=p;break end end
  if target and target.x-c.x<=90 then
   local action='walk'
   if cross==target.x then
    b={right=true}
    if target.x>=1000 and c.x>=1008 and c.x<1120 and c.grounded then b.down=true;b.a=c.r('MmSliding')==0 and not c.lastA end
   else
    local wait=target.x-70
    for _,p in ipairs(bars)do if p.x<target.x then wait=math.max(wait,p.x+46)end end
    local ready=target.dir~=0 and target.angle==7 or target.dir==0 and target.angle==25
    if c.grounded and math.abs(c.x-wait)<=2 and ready then cross=target.x;b={right=true};action='admit';print('MM-S2 ceiling bar admission '..c.poll..' center'..target.x..' angle'..target.angle)
    else b={right=c.x<wait-1,left=c.x>wait+2};action='wait'end
   end
   if c.poll%4==0 then f:write(table.concat({c.poll,c.x,c.y,c.status,target.x,target.angle,target.low,target.dir,action},',')..'\n');f:flush()end
  end
 end
 return b
end
