-- Ordinary 1-1 input only. `base` is the retained natural first-M route.
local phase,at,hold,defense='mushroom',0,0,-1
local T={changes={}}
TANK_BOOT_POLICY=T
local function change(c,p)
 phase=p;at=c.update;T.phase=p
 T.changes[#T.changes+1]={phase=p,update=c.update,x=c.x,y=c.y,status=c.status}
 assert(#T.changes<=30,'Finite Tank boot phases')
end
local function steer(c,x,tolerance)
 local v=c.vx<128 and c.vx or c.vx-256
 local d=x-c.x;local lead=v*v/24+4;local band=tolerance or 2
 if v>2 and d<=lead then return {left=true}end
 if v< -2 and -d<=lead then return {right=true}end
 if d>band then return {right=true}end
 if d< -band then return {left=true}end
 return {left=v>0,right=v<0}
end
local function item(c,kind)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==kind then
   return {x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
end
return function(c)
 assert(c.char==0 and c.variant==7,'Tank controller identity')
 if c.status==0 then
  if phase=='mushroom'and c.x<256 then return base(c)end
  if phase=='mushroom'then change(c,'first-drop')end
  if phase=='first-drop'then
   if c.grounded and c.y>=160 and c.x>=390 then change(c,'first-align')else
    local e=c.enemy();local b=steer(c,400)
    if c.grounded and not c.lastA and e and e.dx>0 and e.dx<64 and math.abs(e.y-c.y)<48 then defense=c.update+22 end
    b.a=c.update<defense;return b
   end
  end
  local a=item(c,0)
  if a and phase~='first-collect'then change(c,'first-collect')end
  if phase=='first-align'then
   local v=c.vx<128 and c.vx or c.vx-256
   if c.grounded and c.y>=160 and math.abs(c.x-332)<=2 and math.abs(v)<=2 and not c.lastA then
    change(c,'first-bump');hold=c.update+28;return {a=true}
   end
   return steer(c,332)
  elseif phase=='first-bump'then
   if c.grounded and c.update-at>65 then change(c,'first-align')end
   local b=steer(c,332);b.a=c.update<hold;return b
  elseif phase=='first-collect'then
   if a and a.y>=152 then return steer(c,a.x-4)end
   return steer(c,400)
  end
  return {}
 end
 if c.engine~=8 then return {}end
 if c.status==1 then
  if phase=='mushroom'or phase:sub(1,5)=='first'then change(c,'travel')end
  if phase=='travel'then
   if c.x<1150 then return base(c)end
   change(c,'boot-align')
  end
  local a=item(c,1)
  if a and phase~='boot-stage'and phase~='boot-jump'and phase~='boot-walk'then change(c,'boot-stage')end
  if phase=='boot-align'then
   local v=c.vx<128 and c.vx or c.vx-256
   if c.grounded and c.y>=160 and math.abs(c.x-1244)<=2 and math.abs(v)<=2 and not c.lastA then
    change(c,'boot-bump');hold=c.update+18;return {a=true}
   end
   return steer(c,1244)
  elseif phase=='boot-bump'then
   if c.update-at>75 and c.grounded then change(c,'boot-align')end
   local b=steer(c,1244);b.a=c.update<hold;return b
  elseif phase=='boot-stage'then
   local v=c.vx<128 and c.vx or c.vx-256
   if a and a.state&128~=0 and c.grounded and c.y>=160 and math.abs(c.x-1206)<=3 and math.abs(v)<=3 and not c.lastA then
    change(c,'boot-jump');hold=c.update+28;return {right=true,a=true}
   end
   return steer(c,1206)
  elseif phase=='boot-jump'then
   if c.grounded and c.update-at>4 then
    if c.y<=112 then change(c,'boot-walk')else change(c,'boot-stage')end
   end
   local b=steer(c,a and a.x-4 or 1244);b.a=c.update<hold;return b
  elseif phase=='boot-walk'then return steer(c,a and a.x-4 or 1244)end
  return {}
 end
 assert(c.status==2,'Earned boots retain native power2')
 if phase:sub(1,4)=='boot'or phase=='travel'or phase=='mushroom'then change(c,'drop-after-boots')end
 -- No B is used from here: preserve the earned boot contact/terrain proof
 -- independently of the host's still available powered fireball feature.
 if not TANK_BOOT_PROGRESS.terrain and C.test~='enemy'then
  if phase=='drop-after-boots'then
   if c.grounded and c.y>=160 then change(c,'terrain-align')else return steer(c,1320)end
  end
  if phase=='terrain-align'then
   local v=c.vx<128 and c.vx or c.vx-256
   if c.grounded and c.y>=160 and math.abs(c.x-1244)<=2 and math.abs(v)<=2 and not c.lastA then
    change(c,'terrain-jump');hold=c.update+20;return {a=true}
   end
   return steer(c,1244)
  elseif phase=='terrain-jump'then
   if c.grounded and c.update-at>40 then change(c,'terrain-align')end
   local b=steer(c,1244);b.a=c.update<hold;return b
  end
 end
 if TANK_BOOT_PROGRESS.complete then
  if not T.stop then T.stop=c.x end
  return steer(c,T.stop)
 end
 local e=c.enemy()
 if c.grounded and e and e.id==6 and e.dx>0 and e.dx<96 and math.abs(e.y-c.y)<=24 then return {right=true}end
 local b=base(c);b.b=false;return b
end
