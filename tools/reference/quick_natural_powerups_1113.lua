-- Read-only game observation plus native controller input. No state grants.
local frame,age,phase,game,done=0,0,'title',false,false
if CPU_CONTROLLER_OPENING then frame=541;phase='game';game=true end
local epoch,priorCounter=0,nil
local pickups,births,recent,heads={},{},{},{}
local pending,returns=nil,{}
local jumpLeft,cooldown=0,0
local wallRelease=nil
local lastX,stalled=nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function actor(i)return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function state()return {frame=frame,epoch=epoch,x=wx(),y=r('Player_Y_Position'),dy=r('Player_Y_Speed'),state=r('Player_State'),source_state=r('QmField_002C'),source_held=r('QmField_0023'),source_edges=r('QmField_0027'),engine=r('GameEngineSubroutine'),world=r('WorldNumber'),level=r('LevelNumber'),lives=r('NumberofLives'),HP=r('QmField_06C0'),maxHP=r('QmField_0099'),status=r('PlayerStatus'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')}end
local function encode(v)
 if type(v)=='table'then local a,n=true,0;for k in pairs(v)do if type(k)~='number'then a=false end;n=n+1 end;local out={}
  if a then for i=1,n do out[#out+1]=encode(v[i])end;return '['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return '{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='nil'then return 'null'else return tostring(v)end
end
local function finish(ok,why)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=why,ROM_SHA256=ROM_SHA,controller_only=true,terminal=state(),pickups=pickups,births=births,recent=recent,head_effects=heads}))
 emu.stop(ok and 0 or 1)
end
local function mapped(pc,offset)local m=emu.convertAddress(pc);return m and m.memType==emu.memType.nesPrgRom and m.address==offset end
local function jump()
 if #pickups>0 and r('QmField_002C')==12 then
  if wallRelease==nil then wallRelease=2;jumpLeft=0 end
  if wallRelease>0 then return 0 end
  jumpLeft=40;cooldown=48
 else
  wallRelease=nil
  if r('Player_State')==0 and jumpLeft==0 and cooldown==0 then jumpLeft=#pickups==0 and 12 or 40;cooldown=#pickups==0 and 42 or 48 end
 end
 return jumpLeft>0 and 128 or 0
end
local function control()
 local x=wx();local b=epoch%12<6 and 64 or 0
 local item=nil;for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 then item=a;break end end
 if item then
  local target=item.x-8
  if item.kind==1 then return (x<item.x-1 and 1 or x>item.x+2 and 2 or 0)+jump()+b end
  return (x<target-1 and 1 or x>target+1 and 2 or 0)+b
 end
 if #pickups==3 and x<1598 then
  -- Keep below the Star row: only jump for the first ground gap.
  if x<1350 then return 1+b end
  if x<1428 then return 1+jump()+b end
  return 1+b
 end
 local target=#pickups==0 and 328 or #pickups==1 and 1020 or #pickups==2 and 1240 or #pickups==3 and 1608 or nil
 if target and x>=target-8 then
  if x>target+2 then return 2+b elseif x<target-2 then return 1+b end
  return jump()+b
 end
 return 1+jump()+b
end
emu.addMemoryCallback(function()
 if not game or not mapped(L.HandlePowerUpCollision,PICKUP_OFFSET)then return end
 local c=emu.getState();local i=c['cpu.x'];if i>5 then return end
 local a=actor(i);if a.flag==0 or a.id~=46 then return end
 assert(a.state>=128,'Item collected before genuine maturity')
 assert(r('InvPickupOwner',i)==9 and r('InvPickup',i)==252,'Quick item owner/preparation mismatch')
 local sp=c['cpu.sp'];local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 pending={item=a,before=state(),sp=(sp+2)&255,ret=ret&65535}
 if not returns[ret&65535]then returns[ret&65535]=true;emu.addMemoryCallback(function()
  if not pending then return end;local c=emu.getState();if c['cpu.pc']~=pending.ret or c['cpu.sp']~=pending.sp then return end
  local q=pending;pending=nil;q.ret=nil;q.sp=nil;q.after=state();q.erased=r('Enemy_Flag',q.item.slot)==0
  assert(q.erased);if q.item.kind<2 then assert(q.after.HP==q.after.maxHP and q.after.status==q.before.status)end
  pickups[#pickups+1]=q;print('QUICK_NATURAL_PICKUP '..encode(q))
 end,emu.callbackType.exec,ret&65535)end
end,emu.callbackType.exec,L.HandlePowerUpCollision)
emu.addMemoryCallback(function()
 if not game or not mapped(L.NativeRarePlayerHeadCollisionCore,HEAD_OFFSET)then return end
 local c=emu.getState();heads[#heads+1]={frame=frame,epoch=epoch,tile=c['cpu.a'],x=wx(),y=r('Player_Y_Position'),dy=r('Player_Y_Speed'),fraction=r('R4')};if #heads>16 then table.remove(heads,1)end
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
emu.addEventCallback(function()
 local pad=0
 if not game and age<4 then
  if phase=='open'or phase=='start'then pad=16 elseif phase=='down'then pad=4 elseif phase=='right'then pad=1 elseif phase=='select1'or phase=='select2'then pad=32 end
 elseif game and r('GameEngineSubroutine')==8 then pad=control()end
 emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then phase='open';age=0
 elseif phase=='open'and age>=50 then assert(r('CrossoverMenuState')==2);phase='down';age=0
 elseif phase=='down'and age>=30 then assert(r('CrossoverMenuIndex')==8);phase='right';age=0
 elseif phase=='right'and age>=30 then assert(r('CrossoverMenuIndex')==9);phase='select1';age=0
 elseif phase=='select1'and age>=30 then phase='select2';age=0
 elseif phase=='select2'and age>=30 then assert(r('SelectedCharacter')==9 and r('FmAlts')&32~=0);phase='start';age=0
 elseif phase=='start'and age>=300 then assert(r('GameEngineSubroutine')==8);phase='game';game=true;age=0 end
 if not game then return end
 if r('GameEngineSubroutine')==11 or r('NumberofLives')<2 or r('QmField_06C0')==0 then finish(false,'life-lost');return end
 local counter=r('FrameCounter');if counter~=priorCounter then
  priorCounter=counter;epoch=epoch+1;jumpLeft=math.max(0,jumpLeft-1);cooldown=math.max(0,cooldown-1);if wallRelease then wallRelease=math.max(0,wallRelease-1)end
  if wx()==lastX then stalled=stalled+1 else stalled=0;lastX=wx()end
 end
 for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 then
  local last=births[#births];if not last or last.slot~=i or last.collection~=#pickups then a.collection=#pickups;a.frame=frame;births[#births+1]=a end
  if a.state>=128 then births[#births].mature=true end
 end end
 if MODE=='mushroom'and #pickups>=1 then finish(true,'natural-mushroom');return end
 if MODE=='items'and #pickups>=4 then finish(true,'four-authored-items');return end
 if MODE=='full'and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 then finish(true,'full-1-1');return end
 if frame%120==0 then recent[#recent+1]=state();if #recent>24 then table.remove(recent,1)end;print('QUICK_NATURAL_PROGRESS '..encode(state()))end
 if stalled>600 then finish(false,'route-stall');return end
 if epoch>12000 or frame>24000 then finish(false,'route-bound')end
end,emu.eventType.endFrame)
