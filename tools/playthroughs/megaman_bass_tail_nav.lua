-- Generic tail for the native Mega Man/Bass motion, read-only controller policy.
local stage=''
local still,lastX=0,-1
local age=-1
return function(c)
 local key=c.world..'-'..c.level..'-'..c.areaType
 if key~=stage then stage=key;age=-1;still=0 end
 if c.grounded and not c.lastA then age=-1 elseif age>=0 then age=age+1 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 local solid=function(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 local b={right=true}
 local e=c.enemy()
 if c.areaType==0 and e and e.dx<0 then
  -- A nearby fish behind the player must not hide the approaching fish from
  -- the aim policy. This reads native actors; it only changes controller aim.
  local ahead
  for i=0,5 do
   local id,flag,st=c.r('Enemy_ID',i),c.r('Enemy_Flag',i),c.r('Enemy_State',i)
   if flag>0 and flag<128 and id<0x15 and st<0x20 and not(id==6 and st>=2)then
    local x=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local dx=x-c.x
    if dx>=0 and dx<160 and(not ahead or dx<ahead.dx)then
     ahead={slot=i,id=id,x=x,y=c.r('Enemy_Y_Position',i),state=st,dx=dx}
    end
   end
  end
  e=ahead or e
 end
 local close=e and e.dx>0 and e.dx<120 and math.abs(e.y-c.y)<48
 b.b=close and c.poll%8<3
 if c.char==9 and e and math.abs(e.dx)<120 then
  b.up=e.y<c.y-16;b.down=not c.grounded and e.y>c.y+16
 end
 if c.areaType==0 then
  local coral=solid(c.x+24,c.y+8)or solid(c.x+24,c.y+24)
  -- Guests jump from real support rather than paddling. Staying low on the
  -- clear floor avoids an unnecessary arc through the pursuing fish.
  if c.grounded and coral and not c.lastA then b.a=true;age=0 end
  if c.char==9 then
   if coral and c.yHigh==1 and not c.grounded and c.vy<128 and c.r('XgJumpUsed')==0 then b.a=not c.lastA end
   b.b=false;b.up=false;b.down=false
   if e and e.dx>=0 and e.dx<150 then
    -- Source cannon origins and 45-degree rays. Firing forever at a fish
    -- between the available rays locks Bass in place without hitting it.
    local mid=e.y+8
    local height=c.grounded and 18.5 or 14.5
    local reach=math.max(0,e.dx-16)
    local aim,err=0,math.abs(c.y+height-mid)
    local upErr=math.abs(c.y+height-7-reach-mid)
    local downErr=math.abs(c.y+height+7+reach-mid)
    if upErr<err then aim=1;err=upErr end
    if downErr<err then aim=2;err=downErr end
    if mid<c.y and math.abs(e.dx-5)<12 then aim=3;err=0 end
    if err<14 then
     b.b=c.poll%8<3;b.up=aim==1 or aim==3;b.down=aim==2
     if aim==3 then b.right=false;b.left=false end
    end
   end
   -- Down+A starts a dash on support, so release Down for a coral jump.
   if b.a then b.down=false end
  end
  return b
 end
 -- Mega Man's walk is slower than Mario's run. A 32-pixel lead launches too
 -- early at 2-1's 64-pixel floor gap; use the actual near edge instead.
 local lead=c.char==1 and 16 or 32
 if c.char==1 and c.world==0 and c.level==3 and c.x>=464 and c.x<512 then lead=12 end
 local gap=not solid(c.x+lead,math.min(c.y+40,232))
 -- Native moving platforms never appear in the metatile buffer. This foot/
 -- width match was validated by the Ryu route; MM/Bass final retiming still
 -- needs its own controller proof. Walk across the platform before launching.
 if c.grounded and not solid(c.x+8,math.min(c.y+34,232))then
  local feet=c.y+32
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   if c.r('Enemy_Flag',i)>0 and id>=0x24 and id<=0x2c then
    local left=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local top=c.r('Enemy_Y_Position',i)
    local ctrl=c.r('Enemy_BoundBoxCtrl',i)
    local width=ctrl==6 and 48 or ctrl==5 and 32 or 24
    if(math.abs(feet-top)<8 or(id>=0x2b and math.abs(feet-(top+128)%256)<8))and c.x+14>=left and c.x+2<left+width then
     gap=c.x+20>=left+width;break
    end
   end
  end
 end
 local obstacle=solid(c.x+40,c.y+24)or solid(c.x+40,c.y+8)
 local enemy=e and e.dx>0 and e.dx<40 and math.abs(e.y-c.y)<40
 if c.grounded and not c.lastA and(gap or obstacle or enemy or still>20)then b.a=true;age=0 end
 if c.char==9 and c.yHigh==1 and not c.grounded and c.vy<128 and c.r('XgJumpUsed')==0 and(gap or obstacle)then b.a=not c.lastA end
 -- Fire at grounded threats from the same floor. Keep air movement directed
 -- toward the next actual support instead of freezing at an airborne enemy.
 if e and(e.id~=0x2d or e.dx>0)and math.abs(e.dx)<104 and math.abs(e.y-c.y)<24 and c.grounded and not gap then
  b.right=false;b.left=false
  local dir=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=dir then b.right=dir==1;b.left=dir==2 end
  b.b=c.poll%8<3
  if math.abs(e.dx)<18 then b.a=not c.lastA;age=0 end
 end
 -- Castle breath is a native enemy object outside the generic enemy() range.
 -- The verified Bass branch first jumps vertically to gain clearance, then
 -- advances. Walking into a nearby flame while rising closes the gap too fast.
 if c.areaType==3 then
  for i=0,5 do
   local flag=c.r('Enemy_Flag',i)
   if flag>0 and flag<128 and c.r('Enemy_ID',i)==0x15 then
    local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
    local fy=c.r('Enemy_Y_Position',i)
    if dx> -16 and dx<112 and c.grounded and obstacle and fy+8<=c.y and fy>c.y-80 then
     -- Standing below an overhead flame is safe. Let it pass before a
     -- mandatory pillar jump would put the body directly into its path.
     b.a=false;b.right=false;b.left=false;b.b=false
    elseif dx>0 and dx<112 and c.y<fy+8 and c.y+31>fy-2 then
     b.b=false;b.up=false;b.down=false
     if c.grounded and not c.lastA then b.a=true;age=0 end
     if dx<64 then b.right=false;b.left=false end
    end
   end
  end
 end
 return b
end
