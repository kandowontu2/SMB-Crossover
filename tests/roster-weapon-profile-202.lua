-- Explicit full-inventory arena profile; not a playthrough. Controller presses
-- produce weapons. Report inclusive CPU costs and skipped physical NMIs for
-- empty terrain and six live native enemy targets separately.
local c=assert(PROFILE_CHARACTER)
local choices=c==4 and{0,1,2,3,6}or c==5 and{0,2,3,4,5,6}or{0,1,2,3,4,5}
local frame,age,index,control=0,-1,0,0
local selected,scene,seen,skipped=0,0,false,0
local samples={}
local starts={}
local out=assert(io.open(OUTPUT..ROM_NAME..'-weapon-profile-'..c..'.csv','w'))
out:write('frame,character,weapon,enemies,routine,cycles,activeShots,skippedNmis\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function shots()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
for _,routine in ipairs({{'RosterWeapons','RosterWeaponsFinish',8},{'ExpandedWeapons','ExpandedWeaponsFinish',37},{'RemainingWeapons','RemainingWeaponsFinish',6}})do
 local name,finish,bank=table.unpack(routine)
 emu.addMemoryCallback(function()
  if age>=0 and r('CurrentBank')%128==bank then starts[name]=emu.getState()['cpu.cycleCount']end
 end,emu.callbackType.exec,assert(L[name]))
 emu.addMemoryCallback(function()
  if starts[name]and r('CurrentBank')%128==bank then
   local cycles=emu.getState()['cpu.cycleCount']-starts[name]
   starts[name]=nil
   out:write(table.concat({frame,c,selected,scene,name,cycles,shots(),skipped},',')..'\n')
   local key=selected..'/'..scene..'/'..name
   local s=samples[key]or{n=0,total=0,max=0};samples[key]=s
   s.n=s.n+1;s.total=s.total+cycles;s.max=math.max(s.max,cycles)
  end
 end,emu.callbackType.exec,assert(L[finish]))
end
emu.addMemoryCallback(function()
 if age>=0 and r('NmiDisable')>=128 then skipped=skipped+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('RgEnemyStun',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i);w('RgShotImpact',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerFacingDir',1);w('PlayerStatus',1);w('RgCrouch',0);w('CrouchingFlag',0)
 w('RgAttack',0);w('RgPreviousButtons',0);w('RgCooldown',0);w('AvSlash',0);w('AvFlip',0);w('AvStopwatch',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',255)
 w('InvOwnedLo',c==4 and 127 or c==5 and 255 or 255,c);w('InvOwnedHi',c==5 and 3 or 0,c)
 w('InvSelected',selected,c);w('InvAmmo',99,c*16);w('InvAmmo',20,c*16+1);w('InvAmmo',20,c*16+2)
 if scene==6 then
  for i=0,5 do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i)
   w('Enemy_X_Position',120+18*i,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',176,i);w('Enemy_Y_HighPos',1,i)
   w('EnemyOffscrBitsMasked',0,i);w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i)
   w('MmEnemyHealthLo',255,i);w('MmEnemyHealthHi',127,i)
  end
 end
end
emu.addEventCallback(function()
 if age>=0 then control=control+1 end
 local choosing=c<6 and frame>=80 and frame<80+c*20 and frame%20==0 or c>=6 and frame>=100 and frame<100+(c-6)*20 and frame%20==0
 local t=control%150
 emu.setInput({right=choosing,down=c>=6 and frame==80,start=frame==240,
  b=age>=0 and selected==0 and control%24>=18 and control%24<22,select=age>=0 and selected~=0 and control%24>=18 and control%24<22,
  a=c==10 and selected==5 and t%50<25},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<600 then return end
 age=age+1
 if age%150==0 then
  if age>0 then assert(seen,'Controller produced attack c='..c..' weapon='..selected..' enemies='..scene)end
  index=index+1
  local weapon=choices[math.floor((index-1)/2)+1]
  if not weapon then
   for key,s in pairs(samples)do print('PROFILE '..key..' n='..s.n..' mean='..math.floor(s.total/s.n)..' max='..s.max)end
   out:close();print('PASS source inventory weapon profile '..c..' with empty/six-enemy scenes, skipped NMIs='..skipped);emu.stop(0);return
  end
  selected=weapon;scene=index%2==0 and 6 or 0;seen=false;setup()
 end
 if age%150==30 then print('PROFILE state c='..c..' weapon='..selected..' enemies='..scene..' engine='..r('GameEngineSubroutine')..' state='..r('Player_State')..' buttons='..r('A_B_Buttons')..' attack='..r('RgAttack')..' timer='..r('TimerControl'))end
 if r('RgAttack')>0 or shots()>0 or r('AvStopwatch')>0 or r('AvSlash')>0 then seen=true end
end,emu.eventType.endFrame)
