-- Input-only recovery/toolkit controller over the surviving natural route.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')
local phase='route';local origin,ground,arrowSlot=nil,nil,nil
local wall,wallTop,wallEnd,attempt=nil,nil,nil,nil
local function report(c,p)
 if phase~=p then
  phase=p;print('Darkwing route '..p..' x'..c.x..' y'..c.y..' gas'..c.r('DwGas')..' adaptor'..c.r('DwAdaptor')..' mode'..c.r('DwMode'))
 end
end
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 assert(c.char==12 and c.r('DarkwingVariant')==1,'Actual Darkwing controller owner')
 local pipe=c.block(c.x+32,c.y-20)
 -- Recovery creation stays typed-pipe-only in the game. At another tall
 -- solid face use an already-earned Arrow, without assuming a new cache.
 local typedPipe=pipe>=0x10 and pipe<0x16
 local near=c.block(c.x+16,c.y-20)
 local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 local tallFace=solid(pipe)or solid(near)
 local earnedArrow=c.r('DwAdaptor')==2 and c.r('DwGas')>=3
 if phase=='route'and c.x>450 and c.grounded and c.vx==0 and(typedPipe or tallFace and earnedArrow)then
  if not typedPipe then print('Darkwing earned tall face near'..near..' far'..pipe..' grounded'..tostring(c.grounded)..' previous'..c.r('DwPrevious'))end
  origin=c.x;ground=c.y
  wall=(((solid(near)and c.x+16 or c.x+32)//16)*16)
  wallTop=32;while wallTop<c.y+32 and not solid(c.block(wall+8,wallTop+1))do wallTop=wallTop+16 end
  wallEnd=wall+16;while wallEnd<wall+96 and solid(c.block(wallEnd+8,ground+17))do wallEnd=wallEnd+16 end
  print('Darkwing actual wall '..wall..' top'..wallTop..' end'..wallEnd)
  report(c,'acquire')
 end
 if phase=='route'then
  -- Free basic only at actual forward Goombas/Koopas with a clear shot lane.
  local e=c.enemy();local aim=c.y+17
  local near=e and(e.id==0 or e.id==1 or e.id==6)and e.dx>0 and e.dx<96
   and e.x>=c.camera and e.x<c.camera+240 and math.abs(e.y-aim)<24
   and c.r('PlayerFacingDir')==1
  if near then
   for x=c.x+24,e.x-8,8 do if solid(c.block(x,aim))then near=false;break end end
  end
  b.b=not not(b.b and near and c.r('DwMode')==0)
  return b
 end
 if phase~='basic-release'and phase~='basic-press'then
  if c.grounded and c.x+8>=wall and c.y+32<=wallTop then report(c,'cross-top')end
  if c.x>=wallEnd+8 then report(c,'basic-release')end
 end
 if phase=='cross-top'then return{right=true}end
 if phase=='basic-release'then
  if c.r('DwMode')==0 then report(c,'route');return{right=true}end
  if c.r('DwPrevious')&32==0 then report(c,'basic-press')end
 end
 if phase=='basic-press'then
  if c.r('DwMode')==0 then report(c,'route');return{right=true}end
  return{right=true,select=true}
 end
 if phase=='basic-release'then return{right=true}end
 b={right=true}
 local function ownedArrow()
  for i=0,9 do if c.r('RgShotType',i)==6 and c.r('RgShotDir',i)==1 then
   local actor=c.r('RgShotImpact',i)-1
   if actor>=0 and actor<=5 and c.r('Enemy_Flag',actor)==1 and c.r('Enemy_ID',actor)==0x26 and(c.r('Enemy_State',actor)&0x7f)==(0x20|i)then
    local sx=c.r('RgShotX',i)+256*c.r('RgShotPage',i)
    local ax=c.r('Enemy_X_Position',actor)+256*c.r('Enemy_PageLoc',actor)
    local ay=c.r('Enemy_Y_Position',actor);local lift=c.y+32-ay
    -- Genuine right-attachment equations: shotX=cellLeft-12,
    -- actorX=shotX-12. The leading probe may attach inside the second cell.
    -- A globally valid Arrow at another wall/height cannot be our next step.
    if sx+12>=wall and sx+12<wallEnd and ax==sx-12 and(c.r('SsMode',i)==0 and lift>=-8 and lift<=50 or c.r('PlatformCollisionFlag',actor)<128)then return i end
   end
  end end
 end
 local function rememberAttempt()
  attempt={};for i=0,9 do attempt[i]={t=c.r('RgShotType',i),age=c.r('RgShotAge',i)}end
 end
 local function newArrow()
  if not attempt then return end
  for i=0,9 do
   local t,a=c.r('RgShotType',i),c.r('RgShotAge',i)
   local dx=c.r('RgShotX',i)+256*c.r('RgShotPage',i)-c.x
   if(t==8 and c.r('RgShotImpact',i)==2 or t==5)and c.r('RgShotDir',i)==1 and a<13 and dx>=8 and dx<=44 and(attempt[i].t~=t or a<attempt[i].age)then return i end
  end
 end
 if phase=='acquire'then
  if c.r('DwAdaptor')==2 and c.r('DwGas')>=3 then report(c,'select-release')
  else
   local item
   for i=0,5 do
    if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==0x2e and c.r('Enemy_State',i)>=128 and c.r('InvPickupOwner',i)==12 and c.r('InvPickup',i)==0x26 then
     item=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);break
    end
   end
   -- Without a live recovery actor keep genuine wall pressure; only the
   -- game can create it. Never seed an adaptor, gas, pickup or platform.
   if item then b.right=c.x<item-4;b.left=c.x>item+8 end
   return b
  end
 end
 if phase=='select-release'then
  if c.r('DwMode')==1 then report(c,'fire-release')
  elseif c.r('DwPrevious')&32==0 then report(c,'select-press')end
 end
 if phase=='select-press'then
  b.select=true
  if c.r('DwMode')==1 then b.select=false;report(c,'fire-release')end
  return b
 end
 if phase=='fire-release'then
  arrowSlot=ownedArrow()
  if arrowSlot then report(c,'jump-release')
  elseif c.r('DwPrevious')&64==0 then rememberAttempt();report(c,'fire-press')end
 end
 if phase=='fire-press'then
  local created=newArrow()
  if created then arrowSlot=created;b.b=false;report(c,'attach')
  elseif c.r('DwPrevious')&64~=0 then b.b=false;report(c,'fire-release')
  else b.b=true end
  return b
 end
 if phase=='attach'then
  local usable=ownedArrow()
  if usable then arrowSlot=usable;report(c,'jump-release')
  elseif arrowSlot and c.r('RgShotType',arrowSlot)==0 then report(c,'fire-release')end
  return b
 end
 if phase=='jump-release'then
  if c.r('DwPrevious')&128==0 then report(c,'jump-hold');b.a=true end
  return b
 end
 if phase=='jump-hold'then
  b.a=true
  if c.grounded and c.y<ground-4 then ground=c.y;b.a=false;report(c,'jump-release')
  elseif c.grounded and not ownedArrow()then b.a=false;report(c,'acquire')end
  -- Actual DwPrevious confirms every release before another real press.
  -- The existing arrow's native landing/jump/collision owns all movement.
  return b
 end
 return b
end
