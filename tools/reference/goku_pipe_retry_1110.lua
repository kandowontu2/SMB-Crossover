-- Insert after the bound controller's read-only RAM and JSON helpers.
C.ram.DpPrevious=0x5fd9
C.ram.DpJumping=0x5c0b
local pipe={phase='approach',start=-1,attempts=0,events={}}

local function pipeEvent(c,event)
 if #pipe.events>=32 then return end
 pipe.events[#pipe.events+1]={event=event,x=c.x,y=c.y,main=c.stageFrame,
  action=c.r('DpAction'),previous=c.r('DpPrevious'),jumping=c.r('DpJumping')}
end

local function writePipeRetry()
 local f=assert(io.open(OUTPUT..'pipe-retry.json','w'))
 f:write(json(pipe));f:close()
end

local function secondPipeRetry(c)
 if c.world~=0 or c.level~=0 or c.engine~=8 or pipe.phase=='crossed' then return end
 if c.x>=640 then
  if pipe.start>=0 then pipeEvent(c,'crossed');pipe.phase='crossed' end
  return
 end
 if c.x<576 and pipe.start<0 then return end
 if pipe.start<0 then pipe.start=c.stageFrame;pipeEvent(c,'approach') end
 if c.stageFrame-pipe.start>480 then pipeEvent(c,'deadline');return nil,true end

 local action=c.r('DpAction')
 local latched=c.r('DpPrevious')&0x80~=0
 local ready=action==1 and c.grounded
 if pipe.phase=='press' then
  if action==2 or (action==3 and c.r('DpJumping')~=0) then
   pipe.phase='airborne';pipeEvent(c,'source-jump')
  elseif latched then
   pipe.phase='release';pipeEvent(c,'sampled-without-jump')
   return {right=true}
  end
  return {right=true,a=true}
 end
 if pipe.phase=='airborne' then
  if not ready then return {right=true,a=true} end
  pipe.phase='release';pipeEvent(c,'landed-before-crossing')
 end
 if ready and not latched then
  pipe.phase='press';pipe.attempts=pipe.attempts+1;pipeEvent(c,'press')
  return {right=true,a=true}
 end
 return {right=true}
end
