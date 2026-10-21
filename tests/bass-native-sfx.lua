-- Real buster/jump inputs plus explicit effect-queue fixtures. Native MM3
-- track definitions specify channel ownership; the MM10 music image must
-- continue independently and be restored when each effect releases.
local frame=0
local seen={};local writes=0;local landed=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local cues={{frame=800,queue='Square1SoundQueue',value=16,track=22,mask=10},
 {frame=1000,queue='Square1SoundQueue',value=8,track=24,mask=12}, -- 2.02 selects MM6: triangle + noise.
 {frame=1200,queue='Square2SoundQueue',value=64,track=20,mask=2}}
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==240,b=frame==600,a=frame>=1400 and frame<1430},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()writes=writes+1 end,emu.callbackType.write,0x4000,0x400f)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 and frame<1600 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
 end
 if frame==602 then
  assert(r('BassAudioMask')==2,'Native buster owns pulse 2')
  assert(r('Square1SoundBuffer')&32==0,'Buster does not also play the generic fireball cue')
  seen[21]=true
 end
 for _,cue in ipairs(cues) do
  if frame==cue.frame then w(cue.queue,cue.value) end
  if frame==cue.frame+2 then
   assert(r('BassAudioMask')==cue.mask,'Native effect track '..cue.track..' owns its source channels')
   seen[cue.track]=true
  end
  if frame==cue.frame+160 then
   assert(r('BassAudioMask')==0,'Native cue releases its channels')
   for i=0,15 do assert(r('GuestNativeApu',i)==r('XgMusicApu',i),'Music register restored after native effect') end
  end
 end
 if frame>1400 and frame<1550 and r('BassAudioRequest')==19 then
  assert(r('BassAudioMask')==10,'Landing uses native pulse 2 and noise')
  landed=true
 end
 if frame==1600 then
  assert(landed,'A real jump/landing queues the source landing cue')
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',r('Player_X_Position'));w('Enemy_PageLoc',r('Player_PageLoc'))
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
  w('PlayerStatus',0);w('InjuryTimer',0);w('Player_State',0)
 end
 if frame>=1602 and frame<=1610 and r('MmDeathFlag')~=0 and r('MmDeathAge')>0 then
  assert(r('BassAudioMask')==3,'Death burst has its native two-pulse cue: frame '..frame..' mask '..r('BassAudioMask')..' request '..r('BassAudioRequest')..' death age '..r('MmDeathAge')..' sound '..r('BassSourceId')..' kill '..r('BassSourceKill'))
  seen[23]=true
 end
 if frame==1620 then
  for _,id in ipairs({20,21,22,23,24}) do assert(seen[id],'Native cue was exercised: '..id) end
  assert(writes>200,'Effects and music reached the physical APU')
  print('PASS Bass native buster, hit, damage, extra-life, actual landing and death effects with source channel masks and music restoration');emu.stop(0)
 end
end,emu.eventType.endFrame)
