-- Appended in the original observer's lexical scope. No original guard body
-- is replaced. All native callback registrations happen during startup.
local lifeGeneration,lifeInitPubs,lifeInitDMAs=0,0,0
local lifeCarryDMAs,lifeOffPartial,lifeVisibleChecks=0,0,0
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
emu.addMemoryCallback(function(_,v)
 if not lifeOwn()or active()then return end
 assert(lastPub,'Inactive DMA must have a real observed blank/portrait/draw owner')
 local image=bytes(v*256,emu.memType.nesDebug);assert(equal(image,lastPub.oam),'Init DMA exact last complete native source')
 local s=emu.getState();local pc=s['cpu.pc'];local physicalBank=bank(pc)
 dmaid=dmaid+1;lastDMA={id=dmaid,ppu=stamp(),publication=lastPub,mask=ppuMask,oam_address=oamAddress,writer_callback_pc=pc,writer_bank=physicalBank,writer_instruction={emu.read(pc-3,emu.memType.nesDebug),emu.read(pc-2,emu.memType.nesDebug),emu.read(pc-1,emu.memType.nesDebug)},state=detail(),nmi_depth=nmiDepth,phase='init',game_generation=lifeGeneration,source_generation=lastPub.generation}
 dmaPending=lastDMA;lifeInitDMAs=lifeInitDMAs+1
 if lastPub.generation~=lifeGeneration then lifeCarryDMAs=lifeCarryDMAs+1 end
 row(bus,{kind='lifecycle-init-4014-start',dma_id=dmaid,ppu=lastDMA.ppu,mask=ppuMask,oam_address=oamAddress,writer_pc=pc,bank=physicalBank,nmi_depth=nmiDepth,game_generation=lifeGeneration,source_generation=lastPub.generation,source_phase=lastPub.phase})
 assert(emu.read(pc,emu.memType.nesDebug)==0xa2 and emu.read(pc+1,emu.memType.nesDebug)==1,'Actual init DMA next instruction LDX#1')
 local finishpc=pc+2;local key=tostring(physicalBank)..':'..finishpc
 if not completionHooks[key]then completionHooks[key]=true;queueReturnSlot(finishpc,function()
  if not dmaPending or bank(finishpc)~=physicalBank then return end
  local q=dmaPending;dmaPending=nil;q.complete={ppu=stamp(),hardware=bytes(0,emu.memType.nesSpriteRam),mask=ppuMask,state=detail(),nmi_depth=nmiDepth,completed_2004_writes=q.data_writes};q.complete.exact_source=equal(q.complete.hardware,q.publication.oam);row(bus,{kind='4014-complete-after-next-LDX',dma_id=q.id,ppu=q.complete.ppu,exact_source=q.complete.exact_source,completed_2004_writes=q.data_writes,mask=ppuMask,nmi_depth=nmiDepth,hardware=q.complete.hardware,source=q.publication.oam});assert(q.data_writes==256,'Completed DMA256 writes');if not q.complete.exact_source then completeMismatches=completeMismatches+1;assert(C.diagnostic,'Completed DMA hardware exact source image')end
 end)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 if not lifeOwn()or active()or not lastDMA then return end
 assert(visible==nil,'Original nonlive startFrame clears only its new visible latch')
 local hardware=bytes(0,emu.memType.nesSpriteRam);local exact=equal(hardware,lastDMA.publication.oam);local rendering=(ppuMask&16)~=0
 if rendering then assert(lastDMA.complete and exact,'Visible init has complete exact hardware source');lifeVisibleChecks=lifeVisibleChecks+1
 elseif not lastDMA.complete or not exact then lifeOffPartial=lifeOffPartial+1 end
 local s=emu.getState();local banks={};for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual init MMC5 CHR writes');banks[#banks+1]=s['mapper.chrBanks'..i]end
 visible={start=stamp(),dma=lastDMA,chr_banks=banks,palette={},start_hardware=hardware,start_hardware_exact_source=exact,mask=ppuMask,nmi_depth=nmiDepth,start_state=detail(),dma_finished_before_start=lastDMA.complete~=nil,phase='init',game_generation=lifeGeneration,source_generation=lastDMA.publication.generation,display_off_partial=not rendering and(not lastDMA.complete or not exact)}
 for i=0,31 do visible.palette[#visible.palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
 row(bus,{kind='lifecycle-init-visible-start',ppu=visible.start,mask=ppuMask,source_generation=visible.source_generation,game_generation=lifeGeneration,exact_source=exact,DMA_complete=visible.dma_finished_before_start,display_off_partial=visible.display_off_partial})
end,emu.eventType.startFrame)
PARODIUS_LIFECYCLE_OBSERVER_RESULT=function()
 local q={passed=true,ROM_sha256=C.ROM_sha256,game_generation=lifeGeneration,observed_init_publications=lifeInitPubs,init_DMAs=lifeInitDMAs,prior_generation_init_DMAs=lifeCarryDMAs,display_off_partial_starts=lifeOffPartial,visible_init_exact_checks=lifeVisibleChecks,no_emulated_writes=true,limits='Prior-generation sources retain exact original labels and256B identity; display-off partial starts are separate observations, not visible/new-life proof. Native lifecycle coverage requires a current-generation completed owner.'}
 local f=assert(io.open(C.output..'lifecycle-init-native-result.json','w'));f:write(json(q));f:close();return q
end
