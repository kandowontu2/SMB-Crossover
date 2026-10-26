-- Read-only physical timing preflight. Only controller inputs alter emulation.
local C=assert(PRESENTATION_PREFLIGHT)
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function stamp()
 local s=emu.getState()
 return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],cpu=s['cpu.cycleCount']}
end
local function json(v)
 if type(v)=='table'then
  local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end
  table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)
 elseif v==nil then return'null'else return tostring(v)end
end
local log=assert(io.open(C.out..'timing.jsonl','w'))
local pixels=assert(io.open(C.out..'direct.argb','wb'))
local index=assert(io.open(C.out..'direct-index.csv','w'))
index:write('ppuFrame,cpuCycle,pixels\n')
local function row(v)log:write(json(v)..'\n');log:flush()end
local function bytes(at,n,kind)
 local t={};for i=0,n-1 do t[#t+1]=emu.read(at+i,kind or emu.memType.nesDebug)end;return t
end
local function equal(a,b)
 if #a~=#b then return false end
 for i,v in ipairs(a)do if b[i]~=v then return false end end;return true
end
local function scope()
 if r('DisableScreenFlag')~=0 then return false end
 return r('CrossoverMenuState')==2 and r('OperMode')==0 or
  r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
-- PURE_ENABLE_DEADLINE_BEGIN
function PRESENTATION_SAFE_ENABLE(line,dot)
 return line>=241 and line<=260 or line==-1 and dot<=274
end
-- PURE_ENABLE_DEADLINE_END
local mask,ctrl,pending,nmi,depth=0,0,nil,nil,0
local dmas,nmis,irqs,enables,late,hardwareBad,frames,polls=0,0,0,0,0,0,0,0
local fixed={}
for line in io.lines(C.prefix)do
 local frame,value=line:match('^(%d+),(%d+)$')
 if frame then fixed[tonumber(frame)]=tonumber(value)end
end
local function hook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.pc);if not p or p.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..n)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function smc()local t={};for _,a in ipairs(C.smc)do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return t end
hook('NmiEntry',function(s)
 assert(not nmi,'No recursive NMI in bounded preflight')
 nmi={a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],sp=s['cpu.sp'],smc=smc(),bankA=r('CurrentBank'),bankC=r('CurrentBankC')}
 depth=depth+1;nmis=nmis+1;row({kind='NMI-entry',ppu=stamp(),depth=depth,scope=scope(),sprite0=r('Sprite0HitDetectFlag'),reload=r('ReloadCHRBank'),wide=r('X5WideChrActive')})
