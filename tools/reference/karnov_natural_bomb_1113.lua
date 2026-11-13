-- Controller-only: genuine native items, their maturity and collection.
-- L, ROM_SHA and STOP_AFTER are supplied by the small replay/CPU binder.
local frame,age,phase,done=0,0,'title',false
local game,epoch,routeAge,routePhase=CPU_CONTROLLER_OPENING or false,0,0,'first'
if game then frame=511;phase='game' end
local lives,previousCounter,lastPulse,jumpAge,release=2,nil,-100,0,0
local passedLift,retreatTarget=false,nil
local pickups,births,scenes,trace={},{},{},{}
local pending,blastCalls,armed,blastSeen=nil,0,false,false
local returnHooks={}
local hopPeak,hopStart=255,nil
local liftX,liftY,liftNext=nil,nil,nil
local helpers={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function kr(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function actor(i)return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function state()return {frame=frame,epoch=epoch,x=wx(),y=r('Player_Y_Position'),state=r('Player_State'),engine=r('GameEngineSubroutine'),level=r('LevelNumber'),world=r('WorldNumber'),area=r('AreaAddrsLOffset'),lives=r('NumberofLives'),shot=kr(0x65)&3,health=kr(0x68),cycle=kr(0x860),option=kr(0x8e),owned=kr(0x8f),stock=kr(0xbb),bomb=kr(0xc0),route=routePhase}end
local function encode(v)
 if type(v)=='table'then local a=true;local n=0;for k in pairs(v)do if type(k)~='number'then a=false end;n=n+1 end
  local out={};if a then for i=1,n do out[#out+1]=encode(v[i])end;return '['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return '{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='nil'then return 'null'else return tostring(v)end
end
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,ROM_SHA256=ROM_SHA,reason=reason,controller_only=true,frames=frame,updates=epoch,pickups=pickups,births=births,scenes=scenes,manual_helpers=helpers,recent=trace,terminal=state(),armed=armed,blast_seen=blastSeen,native_blast_contacts=blastCalls}))
 emu.stop(ok and 0 or 1)
end
local function to(p)
 if routePhase=='flower-hop'then print('KARNOV_FLOWER_HOP '..encode({start=hopStart,peak=hopPeak,finish=state()}))end
 routePhase=p;routeAge=0
 if p=='flower-hop'then hopPeak=r('Player_Y_Position');hopStart=state()end
end
local function tile(x,y)
 if y<32 or y>=240 then return 0 end
 return emu.read(L.Block_Buffer_1+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16,emu.memType.nesDebug)
end
local function solid(x,y)local v=tile(x,y);return v~=0 and v~=0x23 and v~=0x26 and v~=0xc2 end
local function enemyNear(x,d)
 for i=0,5 do local a=actor(i);if a.flag>0 and a.flag<128 and a.id<21 and a.state&32==0 and a.x>x and a.x-x<d and math.abs(a.y-r('Player_Y_Position'))<48 then return true end end
 return false
end
local function clearGroundEnemy(x,y)
 for i=0,5 do local a=actor(i)
  if a.flag>0 and a.flag<128 and a.id<21 and a.state&32==0 and math.abs(a.x-x)<100 and math.abs(a.y-y)<48 then
   return 4+(a.x<x and 2 or 1)+(epoch%12<6 and 64 or 0)
  end
 end
 return nil
end
local function beginLift(x,y,nextPhase)liftX=x;liftY=y;liftNext=nextPhase;to('lift-approach')end
local function ordinary(x,y,ground)
 local pad=1
 local wait=x>=600 and x<636 and y<=128 or x>=1000 and x<1090 or x>=1290 and x<1362 or x>=2350 and x<2434
 if x>=1140 then wait=solid(x+16,216)and not solid(x+20,y+16)end
 if x>=2420 and x<2434 and y<=112 then wait=true end
 if ground and jumpAge==0 and release==0 and not wait then jumpAge=36 end
 if jumpAge>0 then pad=pad|128;jumpAge=jumpAge-1;if jumpAge==0 then release=8 end elseif release>0 then release=release-1 end
 if x<530 and epoch%12<6 then pad=pad|64 end
 if x>750 then passedLift=true end
 if not passedLift and x>=688 and x<724 then
  if y>108 then pad=x<700 and 1 or 0;jumpAge=0;release=0 else pad=129 end
 end
 if ground and enemyNear(x,100)then pad=4+(epoch%12<6 and 64 or 0);jumpAge=0;release=8 end
 if x>=2422 and x<2440 and not ground and y<=112 then pad=pad&~1 end
 return pad
