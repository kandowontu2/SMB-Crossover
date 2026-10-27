-- Passive, startup-static observer. Does not change inputs, RAM, or guards.
local C=assert(BASS_HUD_TIMELINE)
local f=assert(io.open(C.output..'bass-hud-timeline.csv','w'))
local header='event,frame,cycle,line,dot,pc,bank,sp,a,x,y,dirty,offset,bufferCtrl,selected,selectedAmmo,knuckleAmmo,hudAmmo,nmiDisable,nmiSkipped,screenOff,ppuCtrl,ppuV,ppuW,address,value,callId,caller,elapsed,windowDMA,digitsHex,queueHex,detail\n'
assert(f:write(header))
local count,size,closed,calls,returns,orphans,captures,dma=0,#header,false,0,0,0,0,0
local live=nil
local ppuCtrl=nil
local shotSamples={}
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or-1 end
local function within(s)return s['ppu.frameCount']>=C.first and s['ppu.frameCount']<=C.last end
local function hex(at,n,kind)local t={};for i=0,n-1 do t[#t+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)end
local function stackReturn(s)local sp=s['cpu.sp'];return(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)&65535 end
local function stamp(s)return{frame=s['ppu.frameCount'],cycle=s['cpu.cycleCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']}end
local function toggle(v)if v==nil then return-1 elseif type(v)=='boolean'then return v and 1 or 0 else return v end end
local function row(event,address,value,snapshot,detail,s)
 if closed then return end;s=s or emu.getState();if not within(s)then return end
 local selected=r('InvSelected',9)
 local values={event,s['ppu.frameCount'],s['cpu.cycleCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc'],bank(s['cpu.pc']),s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],r('InvDirty'),r('VRAM_Buffer1_Offset'),r('VRAM_Buffer_AddrCtrl'),selected,r('InvAmmo',144+selected),r('InvAmmo',147),r('InvHudAmmo'),r('NmiDisable'),r('NmiSkipped'),r('DisableScreenFlag'),ppuCtrl or-1,s['ppu.videoRamAddr']or-1,toggle(s['ppu.writeToggle']),address or-1,value or-1,live and live.id or-1,live and live.caller or-1,live and(s['cpu.cycleCount']-live.cycle)or-1,dma,hex(0x202b,3,emu.memType.nesPpuDebug),snapshot and hex(C.ram.VRAM_Buffer1,C.queue_bytes)or'',detail or''}
 local line=table.concat(values,',')..'\n';count=count+1;size=size+#line
 assert(count<=3000 and size<=1048576,'Bounded passive HUD timeline3000rows/1MiB')
 assert(f:write(line));f:flush()
end
local function hook(h,fn)
 emu.addMemoryCallback(function()
  if closed then return end;local s=emu.getState();if not within(s)then return end
  local actual=bank(h.pc);local allowed=false;for _,b in ipairs(h.banks)do if b==actual then allowed=true end end
  if not allowed then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual passive HUD hook '..h.name)end
  fn(s)
 end,emu.callbackType.exec,h.pc)
end
hook(C.hooks.hud,function(s)
 assert(not live,'No recursive actual InventoryHud owner');calls=calls+1
 live={id=calls,sp=s['cpu.sp'],bank=bank(s['cpu.pc']),caller=stackReturn(s),cycle=s['cpu.cycleCount']}
 row('InventoryHud-entry',nil,nil,true,nil,s)
end)
local function hudReturn(s)
 if not live then orphans=orphans+1;row('InventoryHud-window-clipped-return',nil,nil,true,nil,s);return end
 assert(live.bank==59 and bank(s['cpu.pc'])==59 and live.sp==s['cpu.sp']and stackReturn(s)==live.caller,'Actual InventoryHud bank/SP/caller owner')
 row('InventoryHud-return',nil,nil,true,nil,s);returns=returns+1;live=nil
