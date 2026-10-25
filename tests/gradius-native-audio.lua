-- Real cold menu entry, then an explicit stationary audio-request arena.
-- The arena keeps terrain/player hazards out of long music comparisons. It is
-- not a controller clear, pickup or natural campaign proof.
local wall,t,entered=0,0,false
local currentSong,sourceFrame=nil,0
local before,requested={},false
local actual={};local checked,hardware,borrowChecks=0,0,0
local coreCycles,totalCycles,peakCycles=nil,0,0
local fxSeen,paused,resumed=false,false,false
local cases={{1,0,3,540},{2,0,6,540},{4,0,4,540},{8,0,9,540},
 {16,0,5,540},{32,0,1,540},{64,0,10,540},{0,1,13,1000},
 {0,2,13,1000},{0,4,14,1000},{0,8,14,1000},{0,64,10,540}}
local index,age=1,0
local borrowed={0x15,0xdd,0xde,0xf6,0xf7,0xfa,0xfb}
local protected={'R0','R1','R2','R3','R4','R5','R6','R7',
 'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','GameEngineSubroutine'}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function cycle()return emu.getState()['cpu.cycleCount']end
local function snapshot()
 local result={}
 for _,a in ipairs(borrowed)do result[a]=emu.read(a,emu.memType.nesDebug)end
 for _,n in ipairs(protected)do result[n]=r(n)end
 return result
end
emu.addMemoryCallback(function(address,value)actual[address-0x4000]=value end,emu.callbackType.write,0x4000,0x400f)
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=0x7a then return end
 coreCycles=cycle();before=snapshot()
end,emu.callbackType.exec,L.GradiusAudioUpdate)
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=0x7a then return end
 currentSong=r('RgAudioSong');sourceFrame=0
 print('AUDIO init case='..index..' age='..age..' song='..currentSong..' expected='..cases[index][3]..' area='..r('AreaMusicQueue')..' event='..r('EventMusicQueue'))
 assert(currentSong==cases[index][3],'Every area/event uses its assigned source song case='..index..' age='..age..' actual='..currentSong..' expected='..cases[index][3])
end,emu.callbackType.exec,L.VgEC48)
emu.addMemoryCallback(function()
 if entered and bank(0xa000)==0x7a then sourceFrame=sourceFrame+1 end
end,emu.callbackType.exec,L.VgED30)
emu.addMemoryCallback(function()
 if not entered or not coreCycles then return end
 local spent=cycle()-coreCycles;totalCycles=totalCycles+spent;peakCycles=math.max(peakCycles,spent);coreCycles=nil
 local after=snapshot()
 for k,v in pairs(before)do assert(after[k]==v,'Audio restores interrupted byte '..tostring(k))end
 borrowChecks=borrowChecks+1
 if currentSong then
  local expected=assert(GRADIUS_GOLDEN[currentSong][sourceFrame+1],'Bounded original music comparison')
  for reg=0,15 do
   local value=expected:byte(reg+1)
   assert(r('GuestNativeApu',reg)==value,'Original source APU image song='..currentSong..' tick='..sourceFrame..' register='..reg)
   checked=checked+1
  end
 end
end,emu.callbackType.exec,L.ExpandedAudioDecoded)
local function stationary()
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',48);w('Player_Y_HighPos',1)
 w('VvObjX',40);w('VvObjY',48)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('GameEngineSubroutine',8);w('ScrollLock',1);w('TimerControl',0)
 -- Keep the stationary comparison from generating its own unrelated hurry cue.
 w('GameTimerDisplay',4);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
end
emu.addEventCallback(function()
 local buttons={}
 if not entered and wall>=60 and wall%12==0 then
  if r('CrossoverMenuState')==2 then
   local item=r('CrossoverMenuIndex')
   if item<12 then buttons.down=true elseif item~=17 then buttons.right=true
   elseif r('VvVariant')~=0 then buttons.select=true else buttons.a=true end
  else buttons.start=true end
 end
 emu.setInput(buttons,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==18 and r('VvVariant')==0,'Cold entry selected original Vic Viper')
   entered=true;stationary()
   w('AreaMusicQueue',cases[1][1]);w('EventMusicQueue',cases[1][2])
  end
  assert(wall<1200,'Bounded real-menu entry');return
 end
 t=t+1;age=age+1
 if currentSong then
  for reg=0,15 do
   -- Native NES pulses stay under the source driver while world pulse cues
   -- use MMC5. Noise may be temporarily owned by a real brick cue.
   local borrowedNoise=reg>=12 and(r('GuestMixMask')&8)~=0
   if reg~=9 and reg~=13 and not borrowedNoise and r('GamePauseStatus')%2==0 then
    assert(actual[reg]==r('GuestNativeApu',reg),'Mixer publishes/restores native register '..reg)
    hardware=hardware+1
   end
  end
 end
 stationary()
 if index==1 then
  if age==100 then w('Square1SoundQueue',2);w('NoiseSoundQueue',1)end
  if age>100 and age<140 and r('GuestMixMask')~=0 then fxSeen=true end
  if age==200 then paused=sourceFrame;w('GamePauseStatus',1)end
  if age==230 then assert(sourceFrame==paused,'Pause holds original driver state');w('GamePauseStatus',0)end
  if age==240 then assert(sourceFrame>paused,'Unpause resumes original driver');resumed=true end
 end
 if age>=cases[index][4]then
  assert(currentSong==cases[index][3],'Case completed using the assigned original song')
  index=index+1;age=0
  if index>#cases then
   assert(fxSeen and paused and resumed,'Real shared effects, pause and resume were exercised')
   assert(checked>100000 and hardware>90000 and borrowChecks>7000,'Sustained native APU and interrupted-state comparisons')
   local f=assert(io.open(OUTPUT..'proof.json','w'))
   f:write(string.format('{"passed":true,"audioCases":%d,"sourceRegisterComparisons":%d,"hardwareRegisterComparisons":%d,"borrowedStateChecks":%d,"totalAudioCycles":%d,"peakAudioCycles":%d,"scope":"Real cold menus plus explicit stationary audio-request arena; original song routing, source register image, mixer restoration, pause and borrowed zero page. Campaign proof is separate."}',#cases,checked,hardware,borrowChecks,totalCycles,peakCycles));f:close()
   print('PASS linked Gradius native music and common mixer');emu.stop(0);return
  end
  currentSong=nil
  w('AreaMusicQueue',cases[index][1]);w('EventMusicQueue',cases[index][2])
 end
 assert(wall<11000,'Bounded source-audio arena')
end,emu.eventType.endFrame)
