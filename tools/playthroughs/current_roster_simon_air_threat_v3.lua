-- Link/Simon/Ryu discovery. This is not a verified route.
-- Return function(context); the harness owns menu input, logging and replay.
-- Each agent may copy this file into its own uniquely named character policy.
local jumpAge=-1
local lastStage=''
local lastX,still=0,0
local firstPowerDone,powerStage,powerAge,powerMount=false,'approach',0,nil
local simonFirstPickupSeen=false
local holdA,cooldown=0,0
local allowDouble=true
local lowMount,lowMounted,stairsMounted,pillarLanded,exitPhase='back',false,false,false,'back'
local outdoorStairReady=false
local liftLaunch=0
local springPhase,springJumpAt='approach',nil
local waterExitJumpAt
local function finish(b,c)
 if c.char==10 and b.up and c.r('XgWall')~=0 then
  -- Wall-top jumps consume a fresh A edge. A ground-jump hold must not
  -- replace the release requested by the wall controller below.
  holdA=0;cooldown=0;return b
 end
 if holdA>0 then b.a=true;holdA=holdA-1;if holdA==0 then cooldown=4 end
 elseif cooldown>0 then b.a=false;cooldown=cooldown-1
 elseif b.a then holdA=(c.char==5 and 23 or 31)
 elseif allowDouble and c.char==5 and not c.grounded and c.r('RgDoubleJump')~=0 and not c.lastA and c.y>40 then
  b.a=true;holdA=23
 end
 return b
