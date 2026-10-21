-- Ordinary inputs only. Wait in the actual gap between the first two firebars,
-- then cross the second while its short arm rotates through the upper half.
local base=assert(SCROOGE_P_BASE)
local phase='approach'
local waitAt,launch
local log=assert(io.open(ROSTER_CONFIG.out..'scrooge-castle-phase-i.csv','w'))
log:write('frame,poll,x,y,state,phase,slot,low,high,speed,direction,count,pivotX,pivotY,footL,footR,right,left,a,b\n')
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
return function(c)
 local b=base(c)
 if c.char~=12 or c.world~=0 or c.level~=3 or c.areaType~=3 or c.x<1006 or c.x>=1128 then return b end
 local slot,pivotX,pivotY
 for s=0,5 do
  local flag,id=c.r('Enemy_Flag',s),c.r('Enemy_ID',s)
  if flag>0 and flag<128 and id>=0x1b and id<0x23 then
   local x=c.r('Enemy_X_Position',s)+256*c.r('Enemy_PageLoc',s)
   if x==1076 then assert(slot==nil,'Ambiguous second firebar');slot=s;pivotX=x;pivotY=c.r('Enemy_Y_Position',s)end
  end
 end
 assert(slot~=nil and pivotY==100,'Actual short-firebar corridor differs')
 local low,high=c.r('FirebarSpinState_Low',slot),c.r('FirebarSpinState_High',slot)
 local speed,direction,count=c.r('FirebarSpinSpeed',slot),c.r('FirebarSpinDirection',slot),c.r('FirebarPartCount',slot)
 assert(speed==40 and direction~=0 and count==6,'Actual firebar rotation differs')
 local fl,fr=c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)
 if phase=='approach' then
  b={right=c.x<1013,left=c.x>1015}
  if c.x>=1013 and c.x<=1015 and c.grounded and c.y==112 and not c.lastA then phase='wait';waitAt=c.poll end
 end
 if phase=='wait' then
  assert(c.poll-waitAt<300,'Bounded firebar phase wait exceeded')
  assert(c.grounded and c.y==112 and c.x>=1009 and c.x<=1023,'Left the actual phase-wait ledge')
  b={right=c.x<1013,left=c.x>1015}
  if high==7 then phase='cross';launch=c.poll end
 end
 if phase=='cross' then
  assert(c.poll-launch<110,'Bounded firebar crossing exceeded')
  assert(c.grounded and c.y==112 and solid(fl) and solid(fr),'Actual crossing support differs')
  b={right=true}
 end
 log:write(table.concat({c.frame,c.poll,c.x,c.y,c.state,phase,slot,low,high,speed,direction,count,pivotX,pivotY,fl,fr,
                        b.right and 1 or 0,b.left and 1 or 0,b.a and 1 or 0,b.b and 1 or 0},',')..'\n');log:flush()
 return b
end
