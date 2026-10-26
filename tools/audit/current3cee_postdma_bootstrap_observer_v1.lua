-- DIAGNOSTIC ONLY: complete raw observations, no masked/forgiven equality.
local C=assert(BOOTSTRAP_DMA_DIAGNOSTIC)
-- Direct console buffer for the finite startup window; no decoder screenshots.
local picture=assert(io.open(OUTPUT..'startup-direct.argb','wb'))
local pictureIndex=assert(io.open(OUTPUT..'startup-direct-index.csv','w'))
pictureIndex:write('wallFrame,ppuFrame,cpuCycle,pixels\n')
local pictureFrame=0
emu.addEventCallback(function()
 pictureFrame=pictureFrame+1
 if pictureFrame>=176 and pictureFrame<=190 then
  local s=emu.getState();local pixels=emu.getScreenBuffer();assert(#pixels==61440,'Direct256x240buffer')
  local chunks={};for i,v in ipairs(pixels)do chunks[i]=string.pack('<I4',v)end
  picture:write(table.concat(chunks));pictureIndex:write(table.concat({pictureFrame,s['ppu.frameCount'],s['cpu.cycleCount'],#pixels},',')..'\n')
 end
end,emu.eventType.endFrame)
local originalStop=emu.stop
emu.stop=function(code)picture:close();pictureIndex:close();originalStop(code)end

local f=assert(io.open(OUTPUT..'bootstrap-events.jsonl','w'));local input=assert(io.open(OUTPUT..'inputs.csv','w'));input:write('poll,frame,mask\n')
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function row(t)f:write(json(t)..'\n');f:flush()end
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return read(assert(C.ram[n],n))end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or-1 end
local function stamp()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],cpu=s['cpu.cycleCount']}end
local function ppustate()local t={};for k,v in pairs(emu.getState())do if k:sub(1,4)=='ppu.'then t[k]=v end end;return t end
local function bytes(a,n,kind)local t={};for i=0,n-1 do t[#t+1]=emu.read((a+i)%65536,kind or emu.memType.nesDebug)end;return t end
local function difference(a,b)local t={};for i=1,256 do if a[i]~=b[i]then t[#t+1]={offset=i-1,source=a[i],hardware=b[i]}end end;return t end
local function control()local t={};for n,a in pairs(C.ram)do t[n]=read(a)end;return t end
local frame,poll,dmas,mismatches,nmiDepth,sourceWrites,profileID,rawNewCodeHits=0,0,0,0,0,0,0,0
local mask,ctrl,last2003=0,0,0;local pending=nil;local owners={};local sourceMirror=bytes(0x200,256);local main=nil;local mainSerial=0
local profiles,pendingReturns,installedReturns={},{},{}
for i=1,256 do owners[i]=0 end
row({kind='initial-OAM-source',ppu=stamp(),source=sourceMirror,state=control(),PPU=ppustate()})
local function hook(n,fn)local h=assert(C.hooks[n],n);emu.addMemoryCallback(function()
 if bank(h.pc)~=h.bank then return end
 for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact diagnostic hook '..n)end
 fn()
end,emu.callbackType.exec,h.pc)end
local function onReturn(name,fn)
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(read(256+(sp+1)%256)+256*read(256+(sp+2)%256)+1)%65536;local owner=bank(pc);local key=name..':'..pc..':'..owner
 pendingReturns[key]={sp=(sp+2)%256,fn=fn}
 if not installedReturns[key]then installedReturns[key]=true;emu.addMemoryCallback(function()
  local q=pendingReturns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(pc)~=owner then return end
  pendingReturns[key]=nil;q.fn()
 end,emu.callbackType.exec,pc)end
end
for _,name in ipairs(C.profile_names)do hook(name,function()
 profileID=profileID+1;local id=profileID;local t=stamp();local s=emu.getState();local q={kind='routine-entry',name=name,id=id,ppu=t,SP=s['cpu.sp'],bankA=bank(0xa000),bankC=bank(0xc000),nmi_depth=nmiDepth,state=control(),PPUMASK=mask}
 if t.frame>=176 and t.frame<=190 and(name=='UpdateScreen'or name=='SamusFreezeUpdateScreen')then
  local ptr=r('NmiR0')+256*r('NmiR1');q.actual_packet={pointer=ptr,bank=ptr>=0x8000 and bank(ptr)or-1,bytes1024=bytes(ptr,1024),VRAM_Buffer1=bytes(C.ram.VRAM_Buffer1,256),VRAM_Buffer2=bytes(C.ram.VRAM_Buffer2,256)}
 end
 row(q);onReturn('profile-'..name,function()local at=stamp();row({kind='routine-return',name=name,id=id,ppu=at,entry=t,inclusive_CPU_cycles=at.cpu-t.cpu,nmi_depth=nmiDepth})end)
end)end
hook('NmiEntry',function()nmiDepth=nmiDepth+1;row({kind='NMI-entry',ppu=stamp(),depth=nmiDepth,state=control(),PPU=ppustate(),bankA=bank(0xa000),bankC=bank(0xc000)})end)
hook('NmiReturn',function()row({kind='NMI-return',ppu=stamp(),depth=nmiDepth});nmiDepth=nmiDepth-1;assert(nmiDepth>=0,'Balanced NMI profile')end)
hook('GameLoopEntry',function()mainSerial=mainSerial+1;main=mainSerial;row({kind='Main-entry',id=main,ppu=stamp(),state=control()})end)
emu.addMemoryCallback(function(_,v)
 if v==0 and emu.getState()['cpu.pc']==C.hooks.GameLoopDone.pc then row({kind='Main-release',id=main or-1,ppu=stamp(),writerPC=emu.getState()['cpu.pc'],writerBank=bank(emu.getState()['cpu.pc']),state=control(),source=bytes(0x200,256)})end
end,emu.callbackType.write,C.ram.NmiDisable)
hook('GameLoopDone',function()row({kind='Main-return',id=main or-1,ppu=stamp()});main=nil end)
emu.addMemoryCallback(function(a,v)
 sourceWrites=sourceWrites+1;sourceMirror[a-0x200+1]=v;owners[a-0x200+1]=sourceWrites
 row({kind='source-write',id=sourceWrites,address=a,value=v,writerPC=emu.getState()['cpu.pc'],writerBank=bank(emu.getState()['cpu.pc']),ppu=stamp(),Main=main or-1,state=control()})
end,emu.callbackType.write,0x200,0x2ff)
emu.addMemoryCallback(function(_,v)mask=v;row({kind='PPUMASK-write',ppu=stamp(),value=v,actualPPU=ppustate()})end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(_,v)last2003=v;row({kind='OAMADDR-write',ppu=stamp(),value=v,actualPPU=ppustate()})end,emu.callbackType.write,0x2003)
emu.addMemoryCallback(function(_,v)
 if not pending then row({kind='unassociated2004',ppu=stamp(),value=v,PPUMASK=mask,actualPPU=ppustate()});return end
 pending.writes=pending.writes+1;local t=stamp();if not pending.first_write then pending.first_write=t end;pending.last_write=t
 row({kind='DMA2004',DMA=pending.id,ordinal=pending.writes,ppu=t,value=v,PPUMASK=mask,software2003=last2003,actual_OAMADDR=emu.getState()['ppu.spriteRamAddr'],writerPC=emu.getState()['cpu.pc'],writerBank=bank(emu.getState()['cpu.pc'])})
end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(_,v)
 dmas=dmas+1;local source=bytes(v*256,256);local s=emu.getState()
 pending={id=dmas,begin=stamp(),source_page=v,source=source,before_hardware=bytes(0,256,emu.memType.nesSpriteRam),source_owners=owners,source_write_count=sourceWrites,PPUMASK=mask,PPUCTRL=ctrl,software2003=last2003,actualPPU=ppustate(),state=control(),writerPC=s['cpu.pc'],writerBank=bank(s['cpu.pc']),writes=0}
 row({kind='DMA-start',DMA=pending,observed_source_mirror=sourceMirror})
 assert(s['cpu.pc']==C.dma_next.pc and bank(s['cpu.pc'])==127,'Genuine bootstrap DMA callsite')
 assert(v==2,'Original page2 DMA source')
 assert(#difference(source,sourceMirror)==0,'All recorded source writers reproduce complete source')
end,emu.callbackType.write,0x4014)
hook('DmaComplete',function()
 if not pending then return end
 local q=pending;pending=nil;local hw=bytes(0,256,emu.memType.nesSpriteRam);local wrong=difference(q.source,hw);local at=stamp()
 -- Serialize full raw destination, all mismatches and actual PPU BEFORE checks.
 row({kind='DMA-complete',DMA=q.id,ppu=at,source=q.source,hardware=hw,differences=wrong,exact=#wrong==0,transferred=q.writes,first2004=q.first_write,last2004=q.last_write,PPUMASK=mask,PPUCTRL=ctrl,software2003=last2003,actualPPU=ppustate(),begin=q.begin,writerPC=emu.getState()['cpu.pc'],writerBank=bank(emu.getState()['cpu.pc'])})
 assert(q.writes==256,'Every actual DMA supplies256 writes')
 if #wrong>0 then mismatches=mismatches+1 end
 -- This diagnostic retains the failed equality, continues only to its fixed
 -- bootstrap limit, and exits1 if ANY complete image was unequal. No byte mask.
end)
for _,reg in ipairs({0x2005,0x2006,0x2007,0x5203,0x5204})do emu.addMemoryCallback(function(_,v)
 local t=stamp();if t.frame>=176 and t.frame<=190 then row({kind='bounded-PPU-write',ppu=t,reg=reg,value=v,PPUMASK=mask,nmi_depth=nmiDepth,writerPC=emu.getState()['cpu.pc'],writerBank=bank(emu.getState()['cpu.pc']),vramAddress=emu.getState()['ppu.videoRamAddr']})end
end,emu.callbackType.write,reg)end
emu.addMemoryCallback(function(pc)if bank(pc)==66 then rawNewCodeHits=rawNewCodeHits+1;row({kind='unexpected-new-shot-code-execution',pc=pc,ppu=stamp()})end end,emu.callbackType.exec,0xb9a8,0xbb48)
local fixed={};for line in io.lines(C.prefix)do local p,fr,m=line:match('^(%d+),(%d+),(%d+)$');if p then fixed[tonumber(p)]={frame=tonumber(fr),mask=tonumber(m)}end end
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
emu.addEventCallback(function()
 poll=poll+1;local v=fixed[poll];local value=0;if v then assert(v.frame==frame,'Exact recorded bootstrap input frame');value=v.mask end
 local keys={};for k,bit in pairs(bits)do keys[k]=value&bit~=0 end;input:write(poll..','..frame..','..value..'\n');emu.setInput(keys,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;row({kind='wall-frame',frame=frame,ppu=stamp(),state=control(),PPU=ppustate()})
 if frame>=C.limit then
  local q={diagnostic_complete=true,passed=mismatches==0,hardware_mismatch_DMAs=mismatches,DMAs=dmas,frames=frame,polls=poll,source_writes=sourceWrites,Main_entries=mainSerial,raw_new_shot_code_hits=rawNewCodeHits,all256_bytes_preserved=true,equality_masks_changed=false,no_gameplay_verdict=true,observer_game_state_writes=false,controller_prefix_only=true,static_dispatcher=TMNT_STATIC_EXEC.status()}
  local out=assert(io.open(OUTPUT..'diagnostic-result.json','w'));out:write(json(q));out:close();f:close();input:close();emu.stop(mismatches>0 and 1 or 0)
 end
end,emu.eventType.endFrame)