end
hook(C.hooks.hud_done,hudReturn);hook(C.hooks.hud_tail_done,hudReturn)
hook(C.hooks.screen,function(s)row('UpdateScreen-packet',nil,nil,true,'pointer='..(r('NmiR0')+256*r('NmiR1')),s)end)
hook(C.hooks.dma,function(s)dma=dma+1;row('actual-E008-DMA-complete',nil,nil,false,nil,s)end)
for _,name in ipairs({'InvDirty','VRAM_Buffer1_Offset','VRAM_Buffer_AddrCtrl'})do
 local label=name;emu.addMemoryCallback(function(at,v)row('RAM-write-'..label,at,v,label=='VRAM_Buffer1_Offset','RAM fields show callback-time image; value is actual write')end,emu.callbackType.write,C.ram[name])
end
emu.addMemoryCallback(function(at,v)row('Knuckle-ammo-write',at,v,false,'Includes actual RMW bus multiplicity without normalization')end,emu.callbackType.write,C.ram.InvAmmo+147)
emu.addMemoryCallback(function(_,v)ppuCtrl=v;row('PPUCTRL-write',0x2000,v,false)end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(at,v)row('PPUADDR-write',at,v,false)end,emu.callbackType.write,0x2006)
emu.addMemoryCallback(function(at,v)row('PPUDATA-write',at,v,false,'ppuV is actual callback-time PPU state; committed digits are read at that callback')end,emu.callbackType.write,0x2007)
emu.addEventCallback(function()row('endFrame-committed-HUD',nil,nil,true)end,emu.eventType.endFrame)
local originalScreenshot=emu.takeScreenshot
emu.takeScreenshot=function(...)
 captures=captures+1;assert(captures<=8,'Only eight original fixture screenshot calls')
 local before=emu.getState();local sampled=within(before)
 local sample=nil
 if sampled then
  assert(ppuCtrl~=nil,'Actual PPUCTRL write observed before HUD sample')
  local digits={};local patterns={}
  for i=0,2 do
   local tile=emu.read(0x202b+i,emu.memType.nesPpuDebug);digits[#digits+1]=tile
   patterns[#patterns+1]=hex((ppuCtrl&16)~=0 and 0x1000+tile*16 or tile*16,16,emu.memType.nesPpuDebug)
  end
  sample={original_capture_index=captures,before=stamp(before),digits=digits,pattern_hex=patterns,background_palette_hex=hex(0x3f00,16,emu.memType.nesPpuDebug),attribute_hex=hex(0x23c0,4,emu.memType.nesPpuDebug),ppuCtrl=ppuCtrl,knuckle_ammo=r('InvAmmo',147),dirty=r('InvDirty'),queue_offset=r('VRAM_Buffer1_Offset'),queue_ctrl=r('VRAM_Buffer_AddrCtrl'),limits='Current debug NT/pattern/palette snapshots, not cached raster fetch history.'}
  row('takeScreenshot-before',nil,nil,true,'original-capture='..captures,before)
 end
 local png=originalScreenshot(...)
 if sampled then sample.after=stamp(emu.getState());sample.PNG_bytes=#png;shotSamples[#shotSamples+1]=sample;row('takeScreenshot-after',nil,nil,true,'original-capture='..captures..';PNGbytes='..#png)end
 return png
end
local function json(v)
 if type(v)=='table'then local z={};if #v>0 then for _,x in ipairs(v)do z[#z+1]=json(x)end;return'['..table.concat(z,',')..']'end
  for k,x in pairs(v)do z[#z+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(z);return'{'..table.concat(z,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local originalStop=emu.stop
emu.stop=function(code)
 if not closed then
  closed=true;f:close()
  local o=assert(io.open(C.output..'bass-hud-timeline-summary.json','w'))
  o:write(json({passive=true,ROM_sha256=C.ROM_sha256,first_actual_PPU_frame=C.first,last_actual_PPU_frame=C.last,window_physical_frames=C.last-C.first+1,rows=count,CSV_bytes=size,InventoryHud_entries=calls,InventoryHud_owned_returns=returns,window_clipped_returns=orphans,window_clipped_entry=live~=nil,window_completed_DMAs=dma,original_screenshot_calls=captures,window_screenshots=shotSamples,no_extra_images=true,original_PNG_bytes_returned_unchanged=true,limits='CSV/detailed screenshots only inside61actualPPUframes; PPUCTRL local latch tracks actual writes from boot. Other original screenshot calls counted but not snapshotted. NMI/IRQ/DMA/mechanics guards remain in the unchanged original fixture.'}));o:close()
 end
 return originalStop(code)
end
