-- Real sword-beam input and enemy contact, with a flat-world fixture.
local frame,start,observed,pending=0,nil,0,0
local ready=false
-- These CPU addresses also execute unrelated code in other PRG banks.
-- Manual audio switches do not update foreground CurrentBank; track hardware
-- selection and interrupt depth before accepting a real fragment/render call.
local beamBank,beamSelect,beamDepth=nil,nil,0
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,v)beamBank=v%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,v)beamSelect=v%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if beamSelect==7 then beamBank=v%128 end end,emu.callbackType.write,0x8001)
end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()beamDepth=beamDepth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()beamDepth=beamDepth-1 end,emu.callbackType.exec,pc)end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function word(n)return r(n)+256*r(n,1)end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<160 and (frame-80)%20==0,start=frame==200,b=frame==560},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if not ready or frame<560 or beamBank~=4 or beamDepth~=0 then return end
 pending=4
end,emu.callbackType.exec,L.LinkBeamFragments)
emu.addMemoryCallback(function()
 if pending==0 or beamBank~=4 or beamDepth~=0 then return end
 local slot=r('RgSlot');local age=r('RgShotAge',slot);local quadrant=pending-1
 local d=5+math.floor(age*115/120)
 local x=r('RgShotX',slot)+256*r('RgShotPage',slot)-r('ScreenLeft_X_Pos')-256*r('ScreenLeft_PageLoc')
 local y=r('RgShotY',slot)+256*r('RgShotYHigh',slot)
 local wantx=(x+((quadrant&2)==0 and d or -d))%65536
 local wanty=(y+((quadrant&1)==0 and -d or d))%65536
 assert(word('R4')==wantx and word('R6')==wanty,'Each beam fragment has the source quadrant and diagonal travel at age '..age)
 pending=pending-1;observed=observed+1
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==4,'Link selected')
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('PlayerStatus',2);w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0);w('PlayerFacingDir',1)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_PageLoc',0);w('Enemy_X_Position',120)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0)
  ready=true
 end
 if frame>=550 and frame<620 then w('Enemy_X_Position',120);w('Enemy_Y_Position',184);w('Enemy_X_Speed',0) end
 for i=0,9 do
  if ready and frame>560 and r('RgShotType',i)==4 and r('RgShotImpact',i)>0 and not start then start=frame end
 end
 if start and frame==start+22 then
  assert(observed==84,'Four moving pieces survive exactly 21 updates: '..observed)
  for i=0,9 do assert(r('RgShotType',i)==0,'Beam expires after its source fragment travel') end
  print('PASS Link beam impact: native contact, four mirrored moving fragments, 115 speed and 40-pixel source lifetime');emu.stop(0)
 end
 if frame==700 then assert(false,'Beam did not hit the native enemy') end
end,emu.eventType.endFrame)
