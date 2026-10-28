-- Passive exact-input probe. All callbacks are registered once at startup.
-- This logs RAM/bus/hardware epochs; it does not reconstruct background fetches.
return function(out,C)
 local f=assert(io.open(out..'octopus-visibility.jsonl','w'))
 local rows,total,closed=0,0,false
 local dma,body,draw,publication,lastDma,lastEnd
 local mainId,drawId,bodyId,dmaId=0,0,0,0
 local nmiDepth,irqDepth,ctrl,mask=0,0,nil,nil
 local registrations,sealed=0,false
 local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or -1 end
 local function hex(at,n,kind)
  local z={};for i=0,n-1 do z[#z+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end
  return table.concat(z)
 end
 local function json(v)
  if type(v)=='string'then return '"'..v:gsub('[%z\1-\31\\"]',function(c)return string.format('\\u%04x',c:byte())end)..'"'
  elseif type(v)=='table'then local z={};if #v>0 then for _,a in ipairs(v)do z[#z+1]=json(a)end;return '['..table.concat(z,',')..']'end
   local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys)
   for _,k in ipairs(keys)do z[#z+1]=json(k)..':'..json(v[k])end;return '{'..table.concat(z,',')..'}'
  elseif v==nil then return 'null'else return tostring(v)end
 end
 local function window(s)return s['ppu.frameCount']>=C.first and s['ppu.frameCount']<=C.last end
 local function stamp(s)
  return{ppu_frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],cpu_cycle=s['cpu.cycleCount'],
   pc=s['cpu.pc'],sp=s['cpu.sp'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],
   physical_A=bank(0xa000),physical_C=bank(0xc000),pc_bank=bank(s['cpu.pc']),nmi_depth=nmiDepth,irq_depth=irqDepth}
 end
 local function snapshot(s)
  local q={};for _,n in ipairs(C.scalars)do q[n]=r(n)end
  q.SmPosePtr=r('SmPosePtr')+256*r('SmPosePtr',1)
  q.world_x=r('Player_X_Position')+256*r('Player_PageLoc');q.camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
  q.PnFrame=hex(C.ram.PnFrame,28);q.PnDrawFlags=hex(C.ram.PnDrawFlags,28);q.PnContact=hex(C.ram.PnContact,28)
  q.chr_banks={};for i=0,11 do q.chr_banks[#q.chr_banks+1]=assert(s['mapper.chrBanks'..i],'Actual CHR state')end
  q.last_2000_bus_value=ctrl;q.last_2001_bus_value=mask;q.oamaddr=s['ppu.spriteRamAddr']
  return q
 end
 local function log(kind,q,s)
  if closed or not window(s)then return end
  rows=rows+1;assert(rows<=C.row_cap,'Bounded Octopus probe rows')
  local line=json({kind=kind,stamp=stamp(s),main_id=mainId,draw_id=drawId,body_id=bodyId,dma_id=dmaId,data=q})..'\n'
  total=total+#line;assert(total<=C.byte_cap,'Bounded Octopus probe bytes');f:write(line);f:flush()
 end
 local function returnWord(sp)return emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)end
 local function record()
  local ptr=r('R0')+256*r('R1',0);local q={pointer=ptr,pointer_bank=ptr>=0x8000 and bank(ptr)or -1,
   scratch=hex(C.ram.R0,8)}
  if ptr>=0x6000 and ptr<=0xff00 then
   local count=emu.read(ptr,emu.memType.nesDebug);q.header=count
   if count%4==0 and count<=252 then q.mapped_record=hex(ptr,count+1)end
  end;return q
 end
 local function memory(fn,kind,first,last)
  assert(not sealed,'Probe callback inventory is sealed before execution')
  registrations=registrations+1;emu.addMemoryCallback(fn,kind,first,last or first)
 end
 local function hook(h,fn)
  memory(function(pc)
   local b=bank(pc);local owned=b==h.bank
   if h.banks then owned=false;for _,v in ipairs(h.banks)do if b==v then owned=true end end end
   if not owned then return end
   local s=emu.getState()
   if not window(s)and not h.always then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Probe actual hook bytes: '..h.name)end
   fn(s)
  end,emu.callbackType.exec,h.pc)
 end
 hook(C.hooks.nmi,function(s)nmiDepth=nmiDepth+1;if window(s)then log('nmi-entry',snapshot(s),s)end end)
 hook(C.hooks.nmi_return,function(s)if window(s)then log('nmi-rti-entry',snapshot(s),s)end;nmiDepth=nmiDepth-1 end)
 hook(C.hooks.irq,function(s)irqDepth=irqDepth+1;if window(s)then log('irq-entry',snapshot(s),s)end end)
 hook(C.hooks.irq_return,function(s)if window(s)then log('irq-rti-entry',snapshot(s),s)end;irqDepth=irqDepth-1 end)
 hook(C.hooks.loop,function(s)mainId=mainId+1;log('main-entry',snapshot(s),s)end)
 hook(C.hooks.loop_return,function(s)log('main-rts-entry',{state=snapshot(s),source256=hex(0x200,256),last_publication=publication},s)end)
 hook(C.hooks.draw,function(s)
  drawId=drawId+1;draw={sp=s['cpu.sp'],return_word=returnWord(s['cpu.sp']),entry=stamp(s)}
  log('draw-all-entry',{owner=draw,state=snapshot(s)},s)
 end)
 hook(C.hooks.reservation,function(s)log('body-reservation',{state=snapshot(s),mapped_pointer=record()},s)end)
 hook(C.hooks.body,function(s)
  if s['cpu.y']~=0 then return end
  bodyId=bodyId+1
  body={sp=s['cpu.sp'],return_word=returnWord(s['cpu.sp']),entry=stamp(s),source256_before=hex(0x200,256),writes={}}
  log('body-entry',{owner=body,state=snapshot(s),expected_return=C.hooks.body_return.pc},s)
 end)
 hook(C.hooks.pointer,function(s)if body and nmiDepth==0 then log('body-resolved-pointer',{record=record(),state=snapshot(s)},s)end end)
 hook(C.hooks.renderer,function(s)if body and nmiDepth==0 then log('body-native-renderer',{record=record(),state=snapshot(s)},s)end end)
 hook(C.hooks.body_return,function(s)
  if not body then log('body-return-without-observed-entry',snapshot(s),s);return end
  local q=body;body=nil
  log('body-caller-after-return',{owner=q,matching_owner=s['cpu.sp']==q.sp+2 and q.return_word+1==C.hooks.body_return.pc and nmiDepth==0,
   source256_after=hex(0x200,256),record_after=record(),state=snapshot(s)},s)
 end)
 hook(C.hooks.draw_ready,function(s)
  local q=draw;publication={draw_id=drawId,body_id=bodyId,stamp=stamp(s),source256=hex(0x200,256)}
  log('rotated-draw-rts-entry',{owner=q,matching_owner=q~=nil and q.sp==s['cpu.sp']and q.return_word==returnWord(s['cpu.sp'])and nmiDepth==0,
   source256=publication.source256,state=snapshot(s),freeze_outer_path=r('SmFreezeRenderState')},s);draw=nil
 end)
 memory(function(a,v)
  if body then local s=emu.getState();if window(s)then
   assert(#body.writes<512,'Bounded body writes');body.writes[#body.writes+1]={offset=a-0x200,value=v,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),nmi_depth=nmiDepth}
  end end
 end,emu.callbackType.write,0x200,0x2ff)
 memory(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
 memory(function(_,v)local old=mask;mask=v;local s=emu.getState();log('mask-write',{before=old,value=v,state=snapshot(s),last_dma=lastDma},s)end,emu.callbackType.write,0x2001)
 memory(function(_,page)
  local s=emu.getState();if not window(s)then return end
  dmaId=dmaId+1;dma={id=dmaId,page=page,request=stamp(s),source256=hex(page*256,256),writes={},publication=publication}
  log('dma-request',{dma=dma,state=snapshot(s)},s)
 end,emu.callbackType.write,0x4014)
 memory(function(_,v)if dma then
  local s=emu.getState();assert(#dma.writes<256,'Probe full DMA bound');dma.writes[#dma.writes+1]={value=v,oamaddr=s['ppu.spriteRamAddr']}
 end end,emu.callbackType.write,0x2004)
 hook(C.hooks.dma_complete,function(s)
  lastDma={id=dma and dma.id or -1,complete=stamp(s)}
  log('dma-complete-before-mask',{dma=dma,physical256=hex(0,256,emu.memType.nesSpriteRam),current_source256=hex(0x200,256),state=snapshot(s)},s);dma=nil
 end)
 registrations=registrations+1;emu.addEventCallback(function()
  local s=emu.getState();if not window(s)then return end;log('start-frame',{physical256=hex(0,256,emu.memType.nesSpriteRam),palette32=hex(0,32,emu.memType.nesPaletteRam),
   state=snapshot(s),last_dma=lastDma,last_end=lastEnd},s)
 end,emu.eventType.startFrame)
 registrations=registrations+1;emu.addEventCallback(function()
  local s=emu.getState();if window(s)then
   log('end-frame-before-route-capture',{physical256=hex(0,256,emu.memType.nesSpriteRam),palette32=hex(0,32,emu.memType.nesPaletteRam),
    state=snapshot(s),last_dma=lastDma},s);lastEnd=stamp(s)
  end
 end,emu.eventType.endFrame)
 assert(registrations==21,'Exact startup callback inventory');sealed=true
 return function()
  if not closed then f:close();closed=true end
  return{passive_octopus_probe=true,rows=rows,bytes=total,window={C.first,C.last},startup_registration_count=registrations,
   registration_inventory_sealed=sealed,native_screenshots=0,scope='Source/DMA/display epochs only; physical bank readback is not a pattern fetch trace.'}
 end
end
