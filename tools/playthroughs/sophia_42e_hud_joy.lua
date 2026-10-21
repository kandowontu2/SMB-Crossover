-- Bounded passive candidate42e HUD producer/consumer receipt; guards independently checked against candidate42e ROM; no emulated writes.
local cfg=assert(ROSTER_CONFIG)
local root=assert(cfg.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/sophia_38d_policy.lua'))
local mf=assert(io.open(cfg.out..'manifest.json','r'))
local sourceRomSha=assert(mf:read('*a'):match('"rom_sha256"%s*:%s*"([0-9a-f]+)"'));mf:close()
local frame,nmiDepth,irqDepth=0,0,0
local selector,prgMode=0,0
local chr,prg={},{}
local function r(n,i)return L[n] and emu.read(L[n]+(i or 0),emu.memType.nesDebug) or -1 end
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function physical(pc)
 if pc>=0xe000 then return 63 end
 if pc>=0xc000 then return prgMode==0 and 62 or (prg[6] or -1)end
 if pc>=0xa000 then return prg[7] or -1 end
 if pc>=0x8000 then return prgMode==0 and (prg[6] or -1) or 62 end
 return -1
end
emu.addMemoryCallback(function(_,v)selector=v&7;prgMode=(v>>6)&1 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if selector<6 then chr[selector]=v elseif selector<8 then prg[selector]=v end end,emu.callbackType.write,0x8001)
local function match(pc,bank,bytes)
 if physical(pc)~=bank then return false end
 for i,v in ipairs(bytes)do if read(pc+i-1)~=v then return false end end
 return true
end
emu.addMemoryCallback(function()if match(L.NonMaskableInterrupt,63,{0x48,0x8a,0x48,0x98,0x48,0xad})then nmiDepth=nmiDepth+1 end end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()if nmiDepth>0 and physical(L.NonMaskableInterrupt_RTI)==63 and read(L.NonMaskableInterrupt_RTI)==0x40 then nmiDepth=nmiDepth-1 end end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()if match(L.IrqScrollSplit,62,{0x48,0x8a,0x48,0x8d,0x00,0xe0})then irqDepth=irqDepth+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()if irqDepth>0 and physical(L.IrqScrollSplit_RTI)==62 and read(L.IrqScrollSplit_RTI)==0x40 then irqDepth=irqDepth-1 end end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
local function file(n,h)local f=assert(io.open(cfg.out..n..'.csv','w'));f:write(h..'\n');return f end
local header='physicalFrame,lastEndFrame,pc,physicalPrgBank,currentBank,nmiDepth,irqDepth,sp,cycle,NmiDisable,NmiSkipped,ShouldSkipDrawSprites'
local consumer=file('hud-consumer-commands',header..',pointer,hi,lo,length,bufferOffset,headerBytes,stack')
local producer=file('hud-buffer-writes',header..',address,value,bufferOffset,R0,R1,R7,nmiPointer,siteBytes,stack')
local ppu=file('hud-port-writes',header..',register,value,trackedAddress,bufferOffset,nmiPointer,siteBytes')
local snapshot=file('hud-state','frame,mode,task,engine,world,level,x,y,disabled,goodLabels,chrRegisters,prg6,prg7,prgMode,bufferOffset,hudHex')
local flow=file('hud-flow',header..',event,eventAddress,eventValue,a,xreg,yreg,bufferOffset,bufferTail')
local function bytes(a,n,mem)
 local b={};for i=0,n-1 do b[#b+1]=string.format('%02x',emu.read(a+i,mem or emu.memType.nesDebug))end;return table.concat(b)
end
local function context()
 local s=emu.getState();local pc=s['cpu.pc'] or 0;local sp=s['cpu.sp'] or 0
 return {frame+1,frame,pc,physical(pc),r('CurrentBank'),nmiDepth,irqDepth,sp,s['cpu.cycleCount'] or s['cpu.cycle'] or -1,r('NmiDisable'),r('NmiSkipped'),r('ShouldSkipDrawSprites')},pc,sp
end
local function pointer()return read(0)+256*read(1)end
local firstBad=nil
local function enabled()return frame>=450 and frame<=6500 end
local function flowEvent(event,address,value)
 if frame<450 or frame>6500 then return end
 local c=context();local s=emu.getState()
 c[#c+1]=event;c[#c+1]=address or -1;c[#c+1]=value or -1;c[#c+1]=s['cpu.a']or-1;c[#c+1]=s['cpu.x']or-1;c[#c+1]=s['cpu.y']or-1;c[#c+1]=r('VRAM_Buffer1_Offset');c[#c+1]=bytes(L.VRAM_Buffer1+r('VRAM_Buffer1_Offset'),8)
 flow:write(table.concat(c,',')..'\n')
end
for _,q in ipairs({
 {'GameLoop',L.GameLoop,62,{0xa9,0xff,0x8d,0x39,0x01}},
 {'GameLoopProtected',L.GameLoop+5,62,{0x20,0x32,0x83,0x8d,0x6d,0x01}},
 {'GoToNextFrameImmediately',L.GoToNextFrameImmediately,62,{0xad,0x3a,0x01,0x48,0x20,0xb5}},
 {'CatchUpOnce',L.CatchUpOnce,62,{0xad,0x3a,0x01,0x48,0x20,0xb5}},
 {'SetupNums',L.SetupNums,62,{0x9d,0xaf,0x04,0xb9,0xed,0x8b}},
 {'NMIEntry',L.NonMaskableInterrupt,63,{0x48,0x8a,0x48,0x98,0x48,0xad}}
})do
 local event,pc,bank,expected=q[1],assert(q[2]),q[3],q[4]
 emu.addMemoryCallback(function()if match(pc,bank,expected)then flowEvent(event,pc)end end,emu.callbackType.exec,pc)
end
for _,name in ipairs({'NmiDisable','NmiSkipped','ShouldSkipDrawSprites'})do
 emu.addMemoryCallback(function(a,v)flowEvent(name..'Write',a,v)end,emu.callbackType.write,assert(L[name]))
end
emu.addMemoryCallback(function(a,v)
 if not enabled()then return end
 local c,pc,sp=context();c[#c+1]=a;c[#c+1]=v;c[#c+1]=r('VRAM_Buffer1_Offset');c[#c+1]=r('R0');c[#c+1]=r('R1');c[#c+1]=r('R7');c[#c+1]=pointer();c[#c+1]=bytes((pc-3)&65535,6);c[#c+1]=bytes(0x100+((sp+1)&255),math.min(16,255-sp))
 producer:write(table.concat(c,',')..'\n')
end,emu.callbackType.write,L.VRAM_Buffer1-1,L.VRAM_Buffer1+0xfe)
emu.addMemoryCallback(function()
 if not enabled()or not match(L.WriteBufferToScreen,62,{0x8d,0x06,0x20})then return end
 local c,_,sp=context();local p=pointer();c[#c+1]=p;c[#c+1]=read(p);c[#c+1]=read(p+1);c[#c+1]=read(p+2);c[#c+1]=r('VRAM_Buffer1_Offset');c[#c+1]=bytes(p,24);c[#c+1]=bytes(0x100+((sp+1)&255),math.min(16,255-sp));consumer:write(table.concat(c,',')..'\n')
end,emu.callbackType.exec,L.WriteBufferToScreen)
local latch,hi,address,increment=0,0,0,1
emu.addMemoryCallback(function()latch=0 end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function(a,v)
 if enabled()and(a==0x2006 or a==0x2007)then
  local c,pc=context();c[#c+1]=a;c[#c+1]=v;c[#c+1]=address;c[#c+1]=r('VRAM_Buffer1_Offset');c[#c+1]=pointer();c[#c+1]=bytes((pc-3)&65535,6);ppu:write(table.concat(c,',')..'\n')
 end
 if a==0x2000 then increment=(v&4)~=0 and 32 or 1
 elseif a==0x2005 then latch=1-latch
 elseif a==0x2006 then if latch==0 then hi=v&63 else address=hi*256+v end;latch=1-latch
 elseif a==0x2007 then address=(address+increment)&0x3fff end
end,emu.callbackType.write,0x2000,0x2007)
local function dump(n,a,count,mem)
 local f=assert(io.open(cfg.out..n,'wb'));for i=0,count-1 do f:write(string.char(emu.read(a+i,mem)))end;f:close()
end
local last=''
emu.addEventCallback(function()
 frame=frame+1
 if frame<450 or frame>6500 then return end
 local hud=bytes(0x2000,128,emu.memType.nesPpuDebug)
 local word=bytes(0x2052,5,emu.memType.nesPpuDebug)
 -- Static native label is row2, columns25..28 (WORLD is columns18..22).
 local time=bytes(0x2059,4,emu.memType.nesPpuDebug)
 local good=word=='20181b150d'and time=='1d12160e'
 local banks={};for i=0,5 do banks[#banks+1]=chr[i]or-1 end
 if hud~=last then snapshot:write(table.concat({frame,r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('WorldNumber'),r('LevelNumber'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('DisableScreenFlag'),good and 1 or 0,table.concat(banks,':'),prg[6]or-1,prg[7]or-1,prgMode,r('VRAM_Buffer1_Offset'),hud},',')..'\n');last=hud end
 if not firstBad and frame>=541 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('DisableScreenFlag')==0 and not good then
  firstBad=frame
  dump('first-bad.nametable',0x2000,4096,emu.memType.nesPpuDebug)
  dump('first-bad.chr',0,8192,emu.memType.nesPpuDebug)
  dump('first-bad.palette',0x3f00,32,emu.memType.nesPpuDebug)
  dump('first-bad.cpu-ram',0,2048,emu.memType.nesDebug)
  dump('first-bad.sram',0x6000,8192,emu.memType.nesDebug)
  local f=assert(io.open(cfg.out..'first-bad.png','wb'));f:write(emu.takeScreenshot());f:close()
  local j=assert(io.open(cfg.out..'first-bad.json','w'));j:write(string.format('{"frame":%d,"world":%d,"level":%d,"x":%d,"y":%d,"source_rom_sha256":"%s","read_only":true}',frame,r('WorldNumber'),r('LevelNumber'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),sourceRomSha));j:close()
 end
 if frame==541 or frame==4103 or frame==4498 then
  dump('prior-'..frame..'.nametable',0x2000,4096,emu.memType.nesPpuDebug)
  dump('prior-'..frame..'.chr',0,8192,emu.memType.nesPpuDebug)
  local f=assert(io.open(cfg.out..'prior-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 snapshot:flush();consumer:flush();producer:flush();ppu:flush();flow:flush()
end,emu.eventType.endFrame)

-- Actual native controller sampling supplement. Host inputPolled is distinct.
local joy=file('hud-native-input',header..',event,value,SavedJoypad1,SavedJoypad2,port1Reads,world,level,engine,mode,task')
local port1Reads=0
local function joyEvent(event,value)
 local c=context();c[#c+1]=event;c[#c+1]=value or -1;c[#c+1]=r('SavedJoypadBits');c[#c+1]=r('SavedJoypad2Bits');c[#c+1]=port1Reads;c[#c+1]=r('WorldNumber');c[#c+1]=r('LevelNumber');c[#c+1]=r('GameEngineSubroutine');c[#c+1]=r('OperMode');c[#c+1]=r('OperMode_Task');joy:write(table.concat(c,',')..'\n')
end
local nativeRead=assert(L.OAMandReadJoypad)
emu.addMemoryCallback(function()
 if nmiDepth==1 and irqDepth==0 and match(nativeRead,63,{0xa9,0x02,0x8d,0x14,0x40,0xa2})then port1Reads=0;joyEvent('OAMReadEntry')end
end,emu.callbackType.exec,nativeRead)
emu.addMemoryCallback(function(a,v)
 local _,pc=context()
 if nmiDepth==1 and irqDepth==0 and match(pc-3,63,{0x8e,0x16,0x40})then joyEvent('4016StrobeWrite',v)end
end,emu.callbackType.write,0x4016)
emu.addMemoryCallback(function()
 local _,pc=context()
 if nmiDepth==1 and irqDepth==0 and match(pc-3,63,{0xad,0x16,0x40})then port1Reads=port1Reads+1 end
end,emu.callbackType.read,0x4016)
emu.addMemoryCallback(function()
 if nmiDepth==1 and irqDepth==0 and match(nativeRead+0x20,63,{0x26,0xdc,0x90,0xec,0x60})then joyEvent('OAMReadDone')end
end,emu.callbackType.exec,nativeRead+0x24)
emu.addEventCallback(function()joyEvent('SavedJoypadAtFrameEnd');joy:flush()end,emu.eventType.endFrame)

return base
