-- Read-only lifecycle/scene coverage plus ordinary controller decisions.
-- Installed before existing guard callbacks; all native callbacks register now.
local LC=assert(PARODIUS_VISIBILITY);local K=assert(LC.lifecycle)
local log=assert(io.open(LC.output..'lifecycle-events.jsonl','w'))
local ticks,gameUpdates,lifeStarts,deaths,resets,areaChanges=0,0,0,0,0,0
local initialLife,lastLife,lastArea,lastState=nil,nil,nil,nil
local newLifeUpdates,newAreaUpdates,queue2,holds,crowds,freshGameUpdates=0,0,0,0,0,0
local areaResets,areaHolds,catchupAfterAreaHold=0,0,false
local nmiPending=nil;local menuPhase='open';local variants={};local menuReturned,menuReentered=false,false
local function r(n)return emu.read(assert(LC.lifecycle_ram[n],n),emu.memType.nesDebug)end
local function stamp()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount']}end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function event(kind,extra)local q={kind=kind,ppu=stamp(),mode=r('CrossoverBehaviorVersion'),variant=r('VvVariant'),engine=r('GameEngineSubroutine'),oper=r('OperMode'),task=r('OperMode_Task'),life=r('NumberofLives'),area=r('AreaPointer'),active=r('InvHudActive'),upper=r('X5HudChrUpper'),dirty=r('VvHudDirty')};for k,v in pairs(extra or{})do q[k]=v end;log:write(json(q)..'\n');log:flush()end
local function live()return r('SelectedCharacter')==18 and r('VvVariant')==1 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function hook(n,fn)local h=assert(LC.lifecycle_hooks[n]);emu.addMemoryCallback(function()if emu.convertAddress(h.address).address//8192~=h.bank then return end;for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact lifecycle hook '..n)end;fn()end,emu.callbackType.exec,h.address)end
local function invalidate(reason)
 assert(PARODIUS_INVALIDATE_PUBLICATION,'Startup observer generation bridge')
 PARODIUS_INVALIDATE_PUBLICATION(reason);event('publication-generation-changed',{reason=reason})
end
hook('VvReset',function()if r('SelectedCharacter')==18 then resets=resets+1;if r('AreaPointer')~=37 then areaResets=areaResets+1 end;invalidate('VvReset-native-entry')end end)
hook('VvDeathStart',function()if r('SelectedCharacter')==18 then deaths=deaths+1;invalidate('VvDeathStart-native-entry');event('actual-death-owner')end end)
hook('PnHudNewLife',function()if r('SelectedCharacter')==18 then lifeStarts=lifeStarts+1;invalidate('PnHudNewLife-native-entry');event('native-new-life-owner')end end)
hook('KillPlayer',function()if r('SelectedCharacter')==18 then event('actual-KillPlayer',{buttons=r('SavedJoypadBits')})end end)
hook('GameLoop',function()
 if not live()then return end
 gameUpdates=gameUpdates+1;assert(r('CrossoverBehaviorVersion')==LC.mode,'Lifecycle numeric mode readback')
 local life,area=r('NumberofLives'),r('AreaPointer');initialLife=initialLife or life
 if lastLife and life~=lastLife then assert(((lastLife-life)&255)==1,'Actual single lost life, no fixture grant');event('actual-life-decrement',{before=lastLife,after=life})end
 if lastArea and area~=lastArea then areaChanges=areaChanges+1;event('actual-area-change',{before=lastArea,after=area})end
 lastLife,lastArea=life,area
 local _,pub=PARODIUS_PUBLICATION_SNAPSHOT();local fresh=pub and pub.generation==PARODIUS_LIFECYCLE_GENERATION()
 if fresh then freshGameUpdates=freshGameUpdates+1 end
 if life<initialLife and fresh then newLifeUpdates=newLifeUpdates+1 end
 if area~=37 and fresh then newAreaUpdates=newAreaUpdates+1 end
end)
hook('SamusFreezeUpdateScreen',function()
 nmiPending=nil
 if r('SelectedCharacter')~=18 or r('VvVariant')~=1 then return end
 if r('VRAM_Buffer_AddrCtrl')==6 and r('VRAM_Buffer2_Offset')>0 then
  queue2=queue2+1;event('genuine-Buffer2-flush',{offset=r('VRAM_Buffer2_Offset')})
  if(r('X5HudChrUpper')&128)~=0 and r('InvHudActive')==0 then
   nmiPending={area=r('AreaPointer'),upper=r('X5HudChrUpper'),active=r('InvHudActive'),physical=r('InvHudPhysical'),offset=r('VRAM_Buffer1_Offset'),bytes={}}
   for i=0,nmiPending.offset do nmiPending.bytes[#nmiPending.bytes+1]=emu.read(LC.hud_buffer1+i,emu.memType.nesDebug)end
   event('pending-full-labels-meet-Buffer2',{offset=nmiPending.offset})
  end
 end
end)
hook('NmiReturn',function()
 if not nmiPending then return end
 local q=nmiPending;nmiPending=nil
 assert(r('X5HudChrUpper')==q.upper and r('InvHudActive')==q.active and r('InvHudPhysical')==q.physical,'Buffer2 NMI retains exact pending full HUD owner')
 assert(r('VRAM_Buffer1_Offset')==q.offset and r('VRAM_Buffer2_Offset')==0,'Buffer2 clears its own queue and preserves Buffer1 extent')
 for i,v in ipairs(q.bytes)do assert(emu.read(LC.hud_buffer1+i-1,emu.memType.nesDebug)==v,'Buffer2 retains matching full-label payload')end
 holds=holds+1;if q.area~=37 then areaHolds=areaHolds+1 end;event('actual-Buffer2-pending-retained',{retained_area=q.area})
end)
-- Bind every active DMA to a known actual native owner. Prior-generation
-- carried images stay labeled prior; only current-generation owners count
-- toward meaningful new-life/new-area coverage.
emu.addMemoryCallback(function()
 if live()then
  local _,pub=PARODIUS_PUBLICATION_SNAPSHOT();assert(pub and pub.generation~=nil,'Active DMA has an observed native init/game publication owner')
  if pub.generation~=PARODIUS_LIFECYCLE_GENERATION()then event('prior-generation-image-carried',{publication=pub.id,source_generation=pub.generation,game_generation=PARODIUS_LIFECYCLE_GENERATION()})end
 end
end,emu.callbackType.write,0x4014)

-- The controller harness calls this only while its real selection is pending.
PARODIUS_LIFECYCLE_MENU=function(c)
 if K.kind~='menu' then return nil end
 if c.frame<180 or c.frame%12~=0 then return{}end
 local state=r('CrossoverMenuState')
 if menuPhase=='open'then if state==2 then menuPhase='select'else return{start=true}end end
 if menuPhase=='select'then
  if state~=2 then return{}end
  local index=r('CrossoverMenuIndex');if index<12 then return{down=true}end;if index~=17 then return{right=true}end
  local variant=r('VvVariant');variants[variant]=true
  if variants[0]and variants[1]and variants[2]and variants[3]and variant==1 then menuPhase='cancel';return{b=true}end
  return{select=true}
 end
 if menuPhase=='cancel'then if state~=0 then return{}end;menuReturned=true;menuPhase='reopen';event('menu-title-return');return{}end
 if menuPhase=='reopen'then if state==2 then menuReentered=true;menuPhase='delegate';event('menu-selection-reentry');return nil end;return{start=true}end
 return nil
end
local target=nil
PARODIUS_LIFECYCLE_POLICY=function(c)
 if K.kind=='death'then
  if deaths==0 and gameUpdates>=35 then return{down=true}end
  if deaths>0 and c.engine==8 then return nil end -- retained safe route after native respawn
  return{}
 elseif K.kind=='area'then
  if c.engine~=8 or c.area~=37 then return{}end
  if not target then
   for wx=(c.camera//16)*16,(c.camera//16)*16+224,16 do for yy=64,192,16 do
    if c.block(wx,yy)==0x10 and c.block(wx+16,yy)==0x11 then target={x=wx+8,y=yy-8};event('natural-enterable-pipe-found',{x=wx,top=yy});break end
   end;if target then break end end
  end
  local desiredY=target and target.y-6 or 104;local b={a=c.poll%8<2}
  if not target then b.right=true elseif c.x<target.x-1 then b.right=true elseif c.x>target.x+1 then b.left=true else desiredY=target.y;b.down=true end
  if c.y<desiredY-1 then b.down=true elseif c.y>desiredY+1 then b.up=true;b.down=false end
  return b
 end
 return nil
end
emu.addEventCallback(function()
 ticks=ticks+1
 if live()and r('AreaPointer')~=37 and areaHolds>0 and r('InvHudActive')==3 and emu.getState()['mapper.chrBanks8']==396 then catchupAfterAreaHold=true end
 local state=table.concat({r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('CrossoverMenuState'),r('NumberofLives'),r('AreaPointer'),r('InvHudActive'),r('X5HudChrUpper')},':')
 if state~=lastState then lastState=state;event('lifecycle-state')end
 if K.kind=='crowd'then
  local visible=PARODIUS_PUBLICATION_SNAPSHOT()
  if visible and visible.dma.publication.body and stamp().frame>=570 and stamp().frame<=620 then
   local b=visible.dma.publication.body;local peak=0;local peakY=0
   for _,p in ipairs(b.parts)do if p[1]<239 then for y=p[1]+1,math.min(p[1]+16,239)do local count=0;for i=0,63 do local sy=visible.start_hardware[i*4+1];if sy<239 and y>sy and y<=sy+16 then count=count+1 end end;if count>peak then peak=count;peakY=y end end end end
   if peak>8 then crowds=crowds+1;event('actual-body-row-overload',{peak=peak,y=peakY,DMA=visible.dma.id,publication=visible.dma.publication.id,body_source=b.source.label})end
  end
 end
 if stamp().frame~=LC.limit then return end
 if K.kind=='crowd'then assert(crowds>=1,'Actual crowded Octopus body rows must reproduce, no empty stress pass')
 elseif K.kind=='menu'then assert(menuReturned and menuReentered and variants[0]and variants[1]and variants[2]and variants[3]and freshGameUpdates>=45,'Real title/selection cancellation, all variant readbacks and active re-entry')
 elseif K.kind=='death'then assert(deaths==1 and lifeStarts>=2 and newLifeUpdates>=45 and r('NumberofLives')==initialLife-1,'Actual fatal terrain contact, native death, one life loss and meaningful new life')
 elseif K.kind=='area'then assert(areaChanges>=1 and areaResets>=1 and newAreaUpdates>=45 and queue2>=1 and areaHolds>=1 and catchupAfterAreaHold,'Actual pipe area transition and pending full HUD retained through real nonempty Buffer2 then catch-up')end
 assert(live()and r('InvHudActive')==3 and emu.getState()['mapper.chrBanks8']==396,'Final live Octopus actual HUD lease')
 local init=PARODIUS_LIFECYCLE_OBSERVER_RESULT();assert(init.observed_init_publications>=1,'Real init publication owner coverage')
 local _,finalPub=PARODIUS_PUBLICATION_SNAPSHOT();assert(finalPub and finalPub.generation==PARODIUS_LIFECYCLE_GENERATION(),'Final source owner belongs to current game generation')
 local q={fresh_current_generation_updates=freshGameUpdates,init_owner_result=init,passed=true,kind=K.kind,ROM_sha256=LC.ROM_sha256,game_updates=gameUpdates,deaths=deaths,native_life_starts=lifeStarts,resets=resets,new_life_updates=newLifeUpdates,area_changes=areaChanges,new_area_updates=newAreaUpdates,actual_Buffer2_flushes=queue2,pending_Buffer2_holds=holds,new_area_resets=areaResets,new_area_pending_holds=areaHolds,new_area_catchup=catchupAfterAreaHold,overloaded_body_frames=crowds,menu_return=menuReturned,menu_reentry=menuReentered,no_emulated_state_writes=true,limits='Prepared controller/coverage contract. Actual source/PPU proofs are separate; natural reachability and same-NMI pending/Buffer2 overlap require a real run. No invisible-actor, arbitrary queue or resource injection.'}
 local f=assert(io.open(LC.output..'lifecycle-native-result.json','w'));f:write(json(q));f:close();log:close()
end,emu.eventType.endFrame)