end
local function control()
 local x,y,ground=wx(),r('Player_Y_Position'),r('Player_State')==0
 local item=nil;for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 and a.kind<2 then item=a;break end end
 if routePhase:sub(1,5)=='lift-'then
  if ground then local clear=clearGroundEnemy(x,y);if clear then return clear end end
  if routePhase=='lift-approach'then
   if x>liftX+1 then return 2 elseif x<liftX-1 then return 1 end
   to('lift-request');return 40 -- Existing user-authored Up+Select helper.
  end
  if routePhase=='lift-request'then
   for i=0,5 do local a=actor(i);if a.flag==1 and a.id==37 and a.state==65 and math.abs(a.x-(liftX-8))<=1 then to('lift-ride');return 0 end end
   return routeAge<3 and 40 or 0
  end
  if y<=liftY then to(liftNext)end
  return 0
 end
 if #pickups>=4 then
  if not armed then return routeAge%8<2 and 68 or 0 end
  return 0
 end
 if item then
  if ground then local clear=clearGroundEnemy(x,y);if clear then return clear end end
  if item.kind==0 then local target=math.min(item.x-8,414);return x<target-1 and 1 or x>target+1 and 2 or 0 end
  if routePhase~='flower-hop'then beginLift(item.y<100 and 1720 or item.x-40,item.y<100 and 80 or 128,'flower-hop');return 0 end
  if routePhase=='flower-hop'then
   hopPeak=math.min(hopPeak,y)
   if routeAge>100 then beginLift(item.y<100 and 1720 or item.x-40,item.y<100 and 80 or 128,'flower-hop');return 0 end
   return (x<item.x+2 and 1 or 0)+(routeAge<36 and 128 or 0)
  end
 end
 if r('LevelNumber')==1 and r('AreaType')==0 then
  if x<152 then if ground and enemyNear(x,88)then return 4+(epoch%12<6 and 64 or 0)end;return 1 end
  if ground and epoch-lastPulse>30 then lastPulse=epoch;return 128 end
  return 0
 end
 if #pickups==0 then
  if x<328 then if ground and enemyNear(x,88)then return 4+(epoch%12<6 and 64 or 0)end;return 1 end
  if ground and epoch-lastPulse>30 then lastPulse=epoch;return 128 end
  return 0
 end
 if #pickups==1 and (routePhase=='flower-ground'or x>=1140)then
  -- Clear the two ground Goombas before approaching the block. The source
  -- standing shot passes above them; native Down+B supplies its low shot.
  if routePhase~='flower-ground'then to('flower-ground')end
  if not ground then return 0 end
  if enemyNear(x,200)then return 4+(epoch%12<6 and 64 or 0)end
  if x<1242 then return 1 end
  if ground and epoch-lastPulse>30 then lastPulse=epoch;return 128 end
  return 0
 end
 if #pickups==2 and x>=1640 then
  if routePhase~='third-bump'then beginLift(1720,112,'third-bump');return 0 end
  if x<1738 then return 1 end
  if ground and epoch-lastPulse>30 then lastPulse=epoch;return 128 end
  return 0
 end
 return ordinary(x,y,ground)
end
local function mapped(pc,physical)
 local map=emu.convertAddress(pc)
 return map and map.memType==emu.memType.nesPrgRom and map.address==physical
