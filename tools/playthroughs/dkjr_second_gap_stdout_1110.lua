-- Natural DK Jr. selection, four stock girder crossings and both early gaps.
local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''
local cookieBytes={}
for at=534485-16,534500-16 do
 cookieBytes[#cookieBytes+1]=string.format('%02x',emu.read(at,emu.memType.nesPrgRom))
end
local cookie=table.concat(cookieBytes)
local frame,updates,polls,bits,hold,rearm=0,0,0,0,0,0
local pipes={{448,176},{608,160},{736,144},{912,144}}
local lifts={416,480,560,624,688,752,880,944}
local centers={[416]=128,[480]=128,[560]=177,[624]=177,[688]=169,[752]=169,[880]=161,[944]=161}
local phase,index='approach',1
local done,playing=false,false
local births,carries,visible,events,crossings={},{},{},{},{}
local priorTop,lastUpdate={},-1
local fourthEntry=false
local injury
local descentSamples={}
local firstGap
local gap={planes=0,native_carries=0}
local gapLeft,gapTop,takeoffX,farBank=1408,208,1366,1424
local pendingPlane
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function ram(bank,at)return emu.read(bank*8192+at,emu.memType.nesWorkRam)end
local function pos(lo,hi,i)return read(lo+(i or 0))+256*read(hi+(i or 0))end
local function x()return pos(0x75,0x5c)end
local function camera()return pos(0x71f,0x71d)end
local function groundTile(worldX)
 return read(0x300+((worldX>>8)&1)*208+11*16+((worldX>>4)&15))
end
local function active()
 return read(0x6002)==40 and read(0x771)==1 and read(0x773)==3 and read(0x0f)==8 and ram(2,0x8fe)==2
end
local function mapped(at,kind,address)
 local m=emu.convertAddress(at)
 return m and m.memType==emu.memType[kind] and m.address==address
end
local function header(bank)
 local out={}
 for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',ram(bank,at))end
 return table.concat(out)
end
local function quote(s)
 return'"'..s:gsub('[%z\1-\31\\"]',function(c)
  if c=='"'then return'\\"'elseif c=='\\'then return'\\\\'end
  return string.format('\\u%04x',string.byte(c))
 end)..'"'
end
local function json(v)
 local t=type(v)
 if t=='string'then return quote(v)end
 if t=='nil'then return'null'end
 if t~='table'then return tostring(v)end
 local out={}
 if #v>0 then
  for _,value in ipairs(v)do out[#out+1]=json(value)end
  return'['..table.concat(out,',')..']'
 end
 for k,value in pairs(v)do out[#out+1]=quote(tostring(k))..':'..json(value)end
 table.sort(out)
 return'{'..table.concat(out,',')..'}'
end
local function snapshot()
 return {frame=frame,Main=updates,x=x(),y=read(0xbd),camera=camera(),
  lives=read(0x75f),source=ram(2,0x6b),state=read(0x1e),engine=read(0x0f),phase=phase,pipe=index}
end
local function finish(ok,why)
 if done then return end
 done=true;bits=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=rom,
  controller_only=true,script_RAM_writes=false,output_files=0,terminal=snapshot(),
  births=births,visible=visible,carries=carries,events=events,crossings=crossings,input_polls=polls,
  injury=injury,descent_samples=descentSamples,first_gap=firstGap,second_gap=gap}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name,fn)
 return function(...)
  if done then return end
  local ok,why=pcall(fn,...)
  if not ok then finish(false,name..': '..tostring(why))end
 end
end
local function currentTop(left)
 local b=births[tostring(left)]
 if b and read(0x10+b.slot)==1 and read(0x17+b.slot)==0x25 and pos(0x76,0x5d,b.slot)==left then
  return read(0xbe+b.slot)
 end
end
local function gapActor()
 local b=gap.birth
 if b and read(0x10+b.slot)==1 and read(0x17+b.slot)==0x28
   and read(0xbe+b.slot)==gapTop and read(0x646+b.slot)==6 then
  return pos(0x76,0x5d,b.slot),read(0x53f+b.slot)
 end
end
local function gapBox(slot)
 local at=0x658+4*(slot+1)
 return {read(at),read(at+1),read(at+2),read(at+3)}
end
local function remember(name,top)
 assert(#events<100,'Phase event bound')
 local s=snapshot();s.event=name;s.top=top;events[#events+1]=s
end
local function setPhase(name,top)
 phase=name;remember(name,top)
end
local function nearEnemy(player)
 for i=0,5 do
  local id=read(0x17+i);local dx=pos(0x76,0x5d,i)-player
  if read(0x10+i)==1 and (id==2 or id==6) and read(0x1f+i)&32==0
     and read(0xbe+i)>=172 and dx>=8 and dx<=30 then return true end
 end
 return false
end
local function drive()
 assert(read(0x75f)==2 and read(0x0f)~=11 and ram(2,0x6b)~=5,
  'Original fall or native injury '..json(snapshot()))
 if not active() or updates==lastUpdate then return end
 lastUpdate=updates
 local player,y=x(),read(0xbd)
 local pipe,cap=table.unpack(pipes[index])
 local u,d=lifts[2*index-1],lifts[2*index]
 local up,down=currentTop(u),currentTop(d)
 local function carried(left,top)
  local c=carries[tostring(left)]
  return top and c and c.last.Main<=updates and updates-c.last.Main<=1
    and y+32==top and ram(2,0x210)==y+15
 end
 local grounded=ram(2,0x6b)==1 and (read(0x1e)==0 or carried(u,up)or carried(d,down))
 local right=false
 for _,left in ipairs(lifts)do
  local key=tostring(left);local top=currentTop(left);local relative=left-camera()
  if top and relative>=0 and relative<256 and not visible[key]then
   visible[key]={frame=frame,Main=updates,top=top,relative=relative}
  end
 end
 local movingLeft,direction=gapActor()
 if movingLeft and not gap.on_screen and movingLeft>=camera() and movingLeft<camera()+256 then
  gap.on_screen={frame=frame,Main=updates,left=movingLeft,camera=camera(),direction=direction}
 end
 if phase=='approach'then
  right=true
  if index==4 and player>=u-30 and not fourthEntry then
   fourthEntry=up and priorTop[u] and up<=152 and up<=priorTop[u]
   right=not not fourthEntry
   if fourthEntry then remember('approach-window',up)end
  end
  if grounded and player<u-24 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('enemy-hop')
  end
  if player>=u+10 then right=false;setPhase('board')end
 end
 if phase=='board'and up then
  if grounded and up-32==y and y<176 then setPhase('rise',up)
  elseif grounded and updates>=rearm and up>=192 and up<=208 then
   hold=updates+8;rearm=updates+47;remember('board-hop',up)
  end
 end
 if phase=='rise'and up then
  local edge=u+(index==1 and 23 or 29)
  right=player<edge
  if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap then
   hold=updates+8
   setPhase('cross',up)
  end
 end
 if phase=='cross'then
  right=true
  if player>=pipe+4 and grounded and y==cap-32 then setPhase('roof')end
 end
 if phase=='roof'and index==4 then
  right=player<d-4
  if player>=d-4 and grounded and down and priorTop[d] and down>=101 and down<=114 and down>priorTop[d]then
   hold=updates+8;right=true;setPhase('jump-down',down)
  end
 elseif phase=='roof'and carried(d,down)then
  setPhase('lower',down)
 elseif phase=='roof'then
  right=player<d-2
  if player>=d-2 and grounded and down and priorTop[d]and down>=cap+8 and down<=cap+17 and down<=priorTop[d]then
   setPhase('step-down',down)
  end
 end
 if phase=='jump-down'then
  right=player<d+16
  if updates%5==0 and #descentSamples<25 then
   descentSamples[#descentSamples+1]={updates,player,y,down or -1,ram(2,0x6b),read(0x1e)}
  end
  if player>=d and carried(d,down)then setPhase('lower',down)end
 end
 if phase=='step-down'then
  right=player<d+8
  if carried(d,down)then setPhase('lower',down)end
 end
 if phase=='lower'and down then
  local leave=d+(index==4 and 16 or 31)
  right=player<leave
  if index==4 and player>=leave and down>=160 and down<=192 and priorTop[d]and down>priorTop[d]then
   setPhase('exit-edge',down)
  elseif index~=4 and player>=leave and grounded and down-32==y and down>=192 and down<=208 and priorTop[d]and down>=priorTop[d]then
   setPhase('depart',down)
  end
 end
 if phase=='exit-edge'and down then
  right=player<d+28
  if player>=d+28 and grounded and y>=160 and y<=176 and down>=192 and priorTop[d]and down>=priorTop[d]then
   setPhase('depart',down)
  end
 end
 if phase=='depart'then
  right=true
  if player>=d+36 and grounded and read(0x1e)==0 and y==176 then
   crossings[#crossings+1]=snapshot()
   if index==#pipes then setPhase('to-gap')
   else index=index+1;setPhase('approach')end
  end
 end
 if phase=='to-gap'then
  right=player<1094
  if player>=1094 and grounded and y==176 then hold=updates+8;setPhase('gap-jump')end
 end
 if phase=='gap-jump'then
  right=true
  if player>=1136 and grounded and read(0x1e)==0 and y==176 then
   for _,left in ipairs(lifts)do
    local key=tostring(left);assert(births[key]and visible[key]and carries[key]and carries[key].count>0,
      'Missing stock actor witness '..key)
   end
   assert(#crossings==#pipes,'All four pipe crossings')
   firstGap=snapshot()
   setPhase('to-second-gap')
  end
 end
 if phase=='to-second-gap'then
  assert(player<=takeoffX,'Missed supported second-gap takeoff X1366')
  right=player<takeoffX
  if right and grounded and y==176 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('second-gap-enemy-hop')
  end
  if player==takeoffX and grounded and read(0x1e)==0 and y==176 then
   assert(gap.birth and gap.initialized and gap.on_screen and movingLeft,'Live stock second-gap actor')
   gap.wait=snapshot()
   setPhase('second-gap-wait')
  end
 end
 if phase=='second-gap-wait'then
  right=false
  assert(player==takeoffX and y==176 and grounded and read(0x1e)==0 and groundTile(player)==0x54,
   'Supported second-gap bank while waiting')
  assert(movingLeft and updates-gap.wait.Main<600,'Second-gap actor lifetime or oscillator window')
  gap.wait_actor={left=movingLeft,direction=direction}
  if movingLeft==gapLeft and direction==2 then
   gap.takeoff=snapshot();gap.takeoff.actor=gap.wait_actor
   hold=updates+8;right=true;setPhase('second-gap-jump')
  end
 end
 if phase=='second-gap-jump'then
  right=true
  if player>=1412 and grounded and read(0x1e)==0 and y==176 and not gap.bank then
   assert(gap.land and gap.plane_at_landing,'Original landing on appended native top before the far bank')
   assert(groundTile(farBank)==0x54,'Authored solid far-bank tile')
   gap.bank=snapshot()
  end
  if player>=farBank and grounded and read(0x1e)==0 and y==176 then
   assert(firstGap and gap.birth and gap.initialized and gap.on_screen and gap.takeoff and gap.bank,
    'Complete menu-to-second-gap witnesses')
   setPhase('far-second-gap-bank')
   finish(true,'Four native DK Jr. pipe crossings, first gap and stock-assisted second gap')
   return
  end
 end
 bits=(right and 1 or 0)|(updates<hold and 128 or 0)
 priorTop[u],priorTop[d]=up,down
end
local function wait(pred)
 for _=1,1000 do if pred()then return end;coroutine.yield()end
 error('Native readiness timeout')
end
local function press(input)
 bits=input;for _=1,4 do coroutine.yield()end
 bits=0;for _=1,8 do coroutine.yield()end
end
local task=coroutine.create(function()
 assert(#rom==64 and os.getenv('SMB_TEST_VARIANT')=='0','ROM digest and replay mode')
 assert(cookie=='a72801b96058ad9af823ba7f575bf9d0','Second-gap DK Jr. owner cookie')
 wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
 press(16);wait(function()return read(0x7307)==2 and read(0x775)==0 end)
 assert(read(0x7309)==0,'Natural menu starts at Mario')
 for _,input in ipairs({4,4,1,1,1,4})do press(input)end
 assert(read(0x7309)==27 and read(0x6002)==28,'Donkey Kong slot')
 press(32);assert(read(0x6002)==40,'Donkey Kong Jr. alternate')
 press(16);wait(active)
 assert(read(0x764)==0 and read(0x761)==0 and read(0x754)==5 and read(0x7fe1)==0
  and read(0x7ffb)==0 and read(0x7ffc)==0,'Native Easy 1-1 with no cheats')
 assert(x()==40 and header(2)==cookie and header(3)==cookie,'Cold actor and both owner headers')
 playing=true
end)
emu.addMemoryCallback(guarded('main',function()
 if active()and mapped(0xd65e,'nesWorkRam',2*8192+0x165e)then updates=updates+1 end
end),emu.callbackType.exec,0xd65e)
emu.addMemoryCallback(guarded('birth',function()
 if not active()or not mapped(0xbd41,'nesWorkRam',3*8192+0x1d41)then return end
 local slot=emu.getState()['cpu.x'];local left=pos(0x76,0x5d,slot)
 local key=tostring(left);local cam=camera();local top=read(0xbe+slot)
 assert(centers[left]and not births[key]
  and left-cam>=256 and left-cam<=287,'Single native offscreen girder')
 assert(read(0x10+slot)==1 and read(0x17+slot)==0x25 and read(0x646+slot)==5 and top==192,
  'Original stock vertical constructor')
 local motionCenter=centers[left]
 assert(read(0x47+slot)==motionCenter,'Stock travel center')
 births[key]={slot=slot,frame=frame,Main=updates,left=left,center=left+16,top=top,camera=cam,motion_center=motionCenter}
end),emu.callbackType.exec,0xbd41)
emu.addMemoryCallback(guarded('gap constructor',function()
 if not active()or ram(2,0x8fd)~=8 or not mapped(0xa74f,'nesPrgRom',2*8192+0x74f)then return end
 local slot=emu.getState()['cpu.x']
 if slot>5 or read(0x17+slot)~=0x28 then return end
 local left,top,cam=pos(0x76,0x5d,slot),read(0xbe+slot),camera()
 assert(not gap.birth and read(0x10+slot)==1 and read(0xa5+slot)==1 and left==gapLeft and top==gapTop
  and cam>=1121 and cam<=1152 and left-cam>=256 and left-cam<=287,'Stock offscreen horizontal birth')
 gap.birth={slot=slot,frame=frame,Main=updates,left=left,center=left+24,top=top,camera=cam,relative=left-cam}
end),emu.callbackType.exec,0xa74f)
emu.addMemoryCallback(guarded('gap constructor return',function()
 if not active()or ram(2,0x8fd)~=8 or not mapped(0xd1ea,'nesWorkRam',2*8192+0x11ea)then return end
 local slot=emu.getState()['cpu.x'];local left=gapActor()
 assert(gap.birth and not gap.initialized and gap.birth.slot==slot and left==gapLeft
  and read(0x47+slot)==0 and read(0x8f+slot)==0,'Stock box 6 and cleared horizontal counters')
 gap.initialized={frame=frame,Main=updates,box=6,secondary=0,primary=0}
end),emu.callbackType.exec,0xd1ea)
emu.addMemoryCallback(guarded('gap top ingress',function()
 if not gap.takeoff or phase~='second-gap-jump' or not mapped(0xb5c8,'nesWorkRam',3*8192+0x15c8)then return end
 if ram(2,0x8f0)~=gap.birth.slot or not gapActor()then return end
 local left,direction=gapActor()
 pendingPlane={Main=updates,frame=frame,x=x(),left=left,direction=direction,
  bbox=gapBox(gap.birth.slot),count=ram(2,0x8dd),top=emu.getState()['cpu.a']}
end),emu.callbackType.exec,0xb5c8)
for _,at in ipairs({0xb5d9,0xb5fd,0xb60a})do
 emu.addMemoryCallback(guarded('gap top reject',function()
  if pendingPlane and mapped(at,'nesWorkRam',3*8192+at-0xa000)then pendingPlane=nil end
 end),emu.callbackType.exec,at)
end
emu.addMemoryCallback(guarded('gap top append',function()
 if not pendingPlane or not mapped(0xb61c,'nesWorkRam',3*8192+0x161c)then return end
 local p=pendingPlane;pendingPlane=nil
 assert(p.Main==updates and p.top==gapTop and p.bbox[2]==gapTop and ram(2,0x8dd)==p.count+4,
  'Native platform top append')
 local list=read(0xb611)+256*read(0xb612)
 assert(list==0xc800 or list==0xc840 or list==0xc880,'DK Jr. source world rectangle list')
 local at=list+p.count
 p.plane={read(at),read(at+1),read(at+2),read(at+3)}
 assert(p.plane[1]==p.bbox[1] and p.plane[2]==gapTop and p.plane[3]==p.bbox[3] and p.plane[4]==gapTop,
  'World plane derived from the published stock bounding box')
 gap.planes=gap.planes+1;gap.last_plane=p
end),emu.callbackType.exec,0xb61c)
emu.addMemoryCallback(guarded('original gap landing',function()
 if not gap.takeoff or phase~='second-gap-jump' or not mapped(0xa966,'nesWorkRam',3*8192+0x966)then return end
 local player=x()
 if player<1376 or player>=farBank or groundTile(player)~=0 or gap.land then return end
 local p=gap.last_plane
 assert(p and p.Main==updates and p.x==player and gapActor(),'Gap landing has a live native plane in this update')
 gap.land=snapshot();gap.land.source_y=ram(2,0x210);gap.land.ground_tile=0
 gap.plane_at_landing=p
end),emu.callbackType.exec,0xa966)
emu.addMemoryCallback(guarded('carry',function()
 if not active()or not mapped(0xac29,'nesPrgRom',71*8192+0xc29)then return end
 local slot=emu.getState()['cpu.x'];local left=pos(0x76,0x5d,slot)
 if gap.birth and slot==gap.birth.slot and gapActor()then gap.native_carries=gap.native_carries+1 end
 local key=tostring(left);local b=births[key];local top=currentTop(left);local y=read(0xbd)
 if not b or b.slot~=slot or not top or y+32~=top or ram(2,0x210)~=y+15 or ram(2,0x6b)~=1 then return end
 local c=carries[key]or {count=0,first=snapshot()};c.count=c.count+1;c.last=snapshot();carries[key]=c
end),emu.callbackType.exec,0xac29)
emu.addMemoryCallback(guarded('injury',function()
 if active()and mapped(0xbd93,'nesWorkRam',3*8192+0x1d93)then injury=snapshot()end
end),emu.callbackType.exec,0xbd93)
emu.addEventCallback(guarded('input',function()
 polls=polls+1
 emu.setInput({right=bits&1~=0,down=bits&4~=0,start=bits&16~=0,select=bits&32~=0,a=bits&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded('frame',function()
 frame=frame+1;assert(frame<18000,'Physical bound')
 if playing then drive() else local ok,why=coroutine.resume(task);assert(ok,why)end
end),emu.eventType.endFrame)
