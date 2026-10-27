-- Input-only recovery/toolkit controller over the surviving natural route.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')
local phase='route';local origin,ground,arrowSlot=nil,nil,nil
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
 if phase=='route'and c.x>450 and c.grounded and c.vx==0 and pipe>=0x10 and pipe<0x16 then
  origin=c.x;ground=c.y;report(c,'acquire')
 end
 if phase=='route'then return b end
 if c.x>origin+64 then report(c,'route');return b end
 b={right=true}
 local function ownedArrow()
  for i=0,9 do
   if c.r('RgShotType',i)==6 then
    local actor=c.r('RgShotImpact',i)-1
    if actor>=0 and actor<=5 and c.r('Enemy_Flag',actor)==1 and c.r('Enemy_ID',actor)==0x26 and(c.r('Enemy_State',actor)&0x7f)==(0x20|i)then return i end
   end
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
  elseif c.r('DwPrevious')&64==0 then report(c,'fire-press')end
 end
 if phase=='fire-press'then
  b.b=true
  for i=0,9 do
   local t=c.r('RgShotType',i)
   if t==5 or t==6 or t==8 and c.r('RgShotImpact',i)==2 then b.b=false;report(c,'attach');break end
  end
  return b
 end
 if phase=='attach'then
  arrowSlot=ownedArrow()
  if arrowSlot then report(c,'jump-release')end
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
