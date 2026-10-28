-- Input-only airborne Arrow pipe climb; inherited repeated-gap route elsewhere.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_darkwing_gap_v6.lua')
local phase='route';local wall,top,wallEnd,ground,slot,attempt
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
local function change(c,p)
 if phase~=p then phase=p;print('Darkwing air-arrow '..p..' x'..c.x..' y'..c.y..' gas'..c.r('DwGas')..' hang'..c.r('DwHang'))end
end
return function(c)
 if c.world~=0 or c.level~=0 then return base(c)end
 assert(c.char==12 and c.r('DarkwingVariant')==1,'Actual airborne Arrow owner')
 if phase=='route'then
  local near=c.block(c.x+16,c.y-20);local far=c.block(c.x+32,c.y-20)
  local n=near>=0x10 and near<0x16;local f=far>=0x10 and far<0x16
  if c.x>450 and c.grounded and c.vx==0 and(n or f)then
   wall=((n and c.x+16 or c.x+32)//16)*16;ground=c.y
   top=32;while top<ground+32 and not solid(c.block(wall+8,top+1))do top=top+16 end
   wallEnd=wall+16;while wallEnd<wall+96 and solid(c.block(wallEnd+8,ground+17))do wallEnd=wallEnd+16 end
   -- These are the source-controlled64/80px cases, reachable by the first
   -- genuine jump. Other geometry remains with the unchanged route policy.
   if top>=ground-48 and top<=ground-32 then slot=nil;attempt=nil;change(c,'acquire')end
  end
  if phase=='route'then return base(c)end
 end
 if phase~='finish-release'and phase~='finish-press'and c.x>=wallEnd+8 then change(c,'finish-release')end
 if phase=='finish-release'then
  if c.r('DwMode')==0 then change(c,'route');return{right=true}end
  if(c.r('DwPrevious')&32)==0 then change(c,'finish-press')end
 end
 if phase=='finish-press'then
  if c.r('DwMode')==0 then change(c,'route');return{right=true}end
  return{right=true,select=true}
 end
 local prev=c.r('DwPrevious')
 local function stable()
  if not slot or c.r('RgShotType',slot)~=6 or c.r('RgShotDir',slot)~=1 or c.r('SsMode',slot)~=0 then return false end
  local a=c.r('RgShotImpact',slot)-1
  if a<0 or a>5 or c.r('Enemy_Flag',a)~=1 or c.r('Enemy_ID',a)~=0x26 or c.r('Enemy_State',a)~=(0x20|slot)then return false end
  local sx=c.r('RgShotX',slot)+256*c.r('RgShotPage',slot)
  return sx+12>=wall and sx+12<wallEnd and c.r('Enemy_X_Position',a)+256*c.r('Enemy_PageLoc',a)==sx-12
   and c.r('Enemy_Y_Position',a)==c.r('RgShotY',slot)and c.r('RgShotY',slot)<=top+20
 end
 if phase=='acquire'then
  if c.r('DwAdaptor')==2 and c.r('DwGas')>=3 then change(c,'select-release')
  else
   for i=0,5 do
    if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==0x2e and c.r('Enemy_State',i)>=128 and c.r('InvPickupOwner',i)==12 and c.r('InvPickup',i)==0x26 then
     local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);return{right=c.x<x-4,left=c.x>x+8}
    end
   end
   return{right=true}
  end
 end
 if phase=='select-release'then
  if c.r('DwMode')==1 then change(c,'takeoff-release')
  elseif(prev&32)==0 then change(c,'select-press')end
 end
 if phase=='select-press'then
  if c.r('DwMode')==1 then change(c,'takeoff-release')else return{right=true,select=true}end
 end
 if phase=='takeoff-release'then
  if c.grounded and(prev&128)==0 then change(c,'rise');return{right=true,a=true}end
  return{right=true}
 end
 if phase=='rise'then
  if not c.grounded and c.y<=top and(prev&64)==0 then
   attempt={};for i=0,9 do attempt[i]={kind=c.r('RgShotType',i),age=c.r('RgShotAge',i)}end
   change(c,'fire');return{right=true,a=true,b=true}
  end
  return{right=true,a=true}
 end
 if phase=='fire'then
  for i=0,9 do
   local t,a=c.r('RgShotType',i),c.r('RgShotAge',i)
   local dx=c.r('RgShotX',i)+256*c.r('RgShotPage',i)-c.x
   if(t==8 and c.r('RgShotImpact',i)==2 or t==5)and c.r('RgShotDir',i)==1 and a<13 and dx>=8 and dx<=44
    and c.r('RgShotY',i)<=top+20 and attempt and(attempt[i].kind~=t or a<attempt[i].age)then
    slot=i;change(c,'hang');return{right=true}
   end
  end
  return{right=true,a=true,b=(prev&64)==0}
 end
 if phase=='hang'then
  if stable()and c.r('DwHang')==(0x80|slot)and(prev&128)==0 then change(c,'hang-jump');return{right=true,a=true}end
  if c.grounded and stable()and(prev&128)==0 then return{right=true,a=true}end
  if slot and c.r('RgShotType',slot)==0 and c.grounded then change(c,'acquire')end
  return{right=true}
 end
 if phase=='hang-jump'then
  if c.grounded and c.y+32<=top and c.x+8>=wall then change(c,'top')end
  return{right=true,a=true}
 end
 return{right=true}
end
