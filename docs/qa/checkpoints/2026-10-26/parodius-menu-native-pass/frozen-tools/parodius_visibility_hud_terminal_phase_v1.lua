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
