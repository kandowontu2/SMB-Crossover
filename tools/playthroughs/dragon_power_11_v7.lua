-- Controller-only boarding of the genuine added 704 platform; original jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/dragon_power_11_v6.lua'))
local boarded=false
local hold=0
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 then
  if hold>0 then
   hold=hold-1
   return {right=true,a=true}
  end
  if not boarded and c.x>=665 and c.x<768 then
   b={right=c.x<703,left=c.x>704}
   local slot=c.r('HpActorSlot')-1
   local riding=slot>=0 and slot<6 and c.r('HpActorOwner',slot)==0x83
    and c.r('Enemy_Flag',slot)==1 and c.r('Enemy_ID',slot)==0x25
    and c.r('Enemy_State',slot)==0x40 and c.r('PlatformCollisionFlag',slot)<0x80
    and c.r('Enemy_X_Position',slot)==0xb0 and c.r('Enemy_PageLoc',slot)==2
   if riding and c.grounded and c.r('DpAction')==1 and c.y<=144 and not c.lastA then
    boarded=true
    hold=7
    b={right=true,a=true}
   end
  end
 end
 return b
end
