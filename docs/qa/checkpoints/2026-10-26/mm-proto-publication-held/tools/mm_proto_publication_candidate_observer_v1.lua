-- Read-only additional ownership observations. Original450 hardware guards
-- and actual input/PPU capture remain in presentation_timing_preflight_v1.lua.
local C=assert(PUBLICATION_OWNERSHIP)
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
local log=assert(io.open(C.out..'ownership.jsonl','w'))
local function row(v)log:write(json(v)..'\n')end
local function bytes(at,n,kind)
 local t={};for i=0,n-1 do t[#t+1]=emu.read(at+i,kind or emu.memType.nesDebug)end;return t
end
local function bank(pc)
 local q=emu.convertAddress(pc);return q and q.address//8192 or -1
end
local function state()
 local t={}
 for _,n in ipairs(C.state_names)do t[n]=r(n)end
 t.ordinary={};for i=0,3 do
  local q={slot=i};for _,n in ipairs(C.ordinary_names)do q[n]=emu.read(C.ram[n]+i,emu.memType.nesDebug)end
  t.ordinary[#t.ordinary+1]=q
 end
 t.special={};for i=0,9 do
  local q={slot=i};for _,n in ipairs(C.special_names)do q[n]=emu.read(C.ram[n]+i,emu.memType.nesDebug)end
  t.special[#t.special+1]=q
 end
 return t
end
local writes,mains,draws,dmas,depth=0,0,0,0,0
local main,draw,pending,lastRelease,lastDraw=nil,nil,nil,nil,nil
local mirror,owners=bytes(0x200,256),{}
local function same(a,b)for i=1,256 do if a[i]~=b[i]then return false end end;return true end
row({kind='initial-source',ppu=stamp(),source=mirror,state=state(),origin='Actual script-start image; future RAM initialization without callbacks is not invented.'})
local function hook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(function()
  if bank(h.pc)~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Ownership hook '..n)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function interrupted(s)
 local sp=s['cpu.sp'];local p=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)
 local lo=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)
 local hi=emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 return{stacked_pc=lo+256*hi,stacked_bank=bank(lo+256*hi),stacked_p=p,sp=sp,callback_pc=s['cpu.pc']}
end
hook('GameLoopEntry',function(s)
 mains=mains+1;main={id=mains,begin=stamp(),sp=s['cpu.sp'],first_write=writes+1,draws=0}
 row({kind='Main-begin',main=main,state=state()})
end)
hook('DrawAll',function(s)
 draws=draws+1;draw={id=draws,main=main and main.id or-1,begin=stamp(),sp=s['cpu.sp'],first_write=writes+1}
 if main then main.draws=main.draws+1 end
 row({kind='DrawAll-begin',construction=draw,state=state()})
end)
hook('RosterReady',function(s)
 lastDraw={id=draw and draw.id or-1,main=main and main.id or-1,ppu=stamp(),sp=s['cpu.sp'],source=bytes(0x200,256),last_write=writes,state=state()}
 row({kind='DrawAll-roster-ready',construction=lastDraw});draw=nil
end)
for _,n in ipairs({'MoveAll','InitializeArea','InitializeGame','MegaClear'})do
 hook(n,function(s)row({kind='lifecycle-or-direct-replacement',name=n,ppu=stamp(),callback_pc=s['cpu.pc'],bank=bank(s['cpu.pc']),main=main and main.id or-1,source_write=writes,state=state()})end)
end
emu.addMemoryCallback(function(a,v)
 writes=writes+1;mirror[a-0x200+1]=v;owners[a-0x200+1]=writes
 local s=emu.getState()
 row({kind='source-write',id=writes,address=a,value=v,callback_pc=s['cpu.pc'],callback_bank=bank(s['cpu.pc']),ppu=stamp(),main=main and main.id or-1,construction=draw and draw.id or-1,nmi_depth=depth})
end,emu.callbackType.write,0x200,0x2ff)
emu.addMemoryCallback(function(_,v)
 local s=emu.getState();local pc=s['cpu.pc']
 row({kind='NmiDisable-write',value=v,callback_pc=pc,bank=bank(pc),ppu=stamp(),main=main and main.id or-1})
 if v==0 and main and pc==C.hooks.GameLoopDone.pc and bank(pc)==126 then
  local source=bytes(0x200,256)
  lastRelease={id=main.id,begin=main.begin,release=stamp(),sp=s['cpu.sp'],writer_pc=pc,writer_bank=126,draws=main.draws,first_write=main.first_write,last_write=writes,last_roster=lastDraw and lastDraw.id or-1,source=source,mirror_exact=same(source,mirror),state=state()}
  row({kind='Main-release',main=lastRelease});log:flush()
 end
end,emu.callbackType.write,C.ram.NmiDisable)
hook('GameLoopDone',function(s)
 row({kind='Main-return',main=main and main.id or-1,ppu=stamp(),sp=s['cpu.sp'],last_release=lastRelease and lastRelease.id or-1});main=nil
end)
hook('NmiEntry',function(s)
 depth=depth+1;row({kind='NMI-acceptance',ppu=stamp(),interrupted=interrupted(s),main=main and main.id or-1,construction=draw and draw.id or-1,last_release=lastRelease and lastRelease.id or-1,last_roster=lastDraw and lastDraw.id or-1,source_write=writes,state=state(),depth=depth})
end)
hook('NmiReturn',function(s)row({kind='NMI-return',ppu=stamp(),main=main and main.id or-1,sp=s['cpu.sp'],depth=depth,state=state()});depth=depth-1 end)
emu.addMemoryCallback(function(_,v)
 local s=emu.getState()
 row({kind='publication-state-write',value=v,callback_pc=s['cpu.pc'],callback_bank=bank(s['cpu.pc']),ppu=stamp(),main=main and main.id or-1,construction=draw and draw.id or-1,nmi_depth=depth})
end,emu.callbackType.write,C.ram.MmPublicationState)
emu.addMemoryCallback(function(_,v)
 assert(not pending,'Ownership observer DMA pair is not nested')
 dmas=dmas+1;local s=emu.getState();local source=bytes(v*256,256)
 pending={id=dmas,start=stamp(),page=v,source=source,source_write=writes,last_source_writer_per_byte=owners,mirror_exact=same(source,mirror),callback_pc=s['cpu.pc'],callback_bank=bank(s['cpu.pc']),main=main and main.id or-1,construction=draw and draw.id or-1,last_release=lastRelease,last_roster=lastDraw,state=state()}
 -- Serialize provenance before any original hardware assertion can fail.
 row({kind='DMA-source-owner',DMA=pending});log:flush()
end,emu.callbackType.write,0x4014)
hook('DmaComplete',function()
 if not pending then return end
 local q=pending;pending=nil
 row({kind='DMA-completed-owner',id=q.id,ppu=stamp(),source_write=writes,hardware=bytes(0,256,emu.memType.nesSpriteRam),last_release=q.last_release and q.last_release.id or-1,last_roster=q.last_roster and q.last_roster.id or-1});log:flush()
end)
emu.addEventCallback(function()
 local p=stamp()
 if p.frame>=176 and p.frame<=C.limit then
  row({kind='visible-cutoff-owner',ppu=p,completed_DMAs=dmas,source_write=writes,main=main and main.id or-1,construction=draw and draw.id or-1,last_release=lastRelease and lastRelease.id or-1,last_roster=lastDraw and lastDraw.id or-1,state=state()})
 end
 log:flush()
 if p.frame>=C.limit then
  local f=assert(io.open(C.out..'ownership-result.json','w'))
  f:write(json({observations_complete=true,qualification=false,ROM_sha256=C.ROM_sha256,Main_entries=mains,roster_draws=draws,source_writes=writes,observed_DMA_starts=dmas,pending_DMA=pending~=nil,limits='Read-only finite ownership diagnostic. All original450 hardware/PPU/IRQ/SMC/input guards remain separately authoritative. Callback PC is labeled literally; no invented instruction-start provenance.'})..'\n');f:close();log:close()
 end
end,emu.eventType.endFrame)
