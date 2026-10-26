-- Read-only observations. No emulated state, OAM, resources or outcome writes.
local C=assert(PARODIUS_VISIBILITY);local D=C.ram
local wall,updates,txid,pubid,dmaid=0,0,0,0,0
local nmis,chrChecks,dmaChecks,minSP=0,0,0,255
local transaction,body,bodyPending,drawOwner,lastPub,lastDMA,visible=nil,nil,nil,nil,nil,nil,nil
local ownerSequence={};local records=assert(io.open(C.output..'epochs.jsonl','w'))
local writes=assert(io.open(C.output..'body-writes.jsonl','w'))
local bus=assert(io.open(C.output..'oam-bus.jsonl','w'))
local oamAddress,ppuMask,nmiDepth,partialStarts=0,0,0,0
local completeMismatches,bodyRowMismatches,firstMismatch,irqDepth,profileSerial,ownerChecks=0,0,false,0,0,0
local dmaPending,completionHooks=nil,{}
local function r(n,i)return emu.read(assert(D[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function stamp()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount']}end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function row(f,t)f:write(json(t)..'\n');f:flush()end
local function detail()local t={};for k,v in pairs(emu.getState())do if k:sub(1,4)=='ppu.'then t[k]=v end end;return t end
emu.addMemoryCallback(function(_,v)oamAddress=v;if wall>=440 then row(bus,{kind='2003',ppu=stamp(),value=v,state=detail(),nmi_depth=nmiDepth})end end,emu.callbackType.write,0x2003)
emu.addMemoryCallback(function(_,v)
 local q=dmaPending;if q then q.data_writes=(q.data_writes or 0)+1;q.last_data_write=stamp()end
 if wall>=440 then local s=emu.getState();row(bus,{kind=q and'dma-2004'or'2004-unassociated',dma_id=q and q.id,byte=q and q.data_writes,ppu=stamp(),value=v,last_software_address=oamAddress,actual_hardware_address=s['ppu.spriteRamAddr'],writer_pc=s['cpu.pc'],writer_bank=bank(s['cpu.pc']),mask=ppuMask,nmi_depth=nmiDepth})end;oamAddress=(oamAddress+1)%256
end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(_,v)ppuMask=v;if wall>=440 then row(bus,{kind='2001-mask',ppu=stamp(),value=v,state=detail(),nmi_depth=nmiDepth,irq_depth=irqDepth})end end,emu.callbackType.write,0x2001)
for _,a in ipairs({0x2000,0x2005,0x2006,0x5203,0x5204})do
 emu.addMemoryCallback(function(_,v)if wall>=440 then local s=emu.getState();row(bus,{kind='PPU-mapper-write',address=a,value=v,ppu=stamp(),writer_pc=s['cpu.pc'],writer_bank=bank(s['cpu.pc']),nmi_depth=nmiDepth,irq_depth=irqDepth,mask=ppuMask})end end,emu.callbackType.write,a)
end
emu.addMemoryCallback(function(_,v)if wall>=440 then local s=emu.getState();row(bus,{kind='2007-data',value=v,ppu=stamp(),vram_address=s['ppu.videoRamAddr'],writer_pc=s['cpu.pc'],writer_bank=bank(s['cpu.pc']),nmi_depth=nmiDepth,mask=ppuMask})end end,emu.callbackType.write,0x2007)
for _,range in ipairs({{0x4000,0x4013},{0x4015,0x4015},{0x4017,0x4017}})do
 emu.addMemoryCallback(function(a,v)if wall>=440 then local s=emu.getState();row(bus,{kind='APU-write',ppu=stamp(),address=a,value=v,writer_pc=s['cpu.pc'],writer_bank=bank(s['cpu.pc']),nmi_depth=nmiDepth,irq_depth=irqDepth})end end,emu.callbackType.write,range[1],range[2])
end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==C.character and r('VvVariant')==C.variant end
local function bytes(at,kind)local t={};for i=0,255 do t[#t+1]=emu.read(at+i,kind)end;return t end
local function equal(a,b)if not a or not b or#a~=#b then return false end;for i=1,#a do if a[i]~=b[i]then return false end end;return true end
local function hook(n,fn)local h=C.hooks[n];emu.addMemoryCallback(function()if bank(h.address)~=h.bank then return end;for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact observer hook '..n)end;minSP=math.min(minSP,emu.getState()['cpu.sp']);fn()end,emu.callbackType.exec,h.address)end
-- STATIC_RETURN_CORE_START
-- Lua-only slots retain the original dynamic callbacks' first-registration order.
-- Every real emulator callback is registered before emulation begins.
local pending,installed,returnSlotsByPC={},{},{}
local function queueReturnSlot(pc,fn)
 local slots=returnSlotsByPC[pc]
 if not slots then slots={};returnSlotsByPC[pc]=slots end
 slots[#slots+1]=fn
end
local dispatcherInstalled=false
PARODIUS_STATIC_INSTALL_RETURNS=function()
 assert(not dispatcherInstalled,'Static return dispatcher installed exactly once')
 dispatcherInstalled=true
 -- The generated complete run.lua invokes this AFTER the controller harness.
 emu.addMemoryCallback(function(pc)
  local slots=returnSlotsByPC[pc];if not slots then return end
  for i=1,#slots do slots[i]()end
 end,emu.callbackType.exec,0,0xffff)
end
local function onReturn(n,fn)
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536;local key=n..':'..pc
 pending[key]={sp=(sp+2)%256,bank=bank(pc),fn=fn}
 if not installed[key]then installed[key]=true;queueReturnSlot(pc,function()local q=pending[key];if q and emu.getState()['cpu.sp']==q.sp and bank(pc)==q.bank then pending[key]=nil;q.fn()end end)end
end
-- STATIC_RETURN_CORE_END
for _,name in ipairs(C.profile_hooks or{})do
 hook(name,function()
  if name=='UpdateScreen'then
   local s=emu.getState();ownerChecks=ownerChecks+1;assert(nmiDepth==1 and bank(0xc000)==116,'Every actual UpdateScreen entry owns NMI bankC116')
   row(bus,{kind='UpdateScreen-owner',ppu=stamp(),nmi_depth=nmiDepth,actual_bankA=bank(0xa000),actual_bankC=bank(0xc000),SP=s['cpu.sp'],return_word=emu.read(256+(s['cpu.sp']+1)%256,emu.memType.nesDebug)+256*emu.read(256+(s['cpu.sp']+2)%256,emu.memType.nesDebug),mask=ppuMask})
  end
  if wall<440 or nmiDepth==0 then return end
  profileSerial=profileSerial+1;local id=profileSerial;local start=stamp();local s=emu.getState();local fields={}
  for n,a in pairs(C.profile_ram or{})do fields[n]=emu.read(a,emu.memType.nesDebug)end
  local packet=nil;if name=='UpdateScreen'then packet={pointer=fields.NmiR0+256*fields.NmiR1,bytes={}};for i=0,63 do packet.bytes[#packet.bytes+1]=emu.read((packet.pointer+i)%65536,emu.memType.nesDebug)end end
  row(bus,{kind='routine-entry',name=name,id=id,ppu=start,nmi_depth=nmiDepth,irq_depth=irqDepth,mask=ppuMask,sp=s['cpu.sp'],ram=fields,packet=packet,cpu_a=s['cpu.a'],cpu_x=s['cpu.x'],cpu_y=s['cpu.y']})
  onReturn('profile-'..id,function()local finish=stamp();row(bus,{kind='routine-return',name=name,id=id,ppu=finish,entry=start,inclusive_CPU_cycles=finish.cpu-start.cpu,nmi_depth=nmiDepth,irq_depth=irqDepth,mask=ppuMask})end)
 end)
end
hook('IrqScrollSplit',function()irqDepth=irqDepth+1;if wall>=440 then row(bus,{kind='IRQ-entry',ppu=stamp(),depth=irqDepth,mask=ppuMask,nmi_depth=nmiDepth,state=detail()})end end)
hook('IrqReturn',function()if wall>=440 then row(bus,{kind='IRQ-return-before-RTI',ppu=stamp(),depth=irqDepth,mask=ppuMask,nmi_depth=nmiDepth,state=detail()})end;irqDepth=irqDepth-1;assert(irqDepth>=0,'Balanced IRQ depth')end)
hook('GameLoop',function()if active()then updates=updates+1;assert(r('CrossoverBehaviorVersion')==C.mode,'Actual numeric mode readback')end end)
hook('DrawAllMetasprites',function()
 if not active()then return end
 txid=txid+1;transaction={id=txid,entry=stamp(),world_x=r('Player_X_Position')+256*r('Player_PageLoc'),player_y=r('Player_Y_Position'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),native_frame=r('PnFrame'),pool=r('PnPool'),body_pointer=r('SmPosePtr')+256*r('SmPosePtr',1),prior_used=r('RgOamUsed'),prior_first=r('RgOamFirst')};body=nil;ownerSequence={}
end)
hook('PnDraw',function()
 if not active()or not transaction then return end
 local before=r('CurrentOAMOffset');onReturn('pn-prefill',function()transaction.prefill={entry_cursor=before,end_cursor=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),first=r('RgOamFirst'),oam=bytes(D.Sprite_Data,emu.memType.nesDebug),finished=stamp()}end)
end)
hook('DrawMetasprite',function()
 if not active()or not transaction then return end
 local owner=emu.getState()['cpu.y'];drawOwner=owner;ownerSequence[#ownerSequence+1]=owner
 onReturn('draw-owner-'..owner,function()
  if owner==0 and bodyPending then
   body=bodyPending;bodyPending=nil;body.finished=stamp();body.cursor_after=r('CurrentOAMOffset');body.parts={}
   for _,i in ipairs(body.indices)do local p={};for j=0,3 do p[#p+1]=emu.read(D.Sprite_Data+i*4+j,emu.memType.nesDebug)end;body.parts[#body.parts+1]=p end
   body.index_set=nil
  end
  drawOwner=nil
 end)
end)
hook('MetaspriteRenderLoop',function()
 if drawOwner~=0 or not transaction then return end
 local ptr=r('R0')+256*r('R1');local physical=bank(ptr);local source=assert(C.body_sources[tostring(physical)..':'..ptr],'Actual body immutable record alias')
 for i,v in ipairs(source.bytes)do assert(emu.read(ptr+i-1,emu.memType.nesDebug)==v,'Exact current body record bytes')end
 bodyPending={transaction=txid,entry=stamp(),pointer=ptr,bank=physical,source=source,origin={x=r('R4'),page=r('R5'),y=r('R6'),high=r('R7')},attribute=r('R3'),rotation=r('RgOamRotation'),first=r('RgOamFirst'),player_start=r('RgOamPlayerStart'),cursor_before=r('CurrentOAMOffset'),world_prefill=bytes(D.Sprite_Data,emu.memType.nesDebug),indices={},index_set={}}
end)
emu.addMemoryCallback(function(a,v)
 if not bodyPending or drawOwner~=0 then return end
 local index=(a-D.Sprite_Data)//4
 if not bodyPending.index_set[tostring(index)]then bodyPending.index_set[tostring(index)]=true;bodyPending.indices[#bodyPending.indices+1]=index end
 if wall>=C.capture_start-3 and wall<=C.capture_end+3 then local s=emu.getState();row(writes,{ppu=stamp(),transaction=txid,source=bodyPending.source.label,index=index,address=a,previous=emu.read(a,emu.memType.nesDebug),value=v,callback_pc=s['cpu.pc'],writer_bank=bank(s['cpu.pc']),instruction_window={emu.read(s['cpu.pc']-3,emu.memType.nesDebug),emu.read(s['cpu.pc']-2,emu.memType.nesDebug),emu.read(s['cpu.pc']-1,emu.memType.nesDebug)}})end
end,emu.callbackType.write,D.Sprite_Data,D.Sprite_Data+255)
hook('RosterOamReady',function()
 if not active()or not transaction then return end
 pubid=pubid+1;lastPub={id=pubid,ppu=stamp(),transaction=transaction,body=body,owners=ownerSequence,oam=bytes(D.Sprite_Data,emu.memType.nesDebug),used=r('RgOamUsed'),rotation=r('RgOamRotation'),first=r('RgOamFirst')}
 if body then for j,i in ipairs(body.indices)do for k=0,3 do assert(lastPub.oam[i*4+k+1]==body.parts[j][k+1],'Body survives world/publication owner')end end end
end)
emu.addMemoryCallback(function(_,v)
 if not active()or not lastPub then return end
 local image=bytes(v*256,emu.memType.nesDebug);assert(equal(image,lastPub.oam),'Actual DMA is exact last completed native publication')
 local s=emu.getState();local pc=s['cpu.pc'];local physical=bank(pc)
 dmaid=dmaid+1;lastDMA={id=dmaid,ppu=stamp(),publication=lastPub,mask=ppuMask,oam_address=oamAddress,writer_callback_pc=pc,writer_bank=physical,writer_instruction={emu.read(pc-3,emu.memType.nesDebug),emu.read(pc-2,emu.memType.nesDebug),emu.read(pc-1,emu.memType.nesDebug)},state=detail(),nmi_depth=nmiDepth}
 dmaPending=lastDMA;row(bus,{kind='4014-start',dma_id=dmaid,ppu=lastDMA.ppu,mask=ppuMask,oam_address=oamAddress,writer_pc=pc,bank=physical,nmi_depth=nmiDepth})
 assert(emu.read(pc,emu.memType.nesDebug)==0xa2 and emu.read(pc+1,emu.memType.nesDebug)==1,'Actual DMA caller next instruction LDX#1')
 local finishpc=pc+2 -- Exec at pc itself runs before the DMA halt; after LDX is completed.
 local key=tostring(physical)..':'..finishpc
 if not completionHooks[key]then completionHooks[key]=true;queueReturnSlot(finishpc,function()
  if not dmaPending or bank(finishpc)~=physical then return end
  local q=dmaPending;dmaPending=nil;q.complete={ppu=stamp(),hardware=bytes(0,emu.memType.nesSpriteRam),mask=ppuMask,state=detail(),nmi_depth=nmiDepth,completed_2004_writes=q.data_writes};q.complete.exact_source=equal(q.complete.hardware,q.publication.oam);row(bus,{kind='4014-complete-after-next-LDX',dma_id=q.id,ppu=q.complete.ppu,exact_source=q.complete.exact_source,completed_2004_writes=q.data_writes,mask=ppuMask,nmi_depth=nmiDepth,hardware=q.complete.hardware,source=q.publication.oam});assert(q.data_writes==256,'Completed DMA256 writes');if not q.complete.exact_source then completeMismatches=completeMismatches+1;assert(C.diagnostic,'Completed DMA hardware exact source image')end
 end)end
end,emu.callbackType.write,0x4014)
local upper,physical=0,{}
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+upper*256;if wall>=440 then row(bus,{kind='CHR-write',ppu=stamp(),address=a,value=v,upper=upper,physical=physical[a-0x5120],nmi_depth=nmiDepth,mask=ppuMask})end end,emu.callbackType.write,0x5120,0x512b)
local saved
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function window(pc,target,shadow)if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end;return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)end
hook('NonMaskableInterrupt',function()
 nmiDepth=nmiDepth+1;if wall>=440 then row(bus,{kind='NMI-entry',ppu=stamp(),depth=nmiDepth,mask=ppuMask})end
 if not active()then return end;local s=emu.getState();local sp=s['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
 saved={a=bank(0xa000),c=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,sp=sp,cpu_a=s['cpu.a'],fields={}};saved.wa=saved.a~=saved.sa and window(pc,0x5115,D.CurrentBank);saved.wc=saved.c~=saved.sc and window(pc,0x5116,D.CurrentBankC)
 for _,a in ipairs(C.smc)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end;nmis=nmis+1
end)
hook('NmiReturn',function()
 if wall>=440 then row(bus,{kind='NMI-return',ppu=stamp(),depth=nmiDepth,mask=ppuMask})end;nmiDepth=nmiDepth-1;assert(nmiDepth>=0,'Balanced NMI depth')
 if not saved then return end;assert(bank(0xa000)==(saved.wa and saved.sa or saved.a)and bank(0xc000)==(saved.wc and saved.sc or saved.c),'NMI actual bank restore');assert(r('CurrentBank')&127==saved.sa and r('CurrentBankC')&127==saved.sc,'NMI bank shadows');assert(emu.getState()['cpu.sp']==saved.sp and emu.getState()['cpu.a']==saved.cpu_a,'NMI A/SP restore');for i,a in ipairs(C.smc)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'NMI5 SMC restore')end;saved=nil
end)
emu.addMemoryCallback(function()if active()then assert(emu.getState()['cpu.sp']>=128,'Lower native stack guard')end end,emu.callbackType.write,0x17f)
emu.addEventCallback(function()
 visible=nil;if not active()or not lastDMA then return end
 local hardware=bytes(0,emu.memType.nesSpriteRam)
 if not equal(hardware,lastDMA.publication.oam)and not firstMismatch then
  firstMismatch=true
  local diff={};for i=1,256 do if hardware[i]~=lastDMA.publication.oam[i]then diff[#diff+1]={offset=i-1,hardware=hardware[i],DMA_source=lastDMA.publication.oam[i]}end end
  local f=assert(io.open(C.output..'first-hardware-mismatch.json','w'));f:write(json({start=stamp(),last_DMA=lastDMA,hardware=hardware,differences=diff,live_transaction=transaction,live_body=body,updates=updates}));f:close()
 end
 local exact=equal(hardware,lastDMA.publication.oam)
 if not exact then partialStarts=partialStarts+1;assert(C.diagnostic,'Actual visible-start hardware OAM matches DMA publication')else dmaChecks=dmaChecks+1 end
 local s=emu.getState();local banks={};for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual write-time MMC5 CHR');banks[#banks+1]=s['mapper.chrBanks'..i];chrChecks=chrChecks+1 end
 visible={start=stamp(),dma=lastDMA,chr_banks=banks,palette={},start_hardware=hardware,start_hardware_exact_source=exact,mask=ppuMask,nmi_depth=nmiDepth,start_state=detail(),dma_finished_before_start=lastDMA.complete~=nil};for i=0,31 do visible.palette[#visible.palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
end,emu.eventType.startFrame)
-- Body-pattern reads sample the first actual body raster row, independently
-- of a partially completed cold-transition DMA at pre-render start.
local rasterInstalled=false
emu.addMemoryCallback(function(address)
   if not rasterInstalled then return end
   if not visible or visible.body_row or not visible.dma.publication.body then return end
   local b=visible.dma.publication.body;local wanted=false
   for _,p in ipairs(b.parts)do local tile=p[2];local base=(tile&1)*4096+(tile&254)*16;if address>=base and address<base+32 then wanted=true;break end end
   if not wanted then return end
   local minimum=240;for _,p in ipairs(b.parts)do if p[1]<240 then minimum=math.min(minimum,p[1]+1)end end
   local s=emu.getState();if s['ppu.scanline']<minimum then return end
   visible.body_row={ppu=stamp(),hardware=bytes(0,emu.memType.nesSpriteRam),mask=ppuMask,state=detail(),nmi_depth=nmiDepth,minimum_body_y=minimum,dma_complete=visible.dma.complete~=nil}
   visible.body_row.exact_source=equal(visible.body_row.hardware,visible.dma.publication.oam)
   assert(visible.body_row.dma_complete,'Completed DMA before actual body raster row');if not visible.body_row.exact_source then bodyRowMismatches=bodyRowMismatches+1;assert(C.diagnostic,'Exact published hardware at actual body raster row')end
end,emu.callbackType.read,0,0x1fff,emu.cpuType.nes,emu.memType.nesPpuMemory)
emu.addEventCallback(function()
 wall=wall+1;local s=emu.getState();assert(s['ppu.frameCount']==wall,'Actual endFrame PPU count')
 if wall==C.capture_start-1 and not rasterInstalled then
  rasterInstalled=true
 end
 if visible and wall>=C.start_frame then
  visible.finished=stamp();assert(visible.start.frame==visible.finished.frame and visible.start.scanline==-1 and visible.finished.scanline==240,'Exact visible PPU epoch')
  if wall>=C.capture_start and wall<=C.capture_end then local name=string.format('frame-%06d.argb',wall);local f=assert(io.open(C.output..name,'wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close();visible.capture=name end
  row(records,visible)
 end
 if wall>=C.limit then
  assert(updates>=25 and dmaid>=25 and nmis>=25,'Bounded cold menu reaches meaningful real active gameplay');assert(r('CrossoverBehaviorVersion')==C.mode and r('SelectedCharacter')==C.character and r('VvVariant')==C.variant,'Final numeric mode/character/variant readback')
  local q={passed=partialStarts==0 and completeMismatches==0 and bodyRowMismatches==0,diagnostic=C.diagnostic==true,partial_DMA_visible_starts=partialStarts,completed_DMA_source_mismatches=completeMismatches,body_raster_source_mismatches=bodyRowMismatches,goal_complete=false,component_only=true,ROM_sha256=C.ROM_sha256,actual_mode=r('CrossoverBehaviorVersion'),actual_variant=r('VvVariant'),wall=wall,updates=updates,publications=pubid,DMAs=dmaid,nmis=nmis,chr_checks=chrChecks,dma_checks=dmaChecks,all_boot_UpdateScreen_C116_owner_checks=ownerChecks,min_sampled_SP=minSP,no_emulated_writes=true,scope='Bounded cold-menu native controller; independently bind source publication, completed DMA, actual PPU body rows and NMI/IRQ/APU work. Diagnostics retain failures. No stage clear or sprite-priority-fix verdict.'};local f=assert(io.open(C.output..'native-result.json','w'));f:write(json(q));f:close();records:close();writes:close();bus:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