end
return function(c)
 allowDouble=true
 local b={right=true}
 local stage=c.world..'-'..c.level..'-'..c.areaType
 if stage~=lastStage then jumpAge=-1;lastStage=stage;still=0;holdA=0;cooldown=0 end
 if c.grounded then jumpAge=-1 elseif jumpAge>=0 then jumpAge=jumpAge+1 end
 local small=(c.char==0 or c.char==8)and c.status==0
 local height=small and 16 or 32
 local feet=c.y+height
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local solid=function(wx,y)local t=c.block(wx,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if c.char==10 and c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  -- Native spring compression needs a new A edge after the landing input.
  -- Align over its actual X3008 support before committing to the tall wall.
  holdA=0;cooldown=0
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach'then
   if animation>0 then springPhase='compress';return{}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   local wall=c.r('XgWall')~=0
   local jump=springJumpAt and c.poll-springJumpAt<16
   if wall then
    local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
    jump=not c.lastA and not solid(probe,c.y+3)
   end
   return{right=c.x<3008,left=c.x>3012,a=jump,up=wall}
  elseif springPhase=='compress'then
   if animation==0 and c.vy>=128 then springPhase='cross';return{right=true}end
   return{a=animation>=2 and animation<=4}
  end
  if c.r('XgWall')~=0 then
   -- The boost can reach the tall wall before clearing its top. Ryu's
   -- source grab needs Up and a new top-jump edge to finish the crossing.
   local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
   return{right=true,up=true,a=not c.lastA and not solid(probe,c.y+3)}
  end
  return{right=true}
 end
 if c.areaType==3 and c.x>=2240 and c.x<2290 then
  -- Settle over the axe. Ryu must release wall-climb Up at the right wall;
  -- otherwise he repeatedly climbs into the roof instead of falling onto it.
  holdA=0;cooldown=0
  return{right=c.x<2248,left=c.x>2251}
 end
 -- SimonHard: abandon only the observed, subsequently lost first pickup.
 -- Retrying its head bump while standing on the row cannot reveal it again.
 if ROSTER_CONFIG.name=='simon'and ROSTER_CONFIG.mode_value==1
    and c.char==5 and c.variant==0 and c.world==0 and c.level==0
    and c.areaType==1 and not firstPowerDone then
  local observable=false
  for slot=0,5 do
   if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_ID',slot)==0x2e then observable=true end
  end
  simonFirstPickupSeen=simonFirstPickupSeen or observable
  if simonFirstPickupSeen and not observable and c.camera>=307
     and c.grounded and c.yHigh==1 and c.y==112 and c.x>=c.camera and c.x<416 then
   firstPowerDone=true;holdA=0;cooldown=0
  end
 end
 if c.world==0 and c.level==0 and not firstPowerDone then
  if c.status>0 or c.x>480 then firstPowerDone=true
  elseif c.x>=320 or powerStage~='approach' then
   local px,py
   for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);py=c.r('Enemy_Y_Position',i)end end
   if powerStage=='approach'and c.y<160 then powerStage='settle'end
   if powerStage=='settle'then
    holdA=0;cooldown=0
    if c.grounded and c.y>=160 then powerStage='approach'end
    local target=math.max(300,c.camera+1)
    return{right=c.x<target,left=c.x>target+2}
   end
   if powerStage=='approach'then
    holdA=0;cooldown=0
    if c.x>=330 and c.x<=334 and c.grounded then powerStage='bump';powerAge=0 end
    return{right=c.x<330,left=c.x>334}
   elseif powerStage=='bump'then
    powerAge=powerAge+1
    if px then powerStage='chase'
    else
     if powerAge>65 and c.grounded then powerAge=0;holdA=0;cooldown=4 end
     return finish({a=powerAge<30,right=c.x<330,left=c.x>334},c)
    end
   end
   if px then
    local item={right=c.x<px-5,left=c.x>px+5}
    if not powerMount and py<c.y-10 and c.grounded and c.y>144 then powerMount='back';holdA=0;cooldown=0 end
    if powerMount then
     local target=math.max(284,c.camera+1)
     if powerMount=='back'then
      item={right=c.x<target,left=c.x>target+1}
      if c.x>=target and c.x<=target+1 and c.grounded then powerMount='rise';item.a=true end
     elseif powerMount=='rise'then
      item={a=c.grounded and not c.lastA}
      if c.y<=112 then powerMount='onto'end
     else
      item={right=c.x<px-5,left=c.x>px+5}
      if c.grounded and c.y>144 then powerMount=nil end
     end
    end
    return finish(item,c)
   end
   if c.status==0 then powerStage='bump';powerAge=0;holdA=0;cooldown=4;return{}end
  end
 end
 if c.areaType==0 then
  if c.char==10 and c.world==1 and c.level==1 and c.x>=2900 then
   -- The native side pipe admits the body at Y112. Ryu's Right wall grab
   -- stops gravity, so use his real Down climb to leave the high approach
   -- and then hold Right through the opening, without another jump edge.
   holdA=0;cooldown=0
   if c.x<2935 then return{right=true}end
   if c.r('XgWall')~=0 then return{right=true,down=c.yHigh==0 or c.y<112}end
   if c.x>=2990 then return{right=true}end
   if c.grounded and not c.lastA then waterExitJumpAt=c.poll end
   return{right=true,a=waterExitJumpAt and c.poll-waterExitJumpAt<24}
  end
  -- Swim around mid-height and hold Right into the underwater exit pipe.
  if c.char==0 or c.char==8 then b.a=c.y>100 and not c.lastA
  else b.a=c.grounded and not c.lastA end
  b.b=c.poll%8==0
  if solid(c.x+20,c.y+8)then b.a=not c.lastA end
  if c.char==10 and c.r('XgWall')~=0 then
   b.up=true
   local probe=c.x+(c.r('PlayerFacingDir')==1 and 21 or-5)
   b.a=not solid(probe,c.y+3)and not c.lastA
  end
  return finish(b,c)
 end
 -- SimonHard's descending second-pipe arc meets a real ground Goomba.
 -- The whip needs fourteen logic updates; use the unused native air jump.
 if ROSTER_CONFIG.name=='simon'and ROSTER_CONFIG.mode_value==1
    and c.char==5 and c.variant==0 and c.world==0 and c.level==0
    and c.areaType==1 and c.yHigh==1 and c.x>=640 and c.x<736
    and not c.grounded and c.vy<128 and not c.lastA and c.r('RgDoubleJump')~=0 then
  for slot=0,5 do
   local flag=c.r('Enemy_Flag',slot)
   if flag>0 and flag<128 and c.r('Enemy_ID',slot)==6
      and c.r('Enemy_State',slot)<2 and c.r('Enemy_Y_HighPos',slot)==1
      and c.r('Enemy_BoundBoxCtrl',slot)==9 then
    local left=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)+3
    local above=c.r('Enemy_Y_Position',slot)+14-(c.y+32)
    if left>=c.x-8 and left<c.x+64 and above>=8 and above<=64 then
     holdA=0;cooldown=0
     return{right=true,a=true,b=false}
    end
   end
  end
 end
 local e
 for slot=0,5 do
  local id,st=c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
  local dx=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)-c.x
  if c.r('Enemy_Flag',slot)>0 and id<0x15 and st<0x20 and not(id==6 and st>=2)and dx> -12 and dx<120 then
   if not e or math.abs(dx)<math.abs(e.dx)then e={dx=dx,y=c.r('Enemy_Y_Position',slot),id=id}end
  end
 end
 b.b=e and math.abs(e.dx)<48 and math.abs(e.y-c.y)<44 and c.poll%12==0
 local obstacle=solid(c.x+24,c.y+height-8)or solid(c.x+24,c.y+8)
 if c.char==5 and not c.grounded then
  local supportBelow=false
  for y=math.max(32,feet+4),232,8 do if solid(c.x+8,y)then supportBelow=true;break end end
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   if c.r('Enemy_Flag',i)>0 and id>=0x24 and id<=0x2c then
    local left=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local top=c.r('Enemy_Y_Position',i)
    local ctrl=c.r('Enemy_BoundBoxCtrl',i)
    local width=ctrl==6 and 48 or ctrl==5 and 32 or 24
    if c.x+8>=left and c.x+8<left+width and top>=feet-4 then supportBelow=true end
   end
  end
  allowDouble=not supportBelow or obstacle
 end
 -- A floor far beneath a pipe/platform is not support for its current ledge.
 local ledgeProbe=c.char==5 and 12 or 20
 local supportAhead=solid(c.x+ledgeProbe,math.min(feet+8,232))
 local gap=not supportAhead
 if c.grounded and not solid(c.x+8,math.min(feet+2,232))then
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   if c.r('Enemy_Flag',i)>0 and id>=0x24 and id<=0x2c then
    local left=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)
    local top=c.r('Enemy_Y_Position',i)
    local ctrl=c.r('Enemy_BoundBoxCtrl',i)
    local width=ctrl==6 and 48 or ctrl==5 and 32 or 24
    local vertical=math.abs(feet-top)<8 or(id>=0x2b and math.abs(feet-(top+128)%256)<8)
    if vertical and c.x+14>=left and c.x+2<left+width then
     -- Native platforms are not in the metatile buffer. Cross their actual
     -- width before launching, rather than jumping from their near edge.
     gap=c.x+ledgeProbe>=left+width
     break
    end
   end
  end
 end
 if c.grounded and not c.lastA and(obstacle or gap or still>20)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<30 end
 if allowDouble and c.char==5 and not c.grounded and jumpAge>=31 and c.r('RgDoubleJump')~=0
  and(gap or obstacle)and c.y>60 then b.a=not c.lastA end
 if e and math.abs(e.dx)<(c.char==5 and 43 or 31)and math.abs(e.y-c.y)<32 and c.grounded then
  b.right=false;b.left=false;b.b=c.r('RgAttack')==0;b.a=false
  holdA=0;cooldown=4
  local facing=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=facing then return{left=facing==2,right=facing==1}end
  -- Ryu's crouch blade is seven pixels lower. Keep the standing blade for
  -- a hopping Koopa whose body is above him instead of slashing under it.
  if c.char==10 and e.y>=c.y or c.char==5 and e.id==6 then b.down=true end
 end
 if c.char==4 and e and e.dx>35 and e.dx<90 and math.abs(e.y-c.y)<80 and c.r('RgAttack')==0 then
  b.select=true;b.up=e.y<c.y-28
 end
 if c.char==4 and c.grounded and c.r('RgAttack')>0 and(gap or obstacle)then
  -- Link's source forbids a ground jump during his sword/throw sequence.
  -- Let that attack finish on the support before pressing a fresh A.
  holdA=0;cooldown=4;b.a=false;b.right=false;b.left=false
  return b
 end
 if c.areaType==3 and c.grounded then
  for i=0,5 do
   local id=c.r('Enemy_ID',i)
   local dx=c.r('Enemy_PageLoc',i)*256+c.r('Enemy_X_Position',i)-c.x
   local dy=c.r('Enemy_Y_Position',i)-c.y
   -- Bowser flames use bbox Y+4..8. A high flame can safely pass over a
   -- standing guest; jumping merely because its origin is nearby hits it.
   -- Include its remaining vertical travel toward the native target row.
   local flameTop,flameBottom=c.y+dy+4,c.y+dy+8
   if id==0x15 and c.r('Enemy_Y_MoveForce',i)~=0 then
    local target=({144,128,112,144})[c.r('BowserFlamePRandomOfs',i)%4+1]
    flameTop=math.min(c.y+dy,target)+4
    flameBottom=math.max(c.y+dy,target)+8
   end
   local head=c.y+(c.char==4 and 18 or 1)
   local flameThreat=flameBottom>=head and flameTop<=c.y+32
   if c.r('Enemy_Flag',i)>0 and((id==0x15 and dx>0 and dx<80 and flameThreat)
      or(id==0x2d and dx>0 and dx<55 and math.abs(dy)<40))then
    b.b=false;b.select=false
    if c.char==4 and c.r('RgAttack')>0 then holdA=0;cooldown=0;return{left=true}end
    if not c.lastA then b.a=true;jumpAge=0 end
   end
  end
 end
 if c.char==10 and c.r('XgWall')~=0 then
  b.up=true;b.a=not solid(c.x+21,c.y+3)and not c.lastA
 end
 if c.char==10 and obstacle and c.grounded and still>10 and solid(c.x+8,c.y-8)then
  holdA=0;cooldown=4;b.a=false;b.down=true;b.b=c.r('RgAttack')==0
 end
 if c.char==5 and obstacle and c.grounded and still>8 and solid(c.x+8,c.y-8)then
  -- His standing whip reaches the low wall's bottom brick; crouching passes
  -- underneath that row. Release B between source whip sequences.
  holdA=0;cooldown=4
  return{b=c.poll%28<6}
 end
 if c.world==0 and c.level==0 and c.x>=2390 and c.x<2480 and not outdoorStairReady then
  if c.grounded and c.x>=2430 and c.x<=2437 and c.y<=112 then
   outdoorStairReady=true;holdA=0;cooldown=4;return{right=true}
  end
  return finish({right=c.x<2433,left=c.x>2435,a=c.grounded and c.x<2430 and not c.lastA},c)
 end
 if c.world==0 and c.level==1 and c.areaType==2 then
  if c.x>=2580 then
   holdA=0;cooldown=0
   if exitPhase=='back'then
    local target=math.max(2616,c.camera+1)
    if c.x>=target and c.x<=target+3 and c.grounded and c.y>=128 then exitPhase='enter'end
    return{right=c.x<target,left=c.x>target+3}
   end
   return{right=true}
  end
  if not stairsMounted and c.x>=2144 and c.x<2208 then
   if c.grounded and c.y<=112 then stairsMounted=true;holdA=0;cooldown=4;return{right=true}end
   return finish({right=c.x<2180,left=c.x>2184,a=c.grounded and not c.lastA},c)
  end
  if c.x>=2208 then
   -- Step across the descending lift. A ground launch near the next bank
   -- reaches the rising lift; repeated Simon double jumps reach the roof.
   holdA=0;cooldown=0
   local tail={right=b.right,left=b.left,up=b.up,down=b.down,b=b.b}
   if c.char==10 and c.r('XgWall')~=0 then tail.a=b.a end
   if c.x<2380 and c.grounded and obstacle and not c.lastA then tail.a=true end
   if c.x>=2380 and c.x<2420 then
    if c.grounded and not c.lastA and liftLaunch==0 then liftLaunch=6 end
    if liftLaunch>0 then tail.a=true;liftLaunch=liftLaunch-1 end
   else liftLaunch=0 end
   if c.x>=2490 and c.x<2570 and(c.yHigh==0 or c.y<48)then tail.right=false end
   return tail
  end
  if c.x>=2216 and c.x<2264 and c.grounded and c.block(c.x+8,c.y+32)==0 then holdA=0;cooldown=0;return{right=true}end
  if c.char==4 and not lowMounted and c.x>=1170 and c.x<1290 then
   if c.y<=112 and c.grounded then lowMounted=true
   elseif solid(1224,152)then
    if lowMount=='back'then
     holdA=0;local target=math.max(1196,c.camera+1)
     if c.x>=target and c.x<=target+2 and c.grounded then lowMount='rise';return finish({a=true},c)end
     return{right=c.x<target,left=c.x>target+2}
    elseif lowMount=='rise'then
     if c.y<=112 then lowMount='onto'end
     return finish({a=c.grounded and not c.lastA},c)
    else
     if c.grounded and c.y>112 then lowMount='back';holdA=0;cooldown=4;return{left=true}end
     return finish({right=c.x<1250,left=c.x>1252},c)
    end
   else lowMounted=true end
  end
  if not pillarLanded and c.x>=1944 and c.x<1984 then
   if c.grounded then pillarLanded=true;holdA=0;return finish({right=true,a=not c.lastA},c)end
   return finish({right=c.x<1960,left=c.x>1964},c)
  end
 end
 -- Underground exit: walking into its vertical pipe enters normally.
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>2800 then b.a=false end
 return finish(b,c)
end


