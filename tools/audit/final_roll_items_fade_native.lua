-- Appended to the frozen, previously qualified Roll helper prefix. No raw
-- resources/RNG/drop actors/projectiles are written. World/NPC setup is explicit.
local births,alive,coverage,artSeen={},{},{},{}
local rendered,emptyRenders,fourRenders,expiryCount,pickups,kills=0,0,0,0,0,0
local attempts,fireAt,targetActive,removeEnemy=0,0,false,false
local poolSeen,poolFinished,pickupSlot=false,false,nil
local globalCalls,drawCalls,writeCount=0,0,0
local firstWrong,firstWrongWrite=nil,nil
local violations,drawEpochs,cadence={},{},{}
local drawEpoch,admission,completedRender,publishedRender,dmaRender=nil,nil,nil,nil,nil
local lastDmaImage,lastDmaEpoch,startImage,startEpoch=nil,nil,nil,nil
local publicationSerial,dmaSerial,lastPublication,lastDmaStamp=0,0,nil,nil
local verifyArt=nil
local lastFinish,initialEmptyEnd=nil,nil
local cadenceFile=assert(io.open(OUTPUT..'cadence.csv','w'));cadenceFile:write('update,wall,phase,entry_cycle,finish_cycle,inclusive_cycles,draw_calls,drops\n')
local renderFile=assert(io.open(OUTPUT..'renders.jsonl','w'))
local function count(t)local n=0;for _ in pairs(t)do n=n+1 end;return n end
local function ppuStamp()
 local s=emu.getState();assert(type(s['ppu.frameCount'])=='number'and type(s['ppu.scanline'])=='number'and type(s['ppu.cycle'])=='number','Actual PPU counters available')
 return{frame_count=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle']}
end
local function ageOf(i)return r('InvDropAge',i)+256*r('InvDropAgeHi',i)end
local function snap()
 local t={};for i=0,3 do t[#t+1]={slot=i,kind=r('InvDropKind',i),meter=r('AvDropItem',i),age=ageOf(i),x=r('InvDropX',i),page=r('InvDropPage',i),y=r('InvDropY',i),birth=alive[i]and alive[i].serial}end;return t
end
local function tuple(a,b,c,d)return table.concat({a,b,c,d},',')end
local function coverKey(a,p)return tostring(a)..':'..tostring(p)end
local function nextTarget()
 local slot=3;while slot>=0 and r('InvDropKind',slot)~=0 do slot=slot-1 end
 assert(slot>=0,'A genuinely free drop slot before next defeat attempt')
 writeBoundary=true;target(144+slot*16);writeBoundary=false
 attempts=attempts+1;fireAt=updates;targetActive=true
 event('natural-pool-target',{attempt=attempts,target_x=144+slot*16,next_free_slot=slot})
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==9 and r('RlVariant')==1 and r('CrossoverBehaviorVersion')==C.mode_value,'Actual cold Roll and numeric mode')
  entered=true;phase='settle';age=0;event('actual-cold-selection',{mode=r('CrossoverBehaviorVersion'),character=9,variant=1})
 end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==9 and r('RlVariant')==1 and r('CrossoverBehaviorVersion')==C.mode_value,'Identity/mode readback persists')
 assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlFoodKind')==0 and r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Free buster, no unexpected injury/resource change')
 current={entry=emu.getState()['cpu.cycleCount'],draw_start=drawCalls}
 if removeEnemy then writeBoundary=true;w('Enemy_Flag',0,0);writeBoundary=false;removeEnemy=false end
 if (phase=='pool'and not poolSeen or phase=='supplement'and drops()==0 or phase=='pickup-birth'and drops()==0)and r('Enemy_Flag')==0 and shots()==0 and r('RlAttack')==0 then nextTarget()end
