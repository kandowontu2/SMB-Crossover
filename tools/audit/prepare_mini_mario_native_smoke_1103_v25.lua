-- Controller inputs only. Every state/mapper/art observation is read-only.
local frame,age,phase,at,updates,mains,shots=0,0,'title',1,0,0,0
local done,lastEpoch,pending,last=nil,nil,nil,nil
local returns,drawReturns,boxReturns={},{},{}
local checks,dmas,boxes,draws,minSP=0,0,0,0,255
local startUpdates,startX,startY,startLives,minY,peakX=0,nil,nil,nil,nil,nil
local phases,events={},{}
local csv=assert(io.open(OUTPUT..'smoke.csv','w'))
csv:write('frame,Main,source,phase,x16,y16,xvel,yvel,current,queued,class,contacts,held,fresh,nativeX,nativeY,nativeState,pose\n')
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n)return read(assert(L[n],n))end
local function ram(a)return emu.read(2*8192+a-0xc000,emu.memType.nesWorkRam)end
local function word(a)return ram(a)+256*ram(a+1)end
local function signed(a)local v=word(a);return v>=32768 and v-65536 or v end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',k)..':'..json(x)end;table.sort(a);return '{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return 'null'else return tostring(v)end
end
local function result(ok,why)
 local q={passed=ok,error=why,ROM_sha256=C.ROM_sha256,physical_frames=frame,completed_Main=mains,
  source_updates=updates,checks=checks,normal_DMAs=dmas,box_returns=boxes,draw_returns=draws,
  minimum_observed_hook_SP=minSP,phase=phase,last=last,phases=phases,events=events,screenshots=shots,
  script_RAM_writes=false,controller_only=true,full_stage=false,helpers_added=false,
  source_rise=startY and minY and(startY-minY)/16 or nil}
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\n');f:close();csv:flush();return q
end
local function guard(fn)return function(...)
 if done then return end;local ok,e=pcall(fn,...);if not ok then result(false,tostring(e));csv:close();done=true;print(tostring(e));emu.stop(1)end
end end
local function check(ok,why)checks=checks+1;assert(ok,why)end
local function active()return r('SelectedCharacter')==41 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and ram(0xc300)==2 end
local function valid(h)
 local p=emu.convertAddress(h.pc);if not p or p.memType~=emu.memType[h.memory]or p.address~=h.physical then return false end
 for i,v in ipairs(h.bytes)do check(read(h.pc+i-1)==v,'Compiled Mini hook preimage '..h.name)end
 minSP=math.min(minSP,emu.getState()['cpu.sp']);return true
end
local function transition(p)
 events[#events+1]={phase=p,frame=frame,source=updates,x16=last and last.x,y16=last and last.y}
 phase=p;age=0;startUpdates=updates
end
local function shot(tag)
 shots=shots+1;check(shots<=2,'Two PNG limit');local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function snapshot()
 return{x=word(0xc250),y=word(0xc252),vx=signed(0xc200),vy=signed(0xc220),
  current=ram(0xc240),queued=ram(0xc228),class=ram(0xc246),contacts=ram(0xc24c),
  held=ram(0xc248),fresh=ram(0xc24a),pose=ram(0xc310),fault=ram(0xc247),
  nativeX=r('Player_X_Position')+256*r('Player_PageLoc'),nativeY=r('Player_Y_Position'),
  nativeState=r('Player_State'),lives=r('NumberofLives'),epoch=ram(0xc320)}
end
local function supported(s)return s.class==2 and s.contacts&1~=0 end
local function sample()
 mains=mains+1;local s=snapshot();if s.epoch==lastEpoch then return end
 if lastEpoch then check(((s.epoch-lastEpoch)&255)==1,'Exactly one source animation epoch per completed Main')end
 lastEpoch=s.epoch;updates=updates+1;last=s
 local q=phases[phase]or{updates=0,minY=s.y,maxX=s.x,minX=s.x};phases[phase]=q
 q.updates=q.updates+1;q.minY=math.min(q.minY,s.y);q.maxX=math.max(q.maxX,s.x);q.minX=math.min(q.minX,s.x)
 check(s.fault==0,'Original world fault remains clear');check(s.lives==startLives or not startLives,'Smoke retains lives')
 check(s.current<128 and s.nativeY<240,'Actual Mini remains alive')
 csv:write(table.concat({frame,mains,updates,phase,s.x,s.y,s.vx,s.vy,s.current,s.queued,s.class,s.contacts,s.held,s.fresh,s.nativeX,s.nativeY,s.nativeState,s.pose},',')..'\n')
 if startY then minY=math.min(minY,s.y)end
 local n=updates-startUpdates
 if phase=='game'then startLives=s.lives;transition('settle')
 elseif phase=='settle'then
  check(n<100,'Initial genuine floor settle bound');if supported(s)and s.vx==0 then startX=s.x;startY=s.y;minY=s.y;transition('idle')end
 elseif phase=='idle'then
  check(s.x==startX,'Idle twenty source updates without drift');if n>=20 then transition('right')end
 elseif phase=='right'then
  check(n<120,'Right motion bound');if s.x>=startX+16*16 then check(s.vx>0,'Original positive velocity');peakX=s.x;transition('left')end
 elseif phase=='left'then
  peakX=math.max(peakX,s.x);check(n<180,'Original reversal bound')
  if s.vx<0 and s.x<=peakX-8*16 then transition('brake')end
 elseif phase=='brake'then
  check(n<100,'Neutral original coast bound');if s.vx==0 and supported(s)then startY=s.y;minY=s.y;transition('jump')end
 elseif phase=='jump'then
  if n>=20 then check(minY<=startY-16*16,'Held A causes actual ascent');transition('landing')end
 elseif phase=='landing'then
  check(n<160,'Original jump landing bound')
  if supported(s)and n>=2 then
   check(minY<=startY-32*16 and minY>=startY-44*16,'Original standing jump envelope32..44px')
   check(math.abs(s.y-startY)<=16,'Real supported landing at original floor')
   check(dmas>10 and boxes>10 and draws>10,'Actual hardware/render/bbox observations')
   transition('finish')
  end
 end
end
local function return_context()
 local s=emu.getState();local sp=s['cpu.sp'];local ret=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local a=assert(emu.convertAddress(ret));return{ret=ret,sp=(sp+2)&255,memory=a.memType,physical=a.address}
end
local function matches(q)
 local s=emu.getState();local a=emu.convertAddress(s['cpu.pc'])
 return s['cpu.pc']==q.ret and s['cpu.sp']==q.sp and a and a.memType==q.memory and a.address==q.physical
end
local h=C.hooks.GameCoreRoutine
emu.addMemoryCallback(guard(function()
 if not active()or not valid(h)then return end
 check(not pending,'Synchronous Main return');pending=return_context();local ret=pending.ret
 if not returns[ret]then returns[ret]=true;emu.addMemoryCallback(guard(function()
  if pending and matches(pending)then pending=nil;if active()then sample()end end
 end),emu.callbackType.exec,ret)end
end),emu.callbackType.exec,h.pc)
for _,name in ipairs({'MiniHostMain','MiniStep','MiniAnimate'})do local p=C.hooks[name]
 emu.addMemoryCallback(guard(function()if active()then valid(p)end end),emu.callbackType.exec,p.pc)
end
local function observe_return(name,store,onreturn)
 local p=C.hooks[name];local waiting=nil
 emu.addMemoryCallback(guard(function()
  if not active()or not valid(p)then return end;check(not waiting,'Synchronous '..name);waiting=return_context();waiting.payload=store()
  local ret=waiting.ret;if not drawReturns[name..ret]then drawReturns[name..ret]=true;emu.addMemoryCallback(guard(function()
   if waiting and matches(waiting)then local q=waiting;waiting=nil;onreturn(q.payload)end
  end),emu.callbackType.exec,ret)end
 end),emu.callbackType.exec,p.pc)
end
observe_return('MiniHostBox',function()return{x=r('Player_Rel_XPos'),y=r('Player_Y_Position')}end,function(p)
 boxes=boxes+1;local b=L.BoundingBox_UL_Corner
 check(ram(0xc254)==1 and ram(0xc255)==6 and ram(0xc256)==1 and ram(0xc257)==7,'Original small6x7 integer bounds')
 check(read(b)==((p.x+1)&255)and read(b+2)==((p.x+6)&255)and read(b+1)==((p.y+9)&255)and read(b+3)==((p.y+15)&255),'Native GuestFullBox consumes original bounds')
end)
local latestDraw,checkedTiles=nil,{}
observe_return('MiniNativeDraw',function()return{slot=r('CurrentOAMOffset'),x=word(0xc311),y=word(0xc313),pose=ram(0xc310)}end,function(p)
 draws=draws+1
 check(read(L.ObjectMetasprite)==0 and read(L.SmPosePtr)+256*read(L.SmPosePtr+1)==L.ObjectMetasprite,'Stable zero SmPosePtr/header')
 if ram(0xc315)==1 then latestDraw=p end
end)
emu.addMemoryCallback(guard(function(_,page)
 if not active()then return end;dmas=dmas+1;if dmas<3 then return end
 check(emu.getState()['mapper.chrBanks4']==C.expected_chr4,'Published original Mini CHR4=968')
 if latestDraw then local p=latestDraw;local a=page*256+p.slot
  check(read(a)==((p.y-1)&255)and read(a+3)==p.x,'Actual one-part source canvas in normal DMA')
  local tile=assert(C.pose_tiles[p.pose+1]);local attr=assert(C.pose_attrs[p.pose+1])
  check(read(a+1)==tile and read(a+2)==attr,'Actual original Mini pose tile/facing/priority')
  check(tile%2==1 and tile<=63,'Original32-pair Mini atlas tile')
  if not checkedTiles[tile]then
   for i=0,31 do check(emu.read(0x1000+(tile&254)*16+i,emu.memType.nesPpuDebug)==C.art[(tile&254)*16+i+1],'Actual PPU source2bpp pixels')end
   checkedTiles[tile]=true
  end
  for i,v in ipairs({0x27,0x16,0x18})do check(emu.read(0x3f10+i,emu.memType.nesPpuDebug)==v,'Actual Mini original-derived opaque RGB')end
 end
end),emu.callbackType.write,0x4014)
emu.addEventCallback(guard(function()
 local keys={}
 if phase=='open'and age<6 then keys.start=true
 elseif phase=='select'and age<6 then keys.select=true
 elseif phase=='confirm'and age<6 then keys.start=true
 elseif phase=='right'then keys.right=true
 elseif phase=='left'then keys.left=true
 elseif phase=='jump'then keys.a=true end
 emu.setInput(keys,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;age=age+1;check(frame<C.max_frames,'Bounded native smoke')
 if phase=='title'and frame>=120 then check(r('OperMode')==0,'Cold title');transition('open')
 elseif phase=='open'and age>=70 then
  check(r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Actual initial Mario slot');transition('select')
 elseif phase=='select'and age>=35 then
  check(r('MarioVariant')==C.menu_variants[at],'Actual Km Select cycle')
  if at<8 then at=at+1;age=0 else
   check(r('SelectedCharacter')==41,'Mini raw41 selected')
   for i,v in ipairs(C.name)do check(emu.read(0x2327+i,emu.memType.nesPpuDebug)==v,'Actual MINI MARIO name')end
   shot('mini-menu');transition('confirm')
  end
 elseif phase=='confirm'and age>=8 then transition('game')
 elseif phase=='game'then check(age<650,'Actual ready2/engine8/source entry handoff bound')
 elseif phase=='finish'then
  shot('mini-native');result(true);csv:close();done=true;print('PASS Mini source-epoch smoke');emu.stop(0)
 end
end),emu.eventType.endFrame)
