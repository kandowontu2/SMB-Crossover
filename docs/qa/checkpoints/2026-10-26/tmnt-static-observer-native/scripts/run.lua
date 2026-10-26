dofile("C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/tmnt-static-observer-v1/tmnt_static_exec_dispatcher_v1.lua")
VEHICLE_AUDIO_CONFIG={["nmi"]=58166,["nmi_return"]=58383,["smc"]={354,362,377,364,365},["stack_floor"]=123,["stack_start"]=90,["music"]=0,["chr_observer"]="C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/tmnt-static-observer-v1/chr-commit-observer.lua"}
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
local chr=dofile(C.chr_observer)({out=OUTPUT,character=19})
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
  chr.finish();assert(not chr.failure(),chr.failure())
  local f=assert(io.open(OUTPUT..'ownership-guards.json','w'))
  f:write(string.format('{"passed":true,"nmis":%d,"mapper_store_windows":%d,"protected_page_write_checks":%d,"minimum_sampled_SP":%d,"SMC_stack_floor":%d,"PPU_screenshots":%d,"five_SMC_operands_preserved":true,"visible_world_PPU_address_writes":0}',nmis,windows,stackWrites,minSP,C.stack_floor,captures));f:close()
 end
 stop(code)
end

TMNT_STORAGE_NATIVE={["behavior"]=0,["mode"]="easy",["variant"]=0,["native"]=1,["entered"]=0,["step"]=0,["phase"]="startup",["observer"]="C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/tmnt-static-observer-v1/performance-observer.lua",["ram"]={["Player_PageLoc"]=92,["TnPhase"]=23666,["Block_Buffer_1"]=768,["WorldNumber"]=1892,["Enemy_BoundBoxCtrl"]=1606,["PlayerFacingDir"]=1342,["SelectedCharacter"]=24578,["TnAttack"]=23565,["TnMusicDpcm"]=59584,["TnHealth"]=24416,["TnGearSelected"]=23672,["EnemyFrenzyBuffer"]=1737,["TnVYHi"]=23552,["Player_X_Speed"]=70,["CrossoverOptionsFocus"]=32441,["TnEquipment"]=24420,["InjuryTimer"]=1947,["CrossoverBehaviorVersion"]=32737,["BassDmcActive"]=31755,["Enemy_MovingDir"]=1343,["TnNativePlay"]=42564,["OperMode"]=1905,["TnTimer"]=23668,["TnAudioDmcRegs"]=29904,["TnAudioSilenced"]=29902,["Enemy_Y_HighPos"]=165,["EnemyOffscrBitsMasked"]=1448,["TnVXHi"]=23554,["Enemy_Y_Speed"]=143,["LevelNumber"]=1889,["TnAmmo"]=24424,["NonMaskableInterrupt"]=58166,["CheatInvincible"]=32763,["Enemy_ID"]=23,["OperMode_Task"]=1907,["Player_Y_Speed"]=142,["IrqScrollSplit"]=32768,["GamePauseStatus"]=1911,["Player_X_Position"]=117,["ScrollThirtyTwo"]=1856,["ScrollLock"]=1830,["GuestNativeApu"]=29314,["Enemy_Y_Position"]=190,["DrawAllMetasprites"]=40960,["ScreenRight_PageLoc"]=1822,["TnInputFrame"]=23563,["CrossoverMenuState"]=29447,["SavedJoypadBits"]=220,["TnAudioSong"]=29901,["AreaType"]=1875,["EnemyMetasprite"]=1762,["ScreenLeft_PageLoc"]=1821,["EnemyFrenzyQueue"]=1739,["ScreenRight_X_Pos"]=1824,["NmiSkipped"]=314,["Player_Y_Position"]=189,["TnJumpStage"]=23559,["AreaParserTaskNum"]=1826,["Enemy_CollisionBits"]=1597,["Enemy_State"]=31,["TnAudioDacHold"]=29909,["Enemy_PageLoc"]=93,["Player_Y_HighPos"]=164,["TnVariant"]=24550,["MmDeathFlag"]=24583,["TnShotKind"]=23632,["GameEngineSubroutine"]=15,["TimerControl"]=1866,["GuestCombinedEnable"]=29414,["GameLoop"]=33497,["Player_State"]=30,["Enemy_Flag"]=16,["GuestMixMask"]=29406,["ScreenLeft_X_Pos"]=1823,["TnMovement"]=41810,["TnSeq"]=23664,["TnNativeInit"]=40960,["StarInvincibleTimer"]=1948,["TnPose"]=23670,["CrossoverMenuIndex"]=29449,["Enemy_X_Speed"]=71,["Enemy_X_Position"]=118},["sites"]={{["pc"]=40963,["address"]=16405,["mode"]="abs"},{["pc"]=40968,["address"]=16384,["mode"]="aby"},{["pc"]=42825,["address"]=16384,["mode"]="abx"},{["pc"]=43422,["address"]=16405,["mode"]="abs"},{["pc"]=43428,["address"]=16400,["mode"]="abs"},{["pc"]=43434,["address"]=16401,["mode"]="abs"},{["pc"]=43440,["address"]=16402,["mode"]="abs"},{["pc"]=43446,["address"]=16403,["mode"]="abs"},{["pc"]=43451,["address"]=16405,["mode"]="abs"},{["pc"]=43595,["address"]=16385,["mode"]="abx"},{["pc"]=43618,["address"]=16392,["mode"]="abs"},{["pc"]=43670,["address"]=16384,["mode"]="abx"},{["pc"]=43741,["address"]=16392,["mode"]="abs"},{["pc"]=44041,["address"]=16387,["mode"]="abx"},{["pc"]=44061,["address"]=16386,["mode"]="abx"},{["pc"]=44305,["address"]=16384,["mode"]="abx"},{["pc"]=44862,["address"]=16384,["mode"]="abx"},{["pc"]=44871,["address"]=16405,["mode"]="abs"},{["pc"]=44876,["address"]=16392,["mode"]="abs"},{["pc"]=44881,["address"]=16405,["mode"]="abs"},{["pc"]=44915,["address"]=16396,["mode"]="abs"},{["pc"]=45125,["address"]=16384,["mode"]="abs"},{["pc"]=45128,["address"]=16388,["mode"]="abs"},{["pc"]=45131,["address"]=16396,["mode"]="abs"},{["pc"]=45136,["address"]=16385,["mode"]="abs"},{["pc"]=45139,["address"]=16389,["mode"]="abs"},{["pc"]=45420,["address"]=16384,["mode"]="abx"},{["pc"]=45425,["address"]=16385,["mode"]="abx"}},["gold"]="C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/tmnt-native-storage-current50b5-v1/native-pilots-v1/candidate-easy/gold/"}
TMNT_CFG=TMNT_STORAGE_NATIVE
-- Read-only native hardware/source observations; no emulator state writes.
local C=assert(TMNT_STORAGE_NATIVE)
for n,a in pairs(C.ram)do L[n]=a end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local bus=assert(io.open(OUTPUT..'native-bus.jsonl','w'))
local function stamp()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount'],pc=s['cpu.pc'],sp=s['cpu.sp']}end
local function row(q)bus:write(json(q)..'\n');bus:flush()end
local function active()return C.entered==1 and r('SelectedCharacter')==19 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local nmiDepth,nmis,irqs,maxNmiDepth=0,0,0,0
emu.addMemoryCallback(function()
 nmiDepth=nmiDepth+1;nmis=nmis+1;maxNmiDepth=math.max(maxNmiDepth,nmiDepth)
 assert(nmiDepth==1,'Actual NMI does not nest inside audio')
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()assert(nmiDepth==1,'Balanced actual NMI return');nmiDepth=nmiDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()if active()then irqs=irqs+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
local mask,pending,completed,unsafe,wrong,installed=0,nil,0,0,0,{}
emu.addMemoryCallback(function(_,v)mask=v end,emu.callbackType.write,0x2001)
local function bytes(at,kind)local t={};for i=0,255 do t[i+1]=emu.read(at+i,kind)end;return t end
local function equal(a,b)for i=1,#a do if a[i]~=b[i]then return false end end;return true end
local function safe(q)return q.mask&24==0 or(q.scanline>=241 and q.scanline<=260)end
local function failDMA(q,message)
 local f=assert(io.open(OUTPUT..'first-hardware-failure.json','w'));f:write(json({passed=false,message=message,DMA=q,nmi_depth=nmiDepth,requested_mode=C.behavior,actual_mode=r('CrossoverBehaviorVersion')}));f:close()
 local png=assert(io.open(OUTPUT..'first-hardware-failure.png','wb'));png:write(emu.takeScreenshot());png:close()
 assert(false,message)
end
emu.addMemoryCallback(function()if pending then pending.writes=pending.writes+1 end end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(_,page)
 if not active()then return end
 assert(not pending,'One complete hardware DMA at a time')
 local s=stamp();s.mask=mask
 pending={start=s,source=bytes(page*256,emu.memType.nesDebug),page=page,writes=0,owner=bank(s.pc)}
 row({kind='DMA-start',data=pending})
 -- Mesen's write callback exposes the already fetched LDX#1 after STA4014.
 assert(emu.read(s.pc,emu.memType.nesDebug)==0xa2 and emu.read(s.pc+1,emu.memType.nesDebug)==1,'Exact actual DMA completion hook LDX1')
 local finish=s.pc+2;local owner=pending.owner;local key=owner..':'..finish
 if not installed[key]then
  installed[key]=true
  emu.addMemoryCallback(function()
   if not pending or bank(finish)~=owner then return end
   local q=pending;pending=nil;q.finish=stamp();q.finish.mask=mask;q.hardware=bytes(0,emu.memType.nesSpriteRam)
   q.exact=equal(q.source,q.hardware);q.safe=safe(q.start)and safe(q.finish)
   row({kind='DMA-complete',data=q})
   completed=completed+1
   if not q.exact then wrong=wrong+1;failDMA(q,'Actual completed DMA differs from complete source page')end
   if not q.safe then unsafe=unsafe+1;failDMA(q,'Actual completed DMA crosses rendering-enabled time')end
   assert(q.writes==256,'Exactly256 completed hardware DMA writes')
  end,emu.callbackType.exec,finish)
 end
end,emu.callbackType.write,0x4014)

local sourceActive,sourceCalls,sourceStores,gold,goldSong,sourceFrame=false,0,0,nil,nil,0
local events,actual,images={}, {}, {}
local hardware,drumActive,drumHeld=0,0,0
local returns,returnHooks={},{}
local function onReturn(fn)
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=bank(pc)..':'..pc;returns[key]={sp=(sp+2)%256,fn=fn}
 if not returnHooks[key]then returnHooks[key]=true;local owner=bank(pc)
  emu.addMemoryCallback(function()local q=returns[key];if q and emu.getState()['cpu.sp']==q.sp and bank(pc)==owner then returns[key]=nil;q.fn()end end,emu.callbackType.exec,pc)
 end
end
local gameReturns,draws=0,0
emu.addMemoryCallback(function()
 if not active()or bank(L.DrawAllMetasprites)~=B.DrawAllMetasprites then return end
 draws=draws+1;row({kind='draw-construction',index=C.step,phase=C.phase,draws=draws,stamp=stamp(),nmi_depth=nmiDepth})
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not active()or bank(L.GameLoop)~=B.GameLoop then return end
 onReturn(function()
  gameReturns=gameReturns+1;row({kind='completed-game-update',index=C.step,phase=C.phase,draws=draws,completed=gameReturns,stamp=stamp(),nmi_depth=nmiDepth,skipped=r('NmiSkipped')})
 end)
end,emu.callbackType.exec,L.GameLoop)
if C.native==1 then
 local function source(kind)
  if bank(L.TnNativeInit)~=63 or r('SelectedCharacter')~=19 then return end
  assert(not sourceActive,'One authentic source call at a time');sourceActive=true;events={}
  if kind=='init'then
   goldSong=r('TnAudioSong');sourceFrame=0;if gold then gold:close()end
   gold=assert(io.open(C.gold..'song-'..goldSong..'.bin','rb'))
  else sourceFrame=sourceFrame+1 end
  onReturn(function()
   local n=assert(gold:read(1),'Bounded original gold record'):byte();local record=assert(gold:read(n*2),'Original ordered APUs')
   assert(#events==n,'Exact original source APU count song='..goldSong..' frame='..sourceFrame)
   for i,q in ipairs(events)do assert(q[1]==record:byte(i*2-1)and q[2]==record:byte(i*2),'Exact original source APU sequence');if q[1]<20 then images[q[1]]=q[2]end end
   sourceCalls=sourceCalls+1;sourceStores=sourceStores+n;sourceActive=false
  end)
 end
 emu.addMemoryCallback(function()source('init')end,emu.callbackType.exec,L.TnNativeInit)
 emu.addMemoryCallback(function()source('play')end,emu.callbackType.exec,L.TnNativePlay)
 for _,site in ipairs(C.sites)do
  emu.addMemoryCallback(function()
   if not sourceActive or bank(site.pc)~=63 then return end
   local s=emu.getState();local add=site.mode=='abx'and s['cpu.x']or site.mode=='aby'and s['cpu.y']or 0
   events[#events+1]={site.address+add-0x4000,s['cpu.a']}
  end,emu.callbackType.exec,site.pc)
 end
end
emu.addMemoryCallback(function(at,v)actual[at-0x4000]=v end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()
 if not active()or C.native~=1 then return end
 assert(r('CrossoverBehaviorVersion')==C.behavior,'Every live frame retains actual numeric mode')
 local s=emu.getState()
 if r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 and goldSong then
  for reg=0,15 do
   assert(r('GuestNativeApu',reg)==images[reg],'Original source register image')
   if reg~=9 and reg~=13 and not(reg>=12 and(r('GuestMixMask')&8)~=0)then assert(actual[reg]==r('GuestNativeApu',reg),'Actual mixer restores source register');hardware=hardware+1 end
  end
  for reg=0,3 do assert(r('TnAudioDmcRegs',reg)==images[reg+16],'Original DMC source parameter image')end
  assert(actual[21]==r('GuestCombinedEnable'),'Actual hardware4015 stores match merged enable image')
 end
 if r('BassDmcActive')==4 then
  assert(s['apu.dmc.sampleAddr']==L.TnMusicDpcm and s['apu.dmc.sampleLength']==129,'Actual full original drum/address')
  assert(s['apu.dmc.timer.period']==53 and not s['apu.dmc.irqEnabled']and not s['apu.dmc.loopFlag'],'Original DMC rate15/non-loop/noIRQ')
  drumActive=drumActive+1
 end
 if r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 and r('TnAudioDacHold')==44 and s['apu.dmc.bytesRemaining']==0 and s['apu.dmc.bufferEmpty']and s['apu.dmc.silenceFlag']then
  assert(s['apu.dmc.outputLevel']==44,'Actual completed original drum holds DAC44');drumHeld=drumHeld+1
 end
end,emu.eventType.endFrame)
local originalStop=emu.stop
function emu.stop(code)
 if code==0 then
  assert(nmiDepth==0 and maxNmiDepth==1,'Final balanced real NMI scheduling')
  assert(completed>100 and wrong==0 and unsafe==0,'Sustained actual completed OAM DMA safety')
  if C.native==1 then assert(sourceCalls>500 and sourceStores>1000 and hardware>1000 and drumActive>0,'Actual original music/hardware/DMC coverage')end
  local f=assert(io.open(OUTPUT..'native-source-hardware.json','w'))
  f:write(json({passed=true,source_calls=sourceCalls,source_APU_writes=sourceStores,hardware_comparisons=hardware,active_DMC_frames=drumActive,held_DAC44_frames=drumHeld,completed_DMA=completed,wrong_DMA=wrong,unsafe_DMA=unsafe,nmis=nmis,irqs=irqs,max_NMI_depth=maxNmiDepth}));f:close();bus:close()
 end
 originalStop(code)
end

-- Equal-update native performance arenas; inventory/terrain/targets arranged.
-- Real cold menus/input and ordinary native movement/combat; no cycle bypass.
local C=assert(TMNT_CFG);local wall=0;local entered=false
L.TnInputFrame=0x5c0b -- Source-owned constant, absent from exported linker labels.
local phase=C.behavior==1 and'options-focus'or'start'
local step=0;local completed=false;local phaseIndex=0;local phaseStart=0
local names={'idle','walk','enemies','primary','secondary'}
local liveEnemySamples=0
local finish
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)assert(C.setup==1,'State writes only at before-phase setup');local at=assert(L[n],n)+(i or 0);C.writes[#C.writes+1]={address=at,before=emu.read(at,emu.memType.nesDebug),value=v%256,name=n};emu.write(at,v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local profile=dofile(C.observer)({out=TEST_DIR,phase=function()return names[phaseIndex]or'startup'end,
 onGameLoopReturn=function()if step==600 then completed=true end end})
local boundary=assert(io.open(TEST_DIR..'before-phase-setup.jsonl','w'))
local function json(v)if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end end
local trace=assert(io.open(TEST_DIR..'gameplay.csv','w'));trace:write('update,phase,input,x,page,y,state,vx,vy,hp,gear,ammo,selected,seq,animationPhase,pose,attack,shot0,shot1,shot2,enemy0,enemyX0,enemyY0,enemyState0,enemy1,enemyX1,enemyY1,enemyState1\n')
local function arena()
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1,'Actual1-1 overworld stage')
 assert(r('Player_Y_HighPos')==1 and r('SelectedCharacter')==19,'Live native turtle before phase setup')
 for col=2,15 do assert(emu.read(L.Block_Buffer_1+0xb0+col,emu.memType.nesDebug)~=0,'Native first-screen ground at feet208 is retained')end
 C.setup=1;C.writes={};C.phase=names[phaseIndex]
 local before={phase=names[phaseIndex],step=step,hp=r('TnHealth',C.variant),gear=r('TnEquipment',C.variant),ammo=r('TnAmmo',C.variant),selected=r('TnGearSelected'),behavior=r('CrossoverBehaviorVersion')}
 boundary:write(json({kind='before',data=before})..'\n');boundary:flush()
 for a=0x5c00,0x5cff do C.writes[#C.writes+1]={address=a,before=emu.read(a,emu.memType.nesDebug),value=0,name='native-area-slab'};emu.write(a,0,emu.memType.nesDebug)end
 for _,q in ipairs({{'TnSeq',0x80},{'TnTimer',6},{'TnPose',9},{'TnJumpStage',8},{'TnInputFrame',255}})do w(q[1],q[2])end
 w('TnHealth',128,C.variant);w('TnEquipment',phaseIndex==5 and 2 or 0,C.variant);w('TnAmmo',phaseIndex==5 and 99 or 0,C.variant);w('TnGearSelected',phaseIndex==5 and 1 or 0)
 -- Retain the native first-screen terrain and its collision/provenance cache.
 -- Inventing only a metatile array leaves native actor support inconsistent.
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','InjuryTimer','StarInvincibleTimer'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 if phaseIndex>=3 then
  for i=0,1 do
   -- Native Goomba actor Y184 has feet at208; its sprite adds8 pixels.
   -- Y192 starts inside the floor and cannot establish native support.
   for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},{'Enemy_X_Position',208+i*24},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0xf8},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0},{'EnemyOffscrBitsMasked',0}})do w(q[1],q[2],i)end
  end
 end
 local q={phase=names[phaseIndex],step=step,hp=r('TnHealth',C.variant),gear=r('TnEquipment',C.variant),ammo=r('TnAmmo',C.variant),selected=r('TnGearSelected'),player_y=r('Player_Y_Position'),enemy_y=r('Enemy_Y_Position'),enemy_y1=r('Enemy_Y_Position',1)}
 if phaseIndex>=3 then assert(q.enemy_y==184 and q.enemy_y1==184,'Both real native Goomba actors have supported feet208')end
 boundary:write(json({kind='staged',data=q,writes=C.writes})..'\n');boundary:flush();C.setup=0
