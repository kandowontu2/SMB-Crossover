-- One natural controller-only 1-1 discovery OR exact saved-input replay.
-- No menu-bootstrap, emulated writes, seeded resources, teleporting or cheats.
local C=assert(ROSTER_CONFIG)
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function opt(n,i)return L[n] and r(n,i) or 0 end
local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or -1 end
local function pos(lo,hi)return r(lo)+256*r(hi)end
local function stamp()
 local s=emu.getState();return{ppu_frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],
  cpu_cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],sp=s['cpu.sp'],bank=bank(s['cpu.pc'])}
end
local function json(v)
 if type(v)=='string'then return '"'..v:gsub('[%z\1-\31\\"]',function(c)
  return({['"']='\\"',['\\']='\\\\',['\n']='\\n',['\r']='\\r',['\t']='\\t'})[c]or string.format('\\u%04x',c:byte())end)..'"'
 elseif type(v)=='table'then local z={};if #v>0 then for _,a in ipairs(v)do z[#z+1]=json(a)end;return '['..table.concat(z,',')..']'end
  local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys)
  for _,k in ipairs(keys)do z[#z+1]=json(k)..':'..json(v[k])end;return '{'..table.concat(z,',')..'}'
 elseif v==nil then return 'null'else return tostring(v)end
end
local frame,polls,mask,loops,captures=0,0,0,0,0
local done,entered,failure=false,false,nil
local firstArea,firstLives,first12X,control12,menuReadyAt=nil,nil,nil,0,nil
local previousLives,maxLives,lifeGains,lifeDecreases,deathStateSeen=nil,nil,0,0,false
local sourceBytes,physicalBytes,dmas,chrChecks,nmis,irqs,minSP=0,0,0,0,0,0,255
local maskValue,chrUpper,chrBanks=0,0,{}
local activeLoop,previousLoop,nmiSaved,irqSaved
-- BEGIN STATIONARY_WATCHDOG_LOCAL_V3
local stationaryCount,maxStationary=0,0
-- END STATIONARY_WATCHDOG_LOCAL_V3
local captureStamp={}
local files={}
local function file(name,header)
 local f=assert(io.open(C.prefix..name,'w'));if header then f:write(header..'\n')end;files[#files+1]=f;return f
end
local inputs=file('inputs.csv','poll,frame,mask')
local trace=file('trace.csv','frame,poll,ppu_frame,loops,captured,world,level,area,x,y,yHigh,state,vx,vy,power,engine,mode,task,lives,camera,mask,ceiling,dash,jumpUsed,loopCycles,interruptCycles,foregroundCycles')
local events=file('events.jsonl')
local eventCount=0
local function event(kind,data)
 eventCount=eventCount+1;assert(eventCount<=30000,'Bounded route event log')
 events:write(json({kind=kind,stamp=stamp(),frame=frame,poll=polls,data=data})..'\n');events:flush()
end
local function fail(why,data)
 if not failure then failure=why;event('first-failure',{reason=why,detail=data})end
end
local function check(ok,why,data)if not ok then fail(why,data)end;return ok end
local codec=dofile(C.root..'/tools/audit/final_inventory_compact_capture_v1.lua')
local capture=codec.install(C.prefix,{container_bytes=C.capture_bytes,records=C.limit+8},function()return captureStamp end)
local full=assert(io.open(C.prefix..'actual-ppu.argb','wb'))
local markers={}
local function mark(name,raw)
 if markers[name]then return end
 assert(#C.marker_names<=8,'At most eight review markers')
 local f=assert(io.open(C.prefix..name..'.argb','wb'));f:write(raw);f:close()
 markers[name]={frame=frame,full_ordinal=captures,stamp=captureStamp}
 event('capture-marker',{name=name,full_ordinal=captures})
end
local function scope()
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
local function identity()
 check(r('SelectedCharacter')==C.character,'Requested character readback')
 if C.variant_symbol then check(r(C.variant_symbol)==C.variant,'Requested alternate readback')end
 check(r('CrossoverBehaviorVersion')==C.mode_value,'Actual numeric Easy/Hard readback')
 check(r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Cheats and starting-level override remain off')
end
local function context()
 local c={frame=frame,poll=polls,char=C.character,variant=C.variant,r=r,
  x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),yHigh=r('Player_Y_HighPos'),state=r('Player_State'),
  vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),world=r('WorldNumber'),level=r('LevelNumber'),
  area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),
  lastMask=mask,lastA=mask&128~=0,grounded=r('Player_State')==0,stageFrame=frame-(menuReadyAt or frame)}
 c.block=function(wx,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16))
 end
 c.enemy=function()
  local nearest
  for i=0,5 do local flag,id,st=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
   if flag>0 and flag<128 and(id<0x15 or id==0x2d or id==0x33)and st<0x20 and not(id==6 and st>=2)then
    local x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i);local dx=x-c.x
    if dx> -160 and dx<160 and(not nearest or math.abs(dx)<math.abs(nearest.dx))then
     nearest={slot=i,id=id,x=x,y=r('Enemy_Y_Position',i),state=st,dx=dx}end
   end
  end;return nearest
 end
 return c
