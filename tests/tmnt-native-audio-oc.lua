-- Real cold menu entry, then explicitly arranged music/SFX/pause requests.
local wall,entered=0,false
local index,age=1,0
local song,sourceFrame=nil,0
local saved,coreCycles=nil,nil
local actual={}
local checked,hardware,borrowed,irq,drumActive,drumHeld=0,0,0,0,0,0
local totalCycles,peakCycles=0,0
local fxSeen,pausedAt,resumed,silenced,restarted=false,nil,false,false,false
local cleanup,cleanupAge,cleanupCase=nil,0,1
local transitions={{0,1,'Mario'},{2,1,'Samus'},{19,0,'title'}}
local transitionChecks=0
local vanillaDac=nil
local cases={{1,0,2,600},{2,0,5,600},{4,0,3,600},{8,0,10,600},
 {16,0,8,600},{32,0,1,600},{64,0,11,600},{0,1,15,1000},
 {0,2,13,1000},{0,4,12,1000},{0,8,12,1000},{0,16,13,1000},
 {0,32,12,1000},{0,64,6,600}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local protect={'R0','R1','R2','R3','R4','R5','R6','R7','CurrentBank',
 'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','GameEngineSubroutine'}
local function snapshot()
 local q={};for _,n in ipairs(protect)do q[n]=r(n)end
 -- The fourteen-byte decoder slab is persistently owned by audio, as it was
 -- before this native driver. Every other zero-page byte must be untouched.
 for a=0,255 do
  if a<L.XgAudioPtr or a>=L.XgAudioZeroPageEnd then q[a]=emu.read(a,emu.memType.nesDebug)end
 end
 return q
end
emu.addMemoryCallback(function(at,v)actual[at-0x4000]=v end,emu.callbackType.write,0x4000,0x400f)
emu.addMemoryCallback(function()
 if cleanup=='cut' and r('SelectedCharacter')==0 and r('OperMode')==1 and bank(L.StrWave)==TMNT_VANILLA_MUSIC_BANK then
  vanillaDac=emu.getState()['cpu.y']
 end
end,emu.callbackType.exec,L.StrWave)
emu.addMemoryCallback(function()if saved then irq=irq+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()
 if not entered or bank(L.TnAudioUpdate)~=125 then return end
 assert(not saved,'One native adapter update at a time')
 saved=snapshot();coreCycles=emu.getState()['cpu.cycleCount']
end,emu.callbackType.exec,L.TnAudioUpdate)
emu.addMemoryCallback(function()
 if not entered then return end
 song=r('TnAudioSong');sourceFrame=0
 assert(song==(cleanup and 2 or cases[index][3]),'Area/event routes to the assigned original TMNT song')
end,emu.callbackType.exec,L.TnMusicInitCall)
emu.addMemoryCallback(function()if entered then sourceFrame=sourceFrame+1 end end,emu.callbackType.exec,L.TnMusicPlayCall)
emu.addMemoryCallback(function()
 if not entered or not saved then return end
 local after=snapshot();for k,v in pairs(saved)do assert(after[k]==v,'Restore interrupted state '..tostring(k))end
 assert(bank(0xc000)==38,'Restore the caller audio bank before KbAudioFamily')
 borrowed=borrowed+1;saved=nil
 local spent=emu.getState()['cpu.cycleCount']-coreCycles;totalCycles=totalCycles+spent;peakCycles=math.max(peakCycles,spent)
 if song then
  local expected=assert(TMNT_GOLDEN[song][sourceFrame+1],'Bounded original reference image')
  for i=0,15 do assert(r('GuestNativeApu',i)==expected:byte(i+1),'Original TMNT music image song='..song..' frame='..sourceFrame..' register='..i);checked=checked+1 end
  for i=0,3 do assert(r('TnAudioDmcRegs',i)==expected:byte(i+17),'Original virtual DMC parameters')end
 end
end,emu.callbackType.exec,L.ExpandedAudioDecoded)
local function menu()
 if wall<60 or wall%12~=0 then return{}end
 if r('CrossoverMenuState')==2 then
  local i=r('CrossoverMenuIndex')
  if i<12 then return{down=true}elseif i~=18 then return{right=true}
  elseif r('TnVariant')~=0 then return{select=true}else return{a=true}end
 end
 return{start=true}
end
local function done()
 assert(fxSeen and pausedAt and resumed and silenced and restarted,'Shared effects, pause/resume, silence/restart exercised')
 assert(irq>0 and drumActive>100 and drumHeld>100 and checked>100000 and borrowed>9000,'Sustained original music, native DMC and nested IRQ coverage')
 assert(transitionChecks==#transitions,'Every arranged active-DMC transition completed')
 local f=assert(io.open(TEST_DIR..'proof.json','w'))
 f:write(string.format('{"passed":true,"audio_cases":%d,"active_drum_transition_cases":%d,"source_register_comparisons":%d,"hardware_register_comparisons":%d,"borrowed_state_checks":%d,"nested_IRQs":%d,"active_DMC_frames":%d,"held_DAC44_frames":%d,"total_adapter_cycles_inclusive":%d,"peak_adapter_cycles_inclusive":%d,"frames":%d,"scope":"Real cold menu, then explicitly arranged native audio requests. Source images, mapped DMC parameters and physical DAC44, mixer restoration, pause/silence, nested IRQ and borrowed-state checks. Active drums are cut during arranged Mario, Samus and title transitions; final buffered bits drain, then Mario owns its original DAC counter while Samus/title hold zero. Separate from campaign proof."}',#cases,transitionChecks,checked,hardware,borrowed,irq,drumActive,drumHeld,totalCycles,peakCycles,wall));f:close();emu.stop(0)
end
emu.addEventCallback(function()emu.setInput(entered and{}or menu(),0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==19 and r('TnVariant')==0,'Actual menu selected Leonardo')
   entered=true;w('AreaMusicQueue',cases[1][1]);w('EventMusicQueue',cases[1][2])
  end
  assert(wall<1200,'Real menu entry bounded');return
 end
 age=age+1
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('GameTimerDisplay',4);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 local native=r('SelectedCharacter')==19 and r('OperMode')==1
 if native and song and r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 then
  for reg=0,15 do
   local noise=reg>=12 and(r('GuestMixMask')&8)~=0
   if reg~=9 and reg~=13 and not noise then
    assert(actual[reg]==r('GuestNativeApu',reg),'Mixer publishes/restores original register '..reg);hardware=hardware+1
   end
  end
 end
 local state=emu.getState()
 if native and r('BassDmcActive')==4 then
  assert(state['apu.dmc.sampleAddr']==L.TnMusicDpcm and state['apu.dmc.sampleLength']==129,'Actual DMC fixed sample and complete length')
  assert(state['apu.dmc.timer.period']==53 and not state['apu.dmc.irqEnabled']and not state['apu.dmc.loopFlag'],'Exact native rate15, no IRQ/loop')
  drumActive=drumActive+1
 end
 if native and r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 and r('TnAudioDacHold')==44 and state['apu.dmc.bytesRemaining']==0 and state['apu.dmc.bufferEmpty']and state['apu.dmc.silenceFlag']then
  assert(state['apu.dmc.outputLevel']==44,'Finished source drum retains DAC44: actual='..state['apu.dmc.outputLevel']..' song='..tostring(song)..' sourceFrame='..sourceFrame..' age='..age..' bytes='..state['apu.dmc.bytesRemaining']..' bits='..state['apu.dmc.bitsRemaining']);drumHeld=drumHeld+1
 end
 if cleanup then
  cleanupAge=cleanupAge+1
  if cleanup=='wait' then
   assert(cleanupAge<200,'Wait for an actual active source drum')
   if r('BassDmcActive')==4 and state['apu.dmc.bytesRemaining']>0 then
    local target=transitions[cleanupCase]
    w('SelectedCharacter',target[1]);w('OperMode',target[2]);w('AreaMusicQueue',target[2]==1 and 1 or 0)
    cleanup='cut';cleanupAge=0
   end
  elseif cleanupAge==3 then
   local target=transitions[cleanupCase]
   assert(r('BassDmcActive')~=4 and r('TnDmcDrain')==0,'Native owner and pending drain released for '..target[3])
   assert(state['apu.dmc.bytesRemaining']==0 and state['apu.dmc.bufferEmpty']and state['apu.dmc.silenceFlag'],'Final buffered sample bits drained for '..target[3])
   local expectedDac=target[3]=='Mario' and assert(vanillaDac,'Original Mario music writes its own DAC counter')or 0
   assert(state['apu.dmc.outputLevel']==expectedDac,'No native held DAC after '..target[3]..' transition: actual='..state['apu.dmc.outputLevel']..' expected='..expectedDac)
   assert(r('XgAudioCharacter')~=253,'Leaving native music invalidates its marker')
   transitionChecks=transitionChecks+1;cleanupCase=cleanupCase+1
   if cleanupCase>#transitions then done();return end
   w('SelectedCharacter',19);w('OperMode',1);w('AreaMusicQueue',1);song=nil
   cleanup='wait';cleanupAge=0
  end
  assert(wall<12500,'Native audio transition matrix bounded');return
 end
 if index==1 then
  if age==100 then w('Square1SoundQueue',2);w('NoiseSoundQueue',1)end
  if age>100 and age<140 and r('GuestMixMask')~=0 then fxSeen=true end
  if age==200 then pausedAt=sourceFrame;w('GamePauseStatus',1)end
  if age==220 then assert(sourceFrame==pausedAt and r('BassDmcActive')==0 and state['apu.dmc.outputLevel']==0,'Pause holds native state and releases sample/DAC')end
  if age==230 then w('GamePauseStatus',0)end
  if age==245 then assert(sourceFrame>pausedAt,'Unpause resumes original engine');resumed=true end
  if age==350 then w('AreaMusicQueue',128)end
  if age==370 then assert(r('TnAudioSilenced')==1 and r('GuestNativeEnable')==0 and r('BassDmcActive')==0,'Silence stops native voices/DMC');silenced=true end
  if age==390 then w('AreaMusicQueue',1)end
  if age==410 then assert(song==2 and sourceFrame<25,'Area request restarts after silence');restarted=true end
 end
 if age>=cases[index][4]then
  assert(song==cases[index][3],'Completed requested original song case')
  index=index+1;age=0
  if index>#cases then
   cleanup='wait';cleanupAge=0;song=nil;w('AreaMusicQueue',1);return
  end
  song=nil;w('AreaMusicQueue',cases[index][1]);w('EventMusicQueue',cases[index][2])
 end
 assert(wall<12500,'Native music matrix bounded')
end,emu.eventType.endFrame)
