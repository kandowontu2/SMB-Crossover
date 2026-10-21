-- Real Water Shield input; fixed-bank sample playback, DMA-safe controller
-- reads and independent music, followed by selection/pause/death cleanup.
local frame,age,phase=0,0,0
local activeFrames,started,lastDac,inputChecks=0,false,0,0
local configured={};local lastExpected
local latchedExpected
local checkedPhases,checkedInputs={},{}
local deathStart,deathVerified
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',1);w('InvOwnedLo',133,9);w('InvSelected',7,9);w('InvAmmo',112,151);w('InvDirty',1)
 w('SsFreeze',0);w('SsBodyStop',0);w('SsWaterExpand',0);w('GamePauseStatus',0);w('GamePauseTimer',0)
 age=0;activeFrames=0;started=false;configured={};lastExpected=nil;latchedExpected=nil
 deathStart=nil;deathVerified=false
end
emu.addMemoryCallback(function(address,value)
 if address==0x4011 then lastDac=value end
 if frame>=550 and address>=0x4010 and address<=0x4013 then configured[address]=value end
end,emu.callbackType.write,0x4010,0x4013)
emu.addMemoryCallback(function(address,value)
 if frame>=550 and value&1==0 then latchedExpected=lastExpected end
end,emu.callbackType.write,0x4016)
emu.addMemoryCallback(function()
 if frame<550 then return end
 if r('BassDmcActive')~=0 and latchedExpected then
  assert(r('SavedJoypad1Bits')==latchedExpected,'Completed DMA-era read matches its latched input: '..r('SavedJoypad1Bits')..'/'..latchedExpected..' phase '..phase..' age '..age)
  inputChecks=inputChecks+1
  checkedPhases[phase]=(checkedPhases[phase]or 0)+1
  checkedInputs[latchedExpected]=true
 end
end,emu.callbackType.exec,L.OAMandReadJoypad_RTS)
emu.addEventCallback(function()
 local playing=frame>=550
 local input={down=frame==80,right=frame==100 or frame==120 or frame==140 or(playing and age>=22 and age<37),
  left=playing and phase==0 and age>=45 and age<60,
  start=frame==200 or(playing and phase==2 and((age>=35 and age<41)or(age>=105 and age<111))),
  select=playing and phase==1 and age>=35 and age<41,
  a=playing and phase==0 and age>=25 and age<31,
  b=playing and age>=10 and age<16}
 emu.setInput(input,0)
 if playing then
  lastExpected=(input.a and 128 or 0)+(input.b and 64 or 0)+(input.select and 32 or 0)+(input.start and 16 or 0)
    +(input.up and 8 or 0)+(input.down and 4 or 0)+(input.left and 2 or 0)+(input.right and 1 or 0)
 end
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if phase~=3 or age<35 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if r('BassDmcActive')~=0 then
  started=true;activeFrames=activeFrames+1
  assert(configured[0x4010]==14,'Source sample uses native NTSC DMC rate 14 without IRQ or looping')
  assert(configured[0x4012]==math.floor((L.BassWaterDpcm-0xc000)/64),'DMC points into fixed ROM')
  assert(configured[0x4013]==math.floor((L.BassWaterDpcmEnd-L.BassWaterDpcm-1)/16),'DMC uses the complete source clip')
  if age>=20 then for register=0,15 do
   local sound=r('BassAudioMask')&(1<<math.floor(register/4))~=0
   assert(r('GuestNativeApu',register)==r(sound and 'BassAudioSfxApu' or 'XgMusicApu',register),'Water sample preserves music and any concurrent landing effect')
  end end
 end
 if phase==0 and age==90 then
  assert(started and activeFrames>=60 and activeFrames<=67,'Complete source sample plays for its expected duration: '..activeFrames)
  assert(r('BassDmcActive')==0 and emu.read(0x4015,emu.memType.nesDebug)&16==0 and lastDac==0,'Completed sample stops and restores the silent DAC bias')
 end
 if phase==1 and age==50 then
  assert(started and activeFrames>=15 and r('InvSelected',9)==0,'Select cycles back to normal during sample playback')
  assert(r('BassDmcActive')==0 and emu.read(0x4015,emu.memType.nesDebug)&16==0 and lastDac==0,'Weapon selection cancels the actual DMC channel')
 end
 if phase==2 and age==50 then
  assert(started and r('GamePauseStatus')&1~=0,'Pause occurs during actual sample playback')
  assert(r('BassDmcActive')==0 and emu.read(0x4015,emu.memType.nesDebug)&16==0 and lastDac==0,'Pausing releases DMC and DAC bias')
 end
 if phase==3 and age==35 then
  w('PlayerStatus',0);w('InjuryTimer',0);w('StarInvincibleTimer',0)
  -- Armored Beetle survives the orbiting shield until real body contact.
  w('Enemy_Flag',1);w('Enemy_ID',2);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',r('Player_X_Position'));w('Enemy_PageLoc',r('Player_PageLoc'));w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
 end
 if phase==3 and r('MmDeathFlag')~=0 then
  if not deathStart then deathStart=frame end
  if frame==deathStart+2 then
   assert(started and r('BassDmcActive')==0 and lastDac==0 and r('BassAudioMask')==3,
    'Real body-contact death cancels water and plays the source death effect')
   deathVerified=true
  end
 end
 if age==(phase==2 and 130 or 100)then
  phase=phase+1
  if phase==4 then
   assert(deathVerified,'A real enemy collision interrupts Water Shield within the bounded scenario')
   for p=0,3 do assert((checkedPhases[p]or 0)>=5,'Completed controller reads are checked in every DMA scenario')end
   assert(checkedInputs[0]and checkedInputs[64]and checkedInputs[1]and checkedInputs[2],
    'DMA playback exercises released, firing, right and left controller packets')
   print('PASS Water Shield source DPCM duration/configuration, '..inputChecks..' DMA-safe controller reads, intact music and selection/pause/death cleanup');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
