-- Cold, controller-only traversal: every slot, every Select alternate, launch gates.
local frame,phase,age,at=0,'title',0,1
local raw={0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32}
local counts={5,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,2,4,4,2,2,4,1,1,4,1,2,1,6,2,4,1}
local steps,shots={},0
local seen,variants={},{}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function ram(a)return emu.read(a,emu.memType.nesDebug)end
local function pending(s,v)
 return s==0 and v==2 or (s==2 or s==7 or s==11)and v==1 or s==10 and v>0 or s==9 and v==2 or s==21 or s>=23
end
local visitorder={0,1,2,3,4,5,6,7,15,14,13,12,11,10,9,8,16,17,18,19,20,21,22,23,31,30,29,28,27,26,25,24}
local function add(button,s,v,tag)steps[#steps+1]={button=button,slot=s,variant=v,tag=tag}end
for i,s in ipairs(visitorder)do
 if i>1 then
  local old=visitorder[i-1]
  local b=s//8>old//8 and 'down' or s>old and 'right' or 'left'
  add(b,s,0,({[7]='row1-end',[15]='row2',[23]='row3',[31]='row4'})[s])
 else add('',s,0,'initial')end
 for v=1,counts[s+1]-1 do
  add('select',s,v,(s==28 and v==1 and 'wwf-alt')or(s==29 and v==1 and 'prince')or(s==30 and v==3 and 'contra-beans')or nil)
  if pending(s,v)then add('confirm',s,v)end
 end
 if counts[s+1]>1 then add('select',s,0)end
 if pending(s,0)then add('confirm',s,0)end
end
-- Back to row1 and launch a real playable owner through ordinary controls.
add('down',0,0);add('launch',0,0)
local log=assert(io.open(OUTPUT..'observations.csv','w'))
log:write('frame,action,slot,variant,pending,selected,name\n')
local late,visible,mask=0,0,0
emu.addMemoryCallback(function(_,v)
 local line=emu.getState()['ppu.scanline']
 if phase=='browse'and r('CrossoverMenuState')==2 and mask&24==0 and v&24~=0 and line>=0 and line<240 then late=late+1 end
 mask=v
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()
 local line=emu.getState()['ppu.scanline']
 if phase=='browse'and r('CrossoverMenuState')==2 and mask&24~=0 and line>=0 and line<240 then visible=visible+1 end
end,emu.callbackType.write,0x2007)
emu.addEventCallback(function()
 local b={}
 if phase=='open'and age<6 then b.start=true
 elseif phase=='browse'and age<4 then
  local k=steps[at].button
  if k=='confirm'then b.a=true;b.start=true
  elseif k=='launch'then b.start=true
  elseif k~=''then b[k]=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
local function shot(tag)
 if not tag then return end
 shots=shots+1;assert(shots<=8,'Capture bound')
 local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
 frame=frame+1;age=age+1
 assert(frame<5000,'Native controller bound')
 if phase=='title'and frame==100 then
  assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'Cold title')
  phase='open';age=0
 elseif phase=='open'and age>=36 then
  assert(r('CrossoverMenuState')==2,'Real Start opens selector')
  phase='browse';age=0
 elseif phase=='browse'and age>=20 then
  local s=steps[at]
  if s.button=='launch'then phase='game';age=0;return end
  assert(r('CrossoverMenuState')==2 and r('OperMode')==0,'Unsupported entry must stay in selector')
  assert(r('CrossoverMenuIndex')==s.slot,'Controller slot '..s.slot)
  local p=pending(s.slot,s.variant)
  local first=emu.read(0x2328,emu.memType.nesPpuDebug)
  -- Names are centered; locate explicit pending star within16 columns.
  local name={};local star=false
  for x=0,15 do local c=emu.read(0x2328+x,emu.memType.nesPpuDebug);name[#name+1]=string.format('%02X',c);star=star or c==63 end
  assert(star==p,'Pending marker follows alternate '..s.slot..'/'..s.variant)
  local expect=p and 0 or s.slot==0 and(s.variant==1 and 8 or 0)or raw[s.slot+1]
  assert(r('SelectedCharacter')==expect,'Safe raw owner '..s.slot..'/'..s.variant)
  if p then
   for w=0,3 do
    assert(ram(L.CurrentCHRBank+w)==188+w,'Pending preview physical page')
    assert(ram(L.X5ChrMode+w)==130,'Pending preview direct upper2')
   end
  end
  seen[s.slot]=true;variants[s.slot..'/'..s.variant]=true
  log:write(table.concat({frame,s.button,s.slot,s.variant,tostring(p),r('SelectedCharacter'),table.concat(name,'')},',')..'\n');log:flush()
  shot(s.tag);at=at+1;age=0
 elseif phase=='game'and age>=260 then
  assert(r('OperMode')==1 and r('CrossoverMenuState')==0,'Ready Mario launches')
  assert(r('SelectedCharacter')==0 and r('MarioVariant')==0,'Selected playable owner')
  assert(ram(0x5fe5)==0 and ram(0x5fe8)==0,'Pending-only state cleared before gameplay')
  local ns,nv=0,0;for _ in pairs(seen)do ns=ns+1 end;for _ in pairs(variants)do nv=nv+1 end
  assert(ns==32 and nv==80,'Every requested slot and alternate visited')
  log:close()
  assert(late==0 and visible==0,'No active-display upload or late rendering enable')
  local f=assert(io.open(OUTPUT..'result.json','w'))
  f:write(string.format('{"passed":true,"frames":%d,"slots":%d,"alternates":%d,"screenshots":%d,"late_enables":%d,"visible_ppu_writes":%d}\n',frame,ns,nv,shots,late,visible));f:close()
  print('PASS full32-slot cold controller traversal, all80 Select identities, pending gates, live launch and PPU deadlines')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
