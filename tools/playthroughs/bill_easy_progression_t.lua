-- Ordinary controller discovery: preserve the first mushroom route, then
-- stop for a real second power-up block in 1-1. No emulated state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_middle_edge.lua'))
local target,phase,age,finished=nil,'approach',0,0
local log=assert(io.open(ROSTER_CONFIG.out..'progression.csv','w'));log:write('poll,event,x,y,targetX,targetY,power\n')
local function note(c,event)log:write(table.concat({c.poll,event,c.x,c.y,target and target.x or 0,target and target.y or 0,c.status},',')..'\n');log:flush()end
local function poweredBlock(t)return t==0xc1 or t==0x55 or t==0x5a end
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.status>=2 then
  if finished==0 then note(c,'flower-collected')end
  finished=finished+1
  return {b=finished<180 and c.poll%8<3}
 end
 if c.world~=0 or c.level~=0 or c.status==0 then return base(c)end
 if not target then
  for wx=math.floor(math.max(c.x-16,c.camera)/16)*16,math.min(c.camera+224,c.x+160),16 do
   for y=80,160,16 do
    if poweredBlock(c.block(wx,y))and(not target or wx<target.x)then target={x=wx,y=y};phase='approach';age=0 end
   end
  end
  if target then note(c,'target')else return base(c)end
 end
 local item=c.r('Enemy_Flag',5)>0 and c.r('Enemy_ID',5)==0x2e and c.r('Enemy_State',5)>0
 if item and phase~='collect-jump' then phase='pickup' end
 if phase=='approach' then
  if c.x<target.x-48 then return base(c)end
  if c.y<target.y+12 then return {right=c.x<target.x+28,b=c.poll%8<3}end
  if math.abs(c.x-target.x)<=2 and c.grounded and not c.lastA then phase='bump';age=0;note(c,'head-bump')
  else return {right=c.x<target.x,left=c.x>target.x+2,b=c.poll%8<3}end
 end
 if phase=='bump' then
  age=age+1
  if age>45 then phase='approach';return{}end
  return {a=age<=30,up=true,b=c.poll%8<3}
 end
 if phase=='pickup' then
  if not item then return{}end
  local ix=c.r('Enemy_X_Position',5)+256*c.r('Enemy_PageLoc',5)
  if c.r('Enemy_State',5)<128 then return {left=c.x>target.x-32,right=c.x<target.x-34}end
  if c.grounded then
   if c.x>target.x-32 then return {left=true}end
   if c.x<target.x-34 then return {right=true}end
   if not c.lastA then phase='collect-jump';age=0;note(c,'collect-jump')end
  end
  return{}
 end
 if phase=='collect-jump' then
  age=age+1
  if c.grounded and age>4 then phase='pickup';return{}end
  local ix=c.r('Enemy_X_Position',5)+256*c.r('Enemy_PageLoc',5)
  return {a=age<32,right=c.y<target.y-28 and c.x<ix,left=c.y<target.y-28 and c.x>ix+6}
 end
 return base(c)
end