end
local choose=assert(dofile(C.policy))
local fixed={};local replayRows=0
if C.replay then
 for line in io.lines(C.replay)do local p,f,m=line:match('^(%d+),(%d+),(%d+)$')
  if p then p,f,m=tonumber(p),tonumber(f),tonumber(m);assert(p==replayRows+1,'Consecutive replay polls');fixed[p]={frame=f,mask=m};replayRows=p end
 end
end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
local function unpackMask(m)local b={};for k,v in pairs(bits)do b[k]=m&v~=0 end;return b end
local function pack(b)local m=0;for k,v in pairs(bits)do if b[k]then m=m|v end end;return m end
local nextMenuPoll=0
local function pulse(key)
 if polls<nextMenuPoll then return{}end;nextMenuPoll=polls+8;return{[key]=true}
end
local function menu()
 if frame<45 or r('CrossoverTitleDrawn')==0 then return{}end
 local state=r('CrossoverMenuState')
 if state==0 then
  local want=r('CrossoverBehaviorVersion')==C.mode_value and 0 or 1
  if r('CrossoverOptionsFocus')~=want then return pulse('down')end
  return pulse(want==0 and 'start' or 'a')
 elseif state==4 then
  if r('CrossoverOptionsFocus')~=1 then return pulse('down')end
  if r('CrossoverBehaviorVersion')~=C.mode_value then return pulse('a')end
  return pulse('b')
 elseif state==2 then
  if r('CrossoverMenuIndex')~=C.menu_index then
   return pulse(assert(C.navigation[r('CrossoverMenuIndex')+1],'Compiled menu route'))
  end
  if C.variant_symbol and r(C.variant_symbol)~=C.variant then return pulse('select')end
  identity();return pulse('start')
 end
 return{}
end
local function hookBank(h,physical)
 if h.banks then
  for _,b in ipairs(h.banks)do if physical==b then return true end end
  return false
 end
 return physical==h.bank