end)
hook('InventoryUpdateDrops',function()if entered and not done then globalCalls=globalCalls+1 end end)
hook('ShellOrBlockDefeat',function()
 if entered and emu.getState()['cpu.x']==0 then kills=kills+1;removeEnemy=true;targetActive=false;event('actual-native-defeat',{kills=kills})end
end)
hook('RlDropDispatch',function()
 if not entered then return end
 local before={};for i=0,3 do before[i]=r('InvDropKind',i)end
 local rng={r('PseudoRandomBitReg',1),r('PseudoRandomBitReg',2),r('PseudoRandomBitReg',3)}
 onReturn('fade-real-drop-birth',function()
  for i=0,3 do if before[i]==0 and r('InvDropKind',i)~=0 then
   local q={serial=#births+1,slot=i,born=updates,kind=r('InvDropKind',i),meter=r('AvDropItem',i),frame=r('FrameCounter'),x=r('InvDropX',i),y=r('InvDropY',i),rng=rng,phase=phase}
   assert(rng[1]&3==0 and q.kind==(rng[2]<192 and 1 or 2)and q.meter==(rng[3]&1==0 and 0 or 128),'Original unmodified native RNG policy')
   assert(ageOf(i)==0,'Actual source birth age0 after sole global owner')
   assert(not alive[i],'Native free-slot ownership')
   births[#births+1]=q;alive[i]=q;event('actual-native-drop-birth',q)
   if phase=='pickup-birth'then pickupSlot=i;phase='pickup';age=0 end
  end end
 end)
end)
hook('RlRefillDispatch',function()
 if not entered then return end
 local slot=r('InvDropSlot');local amount=emu.getState()['cpu.a']//4
 assert(phase=='pickup'and pickupSlot==slot,'Only controller-earned final pickup')
 onReturn('fade-real-pickup',function()
  assert(amount==2 or amount==10,'Actual native capsule amount')
  assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('Square2SoundQueue')==C.coin_sfx,'Full resource cap and genuine feedback')
  pickups=pickups+1;alive[slot].collected=updates;event('actual-native-pickup',{slot=slot,amount=amount,meter=r('AvDropItem',slot)})
 end)
end)
hook('RlDraw',function()
 if not entered or done then return end
 assert(not drawEpoch,'Non-reentrant Roll render')
 drawCalls=drawCalls+1
 drawEpoch={id=drawCalls,update=updates,wall=wall,frame=r('FrameCounter'),phase=phase,entry_ppu=ppuStamp(),entry_cycle=emu.getState()['cpu.cycleCount'],actors=snap(),admissions={}}
 onReturn('fade-complete-render',function()
  assert(admission==nil,'All four source drop admissions completed')
  drawEpoch.finish_cycle=emu.getState()['cpu.cycleCount'];drawEpoch.finish_ppu=ppuStamp();drawEpoch.inclusive_cycles=drawEpoch.finish_cycle-drawEpoch.entry_cycle
  completedRender=drawEpoch;drawEpochs[#drawEpochs+1]=drawEpoch;drawEpoch=nil
 end)
end)
hook('DropAdmission',function()
 if not entered or done then return end
 assert(drawEpoch and admission==nil,'Actual drop-loop owner')
 local s=emu.getState();local i=s['cpu.x'];local life=ageOf(i);local k=r('InvDropKind',i)
 local visible=k~=0 and(life<240 or r('FrameCounter')&1==0)
 admission={slot=i,kind=k,meter=r('AvDropItem',i),age=life,frame=r('FrameCounter'),expected_visible=visible,expected_a=visible and k or 0,cursor_before=r('CurrentOAMOffset'),birth=alive[i]and alive[i].serial,record_count=0,write_addresses={}}
end)
hook('DropAdmissionResult',function()
 if not entered or done then return end
 local a=emu.getState()['cpu.a'];admission.actual_a=a
 if a~=admission.expected_a then
  assert(C.role=='baseline','Candidate actual first fade admission state')
  violations[#violations+1]={update=updates,render=drawCalls,slot=admission.slot,age=admission.age,frame=admission.frame,expected=admission.expected_a,actual=a}
  if not firstWrong then firstWrong=violations[#violations];event('first-wrong-native-admission',firstWrong)end
 end
end)
hook('RlDrawRecord',function()
 if not admission then return end
 local a=admission;local art=a.meter>=128 and(a.kind==2 and 4 or 1)or(a.kind==2 and 6 or 5)
 local source=C.art_records[tostring(art)]
 assert(a.kind~=0 and r('RlSlot')==a.slot and r('R0')+256*r('R1')==source.pointer,'Exact supplied source drop art/pool owner')
 a.art=art;a.pointer=source.pointer;a.origin={x=r('R4'),page=r('R5'),y=r('R6')};a.record_count=a.record_count+1
 assert(a.origin.page==0 and a.origin.x>=32 and a.origin.x<208 and a.origin.y>=48 and a.origin.y<224 and a.cursor_before<160,'Documented interior, noncapacity source art fixture')
 verifyArt=function()
  local expected={}
  for _,p in ipairs(source.parts)do
   local y=(a.origin.y+p[3])&255
   if y>=32 and y<240 then local key=tuple(y,p[1],p[2]&0xf3,(a.origin.x+p[4])&255);expected[key]=(expected[key]or 0)+1 end
  end
  local actual={};local stores=0
  for at in pairs(a.write_addresses)do
   if at%4==0 then local key=tuple(emu.read(at,emu.memType.nesDebug),emu.read(at+1,emu.memType.nesDebug),emu.read(at+2,emu.memType.nesDebug),emu.read(at+3,emu.memType.nesDebug));actual[key]=(actual[key]or 0)+1;stores=stores+1 end
  end
  for key,n in pairs(expected)do assert(actual[key]==n,'Actual drop OAM matches supplied tile/attribute/coordinate records')end
  assert(stores==#source.parts,'No extra or lost source OAM parts')
  a.source_art_passed=true;artSeen[tostring(art)]=true
 end
end)
emu.addMemoryCallback(function(at,v)
 if not admission or bank(emu.getState()['cpu.pc'])~=119 then return end
 admission.write_addresses[at]=true;writeCount=writeCount+1
 if not admission.expected_visible and not firstWrongWrite then
  local s=emu.getState();local pc=s['cpu.pc'];firstWrongWrite={update=updates,render=drawCalls,slot=admission.slot,age=admission.age,frame=admission.frame,pc=pc,instruction_pc=pc-3,instruction_bytes={emu.read(pc-3,emu.memType.nesDebug),emu.read(pc-2,emu.memType.nesDebug),emu.read(pc-1,emu.memType.nesDebug)},bank=bank(pc),address=at,previous=emu.read(at,emu.memType.nesDebug),value=v};event('first-wrong-native-oam-write',firstWrongWrite)
 end
end,emu.callbackType.write,L.Sprite_Data,L.Sprite_Data+255)
hook('RlDraw::DropNext',function()
 if not entered or done then return end
 if verifyArt then local f=verifyArt;verifyArt=nil;f()end
 local a=assert(admission);a.cursor_after=r('CurrentOAMOffset');a.emitted=a.record_count>0
 local actualVisible=C.role=='baseline'and a.kind~=0 or a.expected_visible
 assert(a.emitted==actualVisible,'Actual drop art admission/skip without weakened visibility assertions')
 if not a.emitted then assert(a.cursor_after==a.cursor_before and count(a.write_addresses)==0,'Hidden/empty drop emits no OAM')else assert(a.source_art_passed,'Every emitted source record checked')end
 a.write_addresses=nil;drawEpoch.admissions[#drawEpoch.admissions+1]=a;admission=nil
end)
hook('finish',function()
 if not entered or done then return end
 assert(globalCalls==updates,'One sole shared drop-owner call per completed gameplay update')
 local s=emu.getState();local duration=s['cpu.cycleCount']-current.entry
 cadenceFile:write(table.concat({updates,wall,phase,current.entry,s['cpu.cycleCount'],duration,drawCalls-current.draw_start,drops()},',')..'\n')
 for i,q in pairs(alive)do
  if r('InvDropKind',i)==0 then
   if q.collected then assert(updates==q.collected,'Pickup source cleanup in same update')
   else assert(updates-q.born==420 and ageOf(i)==420,'Exact natural420 update expiry');q.expired=updates;expiryCount=expiryCount+1 end
   event('actual-native-drop-cleanup',q);alive[i]=nil
  else assert(ageOf(i)==updates-q.born,'Exact newborn0 and one source age increment per update')end
 end
 if phase=='settle'and age>=30 then
  writeBoundary=true;arena(false);writeBoundary=false;phase='empty-before';age=0
 elseif phase=='empty-before'and age>=120 then initialEmptyEnd=updates;phase='pool';age=0
 elseif phase=='pool'and drops()==4 then poolSeen=true;phase='pool-expiry';age=0;capture('four-natural-actors');event('natural-four-slot-pool',snap())
 elseif phase=='pool-expiry'and drops()==0 and shots()==0 and r('RlAttack')==0 then
  poolFinished=true
  if count(coverage)==24 then phase='pickup-birth'else phase='supplement'end;age=0
 elseif phase=='supplement'and drops()==0 and shots()==0 and r('RlAttack')==0 and count(coverage)==24 then phase='pickup-birth';age=0
 elseif phase=='pickup'and pickups==1 and drops()==0 and shots()==0 and r('RlAttack')==0 then phase='empty-after';age=0;capture('actual-pickup-cleanup')
 elseif phase=='empty-after'and age>=120 then done=true;phase='complete'end
 assert(updates<30000 and age<15000,'Finite natural pool/fade lifecycle; no RNG or actor injection')
end)
emu.addEventCallback(function()
 local b={}
 if not entered then b=menu()
 elseif targetActive then b.b=(updates-fireAt)%12<2
 elseif phase=='pickup'and pickupSlot and alive[pickupSlot]and updates-alive[pickupSlot].born>=30 then b.right=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)

-- Installed after the unchanged native NMI/CHR/publication guards, allowing
-- explicit closures over their committed DMA and write-time CHR epochs.
function FINAL_ROLL_FADE_INSTALL_END_FRAME(getDma,clearDma,getPhysical)
 emu.addEventCallback(function()
  startImage=nil;startEpoch=nil
  if not entered or done or not lastDmaImage or not lastDmaEpoch then return end
  local t={};for i=0,255 do t[#t+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
  assert(table.concat(t)==lastDmaImage,'Actual visible-start OAM exactly equals the committed native DMA publication')
  startImage=lastDmaImage;startEpoch=lastDmaEpoch
  if not startEpoch.committed then
   startEpoch.visible_start={wall=wall,ppu=ppuStamp(),dma=lastDmaStamp,oam={}}
   for i=0,255 do startEpoch.visible_start.oam[#startEpoch.visible_start.oam+1]=emu.read(i,emu.memType.nesSpriteRam)end
  end
 end,emu.eventType.startFrame)
 emu.addEventCallback(function()
  wall=wall+1
  if entered and not done then
   local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==getPhysical(i),'Actual write-time hardware CHR banks');chrChecks=chrChecks+1 end
   local image,epoch=getDma()
   if image then
    local t={};for i=0,255 do t[#t+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
    assert(table.concat(t)==image,'Exact completed publication reaches hardware OAM');dmaChecks=dmaChecks+1
    clearDma()
   end
   local epoch=startEpoch
   if epoch and startImage and not epoch.committed then
     epoch.committed=true;epoch.display_wall=wall;epoch.visible_end=ppuStamp();epoch.capture_binding='Actual OAM latched at startFrame with explicit PPU frame/scanline/cycle and actual DMA/publication IDs; completed image read at this endFrame. No assumed FrameCounter offset.';rendered=rendered+1
     local active=0;for _,a in ipairs(epoch.admissions)do if a.kind~=0 then active=active+1 end end
     if active==0 then emptyRenders=emptyRenders+1 elseif active==4 then fourRenders=fourRenders+1 end
     local sample=false
     for _,a in ipairs(epoch.admissions)do if a.kind~=0 and a.age>=236 and a.age<=247 then
      coverage[coverKey(a.age,a.frame&1)]=true;sample=true
     end end
     if sample then
      local label=string.format('fade-render-%05d-wall-%05d',epoch.id,wall)
      local f=assert(io.open(OUTPUT..label..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close();epoch.capture=label..'.argb'
     end
     renderFile:write(json(epoch)..'\n');renderFile:flush()
   end
  end
  for _,q in ipairs(captures)do local f=assert(io.open(OUTPUT..q.name..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end;captures={}
  if done then
   assert(poolSeen and poolFinished and fourRenders>0 and emptyRenders>=120 and expiryCount>=4 and pickups==1 and count(coverage)==24,'Natural four-slot/empty/fade parity/pickup/expiry completed')
   assert(r('RlHealth')==28 and r('RlEnergy')==28 and drops()==0 and shots()==0,'Final resource and native actor cleanup')
   if C.role=='candidate'then assert(firstWrong==nil and firstWrongWrite==nil,'No candidate fade state/OAM violation')else assert(firstWrong and firstWrongWrite,'Baseline actual missing-fade first state and OAM write reproduced')end
   local q={mechanics_passed=true,fade_policy_passed=firstWrong==nil,passed=firstWrong==nil,goal_complete=false,ROM_sha256=C.ROM_sha256,role=C.role,actual_mode_readback=r('CrossoverBehaviorVersion'),hard=C.hard,mode=C.mode_value,updates=updates,wall=wall,births=births,kills=kills,attempts=attempts,natural_expiries=expiryCount,real_pickups=pickups,committed_fade_coverage=coverage,empty_committed_renders=emptyRenders,four_actor_committed_renders=fourRenders,render_calls=drawCalls,committed_renders=rendered,global_owner_calls=globalCalls,nmis=nmis,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,minSP=minSP,drop_oam_writes=writeCount,source_art_seen=artSeen,first_wrong_native_admission=firstWrong,first_wrong_native_oam_write=firstWrongWrite,known_baseline_fade_violations=violations,initial_empty_control_finished=initialEmptyEnd,scope='Cold numeric mode; staged flat arena/player/default-health Goombas, actual native free buster defeats and RNG drops. Real four-slot births, one age/update, exact420 expiry, genuine controller pickup at full caps, source art/OAM and committed DMA epochs. No resource/RNG/counter/drop/projectile/outcome writes. Native timings are SMB adaptation, not executable mobile fidelity. Random full-pool contents are scenario matched; empty-before control is identical input/state.'}
   local f=assert(io.open(OUTPUT..'native-result.json','w'));f:write(json(q));f:close();log:close();trace:close();apu:close();cadenceFile:close();renderFile:close();emu.stop(0)
  end
  assert(wall<40000,'Finite native wall-frame bound')
 end,emu.eventType.endFrame)
end
local inheritedAssert=assert
function assert(ok,message,...)
 if not ok then
  local s=emu.getState();local q={message=tostring(message),wall=wall,updates=updates,phase=phase,age=age,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp'],actors=snap(),births=#births,pool_seen=poolSeen,coverage=count(coverage),admission=admission,resources=entered and state()or{}}
  local f=io.open(OUTPUT..'first-failure.json','w');if f then f:write(json(q));f:close()end
  local f=io.open(OUTPUT..'first-failure.argb','wb');if f then for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end
 end
 return inheritedAssert(ok,message,...)
end
