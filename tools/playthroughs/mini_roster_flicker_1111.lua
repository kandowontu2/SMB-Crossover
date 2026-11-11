-- Observe visible output while cycling Mario alternates and moving the cursor.
local rom=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local frame,age,step=0,0,1
local phase,done='title',false
local actions,rows,expected={},{},{}
for _=1,10 do actions[#actions+1]='select' end
actions[#actions+1]='right'
actions[#actions+1]='left'
local menuRoute=os.getenv('SMB_MENU_ROUTE')
if menuRoute then
 actions={}
 for key,slot,raw in menuRoute:gmatch('(%a+):(%d+):(%d+)') do
  actions[#actions+1]=key
  expected[#expected+1]={slot=tonumber(slot),raw=tonumber(raw)}
 end
 assert(#actions>=100 and #actions<=180,'Bounded full roster route')
end
local history,events={},{}
local initial,old,miniSeen
local mask=0

local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function state()
 return {slot=read(0x7309),variant=read(0x730a),raw=read(0x6002),menu=read(0x7307),
   screen_disabled=read(0x775),nmi_disabled=read(0x7f)}
end
local function json(value)
 if type(value)=='string' then return string.format('%q',value) end
 if type(value)~='table' then return tostring(value) end
 local out={}
 if #value>0 then
  for _,v in ipairs(value) do out[#out+1]=json(v) end
  return '['..table.concat(out,',')..']'
 end
 for k,v in pairs(value) do out[#out+1]=json(k)..':'..json(v) end
 table.sort(out)
 return '{'..table.concat(out,',')..'}'
end
local function finish(ok,reason)
 if done then return end
 done=true
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=rom,
   physical_frames=frame,controller_only=true,output_files=0,initial=initial,
   terminal=state(),transitions=rows,mini=miniSeen,unsettled=history}))
 emu.stop(ok and 0 or 1)
end

local function visible(reg,value)
 if reg==0x2001 then mask=value end
 if phase~='roster' then return end
 local s=emu.getState()
 local scan=s['ppu.scanline']
 if scan<0 or scan>=240 or #events>=64 then return end
 if reg==0x2001 or reg>=0x5128 then
  events[#events+1]={frame=frame,age=age,reg=reg,value=value,scan=scan,
    dot=s['ppu.cycle'],pc=s['cpu.pc']}
 end
end
for _,reg in ipairs({0x2001,0x5128,0x5129,0x512a,0x512b}) do
 emu.addMemoryCallback(function(_,value)visible(reg,value) end,emu.callbackType.write,reg)
end

local function sample()
 local pixels=emu.getScreenBuffer()
 local bg=pixels[1]&0xffffff
 local function region(x0,y0,x1,y1,stride)
  local hash,ink=0,0
  for y=y0,y1,stride do
   for x=x0,x1,stride do
    local pixel=pixels[y*256+x+1]&0xffffff
    hash=((hash*33)~pixel)&0x7fffffff
    if pixel~=bg then ink=ink+1 end
   end
  end
  return hash,ink
 end
 local heading,headingInk=region(64,8,190,15,1)
 local grid=region(24,30,232,147,2)
 local preview,previewInk=region(72,148,184,194,1)
 local name,nameInk=region(64,198,192,208,1)
 return {frame=frame,age=age,mask=mask,state=state(),bg=bg,heading=heading,
   heading_ink=headingInk,grid=grid,preview=preview,preview_ink=previewInk,
   name=name,name_ink=nameInk}
end

emu.addEventCallback(function()
 local pad={}
 if phase=='open' and age<3 then pad.start=true
 elseif phase=='roster' and age<3 and actions[step] then pad[actions[step]]=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)

emu.addEventCallback(function()
 if done then return end
 frame=frame+1
 age=age+1
 if phase=='title' and frame>=100 and read(0x6004)==1 and read(0x775)==0 then
  phase='open';age=0
 elseif phase=='open' and age>=45 and read(0x7307)==2 and read(0x775)==0 then
  initial=sample()
  if initial.state.slot~=0 or initial.state.variant~=0 or initial.heading_ink<100 then
   finish(false,'Cold roster did not show Mario and its heading');return
  end
  old=initial;phase='roster';age=0
 elseif phase=='roster' then
  history[#history+1]=sample()
  if age>=22 then
   local new=history[#history]
   local abnormal={}
   for _,p in ipairs(history) do
    if p.bg~=initial.bg or p.heading~=initial.heading or
       (p.preview~=old.preview and p.preview~=new.preview) or
       (p.name~=old.name and p.name~=new.name) or
       (p.grid~=old.grid and p.grid~=new.grid) then
     abnormal[#abnormal+1]=p
    end
   end
   local row={key=actions[step],before=old,after=new,transient=abnormal,visible_writes=events}
   rows[#rows+1]=row
   local target=expected[step]
   if target and (target.slot~=new.state.slot or target.raw~=new.state.raw) then
    finish(false,'Unexpected roster slot or selected character at step '..step);return
   end
   if new.state.slot==0 and new.state.variant==8 and new.state.raw==41 then miniSeen=step end
   old=new
   history,events={},{}
   step=step+1;age=0
   if step>#actions then finish(miniSeen~=nil,'Observed Mario Select cycle and D-pad return');return end
  end
 end
 if frame>(menuRoute and 4300 or 720) then finish(false,'Bounded roster transition observer');return end
end,emu.eventType.endFrame)
