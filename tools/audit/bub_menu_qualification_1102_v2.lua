-- Controller-only source; Q is supplied by the hash-bound plan preparer.
local frame,age,phase,at,done=0,0,'title',1,false
local shots,observations,seen=0,{},{}
local upper,chr,mask=0,{},0
local activeData,lateEnable,selectorCalls,freshIdentity,freshReady=0,0,0,nil,false
local bankC=0
local startGroups,restoreQueued=nil,false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function ram(a)return emu.read(a,emu.memType.nesDebug)end
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function shot(tag)
 if not tag then return end
 shots=shots+1;assert(shots<=4,'Four PNG capture limit')
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function equal(a,b,why)
 assert(#a==#b,why..' length')
 for i,v in ipairs(b)do assert(a[i]==v,why..' byte'..i..' actual'..tostring(a[i])..' expected'..v)end
end
local function nameRow()
 local v={};for i=0,15 do v[#v+1]=ppu(0x2328+i)end;return v
end
local function queueHasRestore()
 local i,last=0,r('VRAM_Buffer1_Offset')
 while i<last do
  local base=L.VRAM_Buffer1+i
  local addr=ram(base)*256+ram(base+1);local length=ram(base+2);local n=length&63
  if addr==0x3f15 and n==3 then
   local v={ram(base+3),ram(base+4),ram(base+5)}
   equal(v,Q.restore,'Actual shared P1 restore packet');return true
  end
  i=i+3+((length&64~=0)and 1 or n)
 end
 return false
end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)chr[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
emu.addMemoryCallback(function(_,v)bankC=v end,emu.callbackType.write,0x5116)
emu.addMemoryCallback(function(_,v)
 if phase=='route'and r('CrossoverMenuState')==2 and mask&24==0 and v&24~=0 then
  local line=emu.getState()['ppu.scanline'];if line>=0 and line<240 then lateEnable=lateEnable+1 end
 end
 mask=v
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()
 if phase=='route'and r('CrossoverMenuState')==2 and mask&24~=0 then
  local line=emu.getState()['ppu.scanline'];if line>=0 and line<240 then activeData=activeData+1 end
 end
end,emu.callbackType.write,0x2007)
-- A launch is tested separately from the all-position browse. These callbacks
-- observe the real menu boundary; no state, mapper, position or input RAM is set.
emu.addMemoryCallback(function(_,v)
 if Q.launch and phase=='route'and Q.steps[at].kind=='launch'and v==0 then
  startGroups=r('FmGroups');assert(startGroups==Q.launch.groups,'Start retained exact intended identity')
  if Q.launch.requiresRestore then restoreQueued=queueHasRestore();assert(restoreQueued,'Shared P1 restoration queued before menu exit')end
 end
end,emu.callbackType.write,L.CrossoverMenuState)
emu.addMemoryCallback(function(_,v)
 if Q.launch and Q.launch.raw==39 and bankC==2 then freshIdentity=v end
end,emu.callbackType.write,0xc300)
emu.addMemoryCallback(function(_,v)
 if Q.launch and Q.launch.raw==39 and bankC==2 and v==0xa7 then freshReady=true end
end,emu.callbackType.write,0xc304)
local log=assert(io.open(OUTPUT..'observations.csv','w'))
log:write('frame,tag,state,slot,raw,groups,name\n')
local function observe(s)
 assert(r('OperMode')==0,'Browse remains native title mode')
 assert(r('CrossoverMenuState')==s.state,'Real page state '..s.tag)
 assert(r('CrossoverMenuIndex')==s.slot,'Real controller slot '..s.tag)
 local name={}
 if s.state==2 then
  seen[s.slot]=true
  for _,cell in ipairs({{676,245},{677,246},{708,247},{709,248}})do assert(ppu(0x2000+cell[1])==cell[2],'Actual same-span NT copy/icon survives rebuild')end
  assert(r('SelectedCharacter')==s.raw,'Exact native raw owner '..s.tag)
  if s.name then name=nameRow();equal(name,s.name,'Actual name '..s.tag)end
  if s.slot==32 then
   assert((r('FmGroups')&128)==s.bob*128,'Bub/Bob selector bit retained')
   for _,v in ipairs(name)do assert(v~=63,'BUB/BOB must not show pending star')end
   assert(ppu(0x22a3)==0xfd,'Ordinary cursor on new slot, no invented lock diamond')
   for w=0,3 do assert(chr[w]==700+w,'Actual static portrait hardware CHR window'..w)end
   assert(chr[11]==7,'Actual new BG icon hardware page7')
   equal({ppu(0x3f11),ppu(0x3f12),ppu(0x3f13)},s.bob==1 and{44,35,48}or{42,38,48},'Actual source portrait RGB')
   local expected={159,0,0,120,159,0,0,128,175,2,0,120,175,4,0,128};local actual={}
   for i=0,15 do actual[#actual+1]=emu.read(i,emu.memType.nesSpriteRam)end
   equal(actual,expected,'Actual complete static portrait DMA')
  end
  if s.family=='BT'then assert((r('FmGroups')&32)==s.variant*32,'Existing BT retained alternate')end
  if s.family=='CF'then assert((r('FmGroups')&24)==s.variant*8,'Existing CF retained alternate')end
 end
 local encoded={};for _,v in ipairs(name)do encoded[#encoded+1]=string.format('%02X',v)end
 log:write(table.concat({frame,s.tag,r('CrossoverMenuState'),r('CrossoverMenuIndex'),r('SelectedCharacter'),r('FmGroups'),table.concat(encoded,'')},',')..'\n');log:flush()
 observations[#observations+1]=s.tag;shot(s.shot)
end
local function finish()
 local n=0;for _ in pairs(seen)do n=n+1 end
 if not Q.launch then assert(n==33,'All33 positions actually visited')end
 assert(activeData==0,'No active-display PPUDATA write')
 log:close();local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":true,"controller_only":true,"frames":%d,"mode":%q,"positions":%d,"observations":%d,"screenshots":%d,"active_data_writes":%d,"late_enables":%d,"gameplay_launch":%s,"full_stage":false,"helpers_added":false}\n',frame,Q.mode,n,#observations,shots,activeData,lateEnable,tostring(Q.launch~=nil)));f:close()
 done=true;print('PASS '..Q.mode..' controller-only native menu qualification');emu.stop(0)
end
emu.addEventCallback(function()
 local keys={}
 if phase=='open'and age<6 then keys.start=true
 elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end
 emu.setInput(keys,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 assert(frame<Q.maxFrames,'Global native menu controller frame bound')
 if phase=='title'and frame>=120 then
  assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'Actual cold title')
  phase='open';age=0
 elseif phase=='open'and age>=60 then
  assert(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Real Start opens initial selector')
  phase='route';age=0
 elseif phase=='route'and age>=Q.steps[at].wait then
  local s=Q.steps[at]
  if s.kind=='launch'then phase='game';age=0;return end
  observe(s);at=at+1;age=0;if at>#Q.steps then finish()end
 elseif phase=='game'and age>=360 then
  assert(r('OperMode')==1 and r('OperMode_Task')==3 and r('CrossoverMenuState')==0,'Actual gameplay menu handoff')
  assert(r('SelectedCharacter')==Q.launch.raw and r('GameEngineSubroutine')==8,'Exact active native owner')
  assert(startGroups==Q.launch.groups and r('FmGroups')==Q.launch.groups,'Simultaneous Select/confirm preserved identity')
  if Q.launch.raw==39 then assert(freshIdentity==Q.launch.bob and freshReady,'Actual authenticated Fresh consumed selected Bub/Bob identity')end
  shot('active-owner');finish()
 end
end,emu.eventType.endFrame)
