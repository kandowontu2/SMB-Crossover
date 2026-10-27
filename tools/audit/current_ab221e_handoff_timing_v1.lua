-- Additive read-only diagnostics. Installed before the frozen mechanics/guards.
return function(C)
 local frame,sequence,active,rows,written=0,0,nil,0,0
 local trace_first,trace_last=nil,nil
 local f=assert(io.open(OUTPUT..'handoff-diagnostic.jsonl','w'));f:setvbuf('no')
 local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
 local function hex(at,n,kind)local t={};for i=0,n-1 do t[#t+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)end
 local function json(v)
  if type(v)=='table'then local a={};for k,x in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
  elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
 end
 local function window()local p=emu.getState()['ppu.frameCount'];return trace_first~=nil and p>=trace_first and p<=trace_last end
 local function log(event,extra)
  if not window()then return end
  local s=emu.getState();local v=extra or{}
  v.event=event;v.wall_counter=frame;v.nmi_sequence=sequence;v.in_nmi=active~=nil
  for _,k in ipairs({'cpu.pc','cpu.sp','cpu.a','cpu.x','cpu.y','cpu.ps','cpu.cycleCount','ppu.frameCount','ppu.scanline','ppu.cycle','ppu.spriteRamAddr','ppu.control','ppu.mask','ppu.v','ppu.t','ppu.fineX','ppu.writeToggle'})do v[k]=s[k]end
  v.bank=bank(s['cpu.pc']);v.physicalA=bank(0xa000);v.physicalC=bank(0xc000)
  v.shadowA=r('CurrentBank');v.shadowC=r('CurrentBankC');v.item=r('InvSelected',1)
  v.ownedLo=r('InvOwnedLo',1);v.ownedHi=r('InvOwnedHi',1);v.dirty=r('InvDirty')
  v.hudActive=r('InvHudActive');v.hudPhysical=r('InvHudPhysical');v.reload=r('ReloadCHRBank')
  v.ctrl=r('VRAM_Buffer_AddrCtrl');v.offset1=r('VRAM_Buffer1_Offset');v.offset2=r('VRAM_Buffer2_Offset')
  v.queue1=hex(C.ram.VRAM_Buffer1,84);v.queue2=hex(C.ram.VRAM_Buffer2,84)
  v.opcodes=hex(s['cpu.pc'],8)
  local str=json(v)..'\n';rows=rows+1;written=written+#str
  assert(rows<=3000 and written<=2000000,'Bounded additive diagnostic output')
  f:write(str)
 end
 local function hook(name,fn)
  local h=assert(C.hooks[name])
  emu.addMemoryCallback(function()
   local k=bank(h.pc);local owned=false;for _,b in ipairs(h.banks)do owned=owned or b==k end
   if not owned then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual additive owner '..name)end
   fn(emu.getState())
  end,emu.callbackType.exec,h.pc)
 end
 hook('InventoryGrant',function(s)
  if s['cpu.a']==C.trigger_item and trace_first==nil then
   trace_first=s['ppu.frameCount'];trace_last=trace_first+C.PPU_limit-1
   log('diagnostic-window-armed',{trigger_item=C.trigger_item,first_PPU=trace_first,last_PPU=trace_last})
  end
 end)
 hook('NmiEntry',function(s)sequence=sequence+1;active={cycle=s['cpu.cycleCount'],writes=0};log('nmi-entry')end)
 hook('NmiReturn',function(s)log('nmi-real-RTI-entry',{nmi_CPU=s['cpu.cycleCount']-assert(active).cycle});active=nil end)
 hook('UpdateScreen',function()
  local ptr=r('NmiR0')+256*r('NmiR1');local h=r('NmiR0')
  log('actual-parser-command',{pointer=ptr,command=hex(ptr,40),destination=emu.read(ptr,emu.memType.nesDebug)*256+emu.read(ptr+1,emu.memType.nesDebug),count_flags=emu.read(ptr+2,emu.memType.nesDebug)})
 end)
 hook('BankSwitchCHR',function(s)if active then active.chr=s['cpu.cycleCount']end;log('chr-entry',{current_chr=hex(C.ram.CurrentCHRBank,12),modes=hex(C.ram.X5ChrMode,12)})end)
 hook('BankSwitchCHRReturn',function(s)log('chr-real-RTS-entry',{chr_CPU=active and active.chr and s['cpu.cycleCount']-active.chr or-1,current_chr=hex(C.ram.CurrentCHRBank,12)})end)
 for _,n in ipairs({'InventoryHud','ProtoQueueBasePalette','ProtoFixQueuedPalette','SamusFreezeUpdateScreen'})do hook(n,function()log(n)end)end
 emu.addMemoryCallback(function(_,v)
  log('PPUMASK-before-original-assert',{value=v,nmi_CPU=active and emu.getState()['cpu.cycleCount']-active.cycle or-1,dma_writes=active and active.writes or-1})
 end,emu.callbackType.write,0x2001)
 emu.addMemoryCallback(function(_,v)if active then active.writes=0 end;log('dma-request',{page=v,source256=hex(v*256,256)})end,emu.callbackType.write,0x4014)
 emu.addMemoryCallback(function()if active then active.writes=active.writes+1 end end,emu.callbackType.write,0x2004)
 hook('DmaComplete',function()log('E008-completed-DMA',{writes=active and active.writes or-1,hardware256=hex(0,256,emu.memType.nesSpriteRam)})end)
 emu.addMemoryCallback(function(a,v)log('Buffer1-producer-write',{address=a,value=v})end,emu.callbackType.write,C.ram.VRAM_Buffer1_Offset,C.ram.VRAM_Buffer1+83)
 emu.addMemoryCallback(function(_,v)log('reload-writer',{value=v})end,emu.callbackType.write,C.ram.ReloadCHRBank)
 emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
 -- No screenshot/input/emu.write/remove callback/runtime registration APIs.
end
