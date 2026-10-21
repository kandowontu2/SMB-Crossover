-- Hold the actual coral top and shoot the pursuing water enemy before
-- stepping off. No emulated state writes or manufactured pickups.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_late_wall.lua'))
local phase,age,quiet,saw='approach',0,0,false
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2528 and c.x<2560 and phase~='done' then
  if phase=='approach' then
   if c.grounded and c.y<=48 then phase='fight';age=0 else
    return{right=c.x<2534,left=c.x>2537}
   end
  end
  age=age+1
  local nearest,dist
  for i=0,5 do
   local f,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if f>0 and f<128 and id<0x15 and id~=13 and st<32 and math.abs(x-c.x)<176 then
    local d=math.abs(x-c.x)
    if not dist or d<dist then nearest={x=x,y=c.r('Enemy_Y_Position',i),id=id};dist=d end
   end
  end
  saw=saw or nearest~=nil;quiet=nearest and 0 or quiet+1
  if (age>=90 and saw and quiet>=24) or (age>=150 and not saw) then
   phase='done';print('MM34 coral combat cleared '..c.poll);return{right=true}
  end
  if age==1 or age%60==0 then
   print('MM34 coral combat '..c.poll..' x'..c.x..' y'..c.y..' foe'..(nearest and nearest.id..'/'..nearest.x..'/'..nearest.y or 'none'))
  end
  local face=nearest and (nearest.x>=c.x and 1 or 2) or 1
  return{right=c.r('PlayerFacingDir')~=face and face==1,
   left=c.r('PlayerFacingDir')~=face and face==2,b=age%8<4}
 end
 return prior(c)
end
