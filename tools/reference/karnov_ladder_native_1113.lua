-- Readonly controller for the separately named five-question DATA-only ROM.
assert(os.getenv('SMB_STDOUT_ROM_SHA')==FIXTURE_SHA,'Exact launched private fixture identity')
local frame,completed,last,pad=0,0,-1,0
local phase,since,index='menu',0,1
local game=CPU_KARNOV_LADDER_OPENING or false
local requested,done,mainReturn,pickupReturn=nil,false,nil,nil
local heads,births,pickups,trace,images,imageTags={},{},{},{},{},{}
local grow,climb,retract,terminal=nil,nil,nil,nil
local selection,originalCells,originalAttrs={},{},{}
local returnHooks={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function kr(at)return emu.read(2*8192+(at&8191),emu.memType.nesWorkRam)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function state()return{frame=frame,update=completed,phase=phase,x=wx(),y=r('Player_Y_Position'),ground=r('Player_State')==0,scene=kr(0x5e),count=kr(0x624)&15,tip=kr(0x627),selected=kr(0x8e),owned=kr(0x8f),cycle=kr(0x860),shot=kr(0x65)&3,boots=kr(0xbd),bomb=kr(0xbb),health=kr(0x68),lives=r('NumberofLives'),camera=camera()}end
local function encode(v)
 if type(v)=='table'then local array,n=true,0;for k in pairs(v)do if type(k)~='number'then array=false end;n=n+1 end
  local out={};if array then for i=1,n do out[#out+1]=encode(v[i])end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function finish(ok,reason)if not requested then requested={ok=ok,reason=reason}end end
local function guard(fn)return function(...)if done or requested then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function mapped(pc,kind,address)local q=emu.convertAddress(pc);return q and q.memType==kind and q.address==address end
local function active()return r('SelectedCharacter')==34 and r('FmAlts')&1==1 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function header(bank)local out={};for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',emu.read(bank*8192+at,emu.memType.nesWorkRam))end;return table.concat(out)end
local function to(name,bits)phase=name;since=completed;pad=bits or 0 end
local function walk(target,nextPhase)
 local gap=target-wx();if math.abs(gap)<=1 then to(nextPhase,0)else pad=gap>0 and 1 or 2 end
end
local function item()
 for i=0,5 do local a=actor(i);if a.flag~=0 and a.id==46 and a.kind<2 then return a end end
end
local function rememberCells()
 local col=kr(0x625);local page=(kr(0x626)&0xf0)|((col>>4)&15)
 local bottom=(kr(0x626)&15)*16;local column=col&15;local ppu=emu.memType.nesPpuDebug
 for i=0,7 do local y=bottom-16*i;local at=0x2000+(page&1)*0x400+(y//8)*32+2*column
  for _,offset in ipairs({0,1,32,33})do originalCells[#originalCells+1]={at+offset,emu.read(at+offset,ppu)}end
  local attr=0x23c0+(page&1)*0x400+(y//32)*8+(column//2);originalAttrs[attr]=emu.read(attr,ppu)
 end
end
local function restoredPPU()
 local ppu=emu.memType.nesPpuDebug
 for _,cell in ipairs(originalCells)do if emu.read(cell[1],ppu)~=cell[2]then return false end end
 for at,value in pairs(originalAttrs)do if emu.read(at,ppu)~=value then return false end end
 return true
end
local function art()
 local col=kr(0x625);local page=(kr(0x626)&0xf0)|((col>>4)&15)
 local bottom=(kr(0x626)&15)*16;local column=col&15
 local ppu=emu.memType.nesPpuDebug
 for i=0,7 do local y=bottom-16*i;local at=0x2000+(page&1)*0x400+(y//8)*32+2*column
  assert(emu.read(at,ppu)==0x2c and emu.read(at+1,ppu)==0x2d and emu.read(at+32,ppu)==0x2c and emu.read(at+33,ppu)==0x2d,'Native Ladder quad reaches PPU')
  local attr=emu.read(0x23c0+(page&1)*0x400+(y//32)*8+(column//2),ppu)
  local shift=((y//16)&1)*4+(column&1)*2;assert((attr>>shift)&3==2,'Native Ladder owned palette quadrant')
 end
 assert(emu.read(0x3f0a,ppu)==0x21 and emu.read(0x3f0b,ppu)==0x0f,'Approved blue/black native palette2')
 assert(r('InvHudActive')==0xe9,'Karnov private font owner')
 return{page=page,column=column,bottom=bottom,count=8,glyphs={44,45},palette=2,colors={33,15}}
end
local function tick()
 if not game or completed==last then return end;last=completed
 assert(active() and r('NumberofLives')==2 and kr(0x68)==0,'Healthy native Karnov fixture')
 assert(header(2)==COOKIE and header(3)==COOKIE,'Both complete Karnov identities')
 local age=completed-since
 for i=0,5 do local a=actor(i);if a.flag~=0 and a.id==46 and a.kind<2 then
  local b=births[#births];if not b or b.collection~=#pickups then a.collection=#pickups;a.frame=frame;a.update=completed;births[#births+1]=a;b=a end
  if a.state>=128 then b.mature=true end
 end end
 if phase=='approach'then walk(POINTS[index]-7,'settle')
 elseif phase=='settle'and age>=6 and r('Player_State')==0 then to('bump',128)
 elseif phase=='bump'then
  local a=item();pad=age<9 and 128 or 0
  if a then if a.kind==0 then to('mushroom',1)elseif a.state>=128 then to('back',2)end end
  assert(age<140,'Question reveals a native prepared mature item')
 elseif phase=='mushroom'then
  local a=item();if a then pad=wx()<a.x+2 and 1 or 0 end
  assert(age<160,'First moving native mushroom collection')
 elseif phase=='back'then walk(POINTS[index]-34,'launch')
 elseif phase=='launch'and age>=6 and r('Player_State')==0 then to('collect',129)
 elseif phase=='collect'then
  pad=1|(age<36 and 128 or 0)
  if age>90 then to('back',2)end
  assert(age<150,'Native side-jump flower collection')
 elseif phase=='after-pickup'then
  if r('Player_State')==0 and age>=8 then
   if #pickups<5 then index=#pickups+1;to('approach',1)else to('clear-floor',1)end
  end
 elseif phase=='clear-floor'then walk(POINTS[5]+48,'ready-ladder')
 elseif phase=='ready-ladder'then
  if r('Player_State')==0 and age>=8 then
   assert(#pickups==5 and kr(0x65)&3==2 and kr(0xbd)==1 and kr(0xbb)==1 and kr(0x8f)&4~=0,'Five real pickups earned Ladder with Boots/Bomb retained')
   to('select-ladder',32)
  end
 elseif phase=='select-ladder'then
  pad=age<2 and 32 or 0
  if age>=5 then selection[#selection+1]={update=completed,selected=kr(0x8e)};if kr(0x8e)==2 then to('activate',68)else to('select-ladder',32)end end
 elseif phase=='activate'then
  pad=age<2 and 68 or 0
  if kr(0x5e)==1 then grow=state();rememberCells();to('grow',0)end
  assert(age<30,'Down and fresh B activate earned Ladder')
 elseif phase=='grow'then
  if kr(0x5e)==0 and kr(0x624)&15==8 then to('grown',0)end
  assert(age<80,'Original eight native Ladder growth updates')
 elseif phase=='grown'and age>=4 then
  grow.art=art();grow.complete=state();images[#images+1]='eight-grown';climb={start=state()};to('climb',8)
 elseif phase=='climb'then
  pad=8;if age>=24 then climb.finish=state();assert(climb.finish.y<=climb.start.y-18,'Original Up climbs native Ladder');images[#images+1]='climbed';to('descend',4)end
 elseif phase=='descend'then
  pad=4;if kr(0x5e)==2 then retract={start=state()};to('retract',0)end
  assert(age<90,'Held Down at bottom requests original state2')
 elseif phase=='retract'then
  if kr(0x5e)==0 and kr(0x624)&15==0 and kr(0x627)==0 then
   terminal=state();assert(kr(0x8f)&4~=0 and kr(0x8e)==2 and kr(0xbd)==1 and kr(0xbb)==1,'Reusable ownership and original stock retained')
   assert(#heads==5 and #births==5 and #pickups==5,'Five real heads, births and native collectors');retract.finish=terminal;to('restored-visible',0)
  end
  assert(age<80,'Original native Ladder restoration completes')
 elseif phase=='restored-visible'then
  if age>=4 and r('VRAM_Buffer1_Offset')==0 and restoredPPU()then
   retract.actual_PPU_cells_restored=#originalCells;local n=0;for _ in pairs(originalAttrs)do n=n+1 end;retract.actual_PPU_attributes_restored=n
   terminal=state();finish(true,'Private DATA-only five earned pickups, Select cycle and complete native Ladder PPU lifecycle')
  end
  assert(age<30,'Last native restoration reaches physical PPU')
 end
 if completed%60==0 then trace[#trace+1]=state();if #trace>10 then table.remove(trace,1)end end
 assert(completed<3000,'Logical controller bound3000')
end
emu.addMemoryCallback(guard(function()
 if not mapped(L.NativeRarePlayerHeadCollisionCore,emu.memType.nesPrgRom,NativeRarePlayerHeadCollisionCore_OFFSET)or not game then return end
 local cpu=emu.getState();if cpu['cpu.a']==0xc1 then
  assert(r('R2')+32==160,'Exact private question row');heads[#heads+1]={frame=frame,update=completed,x=wx(),y=r('Player_Y_Position'),tile=cpu['cpu.a'],row=r('R2')+32}
 end
end),emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
emu.addMemoryCallback(guard(function()
 if not game or not mapped(L.HandlePowerUpCollision,emu.memType.nesPrgRom,HandlePowerUpCollision_OFFSET)then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i>5 then return end;local a=actor(i)
 if a.flag==0 or a.id~=46 or a.kind>=2 then return end
 assert(a.state>=128 and r('InvPickupOwner',i)==34 and r('InvPickup',i)==252,'Actual mature native Karnov preparation')
 local sp=cpu['cpu.sp'];local ret=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 pickupReturn={ret=ret,sp=(sp+2)&255,item=a,before=state()}
 if not returnHooks[ret]then returnHooks[ret]=true;emu.addMemoryCallback(guard(function()
  local c=emu.getState();if not pickupReturn or c['cpu.pc']~=pickupReturn.ret or c['cpu.sp']~=pickupReturn.sp then return end
  local q=pickupReturn;pickupReturn=nil;local i=q.item.slot
  assert(r('Enemy_Flag',i)==0 and r('InvPickup',i)==0,'Actual item erased at collector return')
  assert(r('Square2SoundQueue')&32~=0 and r('FloateyNum_Control',i)==6,'Native pickup sound and popup')
  q.ret=nil;q.sp=nil;q.after=state();pickups[#pickups+1]=q
  local expectedCycle=math.max(0,#pickups-2);assert(kr(0x860)==expectedCycle and kr(0x65)&3==math.min(2,#pickups),'Exact original shot and option progression')
  if births[#births]then births[#births].mature=true end;to('after-pickup',0)
 end),emu.callbackType.exec,ret)end
end),emu.callbackType.exec,L.HandlePowerUpCollision)
emu.addMemoryCallback(guard(function()
 if not mapped(L.GameLoop,emu.memType.nesPrgRom,GameLoop_OFFSET)then return end
 local c=emu.getState();mainReturn={pc=(emu.read(0x100+((c['cpu.sp']+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((c['cpu.sp']+2)&255),emu.memType.nesDebug)+1)&65535,sp=(c['cpu.sp']+2)&255}
end),emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(guard(function()
 local c=emu.getState();if not mainReturn or c['cpu.pc']~=mainReturn.pc or c['cpu.sp']~=mainReturn.sp then return end
 mainReturn=nil;if game then completed=completed+1;tick()end
end),emu.callbackType.exec,L.IdleLoop+12)
local function wait(fn)for _=1,1800 do if fn()then return end;coroutine.yield()end;error('Native menu/ingress bound')end
local function press(bits)pad=bits;for _=1,4 do coroutine.yield()end;pad=0;for _=1,8 do coroutine.yield()end end
local menu=coroutine.create(function()
 if not game then
  wait(function()return frame>=100 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
  press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
  -- Native menu defaults to slot8; Left reaches slot7, Select chooses Karnov.
  press(2);assert(r('CrossoverMenuIndex')==7,'Native slot7');press(32)
  assert(r('SelectedCharacter')==34 and r('FmAlts')&1==1,'Real Select chooses Karnov');press(16);wait(active);game=true
 end
 to('approach',0);while not done do coroutine.yield()end
end)
emu.addEventCallback(guard(function()emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end),emu.eventType.inputPolled)
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function base64(bytes)local out={};for i=1,#bytes,3 do local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
 out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1);local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1);j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1)or'=';j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1)or'='end;return table.concat(out)end
emu.addEventCallback(function()
 if done then return end;frame=frame+1;if frame>10000 then finish(false,'Physical frame bound10000')end
 if not requested then local ok,why=coroutine.resume(menu);if not ok then finish(false,tostring(why))end end
 while #images>0 do local tag=table.remove(images,1);if WANT_IMAGES then
  assert(#imageTags<2,'At most two stdout PNGs');local png=emu.takeScreenshot();assert(type(png)=='string'and png:sub(1,8)=='\137PNG\r\n\26\n','Actual in-memory PNG');assert(#png<=4*1024*1024,'Bounded single PNG4MB')
  imageTags[#imageTags+1]={tag=tag,frame=frame,bytes=#png};print('SMB_NATIVE_IMAGE '..base64(png))
 end end
 if requested then done=true;print('SMB_NATIVE_RECEIPT '..encode({passed=requested.ok,reason=requested.reason,ROM_SHA256=FIXTURE_SHA,feature_SHA256=FEATURE_SHA,private_level_DATA_only=true,natural_stock_fifth_item_qualification=false,controller_only=true,runtime_state_writes=0,frames=frame,Main_updates=completed,heads=heads,births=births,pickups=pickups,Select_cycle=selection,grow=grow,climb=climb,retract=retract,terminal=terminal or state(),images=imageTags,recent=trace}));emu.stop(requested.ok and 0 or 1)end
end,emu.eventType.endFrame)
