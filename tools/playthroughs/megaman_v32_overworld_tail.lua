-- Ordinary-controller pipe approach: clear the higher Koopa before dropping.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_castle_tail.lua'))
local pipeDone,quiet=false,0
local lowerGroupDone,lowerQuiet=false,0
return function(c)
 if c.char==1 and c.world==1 and c.level==0 and c.x>=720 and c.x<790 and not pipeDone then
  local foe=false
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if f>0 and f<128 and id<0x15 and id~=13 and st<32 and x>c.x and x<c.x+220 then foe=true end
  end
  quiet=foe and 0 or quiet+1
  if quiet>=16 then pipeDone=true;print('MM32 pipe-side foe clear '..c.poll)
  else return{right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3}end
 end
 if c.char==1 and c.world==1 and c.level==0 and c.x>=1200 and c.x<1420 and c.grounded and c.y<=144 and not lowerGroupDone then
  local below=false
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if f>0 and f<128 and id<0x15 and id~=13 and st<32 and not(id==6 and st>=2)
    and x>c.x-32 and x<c.x+220 and y>=c.y+32 then below=true end
  end
  lowerQuiet=below and 0 or lowerQuiet+1
  if lowerQuiet>=16 then lowerGroupDone=true;print('MM32 lower group passed '..c.poll)
  else return{}end
 end
 if c.char==1 and c.world==1 and c.level==0 and c.grounded then
  local foe
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if f>0 and f<128 and id<0x15 and id~=2 and id~=13 and st<32 and not(id==6 and st>=2)
    and math.abs(x-c.x)<150 and math.abs(y-c.y)<24 and(not foe or math.abs(x-c.x)<math.abs(foe-c.x))then foe=x end
  end
  if foe then
   local face=foe>=c.x and 1 or 2
   return{right=c.r('PlayerFacingDir')~=face and face==1,left=c.r('PlayerFacingDir')~=face and face==2,b=c.poll%8<3}
  end
 end
 return prior(c)
end
