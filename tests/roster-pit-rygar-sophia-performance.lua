-- Explicit flat-room ability fixtures. Inputs fire all projectiles; the test
-- measures exclusive routine cycles with NMI/IRQ time removed, plus lag frames.
local c=assert(PROFILE_CHARACTER)
local names=c==6 and {'normal-arrow','long-arrow','fire-arrow','hammer','flight'}or
 c==7 and {'short-disk','medium-disk','long-disk'}or
 {'normal-cannon','hyper-cannon','crusher-cannon','missile-triplet','homing-four','hover'}
local frame=0
local depth,interruptStart,interruptCycles=0,0,0
local stats,active={},false
local nmiStart,nmiPhase
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycle()return emu.getState()['cpu.cycleCount']end
local function phase()return math.floor((frame-550)/180),(frame-550)%180 end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do
 emu.addMemoryCallback(function()
  if depth==0 then interruptStart=cycle()-7 end;depth=depth+1
  if pc==L.NonMaskableInterrupt and active and r('NmiDisable')>=128 then
   local n=phase();local s=stats[n+1];s.lag=s.lag+1
  end
  if pc==L.NonMaskableInterrupt and active then nmiStart=cycle()-7;nmiPhase=phase()end
 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do
 emu.addMemoryCallback(function()
  depth=depth-1
  if depth==0 then interruptCycles=interruptCycles+cycle()+6-interruptStart end
  if pc==L.NonMaskableInterrupt_RTI and nmiStart then
   local s=stats[nmiPhase+1];local t=s.NMI or{};s.NMI=t;t[#t+1]={cycle()+6-nmiStart,0};nmiStart=nil
  end
 end,emu.callbackType.exec,pc)
end
local function hook(name,bank)
 local entry,sp,at,n,shotCount,activeShotCount
 local returns={}
 emu.addMemoryCallback(function()
  if not active or depth~=0 or r('CurrentBank')%128~=bank then return end
  entry=cycle();sp=emu.getState()['cpu.sp'];at=interruptCycles;n=phase();shotCount=0;activeShotCount=0
  for i=0,9 do if r('RgShotType',i)>0 then shotCount=shotCount+1;local impact=r('RgShotImpact',i);if impact==0 or impact>=128 then activeShotCount=activeShotCount+1 end end end
  local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if not entry or depth~=0 or r('CurrentBank')%128~=bank or emu.getState()['cpu.sp']~=sp+2 then return end
    local s=stats[n+1];local t=s[name]or{};s[name]=t
    t[#t+1]={cycle()-entry-(interruptCycles-at),shotCount,activeShotCount};entry=nil
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,assert(L[name],name))
end
hook('ExpandedMovement',30);hook('ExpandedWeapons',37);hook('ExpandedDrawShots',4)
if c==11 then
 hook('RemainingWeapons',6);hook('RemainingDraw',61)
 if PROFILE_DEEP then hook('HomingMotion',6);hook('HomeDamping',6);hook('DampX',6);hook('Blocks',8);hook('Enemies',8)end
end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('PlayerStatus',math.min(n,2));w('TimerControl',0)
 w('RgAttack',0);w('RgPreviousButtons',0);w('RgCooldown',0);w('XgPitFuel',60);w('XgHover',8)
 w('XgWall',0);w('XgCeiling',0);w('XgRise',0);w('XgHoverActive',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 if c==11 then
  w('PlayerStatus',n==0 and 0 or 1);w('InvOwnedLo',n==0 and 1 or n==1 and 0x81 or 0xff,11)
  w('InvSelected',n==4 and 2 or n==3 and 1 or 0,11);w('InvPrevious',0);w('InvAmmo',60,177);w('InvAmmo',20,178)
  if n==4 then
   w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',220);w('Enemy_PageLoc',0)
   w('Enemy_Y_Position',96);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0)
   w('MmEnemyHealthLo',255);w('MmEnemyHealthHi',127);w('AvStopwatch',240)
  end
 end
end
emu.addEventCallback(function()
 local n,t=phase();local b={start=frame==240,down=frame==80,
  right=frame>=100 and frame<100+20*(c-6)and(frame-100)%20==0}
 if n>=0 and n<#names then
  if(c==6 and n==4)or(c==11 and n==5)then b.a=(t>=4 and t<14)or(t>=20 and t<125)
  elseif c==6 and n==3 then b.select=t%20==4
  elseif c==11 and(n==3 or n==4)then b.select=t%8>=4 and t%8<7
  else b.b=t%4==0 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n,t=phase()
 if n>=#names then
  active=false
  local f=assert(io.open(OUTPUT..ROM_NAME..'-roster-profile-'..c..'.csv','w'))
  f:write('ability,routine,samples,average,maximum,maximum_shots,maximum_active_shots,lag_frames,hardware_frames\n')
  for i,name in ipairs(names)do
   local expected=(c==6 and i<=3)and 2 or c==7 and 1 or(c==11 and i<=3)and 3 or(c==11 and i==4)and 3 or(c==11 and i==5)and 4 or 0
   assert(stats[i].activePeak>=expected,'Full active projectile pool exercised for '..name..': '..stats[i].activePeak..' / '..expected)
   if expected>0 then assert(stats[i].activePeak==expected,'Active projectile cap respected for '..name)end
   if expected==0 then assert(stats[i].ability,'Active ability exercised: '..name)end
   for _,routine in ipairs({'ExpandedMovement','ExpandedWeapons','ExpandedDrawShots','RemainingWeapons','RemainingDraw','HomingMotion','HomeDamping','DampX','Blocks','Enemies','NMI'})do
    local rows=stats[i][routine]
    if rows then
     local sum,maximum,shots,activeShots=0,0,0,0
     for _,row in ipairs(rows)do sum=sum+row[1];maximum=math.max(maximum,row[1]);shots=math.max(shots,row[2]);activeShots=math.max(activeShots,row[3]or 0)end
     assert(#rows>=30,'Profile samples for '..name..'/'..routine)
     f:write(table.concat({name,routine,#rows,math.floor(sum/#rows),maximum,shots,activeShots,stats[i].lag,180},',')..'\n')
    end
   end
  end
  f:close();print('PASS profile '..c..': '..#names..' active ability cases with interrupt-exclusive cycles and hardware lag');emu.stop(0);return
 end
 if t==0 then stats[n+1]={lag=0,peak=0};fixture(n);active=true end
 local count,activeCount=0,0;for i=0,9 do if r('RgShotType',i)>0 then count=count+1;local impact=r('RgShotImpact',i);if impact==0 or impact>=128 then activeCount=activeCount+1 end end end
 stats[n+1].peak=math.max(stats[n+1].peak,count);stats[n+1].activePeak=math.max(stats[n+1].activePeak or 0,activeCount)
 if(c==6 and n==3 and r('RgAttack')>0)or(c==6 and n==4 and r('XgPitFlight')>0)or(c==11 and n==5 and r('XgHoverActive')>0)then stats[n+1].ability=true end
end,emu.eventType.endFrame)
