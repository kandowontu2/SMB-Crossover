-- Passive phase/render diagnostic. Only emu.setInput supplies real controller input.
local sourceUpdates,sourceDraws,sourceTicks,contactCalls,defeatCalls,killCalls,initCalls=0,0,0,0,0,0,0
local admitted,phase0,advances,advanceReturns,controls,controlReturns=0,0,0,0,0,0
local backdropCalls,statusCalls,profileMinSP=0,0,255
local function ps(off,bank)return emu.read((bank or 2)*8192+off,emu.memType.nesWorkRam)end
local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function sourceActive()return r('SelectedCharacter')==38 and ps(0xab)==0xa7 end
local function headers()
 for i,v in ipairs(Q.cookie)do assert(ps(0x1fe0+i-1,2)==v and ps(0x1fe0+i-1,3)==v,'Both complete Prince auth headers')end
end
local function json(v)
 local t=type(v);if t=='nil'then return'null'elseif t=='boolean'or t=='number'then return tostring(v)elseif t=='string'then return string.format('%q',v)end
 local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function writejson(name,v)local f=assert(io.open(OUTPUT..name,'w'));f:write(json(v)..'\n');f:close()end
local function bytes(a,n,kind)local t={};for i=0,n-1 do t[#t+1]=emu.read(a+i,kind or emu.memType.nesDebug)end;return t end
local function stamp()
 local s=emu.getState();return{host_frame=frame,ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],CPU=s['cpu.cycleCount'],PC=s['cpu.pc'],SP=s['cpu.sp']}
end
local function state()
 return{world_x=wx(),native_y=r('Player_Y_Position'),native_y_high=ram(0xa4),source_action=ps(0x616),source_frame=ps(0x617),source_facing=ps(0x615),source_x=ps(0x60f)+256*ps(0x610),source_y=ps(0x611),physical_foot=ps(0x84)+256*ps(0x85),phase=ps(0xa6),epoch=ps(0xa9),epoch_valid=ps(0xaa),native_frame=r('FrameCounter'),pad=ram(0xdc),HP=ps(0x6cf),lives=r('NumberofLives'),engine=r('GameEngineSubroutine')}
end
local part='first-render'
local firstX,initialX,initialY,initialLives,partFrame,partAdvance,partCommit=nil,nil,nil,nil,0,0,0
local leftPeak,renderEvidence,renderFrame=nil,nil,nil
local rows={}
local csv=assert(io.open(OUTPUT..'source-phases.csv','w'))
csv:write('host_frame,event,part,wrappers,commits,phase0_calls,advance_entries,advance_returns,controls,draws,ticks,world_x,native_y,source_action,source_frame,source_facing,source_phase,source_epoch,native_frame,pad,physical_foot,HP,lives\n')
local function row(event)
 local s=state();csv:write(table.concat({frame,event,part,sourceUpdates,admitted,phase0,advances,advanceReturns,controls,sourceDraws,sourceTicks,s.world_x,s.native_y,s.source_action,s.source_frame,s.source_facing,s.phase,s.epoch,s.native_frame,s.pad,s.physical_foot,s.HP,s.lives},',')..'\n');csv:flush()
end
local function summary(passed,why)
 writejson('prince-diagnostic.json',{passed=passed,reason=why,ROM_sha256=Q.ROM_sha256,controller_only=true,emulated_writes=false,frame=frame,state=state(),wrappers=sourceUpdates,admitted_phase_commits=admitted,phase0_calls=phase0,original_advance_entries=advances,original_advance_returns=advanceReturns,original_controls=controls,original_control_returns=controlReturns,source_draws=sourceDraws,native_ticks=sourceTicks,contact_calls=contactCalls,native_kills=killCalls,native_defeats=defeatCalls,initial_lives=initialLives,final_lives=r('NumberofLives'),init_calls=initCalls,backdrop_calls=backdropCalls,status_calls=statusCalls,min_hook_SP=profileMinSP,left_peak=leftPeak,phases=rows,render_evidence=renderEvidence~=nil,full_stage=false,helpers_added=false})
