-- Profile-local successor: physical OAM has no attribute bits2/3/4.
-- Foreground publication/source and every DMA input remain unmasked exact.
local function oamPhysical(source)
 local out={};for i=1,#source do local v=source:byte(i);if(i-1)%4==2 then v=v&0xe3 end;out[i]=string.char(v)end;return table.concat(out)
end
-- Observe actual DMA completion after the real LDA, before STA PPUMASK.
-- E005 EXEC is pre-transfer in the pinned emulator and is NOT completion.
local dmaProtocol=assert(C.dma_protocol)
local dmaMask,dmaSerial,dmaPending,dmaCompleted=0,0,nil,nil
local dmaProofLog=assert(io.open(OUTPUT..'ability-dma-epochs.jsonl','w'))
local function dmaStamp()
 local s=emu.getState()
 return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount'],pc=s['cpu.pc'],sp=s['cpu.sp'],oamaddr=s['ppu.spriteRamAddr'],mask=dmaMask,bankA=bank(0xa000),bankC=bank(0xc000)}
end
local function dmaArray(s)local a={};for i=1,#s do a[i]=s:byte(i)end;return a end
local function dmaRow(q)dmaProofLog:write(json(q)..'\n');dmaProofLog:flush()end
local function dmaScope()
 local function q(n)return emu.read(dmaProtocol.scope_ram[n],emu.memType.nesDebug)end
 if q('DisableScreenFlag')~=0 then return false end
 return q('CrossoverMenuState')==2 and q('OperMode')==0 or q('OperMode')==1 and q('OperMode_Task')==3 and q('GameEngineSubroutine')==8
end
emu.addMemoryCallback(function(_,v)
 local old=dmaMask;dmaMask=v;local s=dmaStamp();local scoped=dmaScope()
 local enabling=old&24==0 and v&24~=0
 local safe=s.scanline>=241 and s.scanline<=260 or s.scanline==-1 and s.cycle<=274
 dmaRow({kind='actual-PPUMASK-write',stamp=s,old=old,value=v,scoped=scoped,enabling=enabling,safe=safe})
 if scoped and enabling then assert(safe,'Scoped render enable precedes native pre-render vertical reload')end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 -- Retain the original publication admission and later endFrame assertion.
 dma=nil
 if entered and not done and published then local s=bytes(v*256,emu.memType.nesDebug);if s==published then dma=s end end
 assert(not dmaPending,'Prior DMA reaches genuine completion before another request')
 dmaSerial=dmaSerial+1
 dmaPending={id=dmaSerial,page=v,source=bytes(v*256,emu.memType.nesDebug),start=dmaStamp(),writes={},source_publication_match=dma~=nil}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 local q=dmaPending;if not q then return end
 local s=dmaStamp();q.writes[#q.writes+1]={value=v,stamp=s}
end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(pc)
 if bank(pc)~=dmaProtocol.bank then return end
 for i,v in ipairs(dmaProtocol.window_bytes)do assert(emu.read(dmaProtocol.window_start+i-1,emu.memType.nesDebug)==v,'Actual eight-byte postDMA protocol')end
 local q=assert(dmaPending,'Genuine completion belongs to an observed DMA')
 q.complete=dmaStamp();q.hardware=bytes(0,emu.memType.nesSpriteRam)
 local row={kind='completed-DMA-before-render-enable',id=q.id,page=q.page,start=q.start,complete=q.complete,source=dmaArray(q.source),hardware=dmaArray(q.hardware),writes=q.writes,source_publication_match=q.source_publication_match,differences={},implemented_differences={},ignored_attribute_differences={}}
 local physical=oamPhysical(q.source)
 for i=1,256 do
  if q.source:byte(i)~=q.hardware:byte(i)then
   local d={offset=i-1,source=q.source:byte(i),hardware=q.hardware:byte(i)};row.differences[#row.differences+1]=d
   if physical:byte(i)==q.hardware:byte(i)then row.ignored_attribute_differences[#row.ignored_attribute_differences+1]=d else row.implemented_differences[#row.implemented_differences+1]=d end
  end
 end
 -- Full raw source/destination and every write precede ALL equality guards.
 dmaRow(row)
 assert(#q.writes==256,'Actual DMA has256 data writes before E008 completion')
 assert(q.page==2 and q.start.pc==dmaProtocol.window_start,'Genuine page2 OAM owner reports its real post-store PC')
 assert(q.start.oamaddr==0 and q.complete.oamaddr==0,'Actual DMA starts/ends at OAMADDR0')
 assert(q.start.mask&0x18==0 and q.complete.mask&0x18==0,'Rendering remains disabled through completed DMA')
 for i,wq in ipairs(q.writes)do
  assert(wq.stamp.mask&0x18==0,'Rendering remains disabled at every actual DMA data write')
  assert(wq.stamp.oamaddr==i-1,'Actual DMA destination ordinal is unmodified')
  assert(wq.value==q.source:byte(i),'Actual DMA reads its exact frozen source byte')
 end
 assert(q.hardware==physical,'All256 physical OAM bytes equal exact PPU encoding of the actual DMA source')
 dmaCompleted=q;dmaPending=nil
end,emu.callbackType.exec,dmaProtocol.complete_pc)
emu.addEventCallback(function()
 -- Bind a displayed epoch only to its last completed transfer; a genuinely
 -- pending transfer is logged separately, never relabeled as completed.
 local hardware=bytes(0,emu.memType.nesSpriteRam)
 dmaRow({kind='startFrame-hardware',stamp=dmaStamp(),completed_dma_id=dmaCompleted and dmaCompleted.id,pending_dma_id=dmaPending and dmaPending.id,hardware=dmaArray(hardware)})
 if dmaCompleted and not dmaPending then assert(hardware==oamPhysical(dmaCompleted.source),'startFrame hardware retains last completed DMA with exact PPU attribute encoding')end
end,emu.eventType.startFrame)
