-- Ordinary native Mario/Luigi controller tail. No emulated state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/luigi_native_policy.lua'))
local bridgeBack,bridgeUnder=false,false
return function(c)
 local b=base(c)
 if c.areaType==0 and c.world==1 and c.level==1 and c.x>=2020 and c.x<2256 then
  if c.grounded and c.y<160 and not bridgeUnder then bridgeBack=true end
  if bridgeBack and not bridgeUnder then
   local target=math.max(2032,c.camera+2)
   if c.grounded and c.y>=176 and math.abs(c.x-target)<=4 then bridgeUnder=true
   else return {left=c.x>target+2,right=c.x<target-2,b=true}end
  end
 end
 if c.areaType==0 and c.world==1 and c.level==1 and c.x<2960 then
  for slot=0,5 do
   local flag=c.r('Enemy_Flag',slot)
   local id=c.r('Enemy_ID',slot)
   if flag>0 and flag<128 and (id==10 or id==11) then
    local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
    local y=c.r('Enemy_Y_Position',slot)
    if x>c.x-8 and x<c.x+72 and y>=c.y+8 and y<c.y+48 then b.a=not c.lastA end
   end
  end
 end
 if c.areaType==0 and c.world==1 and c.level==1 and c.x>=2960 then
  return {right=true,b=true,a=c.x<3000 and c.y>110 and not c.lastA}
 end
 return b
end
