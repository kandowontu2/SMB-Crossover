-- Fresh B while the first small shot is still live must allow the separate
-- balloon. Charged release clamps low energy; stars do not spend it.
local frame,age,phase=0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function count(t)local n=0;for i=0,9 do if r('RgShotType',i)==t then n=n+1 end end;return n end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvSelected',4,9);w('InvAmmo',phase==0 and 112 or phase==1 and 8 or 0,148);w('InvDirty',1)
 w('StarInvincibleTimer',phase==2 and 30 or 0);w('SsBodyStop',0);w('SsFreeze',0)
 age=0
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=frame>=550 and((age>=10 and age<16)or(age>=22 and age<95))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if age==29 then
  assert(count(12)==1 and count(18)==1,'Charging can restart while the first small shot remains in flight')
  assert(r('InvAmmo',148)==(phase==0 and 108 or phase==1 and 4 or 0),'An independent balloon spends no energy until release')
 end
 if age==100 then
  assert(count(14)==1 and count(18)==0,'A full Pharaoh release works at low stock and during star power')
  assert(r('InvAmmo',148)==(phase==0 and 100 or 0),'Charged release clamps low stock; stars preserve zero ammunition')
 end
 if age==130 then
  phase=phase+1
  if phase==3 then print('PASS separate Pharaoh shot/balloon allowance, low-stock charged release and star-powered infinite ammunition');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