end
finish=function()
 assert(liveEnemySamples>=100,'Enemy phase must retain live native actors')
 profile.finish();trace:close();boundary:close();local p=assert(io.open(TEST_DIR..'result.json','w'))
 p:write('{"passed":true,"variant":'..C.variant..',"mode":"'..C.mode..'","equal_game_updates":600,"video_frames":'..wall..',"arranged_native_component":true,"live_enemy_phase_samples":'..liveEnemySamples..'}\n');p:close();emu.stop(0)
end
local function menu()
 if wall<60 or wall%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2
 if row~=2 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local u=(step-phaseStart)%64;local walking=phaseIndex>=2
 emu.setInput({right=walking and u<32,left=walking and u>=32,b=phaseIndex>=4 and step%16<4},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if not entered or bank(L.TnMovement)~=B.TnMovement then return end
 if step%120==0 then phaseIndex=phaseIndex+1;assert(phaseIndex<=5,'Performance work remains bounded');phaseStart=step;arena()end
 local v={step,names[phaseIndex],r('SavedJoypadBits'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('TnVXHi'),r('TnVYHi'),r('TnHealth',C.variant),r('TnEquipment',C.variant),r('TnAmmo',C.variant),r('TnGearSelected'),r('TnSeq'),r('TnPhase'),r('TnPose'),r('TnAttack')}
 for i=0,2 do v[#v+1]=r('TnShotKind',i)end
 for i=0,1 do for _,n in ipairs({'Enemy_Flag','Enemy_X_Position','Enemy_Y_Position','Enemy_State'})do v[#v+1]=r(n,i)end end
 if phaseIndex==3 and(r('Enemy_Flag')~=0 or r('Enemy_Flag',1)~=0)then liveEnemySamples=liveEnemySamples+1 end
 trace:write(table.concat(v,',')..'\n');step=step+1;C.step=step
end,emu.callbackType.exec,L.TnMovement)
emu.addEventCallback(function()
 wall=wall+1
 if completed then finish();return end
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant,'Real requested turtle selected');assert((C.behavior==0 or C.behavior==1)and r('CrossoverBehaviorVersion')==C.behavior,'Actual cold selected numeric Easy/Hard')
   local f=assert(io.open(OUTPUT..'mode-readback.json','w'));f:write('{"requested":'..C.behavior..',"actual":'..r('CrossoverBehaviorVersion')..',"selected":'..r('SelectedCharacter')..'}');f:close()
   entered=true;C.entered=1
 end
 assert(wall<3000,'Performance arena deadline')
end,emu.eventType.endFrame)

TMNT_STORAGE_PROFILE={["hooks"]={{["name"]="AudioUpdate",["pc"]=61533,["bank"]=127},{["name"]="ExpandedAudioUpdate",["pc"]=37211,["bank"]=126},{["name"]="TnAudioUpdate",["pc"]=55753,["bank"]=125},{["name"]="TnNativeInit",["pc"]=40960,["bank"]=63},{["name"]="TnNativePlay",["pc"]=42564,["bank"]=63},{["name"]="TnSourceSTA00",["pc"]=41004,["bank"]=63},{["name"]="TnSourceSTA00X",["pc"]=41058,["bank"]=63},{["name"]="TnSourceSTA00Y",["pc"]=41094,["bank"]=63},{["name"]="TnSourceSTA01",["pc"]=41013,["bank"]=63},{["name"]="TnSourceSTA01X",["pc"]=41067,["bank"]=63},{["name"]="TnSourceSTA02X",["pc"]=41076,["bank"]=63},{["name"]="TnSourceSTA03X",["pc"]=41085,["bank"]=63},{["name"]="TnSourceSTA04",["pc"]=41022,["bank"]=63},{["name"]="TnSourceSTA05",["pc"]=41031,["bank"]=63},{["name"]="TnSourceSTA08",["pc"]=41040,["bank"]=63},{["name"]="TnSourceSTA0C",["pc"]=41049,["bank"]=63},{["name"]="TnSourceSTA10",["pc"]=41161,["bank"]=63},{["name"]="TnSourceSTA11",["pc"]=41168,["bank"]=63},{["name"]="TnSourceSTA12",["pc"]=41178,["bank"]=63},{["name"]="TnSourceSTA13",["pc"]=41192,["bank"]=63},{["name"]="TnSourceSTA15",["pc"]=41199,["bank"]=63}},["stores"]={{["bank"]=63,["pc"]=41164,["register"]=16400},{["bank"]=63,["pc"]=41174,["register"]=16401},{["bank"]=63,["pc"]=41186,["register"]=16402},{["bank"]=63,["pc"]=41195,["register"]=16403},{["bank"]=63,["pc"]=41247,["register"]=16405},{["bank"]=125,["pc"]=49850,["register"]=16401},{["bank"]=125,["pc"]=51663,["register"]=16401},{["bank"]=125,["pc"]=51710,["register"]=16405},{["bank"]=125,["pc"]=51715,["register"]=16401},{["bank"]=125,["pc"]=51761,["register"]=16405},{["bank"]=125,["pc"]=52484,["register"]=16405},{["bank"]=125,["pc"]=55952,["register"]=16401},{["bank"]=125,["pc"]=56018,["register"]=16401},{["bank"]=125,["pc"]=56123,["register"]=16405},{["bank"]=125,["pc"]=56128,["register"]=16401},{["bank"]=125,["pc"]=56144,["register"]=16400},{["bank"]=125,["pc"]=56150,["register"]=16402},{["bank"]=125,["pc"]=56156,["register"]=16403},{["bank"]=125,["pc"]=56177,["register"]=16405},{["bank"]=125,["pc"]=57072,["register"]=16405},{["bank"]=127,["pc"]=58042,["register"]=16401},{["bank"]=127,["pc"]=59855,["register"]=16401},{["bank"]=127,["pc"]=59902,["register"]=16405},{["bank"]=127,["pc"]=59907,["register"]=16401},{["bank"]=127,["pc"]=59953,["register"]=16405},{["bank"]=127,["pc"]=60676,["register"]=16405},{["bank"]=127,["pc"]=65264,["register"]=16405}},["ram"]={["SelectedCharacter"]=24578,["OperMode"]=1905,["GameEngineSubroutine"]=15,["TnAudioSong"]=29901,["TnAudioRam"]=29696,["TnAudioZp"]=222}}
-- Read-only identical-work replay: disjoint audio costs and DMC instruction clocks.
local P=assert(TMNT_STORAGE_PROFILE);local C=assert(TMNT_STORAGE_NATIVE)
local function r(n,i)return emu.read(assert(P.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function tick()return emu.getState()['cpu.cycleCount']end
local function stamp()local s=emu.getState();return{s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.cycleCount']}end
local function st(q)return table.concat(q,',')end
local function active()return C.entered==1 and r('SelectedCharacter')==19 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local audio=assert(io.open(OUTPUT..'audio-components.csv','w'))
audio:write('serial,name,phase,update,startFrame,startScan,startDot,startCPU,endFrame,endScan,endDot,endCPU,inclusiveCycles,IRQCycles,CPUcycles,childCPUcycles,exclusiveCPUcycles\n')
local instructions=assert(io.open(OUTPUT..'dmc-instruction-clocks.csv','w'))
instructions:write('phase,update,bank,pc,register,value,startFrame,startScan,startDot,startCPU,endFrame,endScan,endDot,endCPU,IRQCycles,actualCPUcycles,base6502cycles,extraCycles\n')
local apu=assert(io.open(OUTPUT..'source-apu.csv','w'));apu:write('serial,song,sourceTick,register,value,frame,scan,dot,cpu\n')
local state=assert(io.open(OUTPUT..'source-state.csv','w'));state:write('serial,song,sourceTick,ZP14_RAM174_hex\n')
local irqStart,irqDepth,irqCycles=0,0,0
emu.addMemoryCallback(function()if irqDepth==0 then irqStart=tick()-7 end;irqDepth=irqDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()irqDepth=irqDepth-1;assert(irqDepth>=0,'Profile IRQ balance');if irqDepth==0 then irqCycles=irqCycles+tick()-irqStart+6 end end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
local stack,serial,installed={},0,{}
local sourceSerial,sourceSong,sourceTick=0,0,-1
for _,h in ipairs(P.hooks)do
 emu.addMemoryCallback(function()
  local source=h.name=='TnNativeInit'or h.name=='TnNativePlay'
  if bank(h.pc)~=h.bank or(not active()and not(source and r('SelectedCharacter')==19 and r('OperMode')==1))then return end
  serial=serial+1
  local s=emu.getState();local sp=s['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  local q={serial=serial,name=h.name,phase=C.phase,update=C.step,begin=stamp(),irq=irqCycles,child=0,sp=(sp+2)%256,ret=ret,retbank=bank(ret)}
  if h.name=='TnNativeInit'then sourceSerial=sourceSerial+1;sourceSong=r('TnAudioSong');sourceTick=0;q.source=1
  elseif h.name=='TnNativePlay'then sourceSerial=sourceSerial+1;sourceSong=r('TnAudioSong');sourceTick=sourceTick+1;q.source=1 end
  stack[#stack+1]=q;local key=q.retbank..':'..ret
  if not installed[key]then installed[key]=true
   emu.addMemoryCallback(function()
    local q=stack[#stack];if not q or q.ret~=ret or q.retbank~=bank(ret)or q.sp~=emu.getState()['cpu.sp']then return end
    local finish=stamp();local elapsed=finish[4]-q.begin[4];local irq=irqCycles-q.irq;local cpu=elapsed-irq
    assert(cpu>=q.child,'Disjoint component accounting excludes IRQ exactly once')
    audio:write(table.concat({q.serial,q.name,q.phase,q.update,st(q.begin),st(finish),elapsed,irq,cpu,q.child,cpu-q.child},',')..'\n')
    table.remove(stack);if #stack>0 then stack[#stack].child=stack[#stack].child+cpu end
    if q.source then
     local t={};for i=0,13 do t[#t+1]=string.format('%02x',r('TnAudioZp',i))end;for i=0,173 do t[#t+1]=string.format('%02x',r('TnAudioRam',i))end
     state:write(table.concat({sourceSerial,sourceSong,sourceTick,table.concat(t)},',')..'\n')
    end
   end,emu.callbackType.exec,ret)
  end
 end,emu.callbackType.exec,h.pc)
end
for _,site in ipairs(C.sites)do
 emu.addMemoryCallback(function()
  if bank(site.pc)~=63 or sourceSerial==0 or r('SelectedCharacter')~=19 or r('OperMode')~=1 then return end
  local s=emu.getState();local add=site.mode=='abx'and s['cpu.x']or site.mode=='aby'and s['cpu.y']or 0
  apu:write(table.concat({sourceSerial,sourceSong,sourceTick,site.address+add,s['cpu.a'],st(stamp())},',')..'\n')
 end,emu.callbackType.exec,site.pc)
end
local pending,instructionHooks={},{}
for _,h in ipairs(P.stores)do
 emu.addMemoryCallback(function()
  if not active()or bank(h.pc)~=h.bank then return end
  local s=emu.getState();local key=h.bank..':'..(h.pc+3)
  pending[key]={h=h,begin=stamp(),irq=irqCycles,sp=s['cpu.sp'],phase=C.phase,update=C.step,value=s['cpu.a']}
  if not instructionHooks[key]then instructionHooks[key]=true
   emu.addMemoryCallback(function()
    local q=pending[key];if not q or bank(h.pc+3)~=h.bank or emu.getState()['cpu.sp']~=q.sp then return end
    pending[key]=nil;local finish=stamp();local irq=irqCycles-q.irq;local cycles=finish[4]-q.begin[4]-irq
    instructions:write(table.concat({q.phase,q.update,h.bank,h.pc,h.register,q.value,st(q.begin),st(finish),irq,cycles,4,cycles-4},',')..'\n')
   end,emu.callbackType.exec,h.pc+3)
  end
 end,emu.callbackType.exec,h.pc)
end
local stop=emu.stop
function emu.stop(code)
 if code==0 then assert(#stack==0 and irqDepth==0,'Final disjoint profile balance');audio:close();instructions:close();apu:close();state:close()end
 stop(code)
end

TMNT_STATIC_EXEC.install()
