-- Passive Knuckle body owner/actual return and completed-DMA evidence only.
return function(C)
 local frame,draw,render,serial,last,transfer=0,nil,nil,0,-100,nil
 local f=assert(io.open(OUTPUT..'knuckle-owner.jsonl','w'));f:setvbuf('no');local rows,size=0,0
 local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
 local function hex(at,n,kind)local a={};for i=0,n-1 do a[#a+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(a)end
 local function json(t)local a={};for k,v in pairs(t)do a[#a+1]=string.format('%q',tostring(k))..':'..(type(v)=='string'and string.format('%q',v)or tostring(v))end;table.sort(a);return'{'..table.concat(a,',')..'}'end
 local function watching()
  if r('InvSelected',1)~=3 then return false end
  for i=0,9 do if r('RgShotType',i)==11 and r('RgShotAge',i)<=14 then last=frame;return true end end
  return frame<=last+2
 end
 local function log(event,more)
  local s=emu.getState();local t=more or{};t.event=event;t.wall_counter=frame;t.draw_serial=serial
  for _,n in ipairs({'cpu.pc','cpu.a','cpu.x','cpu.y','cpu.sp','cpu.cycleCount','ppu.frameCount','ppu.scanline','ppu.cycle','ppu.spriteRamAddr'})do t[n]=s[n]end
  for _,n in ipairs(C.fields)do t[n]=r(n)end
  t.physicalA=bank(0xa000);t.physicalC=bank(0xc000);t.currentPCbank=bank(s['cpu.pc'])
  local ptr=r('R0')+256*r('R1');t.pointer=ptr;t.actualHeader=emu.read(ptr,emu.memType.nesDebug)
  t.actualPointerBytes=hex(ptr,41);t.R0_7=hex(C.ram.R0,8);t.SmPosePtr=r('SmPosePtr')+256*r('SmPosePtr',1)
  t.expected_FIST_bank=C.expected.bank;t.expected_FIST_pointer=C.expected.pc
  t.expected_FIST_bytes=hex(C.expected.bank*8192+C.expected.pc%8192,37,emu.memType.nesPrgRom)
  local line=json(t)..'\n';rows=rows+1;size=size+#line;assert(rows<=500 and size<=4000000,'Bounded passive body trace');f:write(line)
 end
 local function hook(n,fn)
  local h=assert(C.hooks[n]);emu.addMemoryCallback(function()
   local owns=false;for _,b in ipairs(h.banks)do owns=owns or bank(h.pc)==b end;if not owns then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Genuine passive hook '..n)end
   fn(emu.getState())
  end,emu.callbackType.exec,h.pc)
 end
 local function returning(s,list)
  local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)&65535
  for _,q in ipairs(list)do if q.pc==pc and q.bank==bank(pc)then return{pc=pc,bank=q.bank,sp=(sp+2)%256}end end
  assert(false,'Actual body callsite/return is a compiled allowed JSR')
 end
 hook('DrawMetasprite',function(s)
  if watching()and s['cpu.y']==0 and r('ObjectMetasprite')==C.body_id then
   assert(not draw,'Body entry not reentrant');serial=serial+1;draw=returning(s,C.draw_returns)
   log('body-DrawMetasprite-entry',{expected_return=draw.pc,expected_return_SP=draw.sp})
  end
 end)
 hook('MetaspriteRenderLoop',function(s)
  if draw then
   assert(not render,'Immediate body renderer not reentrant');render=returning(s,C.render_returns)
   log('body-real-renderer-entry',{expected_return=render.pc,expected_return_SP=render.sp,source256=hex(C.ram.Sprite_Data,256)})
  end
 end)
 -- All possible real returns are registered once before emulation starts.
 for _,q in ipairs(C.return_dispatch)do
  emu.addMemoryCallback(function()
   if bank(q.pc)~=q.bank then return end
   local s=emu.getState()
   if render and render.pc==q.pc and render.sp==s['cpu.sp']then
    log('body-real-renderer-return',{expected_return_SP=render.sp,returned_carry=s['cpu.ps']and s['cpu.ps']&1 or-1,source256=hex(C.ram.Sprite_Data,256)});render=nil
   end
   if draw and draw.pc==q.pc and draw.sp==s['cpu.sp']then
    assert(not render,'Inner renderer completed before genuine outer draw return')
    log('body-real-DrawMetasprite-return',{expected_return_SP=draw.sp,source256=hex(C.ram.Sprite_Data,256)});draw=nil
   end
  end,emu.callbackType.exec,q.pc)
 end
 hook('GameLoopFinish',function()if watching()then log('full-GameLoop-final-source',{source256=hex(C.ram.Sprite_Data,256)})end end)
 emu.addMemoryCallback(function(_,v)
  transfer=watching()and{source=hex(v*256,256),writes=0}or nil
 end,emu.callbackType.write,0x4014)
 emu.addMemoryCallback(function()if transfer then transfer.writes=transfer.writes+1 end end,emu.callbackType.write,0x2004)
 hook('DmaComplete',function()
  if transfer then log('E008-completed-DMA',{source256=transfer.source,hardware256=hex(0,256,emu.memType.nesSpriteRam),writes=transfer.writes});transfer=nil end
 end)
 emu.addEventCallback(function()
  frame=frame+1
  if watching()then
   local s=emu.getState();local t={hardware256=hex(0,256,emu.memType.nesSpriteRam),palette32=hex(0x3f00,32,emu.memType.nesPpuDebug)}
   for i=0,11 do t['physicalCHR'..i]=s['mapper.chrBanks'..i]end
   for i=0,1 do local page=assert(s['mapper.chrBanks'..i]);t['bodyCHRphysicalPage'..i]=hex(page*1024,1024,emu.memType.nesChrRom)end
   log('actual-endFrame-hardware-CHR',t)
  end
 end,emu.eventType.endFrame)
end