end
emu.addMemoryCallback(function()
 if not game or not mapped(L.HandlePowerUpCollision,PICKUP_OFFSET)then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i>5 then return end;local a=actor(i)
 if a.flag==0 or a.id~=46 or a.kind>=2 then return end
 assert(a.state>=128,'Natural item was immature at collection')
 assert(r('InvPickupOwner',i)==34 and r('InvPickup',i)==252,'Item lacked native Karnov preparation')
 local sp=cpu['cpu.sp'];local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 pending={item=a,before=state(),ret=ret&65535,sp=(sp+2)&255}
 if not returnHooks[ret&65535]then
  returnHooks[ret&65535]=true
  emu.addMemoryCallback(function()
   if not pending then return end
   local cpu=emu.getState();if cpu['cpu.pc']~=pending.ret or cpu['cpu.sp']~=pending.sp then return end
   local q=pending;pending=nil;q.after=state();q.erased=r('Enemy_Flag',q.item.slot)==0
   assert(q.erased,'Native collection did not erase actual item');q.ret=nil;q.sp=nil;pickups[#pickups+1]=q
   print('KARNOV_NATURAL_PICKUP '..encode(q));to('travel');jumpAge=0;release=4
  end,emu.callbackType.exec,ret&65535)
 end
end,emu.callbackType.exec,L.HandlePowerUpCollision)
emu.addMemoryCallback(function()
 if not game or r('CurrentBankC')~=2 or kr(0xc0)<129 then return end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)
 if ret==BOMB_CONTACT_RETURN then blastCalls=blastCalls+1 end
end,emu.callbackType.exec,L.HandleEnemyFBallCol)
emu.addMemoryCallback(function()
 if not game or not mapped(MANUAL_CREATED,MANUAL_OFFSET)then return end
 local i=emu.getState()['cpu.x'];if i>5 then return end;local a=actor(i)
 if a.flag==1 and a.id==37 and a.state==65 then helpers[#helpers+1]={frame=frame,world=r('WorldNumber')+1,stage=r('LevelNumber')+1,slot=i,left=a.x,center=a.x+16,initial_top=a.y,width=32,carries=0};print('KARNOV_MANUAL_HELPER '..encode(helpers[#helpers]))end
end,emu.callbackType.exec,MANUAL_CREATED)
emu.addEventCallback(function()
 local pad=0
 if not game and age<4 then if phase=='open'or phase=='start'then pad=16 elseif phase=='left'then pad=2 elseif phase=='select'then pad=32 end end
 if game and r('GameEngineSubroutine')==8 then pad=control()end
 emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then phase='open';age=0
 elseif phase=='open'and age>=50 then assert(r('CrossoverMenuState')==2);phase='left';age=0
 elseif phase=='left'and age>=30 then assert(r('CrossoverMenuIndex')==7);phase='select';age=0
 elseif phase=='select'and age>=30 then assert(r('SelectedCharacter')==34);phase='start';age=0
 elseif phase=='start'and age>=300 then assert(r('GameEngineSubroutine')==8);phase='game';game=true;lives=r('NumberofLives');age=0 end
 if game then
  if r('NumberofLives')~=lives or r('GameEngineSubroutine')==11 then finish(false,'life-lost');return end
  if kr(0x68)&128~=0 then finish(false,'health-depleted-before-four-pickup-sequence');return end
  local counter=r('FrameCounter');if previousCounter~=counter then previousCounter=counter;epoch=epoch+1;routeAge=routeAge+1 end
  for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 and a.kind<2 then
   local last=births[#births];if not last or last.slot~=i or last.collection~=#pickups then a.frame=frame;a.collection=#pickups;births[#births+1]=a end
   if a.state>=128 then births[#births].mature=true end
  end end
  local scene=r('LevelNumber')*256+r('AreaAddrsLOffset');if #scenes==0 or scenes[#scenes].key~=scene then scenes[#scenes+1]={key=scene,state=state()}end
  for _,h in ipairs(helpers)do if h.world==r('WorldNumber')+1 and h.stage==r('LevelNumber')+1 and r('Enemy_Flag',h.slot)==1 and r('Enemy_ID',h.slot)==37 and r('Enemy_State',h.slot)==65 and r('Enemy_X_Position',h.slot)+256*r('Enemy_PageLoc',h.slot)==h.left and r('PlatformCollisionFlag',h.slot)==h.slot then h.carries=h.carries+1 end end
  if kr(0xc0)==128 then armed=true end;if kr(0xc0)>=129 then blastSeen=true end
  if STOP_AFTER and #pickups>=STOP_AFTER then finish(true,'requested-natural-pickups');return end
  if #pickups>=4 and armed and blastSeen and kr(0xc0)==0 then finish(true,'naturally-earned-and-used-bomb');return end
  if frame%120==0 then trace[#trace+1]=state();if #trace>16 then table.remove(trace,1)end;print('KARNOV_NATURAL_PROGRESS '..encode(state()))end
  if epoch>18000 then finish(false,'route-bound')end
 end
 if frame>24000 then finish(false,'physical-bound')end
end,emu.eventType.endFrame)
