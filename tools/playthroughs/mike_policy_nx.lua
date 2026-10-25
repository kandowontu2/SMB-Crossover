-- Discovery controller, never a clear until its saved input stream is replayed.
local phase='approach';local clock=0;local seenItem=false;local itemPhase='wait';local cast=false
local jumpAge=-1;local lastX=0;local still=0
return function(c)
 local b={right=true};local name=ROSTER_CONFIG.name
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 b.b=not not near and c.poll%24<2
 if name=='kirby'then b.b=not not near end
 if c.char==18 then
  b.a=true;b.b=c.poll%8==0;b.right=c.x<3180
  local target=100
  if c.x<400 then target=145 end
  b.up=c.y>target+3;b.down=c.y<target-3
  return b
 end
 if c.world~=0 or c.level~=0 then return b end
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 -- Approach and physically reveal the first real mushroom/upgrade block.
 if phase=='approach'and c.x>=332 then phase='bump';clock=c.frame end
 if phase=='bump'then
  b.right=false;b.b=false
  if c.x>337 then b.left=true end
  local t=c.frame-clock;b.a=t>=16 and t<45
  if t>65 then phase='pickup';clock=c.frame end
  return b
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),kind=c.r('PowerUpType',i)}
  end
 end
 if phase=='pickup'then
  if item then seenItem=true end
  if seenItem and not item then phase='route'
  elseif c.frame-clock>600 then phase='route'
  else
   b.right=false;b.b=false
   if not item or item.state<128 then return b end
   if item.kind==0 then
    b.right=c.x<item.x-4;b.left=c.x>item.x+12
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   else
    if itemPhase=='wait'then itemPhase='left'end
    if itemPhase=='left'then
     b.left=c.x>300
     if c.x<=300 then itemPhase='jump';clock=c.frame end
    else
     b.right=c.x<item.x+3
     b.a=c.frame-clock<38
     if name=='kirby'then b.up=c.y>105 end
     if c.frame-clock>90 then itemPhase='left'end
    end
   end
   return b
  end
 end
 if name=='zelda2'and not cast and(c.r('Z2LearnedSpells')&2)~=0 then
  b.select=true;cast=true;return b
 end
 if name=='kirby'and c.r('KbMouth')~=0 then b.down=true;b.b=false end
 local feet=c.y+32
 local obstacle=solid(c.x+22,feet-8)or solid(c.x+22,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c.x+12,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>16)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if name=='kirby'and not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if name=='grant'then
  if c.r('Cv3Climb')~=0 then b.up=true;b.a=false end
 elseif name=='darkwing'then
  if c.r('DwHang')~=0 then b.a=not c.lastA end
 elseif name=='mac'and c.r('LmStars')>0 and near then b.up=true end
 if c.char==17 then b.b=true end
 if c.x>3120 then b.right=true end
 return b
end