end
local function require(v,why)if not v then summary(false,why);error(why)end end
local pendingDraw,lastDraw,pendingDMA,lastDMA=nil,nil,nil,nil
local dmaCount,drawReturns,metaCalls=0,0,0
local ctrl=0
emu.addMemoryCallback(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
-- Install a matched return observer for the real complete PpHostDraw call.
local returns,installed={},{}
local function onReturn(fn)
 local sp=emu.getState()['cpu.sp'];local pc=(ram(0x100+(sp+1)%256)+256*ram(0x100+(sp+2)%256)+1)%65536
 local at=emu.convertAddress(pc);assert(at,'Mapped HostDraw caller');local key=pc..':'..at.memType..':'..at.address
 returns[key]={SP=(sp+2)%256,fn=fn}
 if not installed[key]then
  installed[key]=true;emu.addMemoryCallback(function()
   local q=returns[key];if not q or emu.getState()['cpu.sp']~=q.SP then return end
   local p=emu.convertAddress(pc);if not p or p.memType~=at.memType or p.address~=at.address then return end
   returns[key]=nil;q.fn()
  end,emu.callbackType.exec,pc)
 end
end
for name,h in pairs(Q.hooks)do
 emu.addMemoryCallback(function()
  if r('SelectedCharacter')~=38 then return end
  local a=emu.convertAddress(h.pc);if not a or a.memType~=emu.memType[h.memory]or a.address~=h.physical then return end
  for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Exact source hook '..name)end
  profileMinSP=math.min(profileMinSP,emu.getState()['cpu.sp'])
  if name=='PpHostUpdate'then sourceUpdates=sourceUpdates+1
  elseif name=='PpPhaseCommit'then admitted=admitted+1
  elseif name=='PpPhase0Call'then phase0=phase0+1;row('phase0-call')
  elseif name=='PpAdvanceActor'then
   advances=advances+1
   local sp=emu.getState()['cpu.sp'];require(ram(0x100+(sp+1)%256)+256*ram(0x100+(sp+2)%256)==0xb398,'Original AdvanceActor actual phase0 caller')
  elseif name=='PpAdvanceReturn'then advanceReturns=advanceReturns+1;row('original-advance-return')
  elseif name=='PpControls'then controls=controls+1;row('original-controls-entry')
  elseif name=='PpControlsReturn'then controlReturns=controlReturns+1
  elseif name=='PpHostDraw'then
   sourceDraws=sourceDraws+1
   if sourceActive()and r('GameEngineSubroutine')==8 then
    require(not pendingDraw,'Nonrecursive real source body draw')
    pendingDraw={id=sourceDraws,entry=stamp(),indices={},metasprites={},state=state()}
    onReturn(function()
     local q=assert(pendingDraw);pendingDraw=nil;q.complete=stamp();q.body={};q.state_after=state()
     for index in pairs(q.indices)do q.body[#q.body+1]={index=index,bytes=bytes(0x200+index*4,4)}end
     table.sort(q.body,function(a,b)return a.index<b.index end);q.indices=nil;lastDraw=q;drawReturns=drawReturns+1
    end)
   end
  elseif name=='MetaspriteRenderLoop'and pendingDraw then
   metaCalls=metaCalls+1;local ptr=ram(3)+256*ram(4);local length=ram(ptr)
   pendingDraw.metasprites[#pendingDraw.metasprites+1]={stamp=stamp(),pointer=ptr,record=bytes(ptr,math.min(length+1,129)),length=length,x=ram(7)+256*ram(8),y=ram(9)+256*ram(10),cursor=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),rotation_active=r('GuestOamRotationActive')}
  elseif name=='DmaComplete'then
   if pendingDMA then
    local q=pendingDMA;pendingDMA=nil;q.complete=stamp();q.hardware=bytes(0,256,emu.memType.nesSpriteRam);q.exact=true
    for i,v in ipairs(q.source)do if q.hardware[i]~=v then q.exact=false end end
    q.hardware_body={};q.body_preserved=true
    for _,b in ipairs(q.draw.body)do
     local actual={};for j=1,4 do actual[j]=q.hardware[b.index*4+j];if actual[j]~=b.bytes[j]then q.body_preserved=false end end
     q.hardware_body[#q.hardware_body+1]={index=b.index,bytes=actual,draw_bytes=b.bytes}
    end
    lastDMA=q
   end
  elseif name=='PpNativeTick'then sourceTicks=sourceTicks+1
  elseif name=='PpNativeContact'then contactCalls=contactCalls+1
  elseif name=='NativeDefeat'then defeatCalls=defeatCalls+1
  elseif name=='KillPlayer'then killCalls=killCalls+1
  elseif name=='PpNativeInit'then initCalls=initCalls+1
  elseif name=='X5QueueAreaBackdrop'then backdropCalls=backdropCalls+1
  elseif name=='PpLiveName'then statusCalls=statusCalls+1 end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function(at)
 if pendingDraw then pendingDraw.indices[(at-0x200)//4]=true end
end,emu.callbackType.write,0x200,0x2ff)
emu.addMemoryCallback(function()
 if pendingDMA then pendingDMA.writes=pendingDMA.writes+1 end
end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(_,page)
 if not sourceActive()or r('GameEngineSubroutine')~=8 or not lastDraw or #lastDraw.body==0 then return end
 dmaCount=dmaCount+1;local s=emu.getState();local banks={};for i=0,11 do banks[i+1]=assert(s['mapper.chrBanks'..i])end
 pendingDMA={id=dmaCount,entry=stamp(),draw=lastDraw,page=page,source=bytes(page*256,256),palette=bytes(0,32,emu.memType.nesPaletteRam),banks=banks,control=ctrl,mask=mask,writes=0}
end,emu.callbackType.write,0x4014)
local function visibleEvidence(q)
 local parts={};local nonzero,first8pixels=0,0
 local function chr(at)return emu.read(q.banks[at//1024+1]*1024+at%1024,emu.memType.nesChrRom)end
 for _,part in ipairs(q.hardware_body)do
  local y,t,attr,x=table.unpack(part.bytes);local n=0;local eligible=0;local pattern={};local tall=q.control&32~=0;local height=tall and 16 or 8
  for yy=0,height-1 do
   local rr=attr&128~=0 and height-1-yy or yy
   local at=tall and((t&1)*4096+(t&254)*16+(rr>=8 and 16 or 0)+rr%8)or((q.control&8~=0 and 4096 or 0)+t*16+rr)
   local lo,hi=chr(at),chr(at+8);pattern[#pattern+1]=lo;pattern[#pattern+1]=hi
   local sy=y+1+yy;local priority=0
   for index=0,part.index do local oy=q.hardware[index*4+1];if sy>=oy+1 and sy<oy+1+height then priority=priority+1 end end
   for xx=0,7 do
    local bit=attr&64~=0 and xx or 7-xx;local px=((lo>>bit)&1)+2*((hi>>bit)&1)
    if px~=0 and y<240 and sy<240 and x+xx<256 then n=n+1;if priority<=8 then eligible=eligible+1 end end
   end
  end
  nonzero=nonzero+n;first8pixels=first8pixels+eligible
  parts[#parts+1]={index=part.index,bytes=part.bytes,pattern_rows=pattern,opaque_onscreen_pixels=n,within_first8_opaque_pixels=eligible,palette={q.palette[17+(attr&3)*4],q.palette[18+(attr&3)*4],q.palette[19+(attr&3)*4],q.palette[20+(attr&3)*4]}}
 end
 return{ROM_sha256=Q.ROM_sha256,captured_after_draw_and_DMA=true,DMA=q,parts=parts,opaque_onscreen_pixels=nonzero,within_first8_opaque_pixels=first8pixels,PPU_background_occlusion_not_inferred=true,screenshot_requires_visual_review=true,source_reads_only=true}
end
local function beginPart(name)
 part=name;firstX=wx();partFrame=frame;partAdvance=advances;partCommit=admitted;row('part-begin')
end
local function controls_begin()
 assert(sourceActive()and r('GameEngineSubroutine')==8,'Authenticated active Prince');headers()
 assert(ps(0x6cf)==5 and ps(0x6ee)==0,'Original5HP/unarmed constructor')
 phase='controls';age=0;initialLives=r('NumberofLives');initialX=wx();initialY=r('Player_Y_Position')
 assert(initialLives==2 and initialY==176 and ram(0xa4)==1,'Exact native entrance Y176/high1 lives2')
 beginPart('first-render');row('first-active')
end
local function control_keys()
 if part=='right-short'then return{'right'}elseif part=='left-turn'then return{'left'}end;return{}
end
local function completePart()
 rows[#rows+1]={name=part,frames=frame-partFrame,first_x=firstX,last_x=wx(),original_advances=advances-partAdvance,admitted_updates=admitted-partCommit,state=state()}
 row('part-end')
end
local function controls_tick(finish)
 require(sourceActive()and r('OperMode')==1 and r('GameEngineSubroutine')==8,'Authenticated native stage retained')
 headers();require(r('NumberofLives')==initialLives and ps(0x6cf)==5,'Diagnostic retains original HP and native lives')
 require(frame-partFrame<800 and advances-partAdvance<64,'Bounded actual source advance/physical turn window')
 if frame%12==0 then row('display-sample')end
 if part=='first-render'then
  require(wx()==firstX,'Original neutral stillness before first body image')
  if not renderEvidence and lastDMA and frame>lastDMA.complete.host_frame and advanceReturns>=4 then
   renderEvidence=visibleEvidence(lastDMA);renderFrame=frame;writejson('render-evidence.json',renderEvidence)
   shot('prince-after-draw-DMA')
   require(lastDMA.writes==256 and lastDMA.exact,'Actual complete256byte hardware DMA')
   require(lastDMA.body_preserved and #lastDMA.hardware_body>0,'Real body draw survives native publication/DMA')
   require(renderEvidence.opaque_onscreen_pixels>0 and renderEvidence.within_first8_opaque_pixels>0,'Actual mapped body CHR contains onscreen first8 sprite pixels')
   completePart();beginPart('right-short')
  end
 elseif part=='right-short'then
  if wx()>=firstX+16 then
   require(advances>partAdvance,'Right executes original actor advance');completePart();beginPart('left-turn');leftPeak=wx()
  end
 elseif part=='left-turn'then
  leftPeak=math.max(leftPeak,wx())
  if wx()<=firstX-2 then
   require(advances>partAdvance and controls>0,'Left reversal follows original controls and actor advance');completePart();beginPart('reversed-rest');shot('prince-actual-left-reversal')
  end
 elseif part=='reversed-rest'and advances-partAdvance>=2 then
  completePart();require(phase0==advances and advances==advanceReturns,'Every original advance has actual phase0 call and return')
  require(backdropCalls>0 and statusCalls>0 and renderEvidence~=nil,'Actual backdrop/status/body consumers')
  summary(true,'Real postdraw hardware body and original-source Left reversal');csv:close();finish()
 end
end
