-- Input only. Aggregate frame evidence; never write game memory or save states.
local counts={7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2}
local frame,age,step,shots=0,0,1,0
local phase,done='title',false
local actions,rows,events={},{},{}
local bad,baseline={},nil
local mask,lastHash=0,nil
local oam,chr,maskEvents=0,0,{}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
 for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function shot(name)
 if shots>=4 then return end;shots=shots+1
 local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local csv=assert(io.open(OUTPUT..'frames.csv','w'))
csv:write('frame,action,age,slot,character,mask,screen_disabled,nmi_disabled,skipped,header_lit,portrait_hash,OAM_DMA,CHR_writes,visible_mask_off\n')
local function finish(ok,reason)
 if done then return end;done=true;shot('endpoint');csv:close()
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=ok,reason=reason,ROM_sha256=EXPECTED_SHA,frames=frame,transitions=rows,anomalies=bad,ppu_events=events,scope='Every32slot full Select wrap and D-pad snake, physical frame display fingerprints and PPU event observations. No RAM writes or gameplay claim.'})..'\n');f:close()
 print('ROSTER_FLICKER '..tostring(ok)..' '..reason);emu.stop(ok and 0 or 1)
end
local slots={}
for row=0,3 do
 for c=0,7 do slots[#slots+1]=row*8+(row%2==0 and c or 7-c)end
end
for i,slot in ipairs(slots)do
 for v=1,counts[slot+1]do actions[#actions+1]={button='select',slot=slot,variant=v%counts[slot+1],kind='Select'}end
 if i<#slots then
  local nextSlot=slots[i+1]
  actions[#actions+1]={button=nextSlot//8~=slot//8 and'down'or(nextSlot>slot and'right'or'left'),slot=nextSlot,variant=0,kind='Dpad'}
 end
end
for _,slot in ipairs({16,8,0})do actions[#actions+1]={button='up',slot=slot,variant=0,kind='Dpad'}end
local function registerEvent(reg,value)
 if phase~='audit'then return end
 local s=emu.getState();local scan=s['ppu.scanline']
 if reg==0x2001 then
  mask=value
  if scan>=0 and scan<240 and value&24~=24 then
   maskEvents[#maskEvents+1]={reg=reg,value=value,scanline=scan,cycle=s['ppu.cycle'],pc=s['cpu.pc']}
  end
 elseif reg>=0x5128 and reg<=0x512b then
  chr=chr+1
  if scan>=0 and scan<240 then events[#events+1]={frame=frame,action=step,reg=reg,value=value,scanline=scan,pc=s['cpu.pc']}end
 end
end
emu.addMemoryCallback(function(_,v)registerEvent(0x2001,v)end,emu.callbackType.write,0x2001)
for reg=0x5128,0x512b do emu.addMemoryCallback(function(_,v)registerEvent(reg,v)end,emu.callbackType.write,reg)end
emu.addMemoryCallback(function()oam=oam+1 end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local pad={}
 if phase=='open'and age<4 then pad.start=true
 elseif phase=='audit'and age<4 and actions[step]then pad[actions[step].button]=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
local function pixels()
 local screen=emu.getScreenBuffer();local black=screen[1]&0xffffff
 local lit,hash=0,0
 for y=8,14 do for x=64,190 do if screen[y*256+x+1]&0xffffff~=black then lit=lit+1 end end end
 -- Portrait interiors omit cursor cells and the colored OAM preview below.
 for row=0,3 do for col=0,7 do
  for y=36+row*32,54+row*32,2 do for x=36+col*24,46+col*24,2 do
   hash=((hash*33)~(screen[y*256+x+1]&0xffffff))&0x7fffffff
  end end
 end end
 return lit,hash
end
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then assert(r('OperMode')==0,'Cold title');phase='open';age=0
 elseif phase=='open'and age>=50 then
  assert(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Cold roster opens first slot')
  local lit,hash=pixels();assert(lit>100,'Visible roster heading');baseline=hash;shot('initial');phase='audit';age=0
 elseif phase=='audit'then
  local lit,hash=pixels()
  csv:write(table.concat({frame,step,age,r('CrossoverMenuIndex'),r('SelectedCharacter'),mask,r('DisableScreenFlag'),r('NmiDisable'),r('NmiSkipped'),lit,hash,oam,chr,#maskEvents},',')..'\n')
  if lit<100 or hash~=baseline or#maskEvents>0 then
   if#bad<128 then bad[#bad+1]={frame=frame,action=step,age=age,header_lit=lit,portrait_hash=hash,mask_off=maskEvents,slot=r('CrossoverMenuIndex')}end
   if shots<3 then shot('anomaly-'..tostring(shots))end
  end
  if age>=20 then
   local a=actions[step];a.frame=frame;a.observed_slot=r('CrossoverMenuIndex');a.character=r('SelectedCharacter');rows[#rows+1]=a
   if a.observed_slot~=a.slot then finish(false,'D-pad/Select route mismatch');return end
   step=step+1;age=0
   if step>#actions then finish(true,'All86 identity wraps and32-slot D-pad route observed; inspect anomaly trace');return end
  end
 end
 oam=0;chr=0;maskEvents={}
 if frame>=4000 then finish(false,'4000 physical frame bound')end
end,emu.eventType.endFrame)
