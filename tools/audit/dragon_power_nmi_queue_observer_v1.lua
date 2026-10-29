-- Passive bounded actual NMI/queue evidence. Startup registrations only.
return function(C,L,api)
 local D=assert(C.diagnostic);local ram=assert(D.ram)
 for _,name in ipairs(D.fields)do assert(type(ram[name])=='number','Bound diagnostic RAM '..name)end
 local function rd(a)return emu.read(a,emu.memType.nesDebug)end
 local function r(n,i)return rd(assert(ram[n],n)+(i or 0))end
 local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or-1 end
 local function state()
  local s=emu.getState();local f,p,l=api.clock()
  return{frame=f,poll=p,loops=l,ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],
   cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y']}
 end
 local function active(s)return s.ppu_frame>=D.first and s.ppu_frame<=D.last end
 local function bytes(at,n)local a={};for i=0,n-1 do a[#a+1]=string.format('%02x',rd((at+i)&65535))end;return table.concat(a)end
 local function packet(at)
  local begin=at;local cmds={};local consumed=0;local terminal=false
  for _=1,32 do
   local hi=rd(at);if hi==0 then terminal=true;consumed=consumed+1;break end
   local lo,flags=rd((at+1)&65535),rd((at+2)&65535);local n=flags&63
   if n==0 then return{pointer=begin,commands=cmds,malformed_zero_length=true,raw=bytes(begin,math.min(consumed+3,192))}end
   local payload=flags&64~=0 and 1 or n
   if consumed+3+payload>191 then break end
   cmds[#cmds+1]={destination=hi*256+lo,flags=flags,count=n,repeat_byte=flags&64~=0,vertical=flags&128~=0,data=bytes((at+3)&65535,payload)}
   consumed=consumed+3+payload;at=(at+3+payload)&65535
  end
  return{pointer=begin,commands=cmds,terminal=terminal,truncated=not terminal,raw=bytes(begin,consumed)}
 end
 local function snapshot()
  local z={};for _,n in ipairs(D.fields)do z[n]=r(n)end
  z.Buffer1=bytes(ram.VRAM_Buffer1,84);z.Buffer2=bytes(ram.VRAM_Buffer2,34)
  z.freeze_packet=bytes(ram.SmFreezePalettePacket,7);z.chr_modes=bytes(ram.X5ChrMode,12)
  local ctrl=z.VRAM_Buffer_AddrCtrl
  z.selected_pointer=rd(D.pointer_low+ctrl)+256*rd(D.pointer_high+ctrl)
  z.selected_packet=packet(z.selected_pointer)
  z.live_Nmi_pointer=z.NmiR0+256*z.NmiR1
  return z
 end
 local log=assert(io.open(C.prefix..'nmi-queues.jsonl','w'));local rows,total=0,0
 local function emit(kind,data)
  local s=state();if not active(s)then return end
  local text=api.json({kind=kind,stamp=s,data=data})..'\n';rows=rows+1;total=total+#text
  assert(rows<=D.row_cap and total<=D.byte_cap,'Bounded NMI diagnostic output')
  log:write(text);log:flush()
 end
 local function matches(h,b)
  for _,v in ipairs(h.banks or{h.bank})do if b==v then return true end end
  return false
 end
 local function at(key,fn)
  local h=assert(D.hooks[key]);assert(type(h.pc)=='number'and h.pc>=0x8000 and #h.bytes==3,'Static actual hook '..key)
  emu.addMemoryCallback(function(pc)
   if not matches(h,bank(pc))then return end
   for i,v in ipairs(h.bytes)do assert(rd(h.pc+i-1)==v,'Actual diagnostic hook '..key)end
   if active(state())then fn()end
  end,emu.callbackType.exec,h.pc)
 end
 at('nmi',function()emit('NMI-entry',snapshot())end)
 at('normal',function()emit('normal-NMI-branch',snapshot())end)
 at('nmi_return',function()emit('NMI-RTI',snapshot())end)
 at('update',function()emit('UpdateScreen-entry',{pointer=r('NmiR0')+256*r('NmiR1'),packet=packet(r('NmiR0')+256*r('NmiR1'))})end)
 at('command',function()emit('parser-command',{pointer=r('NmiR0')+256*r('NmiR1'),packet=packet(r('NmiR0')+256*r('NmiR1'))})end)
 at('screen_done',function()emit('UpdateScreen-InitScroll',{NmiR0=r('NmiR0'),NmiR1=r('NmiR1')})end)
 at('chr',function()emit('BankSwitchCHR-entry',snapshot())end)
 at('chr_return',function()emit('BankSwitchCHR-return',{ReloadCHRBank=r('ReloadCHRBank'),wide=r('X5WideChrActive')})end)
 at('publish',function()emit('X5PublishChr-entry',{ReloadCHRBank=r('ReloadCHRBank'),wide=r('X5WideChrActive'),modes=bytes(ram.X5ChrMode,12)})end)
 at('pre_dma',function()emit('OAMandReadJoypad-entry',snapshot())end)
 at('dma_complete',function()emit('actual-DMA-completion',{OAMADDR=emu.getState()['ppu.spriteRamAddr']})end)
 at('hud',function()emit('GokuHUD-entry',snapshot())end)
 at('hud_return',function()emit('GokuHUD-return',snapshot())end)
 at('palette',function()emit('GokuPalette-entry',snapshot())end)
 local writes=0
 emu.addMemoryCallback(function(_,v)
  writes=0;emit('DMA-request',{page=v,OAMADDR=emu.getState()['ppu.spriteRamAddr']})
 end,emu.callbackType.write,0x4014)
 emu.addMemoryCallback(function(_,v)
  writes=writes+1
  if writes==1 or writes==256 then emit('DMA-data',{ordinal=writes,value=v,OAMADDR=emu.getState()['ppu.spriteRamAddr']})end
 end,emu.callbackType.write,0x2004)
 emu.addMemoryCallback(function(_,v)emit('PPUMASK-write',{value=v})end,emu.callbackType.write,0x2001)
 emu.addMemoryCallback(function(_,v)
  emit('Buffer1-offset-writer',{old=r('VRAM_Buffer1_Offset'),value=v,previous_instruction_bytes=bytes((state().pc-3)&65535,3),snapshot=snapshot()})
 end,emu.callbackType.write,ram.VRAM_Buffer1_Offset)
 C.diagnostic_close=function()
  log:close();return{rows=rows,bytes=total,first_ppu_frame=D.first,last_ppu_frame=D.last,capture_free=true}
 end
end
