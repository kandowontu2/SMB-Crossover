-- Cold real-menu entry, then explicitly arranged native audio request cases.
local wall,entered,step=0,false,0
local opened,finished=nil,false
local interrupts=0
local trace=assert(io.open(TEST_DIR..'audio.csv','w'))
trace:write('call,state,sourceZP,image,hardware\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local protect={'R0','R1','R2','R3','R4','R5','R6','R7','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','GameEngineSubroutine'}
local function snapshot()
 local q={}
 for _,n in ipairs(protect)do q[n]=r(n)end
 for _,a in ipairs({0x1e,0x2e,0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb})do q[a]=emu.read(a,emu.memType.nesDebug)end
 return q
end
local function hex(n,count)
 local q={};for i=0,count-1 do q[#q+1]=string.format('%02x',r(n,i))end;return table.concat(q)
end
local returnHooks={}
emu.addMemoryCallback(function(_,v)
 if opened then opened.writes[#opened.writes+1]=string.format('%04x:%02x',_,v)end
end,emu.callbackType.write,0x4000,0x4015)
emu.addMemoryCallback(function()if opened then interrupts=interrupts+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()
 if not entered or finished then return end
 assert(not opened,'Samus audio has one native entry at a time')
 local group=step//512;local age=step%512
 w('FrameCounter',step);w('PlayerStatus',group%3)
 w('AreaMusicQueue',age==0 and 2^group or 0)
 w('EventMusicQueue',age==256 and 2^group or 0)
 w('Square1SoundQueue',age%5==0 and 2^((age+group)%8)or 0)
 w('SmSfx',age%3==0 and 2^((age//3+group)%7)or 0)
 w('GamePauseStatus',age>=400 and age<404 and 1 or 0)
 local sp=emu.getState()['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 opened={saved=snapshot(),sp=(sp+2)%256,pc=pc,writes={}}
 if not returnHooks[pc]then
  returnHooks[pc]=true
  emu.addMemoryCallback(function()
   if not opened or opened.pc~=pc or emu.getState()['cpu.sp']~=opened.sp then return end
   local after=snapshot()
   for k,v in pairs(opened.saved)do assert(after[k]==v,'Audio restores interrupted state '..tostring(k))end
   trace:write(table.concat({step,hex('SmAudioRam',0x8e),hex('SmAudioZp',12),hex('GuestNativeApu',16),table.concat(opened.writes,';')},',')..'\n')
   opened=nil;step=step+1
   if step==4096 then finished=true end
  end,emu.callbackType.exec,pc)
 end
end,emu.callbackType.exec,L.SamusAudioUpdate)
emu.addEventCallback(function()
 local b={}
 if not entered and wall>=60 and wall%12==0 then
  if r('CrossoverMenuState')==2 then
   if r('CrossoverMenuIndex')~=2 then b.right=true else b.a=true end
  else b.start=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==2,'Actual menu selected Samus');entered=true
  end
  assert(wall<1200,'Cold entry is bounded');return
 end
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('GameTimerDisplay',4);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 if finished then
  assert(not opened and step==4096,'Every requested native audio call returned')
  assert(interrupts>0,'Nested mapper IRQ exercised during audio')
  trace:close();local f=assert(io.open(TEST_DIR..'result.json','w'))
  f:write('{"passed":true,"audio_calls":'..step..',"nested_IRQs":'..interrupts..',"frames":'..wall..',"actual_menu_entry":true,"arranged_audio_requests":true}\n');f:close();emu.stop(0)
 end
 assert(wall<12000,'Native audio matrix is bounded')
end,emu.eventType.endFrame)
