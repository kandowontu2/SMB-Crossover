-- Read-only native platform geometry; controller-only ordinary timing.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_lift_tail.lua'))
local jump=0
return function(c)
 if c.world==0 and c.level==2 and c.x>=1300 and c.x<1568 then
  if jump>0 then jump=jump-1;return{right=true,a=c.char~=9 or jump<16 or jump>20}end
  if c.grounded then
   local platforms={}
   for i=0,5 do
    if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==0x28 then
     local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
     platforms[#platforms+1]={slot=i,x=x,y=c.r('Enemy_Y_Position',i),dir=c.r('Enemy_MovingDir',i)}
    end
   end
   local on
   for _,p in ipairs(platforms)do
    if math.abs(c.y+32-p.y)<4 and c.x+8>=p.x and c.x+8<p.x+48 then on=p;break end
   end
   if on then
    local target=on.x+16
    local ready=false
    if on.y==128 then
     for _,other in ipairs(platforms)do
      if other.y==144 and other.x>on.x then ready=other.x-on.x-48<=64 and other.dir==2 and on.dir==1 end
     end
    elseif on.y==144 then ready=1568-on.x-48<=48 and on.dir==1 end
    if ready and math.abs(c.x-target)<=4 and not c.lastA then
     jump=40;print('MM32 platform jump '..c.poll..' x'..c.x..' from'..on.x..' top'..on.y)
     return{right=true,a=true}
    end
    return{right=c.x<target-2,left=c.x>target+2}
   end
  end
 end
 return prior(c)
end
