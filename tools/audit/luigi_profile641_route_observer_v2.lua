-- Additive read-only route observation; generated module inserts the qualified
-- literal731 DMA body at its marker. No controller or emulated-state writes.
local C=assert(LUIGI_ROUTE_OBSERVER)
local OUTPUT=assert(ROSTER_CONFIG.out)
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function bytes(at,kind)local t={};for i=0,255 do t[#t+1]=string.char(emu.read(at+i,kind))end;return table.concat(t)end
local function json(v)
 if type(v)=='table'then
  local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',k)..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)
 elseif v==nil then return'null'else return tostring(v)end
end
-- Old item's optional publication fields remain false here. Its full raw DMA
-- oracle is unchanged; the original independent body-publication audit stays.
local entered,done,published=false,false,nil
local dma=nil
-- QUALIFIED_DMA_BODY

local function hook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(function()
  if bank(h.pc)~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual route hook '..n)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function smc()local t={};for _,a in ipairs(C.smc)do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return t end
local function equal(a,b)if #a~=#b then return false end;for i,v in ipairs(a)do if b[i]~=v then return false end end;return true end
local events=assert(io.open(OUTPUT..'route-observation.jsonl','w'))
local function row(q)events:write(json(q)..'\n');events:flush()end
local function stamp(s)
 s=s or emu.getState()
 return{frame=s['ppu.frameCount'],cpu=s['cpu.cycleCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],pc=s['cpu.pc'],sp=s['cpu.sp'],bankA=bank(0xa000),bankC=bank(0xc000)}
end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local nmi,irq,stomp=nil,nil,nil
local nmis,irqs,stomps,updates,draws,commits,minSP=0,0,0,0,0,0,255
local function interruptEntry(kind,s)
 local sp=s['cpu.sp'];minSP=math.min(minSP,sp)
 local q={a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],sp=sp,smc=smc(),shadowA=r('CurrentBank'),shadowC=r('CurrentBankC'),stamp=stamp(s)}
 q.interruptedPC=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
 row({kind=kind..'-entry',stamp=q.stamp,interruptedPC=q.interruptedPC,NmiDisable=r('NmiDisable'),NmiSkipped=r('NmiSkipped')})
 return q
end
local function interruptReturn(kind,q,s)
 assert(q and equal(q.smc,smc()),kind..' actual five live SMC operands restored')
 assert(s['cpu.a']==q.a and s['cpu.x']==q.x and s['cpu.y']==q.y and s['cpu.sp']==q.sp,kind..' actual AXY/SP restored')
 assert(r('CurrentBank')==q.shadowA and r('CurrentBankC')==q.shadowC,kind..' bank shadows restored')
 row({kind=kind..'-return',stamp=stamp(s)})
end
hook('NmiEntry',function(s)assert(not nmi,'No recursive NMI');nmi=interruptEntry('NMI',s);nmis=nmis+1 end)
hook('NmiReturn',function(s)interruptReturn('NMI',nmi,s);nmi=nil end)
hook('IrqEntry',function(s)
 assert(not irq,'No recursive IRQ');irq=interruptEntry('IRQ',s);irqs=irqs+1
 if active()and r('Sprite0HitDetectFlag')~=0 then assert(s['ppu.scanline']==31,'Real gameplay IRQ31')end
end)
hook('IrqReturn',function(s)interruptReturn('IRQ',irq,s);irq=nil end)
hook('GameLoop',function(s)updates=updates+1;row({kind='actual-update-entry',stamp=stamp(s),active=active(),skip=r('ShouldSkipDrawSprites')})end)
hook('GameLoopReturn',function(s)commits=commits+1;row({kind='actual-update-published',stamp=stamp(s),active=active(),NmiDisable=r('NmiDisable')});assert(r('NmiDisable')==0,'Complete Main frame publication')end)
hook('DrawAll',function(s)draws=draws+1;row({kind='actual-draw',stamp=stamp(s),active=active(),skip=r('ShouldSkipDrawSprites')})end)
emu.addMemoryCallback(function(_,v)
 if active()and not nmi and not irq then row({kind='actual-draw-decision-read',stamp=stamp(),value=v})end
end,emu.callbackType.read,L.ShouldSkipDrawSprites)
hook('EnemyStomped',function(s)
 if not active()or nmi or irq then return end
 local i=s['cpu.x'];assert(i>=0 and i<=5,'Real ordinary stomp slot')
 assert(r('SelectedCharacter')==8 and r('MarioVariant')==1 and r('CrossoverBehaviorVersion')==0,'Actual LuigiEasy stomp owner')
 assert(not stomp,'Ordinary stomp calls not nested')
 local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 stomp={slot=i,return_pc=pc,return_sp=(sp+2)%256,return_bank=bank(pc),entry=stamp(s),id=r('Enemy_ID',i),flag=r('Enemy_Flag',i),state=r('Enemy_State',i),playerY=r('Player_Y_Position'),playerVY=r('Player_Y_Speed')}
 row({kind='actual-ordinary-stomp-entry',owner=stomp})
end)
-- All host callback registrations are startup-static; only this Lua slot moves.
emu.addMemoryCallback(function(pc)
 if not stomp then return end
 local s=emu.getState()
 if pc~=stomp.return_pc or s['cpu.sp']~=stomp.return_sp or bank(pc)~=stomp.return_bank then return end
 local q=stomp;stomp=nil;local i=q.slot
 q.complete=stamp(s);q.result={enemyID=r('Enemy_ID',i),enemyState=r('Enemy_State',i),vy=r('Player_Y_Speed'),score=r('FloateyNum_Control',i),timer=r('FloateyNum_Timer',i),scoreX=r('FloateyNum_X_Pos',i),scoreY=r('FloateyNum_Y_Pos',i)}
 row({kind='actual-ordinary-stomp-return',owner=q})
 assert(q.flag>0 and q.flag<128 and q.id~=18 and q.state<32,'Live stomp target admitted')
 assert(q.result.vy>=128 and q.result.score>0 and q.result.timer>0,'Real stomp rebound and floating score')
 stomps=stomps+1
end,emu.callbackType.exec,0,65535)

local pixels=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local index=assert(io.open(OUTPUT..'actual-ppu-index.csv','w'))
index:write('ordinal,ppuFrame,cpuCycle,updates,draws,commits,NmiSkipped,mode,character,variant,power\n')
local frames,closed=0,false
-- Registered before the unchanged harness stop callback.
emu.addEventCallback(function()
 local s=emu.getState();local b=emu.getScreenBuffer();assert(#b==61440,'Actual full256x240 PPU')
 local chunks={};for i=1,#b,8 do chunks[#chunks+1]=string.pack('<I4I4I4I4I4I4I4I4',b[i],b[i+1],b[i+2],b[i+3],b[i+4],b[i+5],b[i+6],b[i+7])end
 pixels:write(table.concat(chunks));pixels:flush();frames=frames+1
 index:write(table.concat({frames,s['ppu.frameCount'],s['cpu.cycleCount'],updates,draws,commits,r('NmiSkipped'),r('CrossoverBehaviorVersion'),r('SelectedCharacter'),r('MarioVariant'),r('PlayerStatus')},',')..'\n');index:flush()
end,emu.eventType.endFrame)
local stop=emu.stop
emu.stop=function(code)
 if not closed then
  closed=true;pixels:close();index:close();events:close();dmaProofLog:close()
  local f=assert(io.open(OUTPUT..'route-observation-result.json','w'))
  f:write(json({passed=code==0 and stomps>0,fullPPUframes=frames,updates=updates,draws=draws,commits=commits,nmiChecks=nmis,irqChecks=irqs,ordinaryStompReturns=stomps,minInterruptSP=minSP,actual_numeric_mode=r('CrossoverBehaviorVersion'),actual_character=r('SelectedCharacter'),actual_variant=r('MarioVariant'),source_publication_optional_field_disabled=true,scope='Additive read-only fullPPU/E008complete256/perwrite/scoped-enable/interrupt/liveSMC/cadence/stomp observation. Existing controller/audit/death/motion/CHR guards remain separate; no universal cadence or visual pass.'}));f:close()
 end
 stop(code)
end
