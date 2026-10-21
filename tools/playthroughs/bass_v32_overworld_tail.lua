-- Controller-only second-jump release for 2-1's stepped terrain.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_castle_tail.lua'))
local age=-1
local lowerDone,quiet=false,0
return function(c)
 if c.char==9 and c.world==1 and c.level==0 and c.x>=832 and c.x<920 and c.grounded and c.y<=128 and not lowerDone then
  local below=false
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if f>0 and f<128 and id<0x15 and id~=13 and st<32 and not(id==6 and st>=2)
    and x>c.x-32 and x<c.x+220 and c.r('Enemy_Y_Position',i)>=c.y+32 then below=true end
  end
  quiet=below and 0 or quiet+1
  if quiet>=16 then lowerDone=true;print('BASS32 lower group passed '..c.poll)else return{}end
 end
 local b=prior(c)
 if c.char==9 and c.world==1 and c.level==0 and c.grounded then
  local foe
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if f>0 and f<128 and id<0x15 and id~=2 and id~=13 and st<32 and not(id==6 and st>=2)
    and math.abs(x-c.x)<160 and math.abs(c.r('Enemy_Y_Position',i)-c.y)<24
    and(not foe or math.abs(x-c.x)<math.abs(foe-c.x))then foe=x end
  end
  if foe then local face=foe>=c.x and 1 or 2;b={right=c.r('PlayerFacingDir')~=face and face==1,left=c.r('PlayerFacingDir')~=face and face==2,b=true}end
 end
 if c.char==9 and c.world==1 and c.level==0 and c.x<2944 then
  if c.grounded then
   age=-1
   if b.a and not b.down and not c.lastA then age=0 end
  elseif age>=0 then age=age+1 end
  if age>=0 then b.a=age<20 or(age>=25 and age<56);b.down=false end
 end
 return b
end
