-- Explicit flat ground/inventory fixture; seven real trigger presses.
-- Source2.02 Flare owns an invisible center object, so each live Flare uses
-- two of Bill's six pool units: three coexist and later triggers are rejected.
local frame=0
local peak=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 local age=frame-560
 emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200,
  b=age>=0 and age<84 and age%12<5},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('Player_X_Position',48);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  w('PlayerStatus',1);w('InvOwnedLo',9,3);w('InvSelected',3,3)
 end
 if frame>550 and frame<650 then
  local n=0;for i=0,9 do if r('RgShotType',i)==43 then n=n+1 end end
  peak=math.max(peak,n);assert(n<=3,'Source Flare limit never exceeds three')
 end
 if frame==650 then assert(peak==3,'Three Flares (six pool units with centers) can coexist: '..peak)
  print('PASS Bill Flare three-projectile source limit (six pool units) and later trigger rejection');emu.stop(0)
 end
end,emu.eventType.endFrame)
