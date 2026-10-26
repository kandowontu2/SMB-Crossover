-- Appended in the original observer's lexical scope. No original guard body
-- is replaced. All native callback registrations happen during startup.
local lifeGeneration,lifeInitPubs,lifeInitDMAs=0,0,0
local lifeCarryDMAs,lifeOffPartial,lifeVisibleChecks=0,0,0
local lifeFirstInitStartFailure=false
local function lifeOwn()return r('SelectedCharacter')==C.character and r('VvVariant')==C.variant end
local function lifeFields(phase)
 return{id=txid,entry=stamp(),world_x=r('Player_X_Position')+256*r('Player_PageLoc'),player_y=r('Player_Y_Position'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),native_frame=r('PnFrame'),pool=r('PnPool'),body_pointer=r('SmPosePtr')+256*r('SmPosePtr',1),prior_used=r('RgOamUsed'),prior_first=r('RgOamFirst'),phase=phase,generation=lifeGeneration}
end
local function lifePublish(phase,blank)
 assert(transaction and drawOwner==nil and bodyPending==nil,'Completed real init OAM owner')
 local image=bytes(D.Sprite_Data,emu.memType.nesDebug)
 if blank then for i=1,256,4 do assert(image[i]==248,'Real MoveAllSpritesOffscreen hides all64 sprites')end end
 pubid=pubid+1;lastPub={id=pubid,ppu=stamp(),transaction=transaction,body=body,owners=ownerSequence,oam=image,used=r('RgOamUsed'),rotation=r('RgOamRotation'),first=r('RgOamFirst'),phase=phase,generation=lifeGeneration}
 if body then for j,i in ipairs(body.indices)do for k=0,3 do assert(image[i*4+k+1]==body.parts[j][k+1],'Init body survives complete publication owner')end end end
 lifeInitPubs=lifeInitPubs+1
 row(bus,{kind='lifecycle-init-publication',phase=phase,generation=lifeGeneration,publication=lastPub.id,ppu=stamp(),body_source=body and body.source.label,oper=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine'),oam=image})
end
PARODIUS_LIFECYCLE_GENERATION=function()return lifeGeneration end
PARODIUS_PUBLICATION_SNAPSHOT=function()return visible,lastPub,lastDMA end
PARODIUS_INVALIDATE_PUBLICATION=function(reason)
 assert(nmiDepth==0 and irqDepth==0,'Native reset/death owner outside NMI/IRQ')
 assert(drawOwner==nil and bodyPending==nil and dmaPending==nil,'Reset cannot erase an incomplete emitter or DMA')
 lifeGeneration=lifeGeneration+1
 row(bus,{kind='host-publication-generation-end',reason=reason,ppu=stamp(),generation=lifeGeneration,prior_publication=lastPub and lastPub.id,prior_DMA=lastDMA and lastDMA.id,retained_visible_start=visible and visible.start,retained_source_generation=lastPub and lastPub.generation})
 -- Completed images remain immutable evidence under their old generation.
 -- The normal next startFrame owns clearing visible. No prior image is ever
 -- promoted to a new generation, searched from history, or written to the NES.
 transaction=nil;body=nil;bodyPending=nil;drawOwner=nil;ownerSequence={}
end
hook('DrawAllMetasprites',function()
 if not lifeOwn()or active()then return end
 txid=txid+1;transaction=lifeFields('init-draw');body=nil;ownerSequence={}
end)
hook('RosterOamReady',function()
 if not lifeOwn()then return end
 if active()then assert(lastPub,'Original live publication completed first');lastPub.generation=lifeGeneration;lastPub.phase='live';return end
 assert(transaction and transaction.phase=='init-draw','Init RosterOamReady has actual DrawAll entry')
 lifePublish('init-draw',false)
end)
hook('MoveAllSpritesOffscreen',function()
 if not lifeOwn()or active()then return end
 onReturn('life-blank',function()
  txid=txid+1;transaction=lifeFields('init-blank');body=nil;ownerSequence={};lifePublish('init-blank',true)
 end)
end)
hook('X5PortraitRender',function()
 if not lifeOwn()or active()then return end
 txid=txid+1;transaction=lifeFields('init-portrait');body=nil;ownerSequence={}
 onReturn('life-portrait',function()lifePublish('init-portrait',false)end)
end)
hook('DrawMetasprite',function()
 if not lifeOwn()or active()or not transaction then return end
 local owner=emu.getState()['cpu.y'];drawOwner=owner;ownerSequence[#ownerSequence+1]=owner
 onReturn('life-draw-owner-'..owner,function()
  if owner==0 and bodyPending then
   body=bodyPending;bodyPending=nil;body.finished=stamp();body.cursor_after=r('CurrentOAMOffset');body.parts={}
   for _,i in ipairs(body.indices)do local p={};for j=0,3 do p[#p+1]=emu.read(D.Sprite_Data+i*4+j,emu.memType.nesDebug)end;body.parts[#body.parts+1]=p end
   body.index_set=nil
  end
  drawOwner=nil
 end)
end)
-- The public parser label is also its per-command loop re-entry. Log the
-- actual pointer/return word instead of counting every entry as a JSR call.
hook('UpdateScreen',function()
 if not lifeOwn()or active()then return end
 local function profile(n)return emu.read(assert(C.profile_ram[n],n),emu.memType.nesDebug)end
 local s=emu.getState();local sp=s['cpu.sp'];local ptr=profile('NmiR0')+256*profile('NmiR1');local payload={}
 for i=0,127 do payload[#payload+1]=emu.read((ptr+i)%65536,emu.memType.nesDebug)end
 row(bus,{kind='lifecycle-init-parser-entry',ppu=stamp(),nmi_depth=nmiDepth,irq_depth=irqDepth,mask=ppuMask,SP=sp,PC=s['cpu.pc'],actual_bankA=bank(0xa000),actual_bankC=bank(0xc000),return_word=emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug),pointer=ptr,packet128=payload,ctrl=profile('VRAM_Buffer_AddrCtrl'),offset1=profile('VRAM_Buffer1_Offset'),offset2=profile('VRAM_Buffer2_Offset'),publication=lastPub and lastPub.id,source_generation=lastPub and lastPub.generation,game_generation=lifeGeneration})
end)
emu.addMemoryCallback(function(_,v)
 if not lifeOwn()or active()then return end
 assert(lastPub,'Inactive DMA must have a real observed blank/portrait/draw owner')
 local image=bytes(v*256,emu.memType.nesDebug);assert(equal(image,lastPub.oam),'Init DMA exact last complete native source')
 local s=emu.getState();local pc=s['cpu.pc'];local physicalBank=bank(pc)
 dmaid=dmaid+1;lastDMA={id=dmaid,ppu=stamp(),publication=lastPub,mask=ppuMask,oam_address=oamAddress,writer_callback_pc=pc,writer_bank=physicalBank,writer_instruction={emu.read(pc-3,emu.memType.nesDebug),emu.read(pc-2,emu.memType.nesDebug),emu.read(pc-1,emu.memType.nesDebug)},state=detail(),nmi_depth=nmiDepth,phase='init',game_generation=lifeGeneration,source_generation=lastPub.generation}
 dmaPending=lastDMA;lifeInitDMAs=lifeInitDMAs+1
 if lastPub.generation~=lifeGeneration then lifeCarryDMAs=lifeCarryDMAs+1 end
 row(bus,{kind='lifecycle-init-4014-start',dma_id=dmaid,ppu=lastDMA.ppu,mask=ppuMask,oam_address=oamAddress,writer_pc=pc,bank=physicalBank,nmi_depth=nmiDepth,game_generation=lifeGeneration,source_generation=lastPub.generation,source_phase=lastPub.phase})
 local protocol=assert(C.dma_protocol);assert(pc==protocol.next_pc,'Actual init DMA post-STA PC');for i,v in ipairs(protocol.next_bytes)do assert(emu.read(pc+i-1,emu.memType.nesDebug)==v,'Exact init postDMA eight-byte sequence')end;assert((ppuMask&24)==0,'Rendering disabled throughout actual DMA')
 local finishpc=protocol.complete_pc;assert(finishpc==pc+3,'Completion after actual LDA before STA2001');local key=tostring(physicalBank)..':'..finishpc
 if not completionHooks[key]then completionHooks[key]=true;queueReturnSlot(finishpc,function()
  if not dmaPending or bank(finishpc)~=physicalBank then return end
  local q=dmaPending;dmaPending=nil;q.complete={ppu=stamp(),hardware=bytes(0,emu.memType.nesSpriteRam),mask=ppuMask,state=detail(),nmi_depth=nmiDepth,completed_2004_writes=q.data_writes};q.complete.exact_source=equal(q.complete.hardware,q.publication.oam);row(bus,{kind='4014-complete-after-postDMA-LDA',dma_id=q.id,ppu=q.complete.ppu,exact_source=q.complete.exact_source,completed_2004_writes=q.data_writes,mask=ppuMask,nmi_depth=nmiDepth,hardware=q.complete.hardware,source=q.publication.oam});assert(q.data_writes==256,'Completed DMA256 writes');assert((ppuMask&24)==0,'Completed hardware observed before rendering enable');if not q.complete.exact_source then completeMismatches=completeMismatches+1;assert(C.diagnostic,'Completed DMA hardware exact source image')end
 end)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 if not lifeOwn()or active()or not lastDMA then return end
 assert(visible==nil,'Original nonlive startFrame clears only its new visible latch')
 local hardware=bytes(0,emu.memType.nesSpriteRam);local exact=equal(hardware,lastDMA.publication.oam);local rendering=(ppuMask&16)~=0
 local s=emu.getState();local differences={};for i=1,256 do if hardware[i]~=lastDMA.publication.oam[i]then differences[#differences+1]={offset=i-1,hardware=hardware[i],source=lastDMA.publication.oam[i]}end end
 local smc={};for _,a in ipairs(C.smc)do smc[#smc+1]=emu.read(a,emu.memType.nesDebug)end
 local observation={kind='lifecycle-init-start-before-assertion',ppu=stamp(),mask=ppuMask,sprites_enabled=rendering,software_OAMADDR=oamAddress,hardware_OAMADDR=s['ppu.spriteRamAddr'],CPU_PC=s['cpu.pc'],CPU_SP=s['cpu.sp'],actual_bankPC=bank(s['cpu.pc']),actual_bankA=bank(0xa000),actual_bankC=bank(0xc000),shadowA=r('CurrentBank'),shadowC=r('CurrentBankC'),fiveSMC=smc,nmi_depth=nmiDepth,irq_depth=irqDepth,ppu_state=detail(),DMA_id=lastDMA.id,DMA_start=lastDMA.ppu,DMA_writer_PC=lastDMA.writer_callback_pc,DMA_writer_bank=lastDMA.writer_bank,DMA_write_count=lastDMA.data_writes or 0,DMA_last_write=lastDMA.last_data_write,DMA_complete=lastDMA.complete~=nil,DMA_completion=lastDMA.complete,DMA_still_pending=dmaPending~=nil,hardware256=hardware,exact_source256=lastDMA.publication.oam,current_source_RAM256=bytes(D.Sprite_Data,emu.memType.nesDebug),hardware_exact_source=exact,differences=differences,publication=lastDMA.publication.id,source_phase=lastDMA.publication.phase,source_generation=lastDMA.publication.generation,game_generation=lifeGeneration}
 row(bus,observation)
 if rendering and(not lastDMA.complete or not exact)and not lifeFirstInitStartFailure then
  lifeFirstInitStartFailure=true;local f=assert(io.open(C.output..'first-init-start-mismatch.json','w'));f:write(json(observation));f:close()
 end
 if rendering then assert(lastDMA.complete and exact,'Visible init has complete exact hardware source');lifeVisibleChecks=lifeVisibleChecks+1
 elseif not lastDMA.complete or not exact then lifeOffPartial=lifeOffPartial+1 end
 local banks={};for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual init MMC5 CHR writes');banks[#banks+1]=s['mapper.chrBanks'..i]end
 visible={start=stamp(),dma=lastDMA,chr_banks=banks,palette={},start_hardware=hardware,start_hardware_exact_source=exact,mask=ppuMask,nmi_depth=nmiDepth,start_state=detail(),dma_finished_before_start=lastDMA.complete~=nil,phase='init',game_generation=lifeGeneration,source_generation=lastDMA.publication.generation,display_off_partial=not rendering and(not lastDMA.complete or not exact)}
 for i=0,31 do visible.palette[#visible.palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
 row(bus,{kind='lifecycle-init-visible-start',ppu=visible.start,mask=ppuMask,source_generation=visible.source_generation,game_generation=lifeGeneration,exact_source=exact,DMA_complete=visible.dma_finished_before_start,display_off_partial=visible.display_off_partial})
end,emu.eventType.startFrame)
PARODIUS_LIFECYCLE_OBSERVER_RESULT=function()
 local q={passed=true,ROM_sha256=C.ROM_sha256,game_generation=lifeGeneration,observed_init_publications=lifeInitPubs,init_DMAs=lifeInitDMAs,prior_generation_init_DMAs=lifeCarryDMAs,display_off_partial_starts=lifeOffPartial,visible_init_exact_checks=lifeVisibleChecks,no_emulated_writes=true,limits='Prior-generation sources retain exact original labels and256B identity; display-off partial starts are separate observations, not visible/new-life proof. Native lifecycle coverage requires a current-generation completed owner.'}
 local f=assert(io.open(C.output..'lifecycle-init-native-result.json','w'));f:write(json(q));f:close();return q
end
-- Appended after bridge_v3 in the original observer lexical scope. Read only.
-- This observer records the real HUD-start lease followed by the native
-- IRQ31 world-font takeover; endFrame is deliberately not a HUD-font phase.
local lifeHudPhase=nil
local function lifeHudRAM()
 local q={};for _,n in ipairs({'SelectedCharacter','VvVariant','CrossoverBehaviorVersion','OperMode','OperMode_Task','GameEngineSubroutine','InvHudActive','InvHudPhysical','X5HudChrUpper'})do q[n]=emu.read(assert(C.hud_ram[n],n),emu.memType.nesDebug)end;return q
end
-- PURE_PHASE_PREDICATE_BEGIN
PARODIUS_HUD_FINAL_PHASE_OK=function(q,expected)
 local function need(ok,why)if not ok then return false,why end;return true end
 local ok,why=need(q and q.start and q.endpoint,'Recorded HUD-start and terminal endpoint');if not ok then return ok,why end
 local s,e=q.start,q.endpoint;local a,w,t=q.IRQ_entry,q.IRQ_font_write,q.IRQ_return
 ok,why=need(s.ppu.frame==expected.frame and s.original_start.frame==expected.frame and e.ppu.frame==expected.frame and e.ppu.scanline==240,'Same actual visible/endFrame epoch');if not ok then return ok,why end
 ok,why=need(s.game_generation==expected.generation and s.source_generation==expected.generation and e.game_generation==expected.generation and e.visible_source_generation==expected.generation,'Current displayed source generation');if not ok then return ok,why end
 ok,why=need(s.publication==e.visible_publication and s.DMA==e.visible_DMA and s.publication~=nil and s.DMA~=nil,'Same displayed publication and DMA');if not ok then return ok,why end
 ok,why=need(s.exact256 and s.completed256 and s.dma_finished_before_start and (s.mask&24)==24,'Completed exact visible hardware owner');if not ok then return ok,why end
 ok,why=need(s.font==expected.HUD_font and s.visible_font==expected.HUD_font,'Actual HUD-start hardware lease');if not ok then return ok,why end
 for _,r in ipairs({s.ram,e.ram})do
  ok,why=need(r.SelectedCharacter==18 and r.VvVariant==expected.variant and r.CrossoverBehaviorVersion==expected.mode and r.OperMode==1 and r.OperMode_Task==3 and r.GameEngineSubroutine==8 and r.InvHudActive==2*expected.variant+1 and r.InvHudPhysical==expected.HUD_font%256 and (r.X5HudChrUpper&3)==expected.HUD_font//256,'Matching live mode/variant and supporting lease tag');if not ok then return ok,why end
 end
 ok,why=need(expected.fresh_updates>=45 and e.observed_updates>=s.observed_updates,'Meaningful current-generation update coverage');if not ok then return ok,why end
 ok,why=need(a and a.ppu.frame==expected.frame and a.ppu.scanline==31 and a.ppu.cpu>s.ppu.cpu and a.depth==1 and a.nmi_depth==0 and a.bank==expected.IRQ_bank and a.PC==expected.IRQ_entry_PC,'Recorded physical IRQ31 native owner');if not ok then return ok,why end
 ok,why=need(w and w.ppu.frame==expected.frame and w.ppu.scanline==31 and w.ppu.cpu>a.ppu.cpu and w.depth==1 and w.nmi_depth==0 and w.bank==expected.IRQ_bank and w.PC==expected.IRQ_font_write_PC and w.value==0 and w.upper==0 and w.physical==expected.world_font and w.instruction_exact,'Recorded intended IRQ world-font write');if not ok then return ok,why end
 ok,why=need(t and t.ppu.frame==expected.frame and t.ppu.cpu>w.ppu.cpu and t.ppu.cpu<e.ppu.cpu and t.depth==0 and t.nmi_depth==0 and t.bank==expected.IRQ_bank and t.PC==expected.IRQ_return_PC and t.font==expected.world_font,'Completed IRQ hardware world-font takeover');if not ok then return ok,why end
 ok,why=need(q.last_font_write==w and e.font==expected.world_font,'No later unexpected font ownership');if not ok then return ok,why end
 return true,'Actual HUD-start lease and completed native IRQ31 world-font phase'
end
-- PURE_PHASE_PREDICATE_END
emu.addEventCallback(function()
 lifeHudPhase=nil
 if not active()or not visible then return end
 local s=emu.getState();local p=visible.dma.publication
 lifeHudPhase={start={ppu=stamp(),original_start=visible.start,game_generation=lifeGeneration,source_generation=p.generation,publication=p.id,DMA=visible.dma.id,body_source=p.body and p.body.source.label,font=s['mapper.chrBanks8'],visible_font=visible.chr_banks[9],mask=ppuMask,exact256=visible.start_hardware_exact_source and equal(visible.start_hardware,p.oam),completed256=visible.dma.complete~=nil and visible.dma.data_writes==256,dma_finished_before_start=visible.dma_finished_before_start,observed_updates=updates,ram=lifeHudRAM()}}
 row(bus,{kind='lifecycle-HUD-start-phase',phase=lifeHudPhase.start})
end,emu.eventType.startFrame)
hook('IrqScrollSplit',function()
 if not lifeHudPhase then return end
 local s=emu.getState();lifeHudPhase.IRQ_entry={ppu=stamp(),PC=s['cpu.pc'],bank=bank(s['cpu.pc']),depth=irqDepth,nmi_depth=nmiDepth}
 row(bus,{kind='lifecycle-HUD-IRQ-entry',entry=lifeHudPhase.IRQ_entry,publication=lifeHudPhase.start.publication,DMA=lifeHudPhase.start.DMA,source_generation=lifeHudPhase.start.source_generation})
end)
emu.addMemoryCallback(function(_,v)
 if not lifeHudPhase then return end
 local s=emu.getState();local pc=s['cpu.pc'];local h=assert(C.terminal_phase)
 local instruction_exact=pc==h.IRQ_font_write_PC and bank(pc)==h.IRQ_bank
 for i,x in ipairs(h.IRQ_font_instruction)do if emu.read(h.IRQ_font_instruction_PC+i-1,emu.memType.nesDebug)~=x then instruction_exact=false end end
 local w={ppu=stamp(),PC=pc,bank=bank(pc),depth=irqDepth,nmi_depth=nmiDepth,value=v,upper=upper,physical=v+upper*256,instruction_exact=instruction_exact}
 lifeHudPhase.last_font_write=w
 if irqDepth>0 then lifeHudPhase.IRQ_font_write=w end
 row(bus,{kind='lifecycle-HUD-phase-font-write',write=w,publication=lifeHudPhase.start.publication,DMA=lifeHudPhase.start.DMA})
end,emu.callbackType.write,0x5128)
hook('IrqReturn',function()
 if not lifeHudPhase then return end
 local s=emu.getState();lifeHudPhase.IRQ_return={ppu=stamp(),PC=s['cpu.pc'],bank=bank(s['cpu.pc']),depth=irqDepth,nmi_depth=nmiDepth,font=s['mapper.chrBanks8']}
 row(bus,{kind='lifecycle-HUD-IRQ-return',returned=lifeHudPhase.IRQ_return,publication=lifeHudPhase.start.publication,DMA=lifeHudPhase.start.DMA})
end)
PARODIUS_HUD_FINAL_LEASE_EVIDENCE=function()
 if not lifeHudPhase then return nil end
 local s=emu.getState();local p=visible and visible.dma.publication
 lifeHudPhase.endpoint={ppu=stamp(),game_generation=lifeGeneration,visible_source_generation=p and p.generation,visible_publication=p and p.id,visible_DMA=visible and visible.dma.id,font=s['mapper.chrBanks8'],observed_updates=updates,ram=lifeHudRAM()}
 return lifeHudPhase
end