end
local function hook(h,fn)
 emu.addMemoryCallback(function(pc)
  if done or not hookBank(h,bank(pc))then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook bytes: '..h.name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function shadowWindow(pc,target,shadow)
 local function store(at,a)return emu.read(at,emu.memType.nesDebug)==0x8d and emu.read(at+1,emu.memType.nesDebug)==a%256 and emu.read(at+2,emu.memType.nesDebug)==a//256 end
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
local function interruptEntry(s)
 local sp=s['cpu.sp'];minSP=math.min(minSP,sp)
 local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 local q={sp=sp,a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],p=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug),start=s['cpu.cycleCount'],
  ba=bank(0xa000),bc=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,
  interrupted_pc=pc,interrupted_opcode={},fields={}}
 for i=0,3 do q.interrupted_opcode[#q.interrupted_opcode+1]=emu.read(pc+i,emu.memType.nesDebug)end
 q.wa=q.ba~=q.sa and shadowWindow(pc,0x5115,L.CurrentBank)
 q.wc=q.bc~=q.sc and shadowWindow(pc,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do q.fields[#q.fields+1]=emu.read(a,emu.memType.nesDebug)end
 return q
end
local function interruptReturn(s,q,kind)
 if not q then return end
 check(s['cpu.sp']==q.sp and s['cpu.a']==q.a and s['cpu.x']==q.x and s['cpu.y']==q.y,kind..' restores AXY/SP')
 check(emu.read(0x100+(q.sp+1)%256,emu.memType.nesDebug)==q.p,kind..' preserves the real stacked P')
 -- NMI AudioUpdate may finish a genuine interrupted shadow->mapper gap.
 -- The native68-byte IRQ never writes PRG banks and must keep physical entry banks.
 local expectedA=kind=='NMI'and q.wa and q.sa or q.ba
 local expectedC=kind=='NMI'and q.wc and q.sc or q.bc
 check(bank(0xa000)==expectedA and bank(0xc000)==expectedC,kind..' restores actual A/C banks',
  {entry=q,actual_A=bank(0xa000),actual_C=bank(0xc000),shadow_A=r('CurrentBank')&127,
   shadow_C=r('CurrentBankC')&127,expected_A=expectedA,expected_C=expectedC,nmi_gap_normalization=kind=='NMI'})
 check((r('CurrentBank')&127)==q.sa and(r('CurrentBankC')&127)==q.sc,kind..' restores bank shadows')
 for i,a in ipairs(C.smc_fields)do check(emu.read(a,emu.memType.nesDebug)==q.fields[i],kind..' restores five SMC operands')end
 if activeLoop and kind=='NMI' then activeLoop.interrupt=activeLoop.interrupt+s['cpu.cycleCount']-q.start end
 if activeLoop and kind=='IRQ' and not nmiSaved then activeLoop.interrupt=activeLoop.interrupt+s['cpu.cycleCount']-q.start end
end
hook(C.hooks.nmi,function(s)if entered then nmiSaved=interruptEntry(s);nmis=nmis+1 end end)
hook(C.hooks.nmi_return,function(s)interruptReturn(s,nmiSaved,'NMI');nmiSaved=nil end)
hook(C.hooks.irq,function(s)if entered then irqSaved=interruptEntry(s);irqs=irqs+1 end end)
hook(C.hooks.irq_return,function(s)interruptReturn(s,irqSaved,'IRQ');irqSaved=nil end)
hook(C.hooks.loop,function(s)check(activeLoop==nil,'No nested foreground GameLoop');activeLoop={sp=s['cpu.sp'],start=s['cpu.cycleCount'],interrupt=0}end)
local lastCycles,lastInterrupt=0,0
hook(C.hooks.loop_return,function(s)
 local a=activeLoop;if not a then return end
 check(a.sp==s['cpu.sp'],'Completed GameLoop returns at entry SP')
 loops=loops+1;lastCycles=s['cpu.cycleCount']-a.start;lastInterrupt=a.interrupt;activeLoop=nil
 if not scope()then previousLoop=nil;return end
 local c=context();identity()
 -- BEGIN STATIONARY_WATCHDOG_UPDATE_V3
 local clocking=entered and r('TimerControl')==0 and opt('GamePauseStatus')==0 and opt('InvRefill')==0
 if clocking and previousLoop and previousLoop.world==c.world and previousLoop.level==c.level and previousLoop.area==c.area
  and previousLoop.x==c.x and previousLoop.y==c.y then stationaryCount=stationaryCount+1 else stationaryCount=0 end
 maxStationary=math.max(maxStationary,stationaryCount)
 check(stationaryCount<300,'Controller stationary for 300 genuinely active completed updates',
  {updates=stationaryCount,x=c.x,y=c.y,state=c.state,buttons=mask,enemy=c.enemy(),policy=C.policy})
 -- END STATIONARY_WATCHDOG_UPDATE_V3
 if previousLoop and previousLoop.world==c.world and previousLoop.level==c.level and previousLoop.area==c.area then
  local dx=c.x-previousLoop.x;local dc=c.camera-previousLoop.camera
  -- GuestCameraCatchUp permits a five-pixel moving catch-up step.
  local cameraLimit=(C.character~=0 and C.character~=8)and 5 or 4
  check(math.abs(dx)<=8 and dc>=0 and dc<=cameraLimit,'Completed native world/camera step bound',{previous=previousLoop,current={x=c.x,y=c.y,camera=c.camera},dx=dx,camera_step=dc})
 end
 previousLoop={world=c.world,level=c.level,area=c.area,x=c.x,y=c.y,camera=c.camera}
 if entered and c.world==0 and c.level==1 then
  control12=control12+1;if not first12X then first12X=c.x end
 end
 if c.world==0 and c.level==0 and c.x>=280 and c.x<=460 then
  event('corner-completed-loop',{x=c.x,y=c.y,vy=c.vy,state=c.state,ceiling=opt('SmCeilingHit'),
   cycles=lastCycles,interrupt_cycles=lastInterrupt,foreground_cycles=lastCycles-lastInterrupt})
 end
end)
emu.addMemoryCallback(function(_,v)
 local old=maskValue;maskValue=v
 if entered and scope()and r('DisableScreenFlag')==0 and old&24==0 and v&24~=0 then
  local s=stamp();local safe=s.scanline>=241 and s.scanline<=260 or s.scanline==-1 and s.dot<=274
  check(safe,'Active render enable precedes pre-render vertical reload',s)
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)chrUpper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)chrBanks[a-0x5120]=v+256*chrUpper end,emu.callbackType.write,0x5120,0x512b)
local dma
local function bytes(at,kind)local t={};for i=0,255 do t[#t+1]=string.char(emu.read(at+i,kind))end;return table.concat(t)end
local function hex(s)return(s:gsub('.',function(c)return string.format('%02x',c:byte())end))end
emu.addMemoryCallback(function(_,page)
 check(dma==nil,'Prior DMA has reached genuine completion')
 dma={source=bytes(page*256,emu.memType.nesDebug),count=0,start=stamp(),page=page,mask=maskValue,
  oamaddr=emu.getState()['ppu.spriteRamAddr']}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 if not dma then return end
 local s=emu.getState();local i=dma.count+1
 check(i<=256 and v==dma.source:byte(i)and s['ppu.spriteRamAddr']==i-1 and maskValue&24==0,'Actual DMA source/value/destination/render guard',{ordinal=i,value=v,oamaddr=s['ppu.spriteRamAddr']})
 dma.count=i
end,emu.callbackType.write,0x2004)
hook(C.hooks.dma_complete,function()
 if not check(dma~=nil,'Actual post-DMA completion has a request')then return end
 local q=dma;dma=nil;local hw=bytes(0,emu.memType.nesSpriteRam);dmas=dmas+1
 local same=true;for i=1,256 do local want=q.source:byte(i);if (i-1)%4==2 then want=want&0xe3 end;if hw:byte(i)~=want then same=false end end
 check(q.page==2 and q.start.pc==C.dma_store_return and hookBank(C.hooks.dma_complete,q.start.bank)and q.count==256 and q.oamaddr==0 and emu.getState()['ppu.spriteRamAddr']==0 and q.mask&24==0 and maskValue&24==0 and same,
  'Completed 256-byte physical DMA (hardware attributes E3 only)',{count=q.count,start=q.start,complete=stamp(),source=hex(q.source),physical=hex(hw)})
 sourceBytes=sourceBytes+256;if same then physicalBytes=physicalBytes+256 end
end)
emu.addMemoryCallback(function(a,v)
 if entered and not done and r('WorldNumber')==0 and r('LevelNumber')==0 then
  local x=pos('Player_X_Position','Player_PageLoc')
  if x>=280 and x<=460 then event('corner-position-write',{address=a,before=emu.read(a,emu.memType.nesDebug),value=v,x=x,y=r('Player_Y_Position'),row=r('R2'),tile=r('R3')})end
 end
end,emu.callbackType.write,L.Player_X_Position,L.Player_X_Position)
emu.addMemoryCallback(function()
 if entered then check(emu.getState()['cpu.sp']>=128,'Native lower stack guard')end
end,emu.callbackType.write,0x17f)
emu.addEventCallback(function()
 if done then return end;polls=polls+1;local b
 if C.replay then local q=assert(fixed[polls],'Fixed replay stream exhausted');assert(q.frame==frame,'Exact replay poll/frame');b=unpackMask(q.mask)
 else b=not entered and menu()or(scope()and choose(context())or{})end
 mask=pack(b);inputs:write(polls..','..frame..','..mask..'\n');emu.setInput(b,0)
end,emu.eventType.inputPolled)
local function finish(passed,reason)
 if done then return end;done=true
 full:close();capture.close()
 local bass=C.bass_close and C.bass_close()or nil
 local result={passed=passed,reason=reason,ROM_sha256=C.ROM_sha256,identity=C.name,actual_mode=r('CrossoverBehaviorVersion'),
  frames=frame,polls=polls,completed_loops=loops,full_frames=captures,markers=markers,real_1_1_seen=entered,
  real_1_2_control_updates=control12,zero_deaths=firstLives~=nil and lifeDecreases==0 and not deathStateSeen,
  lives={start=firstLives,ending=r('NumberofLives'),maximum=maxLives,gained=lifeGains,decreased=lifeDecreases,death_state_seen=deathStateSeen},
  cheats_off=r('CheatInvincible')==0 and r('CheatStartLevel')==0,nmi_checks=nmis,irq_checks=irqs,min_SP=minSP,
  completed_DMAS=dmas,unmasked_source_writes_checked=sourceBytes,physical_E3_bytes_checked=physicalBytes,
  chr_window_checks=chrChecks,adapter=capture.stats(),bass_collision=bass,
  scope='Controller-only current 1-1 to controlled 1-2. Selected PPU review remains separate; no every-item/ability/source-fidelity/FPS claim.'}
 -- BEGIN STATIONARY_WATCHDOG_RESULT_V3
 result.stationary_watchdog={limit=300,consecutive=stationaryCount,maximum=maxStationary,unit='genuinely active completed updates; pause/transform/refill excluded'}
 -- END STATIONARY_WATCHDOG_RESULT_V3
 local f=assert(io.open(C.prefix..'result.json','w'));f:write(json(result)..'\n');f:close()
 for _,q in ipairs(files)do q:close()end
 print('ROSTER1-1 '..C.name..' mode='..C.mode_value..' passed='..tostring(passed)..' reason='..tostring(reason)..' frame='..frame)
 emu.stop(passed and 0 or 1)
end
local lastPower
emu.addEventCallback(function()
 if done then return end;frame=frame+1;local c=context();local s=emu.getState();minSP=math.min(minSP,s['cpu.sp'])
 if not entered and scope()then
  identity();check(c.world==0 and c.level==0,'Natural start is World 1-1')
  entered=true;menuReadyAt=frame;firstArea=c.area;firstLives=r('NumberofLives');event('first-active',{x=c.x,y=c.y,mode=r('CrossoverBehaviorVersion')})
  previousLives=firstLives;maxLives=firstLives
 end
 if entered then
  local lives=r('NumberofLives')
  if lives<previousLives then lifeDecreases=lifeDecreases+previousLives-lives end
  if lives>previousLives then
   lifeGains=lifeGains+lives-previousLives;event('earned-life-gain',{before=previousLives,after=lives,amount=lives-previousLives})
  end
  maxLives=math.max(maxLives,lives)
  deathStateSeen=deathStateSeen or c.engine==11 or r('OperMode')==3
  check(lifeDecreases==0 and not deathStateSeen,'Zero-death 1-1 route',
   {previous=previousLives,current=lives,decreases=lifeDecreases,death_state_seen=deathStateSeen})
  previousLives=lives
  check(c.world==0 and(c.level==0 or c.level==1),'Only genuine 1-1 then 1-2 progression')
  for i=0,11 do if chrBanks[i]~=nil then
   check(s['mapper.chrBanks'..i]==chrBanks[i],'Physical CHR write-time latch window '..i);chrChecks=chrChecks+1
  end end
 end
 local endpoint=entered and c.world==0 and c.level==1 and scope()and control12>=25 and c.x>first12X+5
 if entered and(c.level==0 or endpoint or failure)then
  local screen=emu.getScreenBuffer();assert(#screen==256*240,'Actual full PPU dimensions')
  local t={};for i,v in ipairs(screen)do t[i]=string.pack('<I4',v)end;local raw=table.concat(t)
  captureStamp=stamp();full:write(raw);captures=captures+1
  if frame==menuReadyAt then mark('first-active',raw)end
  for _,x in ipairs({332,345,360})do if c.level==0 and c.x>=x then mark('corner-'..x,raw)end end
  if lastPower~=nil and c.status~=lastPower then mark('power-change',raw)end
  if c.level==0 and c.x>=3120 then mark('flagpole',raw)end
  if endpoint then mark('endpoint',raw)end
  if failure or frame>=C.limit then mark('failure',raw)end
 end
 lastPower=c.status
 trace:write(table.concat({frame,polls,s['ppu.frameCount'],loops,captures,c.world,c.level,c.area,c.x,c.y,c.yHigh,c.state,c.vx,c.vy,c.status,c.engine,
  r('OperMode'),r('OperMode_Task'),r('NumberofLives'),c.camera,mask,opt('SmCeilingHit'),opt('XgDash'),opt('XgJumpUsed'),lastCycles,lastInterrupt,lastCycles-lastInterrupt},',')..'\n')
 if failure then finish(false,failure);return end
 if endpoint then check(not C.replay or polls==replayRows,'Complete independent replay consumes every poll');finish(failure==nil,failure or 'cleared 1-1 and controlled 1-2');return end
 if frame>=C.limit then finish(false,'finite frame bound');return end
end,emu.eventType.endFrame)
