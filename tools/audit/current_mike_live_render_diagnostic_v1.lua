-- Passive additive Mike draw->completed Main image->actual DMA->whole PPU log.
local D=assert(C.render_diagnostic)
local renderLog=assert(io.open(OUTPUT..'live-render.jsonl','w'))
local renderRows,renderBytes,renderDraws,renderDmas,renderFrames=0,0,0,0,0
local drawPending,drawsSinceFinish,lastDma=nil,{},nil
local recentImages={}
local captureStamp={}
local codec=dofile(D.codec)
local capture=codec.install(OUTPUT,{container_bytes=134217728,records=3000},function()return captureStamp end)
local full=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local function stamp()
 local s=emu.getState()
 return{ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']}
end
local function hexbytes(at,kind)
 local t={};for i=0,255 do t[#t+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)
end
local function emit(t)
 t.stamp=stamp();t.wall=wall;t.update=updates;t.case=index;t.phase=phase
 local line=json(t)..'\n';renderRows=renderRows+1;renderBytes=renderBytes+#line
 assert(renderRows<=12000 and renderBytes<=67108864 and #line<=16384,'Bounded passive render diagnostics')
 renderLog:write(line);renderLog:flush()
end
local function slots()
 local out={};for i=0,5 do out[#out+1]={slot=i,kind=r('JnShotKind',i),age=r('JnShotAge',i),hit=r('JnShotHit',i),x=r('JnShotX',i),page=r('JnShotPage',i),y=r('JnShotY',i),vx=r('JnShotVX',i)}end;return out
end
hook('RenderShotCall',function(s)
 if not entered then return end
 assert(not drawPending,'No recursive Mike shot renderer')
 local slot=s['cpu.x'];assert(slot>=0 and slot<6 and r('JnSavedY')==slot,'Actual native shot slot saved by JnDraw')
 local kind,age,vx=r('JnShotKind',slot),r('JnShotAge',slot),r('JnShotVX',slot)
 assert(kind>=1 and kind<=13,'Actual live source projectile kind')
 local pose=kind-1
 if vx>=128 or vx==0 and r('PlayerFacingDir')==2 then pose=pose+13 end
 if age&4~=0 then pose=pose+26 end
 local record=assert(D.records[pose+1]);local ptr=r('R0')+256*r('R1')
 assert(s['cpu.y']==pose and ptr==record.pointer and bank(0xc000)==record.bank,'Actual shot art table, pointer and physical C-bank owner')
 assert(emu.read(ptr,emu.memType.nesDebug)==record.header,'Actual compiled source shot record header')
 drawPending={event='actual-shot-draw',draw=renderDraws+1,case=index,name=C.plan[index].name,update=updates,slot=slot,kind=kind,age=age,pose=pose,record=ptr,record_bank=record.bank,header=record.header,
  x=r('R4'),page=r('R5'),y=r('R6'),cursor_before=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),rotation_active=r('GuestOamRotationActive'),before=hexbytes(0x200),writes={},entry=stamp()}
end)
emu.addMemoryCallback(function(at,value)
 if not drawPending then return end
 assert(#drawPending.writes<256,'At most complete source OAM page per shot draw')
 drawPending.writes[#drawPending.writes+1]={address=at,value=value,pc=emu.getState()['cpu.pc'],bank=bank(emu.getState()['cpu.pc'])}
end,emu.callbackType.write,0x200,0x2ff)
hook('RenderShotReturn',function()
 if not entered or not drawPending then return end -- Next is also the genuine empty-slot branch target.
 local p=drawPending
 assert(p.update==updates,'Same Main shot rendering continuation')
 p.cursor_after=r('CurrentOAMOffset');p.after=hexbytes(0x200);p.completed=stamp()
 renderDraws=renderDraws+1;drawsSinceFinish[#drawsSinceFinish+1]=p;emit(p);drawPending=nil
end)
hook('GameLoopFinish',function()
 if not entered then return end
 assert(not drawPending,'No unfinished shot call at completed Main')
 if #drawsSinceFinish>0 then
  local image={event='completed-Main-image-with-shot-draw',update=updates,source=hexbytes(0x200),draws=drawsSinceFinish,draw_ids={}}
  for _,d in ipairs(drawsSinceFinish)do image.draw_ids[#image.draw_ids+1]=d.draw end
  recentImages[#recentImages+1]=image;if #recentImages>8 then table.remove(recentImages,1)end
  emit({event=image.event,source=image.source,draw_ids=image.draw_ids});drawsSinceFinish={}
 end
end)
hook('DmaComplete',function()
 if not entered or not pending then return end
 assert(pending.writes==256,'Diagnostic records only actual complete256 DMA')
 local raw={};for _,v in ipairs(pending.source)do raw[#raw+1]=string.format('%02x',v)end;local source=table.concat(raw)
 local image
 for i=#recentImages,1,-1 do if recentImages[i].source==source then image=recentImages[i];break end end
 renderDmas=renderDmas+1
 local s=emu.getState();local chr={};for i=0,11 do chr[i+1]=s['mapper.chrBanks'..i]end
 local retained={}
 if image then
  for _,d in ipairs(image.draws)do
   local last={};for _,w in ipairs(d.writes)do last[w.address]=w.value end
   local bytes,match=0,true
   for at,v in pairs(last)do bytes=bytes+1;if pending.source[at-0x200+1]~=v then match=false end end
   retained[#retained+1]={draw=d.draw,case=d.case,kind=d.kind,slot=d.slot,source_written_bytes=bytes,all_written_bytes_retained=match}
  end
 end
 lastDma={event='actual-complete-DMA',epoch=renderDmas,source=source,physical=hexbytes(0,emu.memType.nesSpriteRam),
  completed_Main_update=image and image.update or nil,full_completed_Main_source_match=image~=nil,shots=retained,live_slots=slots(),chr=chr,stamp=stamp()}
 if phase=='weapon'or image then emit(lastDma)end
end)
emu.addEventCallback(function()
 if entered and(phase=='weapon'or lastDma and #lastDma.shots>0)then
  local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual full live-shot PPU image')
  local t={};for i,v in ipairs(screen)do t[i]=string.pack('<I4',v)end
  captureStamp={ppu=stamp(),case=index,phase=phase,last_actual_DMA=lastDma and lastDma.epoch or nil,Main_source_update=lastDma and lastDma.completed_Main_update or nil}
  full:write(table.concat(t));renderFrames=renderFrames+1
  emit({event='captured-whole-PPU',ordinal=renderFrames,last_actual_DMA=lastDma and lastDma.epoch or nil,Main_source_update=lastDma and lastDma.completed_Main_update or nil})
 end
 if done then
  full:close();capture.close()
  emit({event='passive-render-diagnostic-terminal',draws=renderDraws,actual_DMAs=renderDmas,whole_frames=renderFrames,
   limits='Draw emission and exact source-page DMA linkage are observed; opaque pixel/per-shot visibility requires offline whole-PPU analysis. Unmatched completed images are recorded without ownership invention.'})
  renderLog:close()
 end
end,emu.eventType.endFrame)
