-- Fire from the source crouch muzzle at grounded enemies and the floor-
-- bouncing green Paratroopa; jumping into its high phase causes contact.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_secondpipe_shortjump.lua'))
local first=4
return function(c)
 if c.world==1 and c.level==0 and c.x>=2490 and c.x<2944 and c.grounded then
  local near
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   if flag>0 and flag<128 and id<0x15 and id~=13 and st<32 and x-c.x>=-12 and x-c.x<112 and math.abs(y-c.y)<(id==14 and 112 or 40)then
    if not near or math.abs(x-c.x)<math.abs(near.dx)then near={dx=x-c.x}end
   end
  end
  if near then
   local dir=near.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=dir then return{right=dir==1,left=dir==2}end
   local b=first>0 or c.poll%8<3;if first>0 then first=first-1 end
   return {down=true,b=b}
  end
 end
 return base(c)
end
