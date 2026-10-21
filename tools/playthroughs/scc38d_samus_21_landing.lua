-- Pause a descending leap over real floor before the paired floor Goombas.
-- Samus has no ordinary stomp: land outside their approach, then use her beam.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_elevated.lua'))
return function(c)
 if c.world==1 and c.level==0 and c.x>=480 and c.x<720 and not c.grounded and c.vy<128 then
  local floor=c.block(c.x+8,216)
  if floor~=0 and floor~=0x23 and floor~=0x26 and floor~=0xc2 and floor~=0xc3 then
   local y=c.y+(c.yHigh==0 and -256 or 0)
   for i=0,5 do
    local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
    if flag>0 and flag<128 and id<0x15 and id~=13 and st<0x20 then
     local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
     if x>c.x and x-c.x<120 and c.r('Enemy_Y_Position',i)>y+24 then
      return {right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3}
     end
    end
   end
  end
 end
 return base(c)
end
