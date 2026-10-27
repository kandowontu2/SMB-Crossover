-- Additive passive live draw -> completed Main -> physical DMA -> whole PPU.
-- Inserted in the frozen fixture's existing lexical scope; no gameplay writes.
local KR=assert(C.render_diagnostic)
local krLog=assert(io.open(OUTPUT..'live-render.jsonl','w'))
local krRows,krBytes,krDrawCount,krMainCount,krDmaCount,krFrames=0,0,0,0,0,0
local krPending,krDma,krLastDma,krBuilt,krEnable=nil,nil,nil,nil,nil
local krDraws,krRecent={},{}
local krUnmatched,krDuplicate,krCarry,krCarryMax,krLastCaptured=0,0,0,0,nil
local krMask=0
local krStamp={}
local krCodec=dofile(KR.codec)
local krCapture=krCodec.install(OUTPUT,{container_bytes=134217728,records=3000},function()return krStamp end)
local krFull=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local function krNow()
 local s=emu.getState();return{ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']}
end
local function krHex(at,kind)
 local t={};for i=0,255 do t[i+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)
end
local function krState()
 local s={action=r('KbAction'),action_age=r('KbActionAge'),copy=r('KbCopy'),mouth=r('KbMouth'),mouth_copy=r('KbMouthCopy'),float=r('KbFloat'),float_age=r('KbFloatAge'),pose=r('KbPose'),pose_group=r('KbPoseGroup'),combo=r('MkCombo'),sword_tick=r('MkMoveTick'),sword_damage=r('MkDamage'),x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),slots={}}
 s.live=s.action~=0 or s.float~=0
 for i=0,2 do local q={slot=i,type=r('KbShotType',i),kind=r('KbShotKind',i),age=r('KbShotAge',i),x=r('KbShotX',i)+256*r('KbShotPage',i),y=r('KbShotY',i)};s.slots[#s.slots+1]=q;if q.type~=0 then s.live=true end end
 return s
end
local function krEmit(t)
 t.stamp=krNow();t.wall=wall;t.update=updates;t.case=rec and rec.case_index or 0;t.name=rec and rec.name or'';t.phase=phase
 local line=json(t)..'\n';krRows=krRows+1;krBytes=krBytes+#line
 assert(krRows<=20000 and krBytes<=67108864 and #line<=16384,'Bounded passive live render journal')
 krLog:write(line);krLog:flush()
end
local function krScope()return entered and r('SelectedCharacter')==13 and r('KbVariant')==C.variant and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local function krArm(kind,s)
 if not krScope()then return end
 assert(not krPending,'No nested tracked body/shot caller')
 krPending={kind=kind,entry=krNow(),entry_sp=s['cpu.sp'],state=krState(),source_before=krHex(0x200),writes={},render_entries=0}
 if kind=='shot'then
  local slot=r('KbSavedSlot');assert(slot<3 and r('KbShotType',slot)~=0,'Only genuine immediate live shot draw, not HUD/drop')
  krPending.slot=slot;krPending.shot_type=r('KbShotType',slot);krPending.shot_kind=r('KbShotKind',slot)
 end
end
hook('LiveBodyCall',function(s)krArm('body',s)end)
hook('LiveShotCall',function(s)krArm('shot',s)end)
hook('LiveRenderer',function(s)
 if not krPending then return end
 local p=krPending;assert(p.render_entries==0,'One real renderer per selected caller');p.render_entries=1
 local ptr=r('R0')+256*r('R1');local h=emu.read(ptr,emu.memType.nesDebug);local data={}
 for i=0,math.min(h,128)do data[#data+1]=emu.read(ptr+i,emu.memType.nesDebug)end
 p.renderer={stamp=krNow(),pointer=ptr,physical_C=bank(0xc000),shadow_C=r('CurrentBankC'),header=h,record=data,cursor=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),rotation_active=r('GuestOamRotationActive'),x=r('R4'),page=r('R5'),y=r('R6'),attr=r('R3')}
 if p.kind=='body'then
  assert(ptr==r('SmPosePtr')+256*r('SmPosePtr',1),'Actual dynamic body pointer consumed by the renderer')
  assert(ptr==KR.outline_buffer or ptr>=0xc000 and ptr<0xe000 and bank(0xc000)==KR.art_bank,'Only real filtered-body RAM buffer or actual Kirby art bank')
 else assert(ptr>=0xc000 and ptr<0xe000 and bank(0xc000)==KR.art_bank,'Actual Kirby live-shot art bank; no HUD/RAM alias')end
end)
emu.addMemoryCallback(function(at,v)
 if krPending then assert(#krPending.writes<256,'Bounded actual draw emission');krPending.writes[#krPending.writes+1]={address=at,value=v}end
end,emu.callbackType.write,0x200,0x2ff)
local function krReturn(kind,s)
 if not krPending then return end
 local p=krPending;assert(p.kind==kind and p.render_entries==1 and p.entry_sp==s['cpu.sp'],'Genuine same caller return/SP, not a stale hook')
 krDrawCount=krDrawCount+1;p.draw=krDrawCount;p.source_after=krHex(0x200);p.completed=krNow();p.cursor_after=r('CurrentOAMOffset');p.live=p.state.live
 krDraws[#krDraws+1]=p;if p.live then p.event='actual-live-draw';krEmit(p)end;krPending=nil
end
hook('LiveBodyReturn',function(s)krReturn('body',s)end)
hook('LiveShotReturn',function(s)krReturn('shot',s)end)
hook('GameLoopFinish',function()
 if not krScope()then return end
 assert(not krPending,'No unfinished caller at completed Main')
 krMainCount=krMainCount+1
 local image={event='completed-Main-image',Main=krMainCount,source=krHex(0x200),state=krState(),draw_ids={},live_draw_ids={},draws=krDraws,case=rec and rec.case_index or 0}
 for _,d in ipairs(krDraws)do image.draw_ids[#image.draw_ids+1]=d.draw;if d.live then image.live_draw_ids[#image.live_draw_ids+1]=d.draw end end
 if #krDraws>0 then krBuilt=image end
 krRecent[#krRecent+1]=image;if #krRecent>32 then table.remove(krRecent,1)end
 krEmit({event=image.event,Main=image.Main,source=image.source,state=image.state,draw_ids=image.draw_ids,live_draw_ids=image.live_draw_ids});krDraws={}
end)
emu.addMemoryCallback(function(_,v)krMask=v;if v&24~=0 and krLastDma then krEnable={epoch=krLastDma.epoch,stamp=krNow()}end end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 if not krScope()then return end
 assert(not krDma,'One actual DMA at a time');krDma={source=krHex(v*256),writes={},address_zero=emu.getState()['ppu.spriteRamAddr']==0,render_off=krMask&24==0}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 if not krDma then return end
 local i=#krDma.writes;assert(i<256 and emu.getState()['ppu.spriteRamAddr']==i and krMask&24==0,'Actual256 byte/destination/render DMA protocol')
 krDma.writes[i+1]=string.format('%02x',v)
end,emu.callbackType.write,0x2004)
hook('DmaComplete',function()
 if not krDma then return end
 local p=krDma;local written=table.concat(p.writes);local hw=krHex(0,emu.memType.nesSpriteRam);local normal={}
 for i=1,256 do local v=tonumber(p.source:sub(i*2-1,i*2),16);if(i-1)%4==2 then v=v&0xe3 end;normal[i]=string.format('%02x',v)end
 assert(p.address_zero and p.render_off and #p.writes==256 and written==p.source and table.concat(normal)==hw,'All raw source/write and physical E3 DMA bytes remain exact')
 local matched,candidates=nil,0
 for i=#krRecent,1,-1 do if krRecent[i].source==p.source then candidates=candidates+1;if not matched then matched=krRecent[i]end end end
 if candidates>1 then krDuplicate=krDuplicate+1 end
 if rec and not matched then krUnmatched=krUnmatched+1;assert(krUnmatched<=32,'At most32 explicitly unmatched scoped DMA epochs')end
 local built=krBuilt and krBuilt.source==p.source and krBuilt or nil
 local retained={};if built then for _,d in ipairs(built.draws)do
  if d.live then local last={};for _,w in ipairs(d.writes)do last[w.address]=w.value end
   local count,same=0,true;for at,v in pairs(last)do count=count+1;if tonumber(p.source:sub((at-0x200)*2+1,(at-0x200)*2+2),16)~=v then same=false end end
   retained[#retained+1]={draw=d.draw,kind=d.kind,source_written_bytes=count,all_written_bytes_retained=same}
  end
 end end
 krDmaCount=krDmaCount+1;local state=emu.getState();local chr={};for i=0,11 do chr[i+1]=state['mapper.chrBanks'..i]end
 krLastDma={event='actual-complete-DMA',epoch=krDmaCount,source=p.source,written=written,physical=hw,raw_write_count=256,destination_order_0_through255=true,completed_Main=matched and matched.Main or nil,source_match_candidates=candidates,built_Main=built and built.Main or nil,built_live=built and #built.live_draw_ids>0 or false,live_draws=retained,live_state=matched and matched.state or krState(),chr=chr}
 krEmit(krLastDma);krDma=nil
end)
emu.addEventCallback(function()
 if krScope()and rec and krLastDma and(krLastDma.built_live or krState().live)then
  if krLastCaptured==krLastDma.epoch then krCarry=krCarry+1 else krCarry=0;krLastCaptured=krLastDma.epoch end;krCarryMax=math.max(krCarryMax,krCarry)
  if krCarry<8 then
   local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual256x240 whole PPU pixels');local raw={};for i,v in ipairs(screen)do raw[i]=string.pack('<I4',v)end
   local actual=krHex(0,emu.memType.nesSpriteRam)
   krStamp={ppu=krNow(),case=rec.case_index,phase=phase,actual_DMA=krLastDma.epoch,Main=krLastDma.completed_Main,built_Main=krLastDma.built_Main}
   krFull:write(table.concat(raw));krFrames=krFrames+1
   krEmit({event='captured-whole-PPU',ordinal=krFrames,actual_DMA=krLastDma.epoch,completed_Main=krLastDma.completed_Main,built_Main=krLastDma.built_Main,physical_OAM_matches_DMA=actual==krLastDma.physical,render_enable=krEnable,live_state=krLastDma.live_state,carry_ordinal=krCarry,scope='Real pixels; page equality is content linkage, not a unique producer or opaque visibility proof.'})
  end
 end
 if done then
  assert(not krPending and not krDma,'No unfinished passive caller/DMA at terminal')
  krFull:close();krCapture.close();krEmit({event='passive-live-terminal',draws=krDrawCount,completed_Mains=krMainCount,actual_DMAs=krDmaCount,whole_frames=krFrames,unmatched_DMA=krUnmatched,duplicate_content_DMA=krDuplicate,max_carry=krCarryMax,capture=krCapture.stats(),limits='No extra PNGs, inputs, setup, mechanics or original guard changes. Duplicate source pages remain explicitly ambiguous; max8 captures per DMA and max32 unmatched scoped epochs. Physical E3 only; raw source/write bytes stay unmasked.'});krLog:close()
 end
end,emu.eventType.endFrame)