end)
hook('NmiReturn',function(s)
 assert(nmi and equal(smc(),nmi.smc),'NMI five SMC bytes restored')
 assert(s['cpu.a']==nmi.a and s['cpu.x']==nmi.x and s['cpu.y']==nmi.y and s['cpu.sp']==nmi.sp,'NMI AXY/SP restored')
 assert(r('CurrentBank')==nmi.bankA and r('CurrentBankC')==nmi.bankC,'NMI bank shadows restored')
 row({kind='NMI-return',ppu=stamp(),depth=depth});depth=depth-1;nmi=nil
end)
hook('IrqEntry',function()
 if scope()and r('Sprite0HitDetectFlag')~=0 then
  local p=stamp();irqs=irqs+1;row({kind='IRQ31',ppu=p,nmi_depth=depth})
  assert(p.scanline==31,'Actual native HUD IRQ31')
 end
end)
hook('DmaComplete',function()
 if not pending then return end
 local q=pending;pending=nil
 q.complete=stamp();q.hardware=bytes(0,256,emu.memType.nesSpriteRam)
 q.completed_writes=q.writes;q.equal=equal(q.source,q.hardware);q.end_mask=mask
 row({kind='DMA-complete',DMA=q})
 assert(q.writes==256 and mask&24==0,'All DMA writes completed while rendering disabled')
 if not q.equal then hardwareBad=hardwareBad+1 end
end)
emu.addMemoryCallback(function(_,v)
 local old=mask;mask=v;local p=stamp()
 if old&24==0 and v&24~=0 and scope()then
  enables=enables+1;local safe=PRESENTATION_SAFE_ENABLE(p.scanline,p.dot)
  if not safe then late=late+1 end
  row({kind='render-enable',ppu=p,value=v,safe=safe,menu=r('CrossoverMenuState'),oper=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine')})
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(_,v)
 assert(not pending,'No unfinished DMA')
 local s=emu.getState();assert(s['cpu.pc']==C.hooks.DmaBefore.pc and v==2,'Real page2 DMA owner')
 for i,x in ipairs(C.hooks.DmaBefore.bytes)do assert(emu.read(s['cpu.pc']+i-1,emu.memType.nesDebug)==x,'Real postDMA instructions')end
 assert(mask&24==0,'Rendering disabled before DMA')
 dmas=dmas+1;pending={id=dmas,start=stamp(),source=bytes(v*256,256),writes=0,mask=mask,ctrl=ctrl,scope=scope()}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 assert(pending,'Associated actual DMA data writer')
 local q=pending;q.writes=q.writes+1
 if q.writes==1 then q.first=stamp()end;q.last=stamp()
 assert(mask&24==0,'Rendering stays disabled during every DMA write')
end,emu.callbackType.write,0x2004)
for _,a in ipairs({0x5203,0x5204})do
 emu.addMemoryCallback(function(_,v)row({kind='IRQ-arm',address=a,value=v,ppu=stamp(),nmi_depth=depth})end,emu.callbackType.write,a)
end
hook('UpdateScreen',function()
 local p=stamp()
 if p.frame>=350 and p.frame<=380 then
  local ptr=r('NmiR0')+256*r('NmiR1')
  row({kind='actual-VRAM-parser',ppu=p,pointer=ptr,packet=bytes(ptr,128),reload=r('ReloadCHRBank'),wide=r('X5WideChrActive'),depth=depth})
 end
end)
local keys={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
emu.addEventCallback(function()
 local p=stamp();local value=fixed[p.frame]or 0;local input={}
 for n,bit in pairs(keys)do input[n]=value&bit~=0 end
 polls=polls+1;emu.setInput(input,0);row({kind='input',ppu=p,mask=value,poll=polls})
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 local p=stamp()
 if p.frame>=176 and p.frame<=C.limit then
  local buf=emu.getScreenBuffer();assert(#buf==61440,'Actual PPU buffer size')
  local chunks={};for i,v in ipairs(buf)do chunks[i]=string.pack('<I4',v)end
  pixels:write(table.concat(chunks));index:write(p.frame..','..p.cpu..','..#buf..'\n');frames=frames+1
 end
 if p.frame>=C.limit then
  assert(not pending,'No terminal pending DMA')
  assert(r('SelectedCharacter')==1 and r('ProtoVariant')==0 and r('CrossoverBehaviorVersion')==0,'Real selected MegaEasy')
  assert(r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'Actual active gameplay endpoint')
  local q={passed=late==0 and hardwareBad==0 and enables>20 and dmas>100 and irqs>20,
   native_run=true,ROM_sha256=C.ROM_sha256,late_enable_count=late,hardware_mismatch_count=hardwareBad,
   completed_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqs,scoped_enables=enables,captured_actual_frames=frames,polls=polls,
   limits='One finite fixed-input MegaEasy startup/menu/first-active timing diagnostic. Full256 OAM and all5SMC/AXY/SP checks; no sprite fairness, campaign, full route, all-roster or adoption claim.'}
  local f=assert(io.open(C.out..'result.json','w'));f:write(json(q)..'\n');f:close()
  log:close();pixels:close();index:close();emu.stop(q.passed and 0 or 1)
 end
end,emu.eventType.endFrame)
