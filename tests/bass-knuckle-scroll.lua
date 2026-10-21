-- Native 1-1 traversal with initial inventory fixture and live enemy/block
-- updates. Controller input supplies moving fire, jumping and weapon cycles.
local frame,age,jumpAge,pipe=0,0,-1,1
local pipes={448,608,736,912}
local knuckles=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
emu.addEventCallback(function()
 local moving=frame>=580 and x()<990
 if frame>=580 then
  while pipes[pipe] and x()>pipes[pipe]+32 do pipe=pipe+1;jumpAge=-1 end
  if pipes[pipe] and r('Player_State')==0 and x()>=pipes[pipe]-42 then jumpAge=0 end
 end
 local a=jumpAge>=0 and jumpAge<36 and jumpAge~=17
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140 or moving,start=frame==200,
  a=a,b=frame>=580 and age%24<6,select=frame>=580 and age%90>=40 and age%90<46},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9);w('InvSelected',3,9);w('InvDirty',1)
  w('InjuryTimer',255)
 end
 if frame<550 then return end
 age=age+1
 if jumpAge>=0 then jumpAge=jumpAge+1 end
 w('InjuryTimer',255)
 for i=0,9 do if r('RgShotType',i)==11 then knuckles=knuckles+1 end end
 assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Native scrolling fire preserves sky: frame '..frame..' x '..x()..' selected '..r('InvSelected',9))
 if frame==2100 then
  assert(x()>960 and knuckles>0,'Native level traversal exercised scrolling and Knuckle: x='..x()..' pipe='..pipe..' shots='..knuckles..' y='..r('Player_Y_Position')..' state='..r('Player_State'))
  print('PASS native 1-1 scrolling, repeated weapon cycles, block/enemy updates and Knuckle preserve sky');emu.stop(0)
 end
end,emu.eventType.endFrame)
