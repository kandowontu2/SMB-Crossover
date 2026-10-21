-- MM/Bass controller discovery only. Never writes emulated memory or registers.
-- A candidate becomes evidence only after the full CSV is replayed from power-on.
local stage=''
local jumpAge=-1
local still,lastX=0,-1
local groundCount=0
local stairsReady=false
local lastMap=-1
return function(c)
 local b={right=true}
 local key=c.world..'-'..c.level..'-'..c.area
 if key~=stage then stage=key;jumpAge=-1;still=0;groundCount=0;stairsReady=false end
 if c.grounded and not c.lastA then jumpAge=-1 elseif jumpAge>=0 then jumpAge=jumpAge+1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 groundCount=c.grounded and groundCount+1 or 0
 local solid=function(wx,y)
  local t=c.block(wx,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 local e=c.enemy()
 local close=e and e.dx>0 and e.dx<112 and math.abs(e.y-c.y)<40
 if c.areaType==0 then
  -- MegaManBase keeps jump/gravity underwater; A is not Mario-style paddling.
  -- Walk along the floor and jump over walls, with an independent Bass air jump.
  b.a=c.grounded and not c.lastA
  if not c.grounded and jumpAge>=0 then b.a=jumpAge<30 end
  if c.char==9 and not c.grounded and c.y>120 and jumpAge>=32 then
   b.a=not c.lastA
  end
  b.b=close and c.poll%8<3
  if c.x>3000 then b.a=false end
  return b
 end
 local feet=c.y+32
 local obstacle=solid(c.x+23,c.y+25)or solid(c.x+23,c.y+8)
 if c.areaType==2 then obstacle=obstacle or solid(c.x+23,c.y-24)end
 -- A lower platform under the same column does not support this ledge.
 -- Check the next foot row so elevated treetops launch before their edge.
 local gap=not solid(c.x+22,math.min(feet+8,232))
 if c.world==0 and c.level==1 and c.x>=1000 and c.x<1800 and math.floor(c.x/128)~=lastMap then
  lastMap=math.floor(c.x/128)
  local left=math.floor((c.x-48)/16)*16
  local rows={}
  for y=64,224,16 do
   local line=''
   for x=left,left+256,16 do line=line..(solid(x,y)and'#'or'.')end
   rows[#rows+1]=y..':'..line
  end
  print('ROUTE-MAP x='..c.x..' left='..left..' '..table.concat(rows,' '))
 end
 local enemy=e and e.dx>0 and e.dx<46 and math.abs(e.y-c.y)<48
 -- Keep the default buster active during route discovery. Bass stops while
 -- shooting on the ground, so shoot at a nearby threat or while airborne.
 b.b=close and c.poll%8<3
 if c.grounded and not c.lastA and(obstacle or gap or enemy or still>20)then
  b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then
  b.a=jumpAge<30
 end
 -- A second Bass jump is reserved for a blocked approach or a long gap.
 if c.char==9 and not c.grounded and jumpAge>=18 and c.r('XgJumpUsed')==0
  and(gap or obstacle)and c.y>80 then b.a=not c.lastA end
 if c.char==1 and c.world==0 and c.level==0 and c.x>=2390 and c.x<2480 then
  if not stairsReady then
   -- Land on the first stair's top before taking off across its open gap.
   b.right=c.x<2433;b.left=c.x>2435;b.a=false
   if c.grounded and c.x>=2430 and c.x<=2437 then stairsReady=true end
   if c.grounded and c.x<2430 then b.a=not c.lastA;jumpAge=0 end
  else b.right=true;b.left=false;b.a=c.grounded and not c.lastA or jumpAge<30 end
 end
 if e and math.abs(e.dx)<112 and math.abs(e.y-c.y)<24 and c.grounded then
  local facing=e.dx>=0 and 1 or 2
  b.a=false;b.right=false;b.left=false
  if c.r('PlayerFacingDir')~=facing then b.right=facing==1;b.left=facing==2 end
  b.b=c.poll%8<3
  if math.abs(e.dx)<22 then b.a=not c.lastA;jumpAge=0 end
 end
 if e and e.dx>0 and e.dx<96 and e.y-c.y>=-64 and e.y-c.y<=-24 and c.grounded and not gap then
  -- Walk beneath elevated enemies instead of jumping into their underside.
  b.a=false
  if c.char==9 then b.up=true;b.b=c.poll%8<3 end
 end
 if c.char==1 and c.status==0 and c.world==0 and c.level==0 and c.x>=280 and c.x<350 then
  local vx=(c.vx>=128 and c.vx-256 or c.vx)/16
  local error=332-c.x-4*vx
  b.right=error>1;b.left=error< -1;b.b=c.poll%8<3
  if math.abs(c.x-332)<4 and c.grounded and not c.lastA then b.a=true;jumpAge=0 end
 end
 for slot=0,5 do
  if c.status==0 and c.r('Enemy_Flag',slot)~=0 and c.r('Enemy_ID',slot)==0x2e
   and c.r('PowerUpType',slot)==0 then
   local px=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
   local py=c.r('Enemy_Y_Position',slot)
   if math.abs(px-c.x)<144 and(not e or math.abs(e.dx)>64)then
    local vx=(c.vx>=128 and c.vx-256 or c.vx)/16
    local error=px-c.x-4*vx
    b.right=error>3;b.left=error< -3;b.b=false
    if py<c.y+8 and c.grounded and not c.lastA then b.a=true;jumpAge=0 end
    break
   end
  end
 end
 -- Enter the normal 1-2 exit pipe from its side, instead of jumping its lip.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2670 then b.a=false end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=1090 and c.x<1240 then
  b.right=true;b.left=false
  if c.grounded and c.x>=1108 and not c.lastA then b.a=true;jumpAge=0
  elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<30 end
 end
 return b
end
