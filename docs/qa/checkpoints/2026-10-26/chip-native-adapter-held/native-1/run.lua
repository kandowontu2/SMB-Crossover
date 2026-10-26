VEHICLE_AUDIO_CONFIG={["nmi"]=58166,["nmi_return"]=58383,["smc"]={354,362,377,364,365},["stack_floor"]=123,["stack_start"]=90,["music"]=0}
-- Current-hash bank/five-SMC/stack/visible-scroll and hardware CHR guards.
local C=assert(VEHICLE_AUDIO_CONFIG)
local wall,nmis,windows,stackWrites,minSP,captures=0,0,0,0,255,0
local saved=nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function active()return r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local function storeAt(pc,target)
 return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256
end
local function bankWindow(pc,target,shadow)
 if storeAt(pc,target)then return storeAt(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and storeAt(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and storeAt(pc+2,target)and storeAt(pc-3,shadow)
end
emu.addMemoryCallback(function()
 if not active()then return end
 assert(bank(L.NonMaskableInterrupt)==127,'Bound actual fixed NMI bank')
 local s=emu.getState();local sp=s['cpu.sp']
 saved={a=bank(0xa000),c=bank(0xc000),fields={},sp=sp,cpu_a=s['cpu.a'],sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127}
 local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 saved.aw=saved.a~=saved.sa and bankWindow(pc,0x5115,L.CurrentBank)
 saved.cw=saved.c~=saved.sc and bankWindow(pc,0x5116,L.CurrentBankC)
 for _,at in ipairs(C.smc)do saved.fields[#saved.fields+1]=emu.read(at,emu.memType.nesDebug)end
 nmis=nmis+1;minSP=math.min(minSP,sp)
 assert(sp>=C.stack_floor,'NMI entry retains copied-code stack margin')
end,emu.callbackType.exec,C.nmi)
emu.addMemoryCallback(function()
 if not saved then return end
 assert(bank(0xa000)==(saved.aw and saved.sa or saved.a)and bank(0xc000)==(saved.cw and saved.sc or saved.c),'Audio NMI restores real foreground banks')
 assert((r('CurrentBank')&127)==saved.sa and(r('CurrentBankC')&127)==saved.sc,'Audio NMI restores bank shadows')
 assert(emu.getState()['cpu.a']==saved.cpu_a and emu.getState()['cpu.sp']==saved.sp,'Audio NMI restores A and stack')
 for i,at in ipairs(C.smc)do assert(emu.read(at,emu.memType.nesDebug)==saved.fields[i],'Audio NMI preserves every SMC operand')end
 if saved.aw or saved.cw then windows=windows+1 end
 saved=nil
end,emu.callbackType.exec,C.nmi_return)
local function stackGuard(at,value)
 if not active()then return end
 local sp=emu.getState()['cpu.sp']
 stackWrites=stackWrites+1
 if at==0x100+sp then
  local nextSP=(sp-1)%256
  assert(nextSP>=C.stack_floor,'Actual CPU stack does not cross copied SMC code')
  minSP=math.min(minSP,nextSP)
 end
end
-- Every descending push crosses this first safe byte before reaching copied
-- code. The lower-page guard also catches an invalid direct TXS below it.
-- Avoid callbacks on legitimate high-frequency SMC operand stores themselves.
emu.addMemoryCallback(stackGuard,emu.callbackType.write,0x100+C.stack_floor)
emu.addMemoryCallback(stackGuard,emu.callbackType.write,0x100,0x100+C.stack_start-1)
emu.addMemoryCallback(function(at,value)
 if not active()or r('DisableScreenFlag')~=0 then return end
 local s=emu.getState();local scan=s['ppu.scanline'];local rendering=(r('Mirror_PPUMASK')&24)~=0
 assert(not(rendering and scan>=32 and scan<240),'No music-induced visible world scroll/address write')
end,emu.callbackType.write,0x2005,0x2006)
-- CHR bytes are unchanged; no CHR observer or CHR verdict in this audio-only control.
emu.addEventCallback(function()
 wall=wall+1
 if C.music==1 and(wall==900 or wall==1800 or wall==5000 or wall==11000)then
  local f=assert(io.open(OUTPUT..'ppu-'..wall..'.png','wb'));f:write(emu.takeScreenshot());f:close();captures=captures+1
 end
end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 if code==0 then
  assert(nmis>100,'Sustained native interrupt/stack-margin coverage')

  local f=assert(io.open(OUTPUT..'ownership-guards.json','w'))
  f:write(string.format('{"passed":true,"nmis":%d,"mapper_store_windows":%d,"protected_page_write_checks":%d,"minimum_sampled_SP":%d,"SMC_stack_floor":%d,"PPU_screenshots":%d,"five_SMC_operands_preserved":true,"visible_world_PPU_address_writes":0}',nmis,windows,stackWrites,minSP,C.stack_floor,captures));f:close()
 end
 stop(code)
end

CHIP_AUDIO_NATIVE={["candidate"]=true,["target"]=13,["moves"]={"up","up","up","left","up","up","down","down","down","left","down","down","right","","left","left","left","right","right"},["loopReturn"]=33621,["loopBank"]=126,["gold"]="C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/root-chip-native-audio-v1/candidate/gold/",["sourceInit"]=44185,["sourcePlay"]=41728,["sourceZp"]=29824,["sourceRam"]=29696,["apuImage"]=29314,["sourceReturn"]=57335}

local C=assert(CHIP_AUDIO_NATIVE)
local wall,entered,updates,dmas,sourceCalls,sourceStores,irqCount=0,false,0,0,0,0,0
local src,events,gold,song,index=nil,{},nil,nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==14 end
local function json(v)
 if type(v)=='table'then local q={};if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end;for k,x in pairs(v)do q[#q+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(q,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local log=assert(io.open(OUTPUT..'cadence.csv','w'))
log:write('wall,updates,dmas,sourceCalls,engine,x,y,camera,nmiSkipped\n')
local image={}
for _,range in ipairs({{0x4000,0x4013},{0x4015,0x4015},{0x4017,0x4017}})do
 emu.addMemoryCallback(function(a,v)image[a]=v end,emu.callbackType.write,range[1],range[2])
end
emu.addMemoryCallback(function()if entered then dmas=dmas+1 end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()if active()and bank(C.loopReturn)==C.loopBank then updates=updates+1 end end,emu.callbackType.exec,C.loopReturn)
emu.addMemoryCallback(function()if entered then irqCount=irqCount+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
local function start(kind)
 assert(bank(C.sourcePlay)==62 and not src,'Exclusive real source entry')
 if kind=='init'then
  song=r('RgAudioSong');index=0;if gold then gold:close()end
  gold=assert(io.open(C.gold..'song-'..song..'.bin','rb'))
 else index=index+1 end
 src=true;events={}
end
local function byte()local s=assert(gold:read(1),'Bound source record');return s:byte()end
local function sourceReturn()
 if not src or bank(C.sourceReturn)~=94 then return end
 local count=byte();assert(count==#events,'Original ordered APU count song'..song..' tick'..index)
 for i=1,count do local at=0x4000+byte();local v=byte();assert(events[i][1]==at and events[i][2]==v,'Original raw ordered source APU song'..song..' tick'..index..' write'..i)end
 local n=byte()
 for i=1,n do
  local at=byte()+256*byte();local v=byte()
  local mapped=at<256 and C.sourceZp+at-0xc0 or C.sourceRam+at-0x700
  assert(emu.read(mapped,emu.memType.nesDebug)==v,'Original source state '..at..' song'..song..' tick'..index)
 end
 sourceCalls=sourceCalls+1;sourceStores=sourceStores+count;src=nil
end
if C.candidate then
 emu.addMemoryCallback(function()if bank(C.sourceInit)==62 then start('init')end end,emu.callbackType.exec,C.sourceInit)
 emu.addMemoryCallback(function()if bank(C.sourcePlay)==62 then start('play')end end,emu.callbackType.exec,C.sourcePlay)
 emu.addMemoryCallback(function(a,v)if src then events[#events+1]={0x4000+a-C.apuImage,v}end end,emu.callbackType.write,C.apuImage,C.apuImage+15)
 emu.addMemoryCallback(function()if src and bank(L.GuestNativeStatusSTA)==127 then events[#events+1]={0x4015,emu.getState()['cpu.a']}end end,emu.callbackType.exec,L.GuestNativeStatusSTA)
 emu.addMemoryCallback(sourceReturn,emu.callbackType.exec,C.sourceReturn)
end
local function menu()
 if wall<180 or wall%12~=0 then return{}end
 if r('CrossoverMenuState')==2 then
  local i=r('CrossoverMenuIndex');if i==C.target then
   if r('CdVariant')~=0 then return{select=true}end
   return{a=true}
  end
  return{[assert(C.moves[i+1])]=true}
 end
 return{start=true}
end
emu.addEventCallback(function()emu.setInput(entered and{}or menu(),0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and active()then
  assert(r('SelectedCharacter')==14 and r('CdVariant')==0 and r('CrossoverBehaviorVersion')==0,'Actual cold-menu Chip/Easy0')
  entered=true
 end
 if entered then
  log:write(table.concat({wall,updates,dmas,sourceCalls,r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),r('NmiSkipped')},',')..'\n')
 end
 if wall>=300 and wall%120==0 then local f=assert(io.open(OUTPUT..'ppu-'..wall..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
 if wall==1300 then
  assert(entered and updates>400 and dmas>400 and irqCount>400,'Sustained actual active-game observations')
  if C.candidate then assert(sourceCalls>500 and sourceStores>1000,'Sustained original driver output/state')end
  log:close();if gold then gold:close()end
  local f=assert(io.open(OUTPUT..'audio-native.json','w'))
  f:write(json({passed=true,candidate=C.candidate,wall_frames=wall,completed_active_updates=updates,DMA_starts=dmas,source_calls=sourceCalls,ordered_original_source_stores=sourceStores,IRQ_entries=irqCount,input_only=true,no_emulated_state_writes=true,scope='Cold menu followed by idle controller input. Natural contact/death remains possible. No campaign clear, forced item use or strict matched-cadence verdict.'}));f:close();emu.stop(0)
 end
 assert(wall<=1300,'Bounded native observation')
end,emu.eventType.endFrame)
