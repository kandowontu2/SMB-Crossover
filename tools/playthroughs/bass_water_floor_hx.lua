-- Water traversal through native floor/obstacle queries and real jump edges.
-- The other rooms retain the verified/source-guided route. No state writes.
local guide=assert(dofile('C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/playthroughs/bass_pipe_exit_gz.lua'))
local lastX,still=0,0
local function solid(t)return t~=0 and t~=0xc2 and t~=0xc3 and t~=0x23 and t~=0x26 end
return function(c)
 if c.world==1 and c.level==1 and c.areaType==0 then
  local b={right=true}
  if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
  assert(still<420,'Bounded actual water obstacle response')
  local wall=solid(c.block(c.x+18,c.y+9))or solid(c.block(c.x+18,c.y+24))
  local gap=not solid(c.block(c.x+20,c.y+32))
  if c.grounded then
   b.a=wall or gap
  else
   b.a=true                    -- Preserve the full source jump while rising.
   local vy=c.vy>=128 and c.vy-256 or c.vy
   if vy>=0 and c.r('XgJumpUsed')==0 then
    b.a=c.r('RgPreviousButtons')&128==0 -- Release, then real second jump edge.
   end
  end
  local e=c.enemy()
  if e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<48 then
   b.b=c.poll%8<3
   b.up=e.y<c.y-10
  end
  return b
 end
 return guide(c)
end
