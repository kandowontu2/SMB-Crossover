-- Startup-only passive diagnostics. No emulated writes/input changes.
local C=assert(PROTO_STARTUP_VRAM_TIMING)
local R=assert(ROSTER_CONFIG)
local f=assert(io.open(R.prefix..'proto-startup-vram.csv','w'))
f:write('event,nmi,frame,cycle,line,dot,pc,bank,sp,elapsed,mode,task,engine,character,variant,nmiDisable,nmiSkipped,screenOff,mirrorMask,bufferCtrl,offset1,offset2,pointer,header0,header1,header2,length,repeatByte,packetHex,reloadCHR,freezePending,freezeState,hudActive,bankA,bankC,ppuDataWrites,stackedPC\n')
local closed,recording,count,nmiId=false,true,0,0
local live={};local nmiStart,dmaStart=nil,nil
local ppuWrites=0
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function packet()
 local ptr=r('NmiR0')+256*r('NmiR1');local a={}
 for y=0,2 do a[y+1]=emu.read(ptr+y,emu.memType.nesDebug)end
 local len=a[1]==0 and 0 or(a[3]&63);if a[1]~=0 and len==0 then len=256 end
 local repeatByte=a[3]&64~=0;local total=a[1]==0 and 1 or 3+(repeatByte and 1 or len)
 local h={};for i=0,total-1 do h[#h+1]=string.format('%02x',emu.read(ptr+i%256,emu.memType.nesDebug))end
 return ptr,a,len,repeatByte and 1 or 0,table.concat(h)
end
local function row(kind,elapsed,stacked)
 local s=emu.getState();local ptr,h,len,repeated,hex=packet();count=count+1;assert(count<30000,'Bounded sparse startup timing rows')
 f:write(table.concat({kind,nmiId,s['ppu.frameCount'],s['cpu.cycleCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc'],bank(s['cpu.pc']),s['cpu.sp'],elapsed or 0,r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('SelectedCharacter'),r('ProtoVariant'),r('NmiDisable'),r('NmiSkipped'),r('DisableScreenFlag'),r('Mirror_PPUMASK'),r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer1_Offset'),r('VRAM_Buffer2_Offset'),ptr,h[1],h[2],h[3],len,repeated,hex,r('ReloadCHRBank'),r('SmFreezePalettePending'),r('SmFreezeRenderState'),r('InvHudActive'),bank(0xa000),bank(0xc000),ppuWrites,stacked or-1},',')..'\n');f:flush()
end
local function hook(h,fn)
 emu.addMemoryCallback(function()
  if closed or not recording then return end;local actual=bank(h.pc);local valid=false;for _,b in ipairs(h.banks)do if actual==b then valid=true end end;if not valid then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual startup timing hook')end;fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
hook(C.hooks.nmi,function(s)
 if C.cutoff_frame and s['ppu.frameCount']>C.cutoff_frame then recording=false;return end
 nmiId=nmiId+1;assert(not nmiStart,'No nested startup NMI');nmiStart={cycle=s['cpu.cycleCount'],sp=s['cpu.sp']};ppuWrites=0
 local sp=s['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug);row('NMI-entry',0,pc)
end)
hook(C.hooks.nmi_return,function(s)if nmiStart then assert(s['cpu.sp']==nmiStart.sp,'Actual startup NMI return SP');row('NMI-return',s['cpu.cycleCount']-nmiStart.cycle);nmiStart=nil end end)
hook(C.hooks.gateway,function(s)assert(not live.gateway,'No recursive screen gateway');live.gateway={cycle=s['cpu.cycleCount'],sp=s['cpu.sp']};row('ScreenGateway-entry')end)
hook(C.hooks.gateway_return,function(s)if live.gateway then assert(s['cpu.sp']==(live.gateway.sp+2)%256,'Real screen gateway caller return SP');row('ScreenGateway-return',s['cpu.cycleCount']-live.gateway.cycle);live.gateway=nil end end)
hook(C.hooks.update,function(s)
 if not live.update then live.update={cycle=s['cpu.cycleCount'],sp=s['cpu.sp']};row('UpdateScreen-entry')else assert(s['cpu.sp']==live.update.sp,'Actual same native VRAM loop frame');row('UpdateScreen-packet',s['cpu.cycleCount']-live.update.cycle)end
end)
hook(C.hooks.update_return,function(s)if live.update then assert(s['cpu.sp']==live.update.sp,'Actual UpdateScreen return frame');row('UpdateScreen-return',s['cpu.cycleCount']-live.update.cycle);live.update=nil end end)
hook(C.hooks.chr,function(s)if nmiStart then assert(not live.chr,'No recursive CHR scope');live.chr={cycle=s['cpu.cycleCount'],sp=s['cpu.sp']};row('BankSwitchCHR-entry')end end)
hook(C.hooks.chr_return,function(s)if live.chr then assert(s['cpu.sp']==live.chr.sp,'Actual CHR return SP');row('BankSwitchCHR-return',s['cpu.cycleCount']-live.chr.cycle);live.chr=nil end end)
hook(C.hooks.dma_complete,function(s)if dmaStart then row('DMA-complete-before-mask-store',s['cpu.cycleCount']-dmaStart);dmaStart=nil end end)
emu.addMemoryCallback(function(_,v)if not closed and recording then assert(v==2,'Actual native DMA page2');assert(emu.getState()['cpu.pc']==C.dma_store_return,'Genuine DMA request return PC');dmaStart=emu.getState()['cpu.cycleCount'];row('DMA-request',nmiStart and dmaStart-nmiStart.cycle or 0)end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)if not closed and recording then row('PPUMASK-'..v,nmiStart and emu.getState()['cpu.cycleCount']-nmiStart.cycle or 0)end end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()if not closed and recording and nmiStart then ppuWrites=ppuWrites+1 end end,emu.callbackType.write,0x2007)
return function()
 if closed then return{already_closed=true}end;closed=true;f:close()
 return{passive=true,recording_stopped=not recording,cutoff_frame=C.cutoff_frame,rows=count,NMI_entries=nmiId,clipped_NMI=nmiStart~=nil,clipped_DMA=dmaStart~=nil,limits='CPU entry-to-opcode/caller-return timings only; packet snapshot uses real nativeY wrap and header bits. Existing shared route observer retains all256 DMA/CHR/SMC/stack/render-enable assertions. No emulated state or input writes.'}
end
