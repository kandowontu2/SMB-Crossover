-- Samus/Bill/Lance candidate discovery. No emulated memory writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/roster_samus_contra_nav.lua'))
local initialUpgrade=false
local phase='approach'
local jumpAge=0
local mount
local pillarLanded=false
local lowMount='back'
local lowMounted=false
local stairsMounted=false
local exitPhase='back'
local plantX,plantReady=nil,false
local holdA,cooldown=0,0
local function finish(b,c)
 if cooldown>0 then cooldown=cooldown-1 end
 if b.a and holdA==0 and cooldown==0 then holdA=32 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end end
 return b
end
return function(c)
 local b=travel(c)
 b.b=c.poll%12<5
 local e=c.enemy()
 -- LanceHard only: the third pipe has continuous floor below its exit.
 -- Walk off rather than treating air8px below its top as a floor gap.
 -- Reset only this controller's own jump latch; never game motion/state.
 if ROSTER_CONFIG.name=='lance'and ROSTER_CONFIG.mode_value==1
    and c.char==3 and c.variant==1 and c.world==0 and c.level==0
    and c.x>=748 and c.x<820 and c.yHigh==1 and c.y<176 then
  holdA=0;cooldown=0
  return {right=true,b=c.poll%12<5,a=false}
 end
 -- Land at the near edge of 1-3's high platform before firing at its Goombas.
 -- Bill and Lance cannot use Mario's stomp to resolve a descending overlap.
 if c.char==3 and c.world==0 and c.level==2 and c.x>=600 and c.x<640 and e and e.id==6 and e.y<80 and e.dx>16 and e.dx<128 then
  return finish({right=c.x<614,left=c.x>618,down=c.grounded,b=c.poll%12<5},c)
 end
 if c.char==3 and e and e.id~=13 and not c.grounded then
  b.up=e.y<c.y-8;b.down=e.y>c.y+8
 end
 -- Drop to the ordinary side entrance before walking into the exit pipe.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then
  holdA=0;cooldown=0
  if exitPhase=='back' then
   local target=math.max(2616,c.camera+1)
   if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter' end
   return {right=c.x<target,left=c.x>target+3,b=c.poll%12<5}
  end
  return {right=true,b=c.poll%12<5}
 end
 -- Land on the final stair before crossing to the descending lift.
 -- A single jump from the lower stair reaches only its bottom copy.
 if c.world==0 and c.level==1 and not stairsMounted and c.x>=2144 and c.x<2208 then
  if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return {right=true,b=true}end
  return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- Walk across the descending lift before jumping toward the next bank.
 -- Its second platform sits overhead, so a jump from the left edge is short.
 if c.world==0 and c.level==1 and c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then
  holdA=0;cooldown=0;return {right=true,b=c.poll%12<5}
 end
 -- Samus can clear a live plant by launching near its pipe, keeping the
 -- apex over the plant rather than using the generic early enemy jump.
 if c.char==2 and e and e.id==13 and e.dx>0 and e.dx<80 then
  if c.grounded and e.dx>42 then holdA=0;return {right=true,b=c.poll%12<5}end
  return finish({right=true,a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- A Piranha is above the floor muzzle. Jump vertically and fire before
 -- crossing its pipe, rather than shooting below it or landing on its head.
 if c.char==3 and e and e.id==13 and e.dx> -16 and e.dx<68 then
  if plantX~=e.x then plantX=e.x;plantReady=false end
  if not plantReady then
   if e.dx<56 then holdA=0;return {left=true,b=false}end
   plantReady=true
  elseif e.dx<32 then plantReady=false;holdA=0;return {left=true}end
  if c.r('PlayerFacingDir')~=1 then return {right=true}end
  return finish({a=c.grounded and not c.lastA,b=c.poll%12<5},c)
 end
 -- Standing muzzles pass above the short enemies. Stop and use the native
 -- prone/crouch muzzle before the enemy reaches contact range.
 if e and e.id~=13 and e.dx> -48 and e.dx<112 and math.abs(e.y-c.y)<32 and c.grounded and holdA==0 and not c.lastA and c.block(c.x+8,c.y+32)~=0 and c.block(c.x+(e.dx<0 and -12 or 24),c.y+24)==0 then
  holdA=0
  local dir=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=dir then return {left=dir==2,right=dir==1}end
  return {down=true,b=c.poll%12<5}
 end
 if c.world==0 and c.level==1 and c.areaType==2 and not lowMounted and c.x>=1170 and c.x<1290 then
  if c.y<=112 and c.grounded then lowMounted=true
  elseif c.block(1224,152)~=0 and c.block(1224,152)~=0x23 then
   if lowMount=='back'then
    holdA=0
    local target=math.max(1196,c.camera+1)
    if c.x>=target and c.x<=target+2 and c.grounded then lowMount='rise';return finish({a=true},c)end
    return {right=c.x<target,left=c.x>target+2}
   elseif lowMount=='rise'then
    if c.y<=112 then lowMount='onto' end
    return finish({a=c.grounded and not c.lastA},c)
   else
    return finish({right=c.x<1250,left=c.x>1252},c)
   end
  else lowMounted=true end
 end
 -- The underground pair of gaps contains a narrow intermediate column.
 -- Land on its real top instead of carrying one jump past both gaps.
 if c.world==0 and c.level==1 and c.areaType==2 and not pillarLanded and c.x>=1944 and c.x<1984 then
  if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c)end
  return finish({right=c.x<1960,left=c.x>1964},c)
 end
 if c.char==2 and c.r('SmBall')~=0 then
  -- Never strand a controller candidate in Morph Ball at a pipe.
  b.up=c.poll%2==0;b.down=false;b.a=false
 end
 -- The first ordinary mushroom is a real native pickup, collected through
 -- head contact and pursuit. Other upgrade coverage uses separate arenas.
 if c.world~=0 or c.level~=0 or initialUpgrade then return finish(b,c)end
 if c.status>0 or(c.char==3 and(c.r('InvOwnedLo',3)+256*c.r('InvOwnedHi',3))>1)then initialUpgrade=true;return finish(b,c)end
 if phase=='approach' and c.x<320 then return finish(b,c)end
 b={}
 if phase=='approach' then
  b.right=c.x<330;b.left=c.x>334
  if c.x>=330 and c.x<=334 and c.grounded then phase='bump';jumpAge=0 end
 elseif phase=='bump' then
  b.a=jumpAge<30;jumpAge=jumpAge+1
  b.right=c.x<330;b.left=c.x>334
  if jumpAge>65 and c.grounded then jumpAge=0 end
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then phase='collect' end end
 elseif phase=='collect' then
  local px,py
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)
  end end
  if not px then phase='bump';jumpAge=0;return finish(b,c)end
  b.right=c.x<px-5;b.left=c.x>px+5
  if not mount and py<c.y-10 and c.grounded and c.y>144 then mount='back';holdA=0 end
  if mount then
   local target=math.max(284,c.camera+1)
   if mount=='back'then
    b.right=c.x<target;b.left=c.x>target+1;b.a=false
    if c.x>=target and c.x<=target+1 and c.grounded then mount='rise';b.a=true end
   elseif mount=='rise'then
    b.right=false;b.left=false
    if c.y<=112 then mount='onto' end
    if c.grounded and not c.lastA then b.a=true end
   else
    b.right=c.x<px-4;b.left=c.x>px+4
    if c.grounded and c.y>144 then mount='back' end
   end
  elseif py<c.y-10 and c.grounded then b.a=not c.lastA end
 end
 if e and math.abs(e.dx)<90 then
  b.b=c.poll%7==0
  if c.char==3 then b.down=c.grounded end
  if math.abs(e.dx)<24 and c.grounded then b.a=not c.lastA;b.down=false end
 end
 return finish(b,c)
end

