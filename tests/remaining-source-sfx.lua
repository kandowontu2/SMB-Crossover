-- Read-only source register comparisons after explicit audio-request fixtures.
-- Controller startup and uninterrupted native music exercise the real mixer.
local expected=dofile(TEST_DIR..'fixtures/remaining-source-sfx.lua')
local frame,case,phase,checks=0,0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if case==0 or r('AvAudioChar')~=3 then return end
 if r('AvAudioId')==case then
  phase=phase+1;local spec=expected[case];local image=assert(spec.frames[phase],'Source stream cannot exceed captured duration')
  assert(r('AvAudioMask')==spec.mask,'Only source effect channels are claimed')
  for a=0,15 do
   if spec.mask&(1<<math.floor(a/4))~=0 then
    assert(r('GuestNativeApu',a)==image[a+1],'Exact source register '..case..'/'..phase..'/'..a);checks=checks+1
   else assert(r('GuestNativeApu',a)==r('AvAudioMusic',a),'Unclaimed music voice is preserved')end
  end
 end
end,emu.callbackType.exec,L.RemainingAudioFrameReady)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 for i=0,5 do w('Enemy_Flag',0,i)end
 if (frame-550)%200==0 then
  if case>0 then assert(phase==#expected[case].frames,'Complete source effect duration')end
  case=case+1;phase=0
  if case>#expected then
   assert(checks>1000 and r('GameEngineSubroutine')==8,'All effects are checked and gameplay remains live')
   print('PASS '..#expected..' remaining source NSF attack effects: '..checks..' exact register comparisons, channel ownership, complete durations and native music restoration');emu.stop(0);return
  end
  w('AvAudioRequest',case)
 end
end,emu.eventType.endFrame)
