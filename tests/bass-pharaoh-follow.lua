-- A controller-created balloon is checked on every update against the
-- independent 2.02 continuous-motion rule, expressed exactly in Q8.8.
local frame,age,checks=0,0,0
local pending,positive,negative,stationary,wrapped,scrolled
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function vx(s)local q=r('RgShotVXHi',s)*256+r('RgShotVXLo',s);return q>=32768 and q-65536 or q end
emu.addMemoryCallback(function()
 if frame<550 or r('CurrentBank')%128~=60 then return end
 local s=emu.getState()['cpu.x']
 local center=(r('Player_PageLoc')*256+r('Player_X_Position')+8)*256
 local pos=(r('RgShotPage',s)*256+r('RgShotX',s))*256+r('RgShotFracX',s)+vx(s)
 pos=math.max(center-2560,math.min(center+2560,pos))
 local movement=r('MmVX')+r('MmVX',1)*256+r('MmVX',2)*65536
 if movement>=8388608 then movement=movement-16777216 end
 local drift=0
 if movement>0 then drift=-160;positive=true
 elseif movement<0 then drift=160;negative=true
 elseif r('PlayerFacingDir')==1 and pos<center then drift=320;stationary=true
 elseif r('PlayerFacingDir')==2 and pos>center then drift=-320;stationary=true end
 pending={slot=s,pos=pos,drift=drift,y=(r('Player_Y_HighPos')*256+r('Player_Y_Position')-9)}
end,emu.callbackType.exec,L.BalloonFollow)
emu.addMemoryCallback(function()
 if not pending or r('CurrentBank')%128~=60 then return end
 local s=pending.slot
 local actual=(r('RgShotPage',s)*256+r('RgShotX',s))*256+r('RgShotFracX',s)
 assert(actual==pending.pos,'Balloon follows source drift/clamp to subpixel precision: '..actual..'/'..pending.pos)
 assert(vx(s)==pending.drift,'Balloon chooses source counter-drift/catch-up velocity')
 assert(r('RgShotYHigh',s)*256+r('RgShotY',s)==pending.y,'Balloon stays above the moving head')
 checks=checks+1;pending=nil
 if r('Player_PageLoc')>0 then wrapped=true end
 if r('ScreenLeft_X_Pos')~=128 or r('ScreenLeft_PageLoc')~=0 then scrolled=true end
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140 or(frame>=550 and age>=35 and age<90),
  left=frame>=550 and age>=110 and age<150,start=frame==200,b=frame>=550 and age>=10 and age<190},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',220);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  w('ScreenLeft_X_Pos',128);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',127);w('ScreenRight_PageLoc',1)
  w('PlayerFacingDir',1);w('PlayerStatus',1);w('InvOwnedLo',17,9);w('InvSelected',4,9);w('InvAmmo',112,148);w('InvDirty',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  return
 end
 age=age+1
 if age==205 then
  assert(checks>=100 and positive and negative and stationary,'Drift was checked while walking both ways and catching up at rest: '..checks)
  assert(wrapped and scrolled,'The same source trajectory survives page crossings and camera scrolling')
  print('PASS '..checks..' independently modeled Pharaoh balloon updates, fractional clamps, reversal, stationary catch-up, page crossing and scrolling');emu.stop(0)
 end
end,emu.eventType.endFrame)
