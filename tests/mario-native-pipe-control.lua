-- Independent original-Mario pipe clamp control. Enemy suppression makes this
-- an environment fixture, not an accepted ordinary-controller level clear.
local frame,clamp=0,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({start=frame==240,right=frame>=620 and frame<1080},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=590 then for i=0,5 do emu.write(L.Enemy_Flag+i,0,emu.memType.nesDebug)end end
 if frame>=1000 and frame<=1080 then
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  assert(r('SelectedCharacter')==0 and r('GameEngineSubroutine')==8,'Original Mario remains playable')
  assert(x>400 and x<448,'Original Mario is held outside the first real pipe')
  if clamp then assert(x==clamp,'Original Mario does not creep through the real pipe')else clamp=x end
 end
 if frame==1080 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-mario-native-pipe-control.json','w'))
  f:write('{"nativeMarioClampX":'..clamp..',"pipeLeftX":448,"stableFrames":81}\n');f:close()
  print('PASS independent original-Mario first-pipe clamp, x='..clamp..',81stable frames');emu.stop(0)
 end
end,emu.eventType.endFrame)
