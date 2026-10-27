-- Controller-only frontend checks. Five screenshots, one small audio summary;
-- no frame dumps, emulated writes, seeded menu states or copied runtime.
local heroes={'MARIO','LUIGI','MEGA MAN','PROTO MAN','SAMUS','BILL','LANCE','LINK',
 'ZELDA II LINK','SIMON','GRANT','SYPHA','ALUCARD','PIT','RYGAR','SCROOGE',
 'DARKWING DUCK','BASS','ROLL','RYU','SOPHIA','KIRBY','META KNIGHT','CHIP','DALE',
 'LITTLE MAC','MIKE JONES','SMB3 MARIO','SMB3 LUIGI','VIC VIPER','OCTOPUS','TWINBEE',
 'PENTAROU','LEONARDO','RAPHAEL','MICHELANGELO','DONATELLO'}
local frame,waiting,buttons,voiceWrites=0,0,{},0
local nmis,safeEnables,minSP=0,0,255
local wraps,lastY=0,nil
local pending,mask=nil,0
local results={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(pc)return emu.convertAddress(pc).address//8192 end
local smc={L.NextBank_SMC+1,L.SafecallA_SMC+1,L.SafereturnA_SMC+1,
 L.FarcallJmpTarget_SMC+1,L.FarcallJmpTarget_SMC+2}
local function operands()local a={};for i,at in ipairs(smc)do a[i]=emu.read(at,emu.memType.nesDebug)end;return table.concat(a,',')end
local function text(at,s)
 for i=1,#s do local c=s:byte(i);local tile=c==32 and 0x24 or c==45 and 0x28 or c>=65 and c<=90 and c-65+10 or c-48
  assert(emu.read(at+i-1,emu.memType.nesPpuDebug)==tile,'Visible text '..s..' at '..string.format('%04x',at)..' frame '..frame)
 end
end
local function shot(tag)
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addMemoryCallback(function()
 if r('CrossoverMenuState')~=8 then return end
 local s=emu.getState();assert(not pending,'NMI does not nest')
 local sp=s['cpu.sp'];minSP=math.min(minSP,sp)
 pending={a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],sp=sp,smc=operands(),
  shadowA=r('CurrentBank'),shadowC=r('CurrentBankC'),
  stackedP=emu.read(256+(sp+1)%256,emu.memType.nesDebug)}
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 if not pending then return end
 local q=pending;local s=emu.getState()
 assert(s['cpu.a']==q.a and s['cpu.x']==q.x and s['cpu.y']==q.y and s['cpu.sp']==q.sp,'NMI restores AXY/SP')
 assert(emu.read(256+(q.sp+1)%256,emu.memType.nesDebug)==q.stackedP,'NMI preserves original stacked flags')
 assert(operands()==q.smc and r('CurrentBank')==q.shadowA and r('CurrentBankC')==q.shadowC,'NMI restores foreground operands and bank shadows')
 assert(bank(0xa000)==q.shadowA%128 and bank(0xc000)==q.shadowC%128,'NMI restores physical A/C mapping')
 nmis=nmis+1;pending=nil
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addMemoryCallback(function(_,v)
 local old=mask;mask=v
 if r('CrossoverMenuState')==8 and r('DisableScreenFlag')==0 and old&24==0 and v&24~=0 then
  local s=emu.getState();local line,dot=s['ppu.scanline'],s['ppu.cycle']
  assert(line>=241 and line<=260 or line==-1 and dot<=274,'Sound menu render enable is late at '..line..':'..dot)
  safeEnables=safeEnables+1
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()voiceWrites=voiceWrites+1 end,emu.callbackType.write,0x4000,0x4013)
emu.addEventCallback(function()emu.setInput(buttons,0)end,emu.eventType.inputPolled)
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(predicate,maximum,label)
 local start=frame
 while not predicate() and frame-start<maximum do wait(1)end
 print('READY '..label..' waited '..(frame-start)..' frames; mode '..r('OperMode')..' task '..r('OperMode_Task')..' menu '..r('CrossoverMenuState')..' title '..r('CrossoverTitleDrawn'))
 assert(predicate(),label..' reaches real input-ready state')
end
local function sample(hero,kind,tag)
 local before=voiceWrites;press('a');wait(18)
 assert(r('SoundTestPlaying')==1 and r('SoundTestCommand')==0,'Actual source playback advances '..hero..' '..tag)
 local writes=voiceWrites-before
 assert(writes>0,'No voice register writes '..hero..' '..tag)
 results[#results+1]={character=hero,kind=kind,cue=tag,voice_register_writes=writes}
 if hero=='MARIO' and kind=='music'then shot('audio-mario')end
 if hero=='BILL' and kind=='sfx' and tag=='first'then shot('audio-bill')end
 press('start');assert(r('SoundTestPlaying')==0,'Start stops actual playback')
end
local task=coroutine.create(function()
 wait(70);press('down');press('start')
 assert(r('CrossoverMenuState')==4,'Ordinary title opens Options');text(0x22c5,'AUDIO TEST');shot('options')
 press('down');press('down');press('a')
 assert(r('CrossoverMenuState')==6 and r('CrossoverOptionsFocus')==0,'Options opens six-row Cheats')
 local at={0x2125,0x2165,0x21a5,0x21e5,0x2225,0x2265}
 local labels={'INVINCIBLE','START LEVEL','MID-AIR JUMPS','SCREEN WRAP','FREEZE TIMER','FULL POWER'}
 for i=1,6 do text(at[i],labels[i])end
 for i=0,21 do assert(emu.read(0x22c5+i,emu.memType.nesPpuDebug)==0x24,'Parent AUDIO row cleared in Cheats')end
 press('a');assert(r('CheatInvincible')==1,'Invincibility bit');press('a')
 press('down');press('right');assert(r('CheatStartLevel')&31==1,'Level selection');press('left')
 for row=2,5 do press('down');press('a');assert(r('CheatInvincible')&(1<<(row-1))~=0,'Each new option enables')end
 assert(r('CheatInvincible')==30,'Four independent new cheat flags');shot('cheats')
 for row=5,2,-1 do press('a');if row>2 then press('up')end end
 assert(r('CheatInvincible')==0,'Four options independently disable')
 press('b');assert(r('CrossoverMenuState')==4 and r('CrossoverOptionsFocus')==2,'Cheats returns focus to its parent row')
 press('down');press('a')
 assert(r('CrossoverMenuState')==8,'Audio submenu opens through actual controller input')
 text(0x208b,'SOUND TEST')
 for i,hero in ipairs(heroes)do
  assert(r('SoundTestHero')==i-1 and r('SoundTestKind')==0 and r('SoundTestIndex')==0,'Character browser identity '..hero)
  text(0x2145,hero);text(0x21a5,'TYPE - MUSIC');text(0x2224,'OVERWORLD')
  sample(hero,'music','overworld')
  press('select');assert(r('SoundTestKind')==1,'Select chooses SFX');text(0x21a5,'TYPE - SFX')
  sample(hero,'sfx','first');press('right');sample(hero,'sfx','second')
  press('select');press('down')
  print('PASS audio frontend '..hero)
 end
 assert(r('SoundTestHero')==0,'Character Down wraps to Mario')
 press('up');assert(r('SoundTestHero')==36,'Character Up wraps to Donatello');press('down')
 press('left');assert(r('SoundTestIndex')==13,'Music cue left wraps');text(0x2224,'TIME LOW')
 press('right');assert(r('SoundTestIndex')==0,'Music cue right wraps')
 press('b');assert(r('CrossoverMenuState')==4 and r('CrossoverOptionsFocus')==3,'Audio returns focus to its parent row')
 assert(r('PlayerOutlinesOff')==1 and r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0,'Unchanged real defaults/options')
 shot('options-return')
 -- Real Mario launch with the four new flags. Repeated fresh mid-air A must
 -- reach the top wrap; the ordinary Mario jump cannot reach that boundary.
 press('up');press('a');press('down');press('down')
 for row=2,5 do press('a');if row<5 then press('down')end end
 assert(r('CheatInvincible')==30,'Launch with four requested flags')
 press('b');press('b')
 ready(function()return r('CrossoverMenuState')==0 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,180,'title rebuild')
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,90,'roster')
 press('start');wait(600)
 assert(r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==0,'Ordinary Mario gameplay launch; mode '..r('OperMode')..' task '..r('OperMode_Task')..' menu '..r('CrossoverMenuState')..' engine '..r('GameEngineSubroutine')..' hero '..r('SelectedCharacter'))
 assert(r('PlayerStatus')==2,'Full Power reaches real Mario fire form')
 local timer=r('GameTimerDisplay')..','..r('GameTimerDisplay',1)..','..r('GameTimerDisplay',2)
 for jump=1,45 do press('a')end
 local after=r('GameTimerDisplay')..','..r('GameTimerDisplay',1)..','..r('GameTimerDisplay',2)
 assert(timer==after,'Freeze Timer holds real countdown digits')
 assert(wraps>0,'Fresh mid-air jumps reach native top-to-bottom wrap')
 assert(r('PlayerStatus')==2 and r('CheatInvincible')==30,'New flags and full power persist in actual gameplay')
 shot('cheats-gameplay')
 assert(nmis>100 and safeEnables>100 and minSP>=128,'Bounded native guard coverage')
 local f=assert(io.open(OUTPUT..'audio-summary.csv','w'));f:write('character,kind,cue,voice_register_writes\n')
 for _,v in ipairs(results)do f:write(v.character..','..v.kind..','..v.cue..','..v.voice_register_writes..'\n')end;f:close()
 f=assert(io.open(OUTPUT..'menu-result.json','w'));f:write(string.format('{"passed":true,"characters":37,"playbacks":%d,"nmis":%d,"safe_render_enables":%d,"minSP":%d,"physical_frames":%d,"screenshots":6,"per_frame_files":0,"Mario_top_wraps":%d,"Mario_air_jump_power_timer_native":true,"scope":"Controller/menu and MMIO activity plus Mario cheat integration; no audible waveform identity claim"}\n',#results,nmis,safeEnables,minSP,frame,wraps));f:close()
 print('PASS bounded native Audio/Cheats menus all37 identities');emu.stop(0)
end)
emu.addEventCallback(function()
 frame=frame+1;assert(frame<14000,'Bounded frontend frame count')
 if r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('CheatInvincible')&4~=0 and r('GuestPowerupActive')==0 then
  local y=r('Player_Y_Position');if lastY and y-lastY>80 then wraps=wraps+1 end;lastY=y
 else lastY=nil end
 if waiting>0 then waiting=waiting-1;return end
 if coroutine.status(task)=='dead'then return end
 local ok,n=coroutine.resume(task);assert(ok,n);waiting=n or 0
end,emu.eventType.endFrame)
