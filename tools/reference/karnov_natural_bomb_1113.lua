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
local lastTravelX,travelStall=nil,0
local undergroundReady,entryTrace=false,0
local entryFirst,entryRecent={},{}
local deathIngress=nil
local bootsUsed=nil
local bombProbe={heads={},shots={},frames={},minY=255}
local bombJumpUntil=0
local bombBrickStable=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function kr(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function actor(i)return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function state()return {frame=frame,epoch=epoch,x=wx(),y=r('Player_Y_Position'),state=r('Player_State'),engine=r('GameEngineSubroutine'),level=r('LevelNumber'),world=r('WorldNumber'),area=r('AreaAddrsLOffset'),lives=r('NumberofLives'),shot=kr(0x65)&3,boots_active=kr(0x65)&128~=0,boots_stock=kr(0xbd),health=kr(0x68),cycle=kr(0x860),option=kr(0x8e),owned=kr(0x8f),stock=kr(0xbb),bomb=kr(0xc0),route=routePhase}end
local function encode(v)
 if type(v)=='table'then local a=true;local n=0;for k in pairs(v)do if type(k)~='number'then a=false end;n=n+1 end
  local out={};if a then for i=1,n do out[#out+1]=encode(v[i])end;return '['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return '{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='nil'then return 'null'else return tostring(v)end
end
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,ROM_SHA256=ROM_SHA,reason=reason,controller_only=true,frames=frame,updates=epoch,pickups=pickups,births=births,scenes=scenes,manual_helpers=helpers,boots_activation=bootsUsed,fourth_probe=bombProbe,recent=trace,underground_entry_first=entryFirst,underground_entry_recent=entryRecent,death_ingress=deathIngress,terminal=state(),armed=armed,blast_seen=blastSeen,native_blast_contacts=blastCalls}))
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
 if x>=2422 and x<2440 and not ground and y>96 and y<=112 then pad=pad&~1 end
 return pad
end
local function control()
 local x,y,ground=wx(),r('Player_Y_Position'),r('Player_State')==0
 -- Let the authored 1-2 falling entrance finish before supplying any
 -- fresh jump or horizontal movement. Engine8 alone starts above ground.
 if r('LevelNumber')==1 and r('AreaType')==2 and not undergroundReady then
  if ground and y>=160 and r('Player_Y_HighPos')==1 then
   undergroundReady=true;jumpAge=0;release=8;to('travel')
  end
  return 0
 end
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
  -- The fourth underground flower has masonry on its west side. The
  -- observed east channel at1136 is clear; approach from that side.
  local east=#pickups==3 and r('LevelNumber')==1 and r('AreaType')==2
  local approach=east and item.x+32 or(item.y<100 and 1720 or item.x-40)
  if routePhase~='flower-hop'then beginLift(approach,item.y<100 and 80 or 128,'flower-hop');return 0 end
  if routePhase=='flower-hop'then
   hopPeak=math.min(hopPeak,y)
   if routeAge>100 then beginLift(approach,item.y<100 and 80 or 128,'flower-hop');return 0 end
   local steer=east and(x>item.x+2 and 2 or 0)or(x<item.x+2 and 1 or 0)
   return steer+(routeAge<36 and 128 or 0)
  end
 end
 if r('LevelNumber')==1 and r('AreaType')==2 then
  if #pickups==3 then
   if kr(0x65)&128==0 and kr(0xbd)>0 then
    if not ground then return 0 end
    return routeAge%8<2 and 68 or 0 -- Original earned Boots: Down + fresh B.
   end
   if routePhase:sub(1,5)=='bomb-'or x>=1040 then
    if routePhase:sub(1,5)~='bomb-'then to('bomb-approach');jumpAge=0;release=0 end
    if routePhase=='bomb-approach'then
     if not ground then return 0 end
     local clear=clearGroundEnemy(x,y);if clear then return clear end
     local anchor=bombBrickStable>=8 and 1097 or 1081
     if x<anchor then return 1 elseif x>anchor+2 then return 2 end
     to('bomb-release');return 0
    elseif routePhase=='bomb-release'then
     if routeAge>=3 then to('bomb-bump')end
     return 0
    end
    -- GroundY176 and the authentic48px jump already reach the underside
    -- at brick128..143. The52 masonry immediately below it must first be
    -- broken by the existing source fireball/native block-effect bridge.
    if ground then
     local clear=clearGroundEnemy(x,y);if clear then return clear end
     local anchor=bombBrickStable>=8 and 1097 or 1081
     if x<anchor or x>anchor+2 then to('bomb-approach');return 0 end
     if r('PlayerFacingDir')~=1 then return 1 end
    end
    local pad=epoch%8<4 and 64 or 0
    -- Input may be polled more than once at the same logical epoch. Keep a
    -- real held A window instead of consuming its edge in the first poll.
    if ground and epoch-lastPulse>30 then lastPulse=epoch;bombJumpUntil=epoch+6 end
    if epoch<bombJumpUntil then pad=pad|128 end
    return pad
   end
   return ordinary(x,y,ground)
  end
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
 if r('LevelNumber')==0 and #pickups>=2 and (routePhase:sub(1,4)=='gap-'or x>=2420 and x<2480)then
  if routePhase:sub(1,4)~='gap-'then to('gap-setup')end
  if routePhase=='gap-setup'then
   if x<2433 then return 1 end
   if ground then to('gap-release')end
   return 0
  elseif routePhase=='gap-release'then
   if routeAge>=3 then to('gap-jump')end
   return 0
  end
  if x>=2480 and ground then to('travel');return 1 end
  return 1+(routeAge<36 and 128 or 0)
 end
 return ordinary(x,y,ground)
end
local function mapped(pc,physical)
 local map=emu.convertAddress(pc)
 return map and map.memType==emu.memType.nesPrgRom and map.address==physical
end
local function probe(name,q,limit)
 local rows=bombProbe[name];rows[#rows+1]=q;if #rows>limit then table.remove(rows,1)end
end
emu.addMemoryCallback(function()
 if not game or #pickups~=3 or r('LevelNumber')~=1 or r('CurrentBankC')~=2 then return end
 local x=kr(0x850)+256*kr(0x851);if x<1024 or x>1184 then return end
 local yy=kr(0x853)
 probe('shots',{frame,epoch,x,yy,tile(x+4,yy+4),kr(0x84f),kr(0x62),kr(0x66),r('SavedJoypadBits')},24)
end,emu.callbackType.exec,L.KrCombatBlock)
emu.addMemoryCallback(function()
 if not game or #pickups~=3 or r('LevelNumber')~=1 or not mapped(L.NativeRarePlayerHeadCollisionCore,HEAD_OFFSET)then return end
 local cpu=emu.getState()
 probe('heads',{frame,epoch,cpu['cpu.a'],wx(),r('Player_Y_Position'),r('Player_Y_Speed'),r('R4'),r('MmBlockAttack')},16)
end,emu.callbackType.exec,L.NativeRarePlayerHeadCollisionCore)
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
if emu.callbackType.write then emu.addMemoryCallback(function(address,value)
 if value~=11 or not game then return end
 local cpu=emu.getState();local stack={};for i=1,16 do stack[i]=emu.read(0x100+((cpu['cpu.sp']+i)&255),emu.memType.nesDebug)end
 local regs={};for _,k in ipairs({'pc','sp','a','x','y'})do regs[k]=cpu['cpu.'..k]end
 deathIngress={address=address,value=value,cpu=regs,bank=r('CurrentBank'),bankC=r('CurrentBankC'),stack=stack,s=state(),high=r('Player_Y_HighPos'),dy=r('Player_Y_Speed'),pad=r('SavedJoypadBits'),source={kr(0x62),kr(0x63),kr(0x64),kr(0x65),kr(0x66),kr(0x67),kr(0x68)}}
end,emu.callbackType.write,L.GameEngineSubroutine)end
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
  if routePhase=='travel'and #pickups>=2 and #pickups<4 and r('GameEngineSubroutine')==8 then if wx()==lastTravelX then travelStall=travelStall+1 else travelStall=0;lastTravelX=wx()end else travelStall=0;lastTravelX=nil end
  if travelStall>240 then finish(false,'travel-stall');return end
  if routePhase=='bomb-bump'and routeAge>480 then finish(false,'fourth-brick-not-revealed');return end
  if #pickups==3 and routePhase:sub(1,5)=='bomb-'then
   if tile(1104,144)==0 then bombBrickStable=bombBrickStable+1 else bombBrickStable=0 end
   bombProbe.minY=math.min(bombProbe.minY,r('Player_Y_Position'))
   if epoch%10==0 then
    local shots={};for i=0,24,3 do if kr(0x6e+i)&128~=0 then shots[#shots+1]={kr(0x6e+i),kr(0x6f+i),kr(0x70+i)}end end
    probe('frames',{frame,epoch,wx(),r('Player_Y_Position'),r('Player_Y_Speed'),r('SavedJoypadBits'),kr(0x62),kr(0x66),kr(0x6a),kr(0x6b),r('PlayerFacingDir'),tile(1104,144),tile(1104,128),shots},32)
   end
  end
  for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 and a.kind<2 then
   local last=births[#births];if not last or last.slot~=i or last.collection~=#pickups then a.frame=frame;a.collection=#pickups;births[#births+1]=a end
   if a.state>=128 then births[#births].mature=true end
  end end
  local scene=r('LevelNumber')*256+r('AreaAddrsLOffset');if #scenes==0 or scenes[#scenes].key~=scene then scenes[#scenes+1]={key=scene,state=state()}end
  if r('LevelNumber')==1 and r('AreaType')==2 and entryTrace<90 then
   entryTrace=entryTrace+1
   local q={s=state(),high=r('Player_Y_HighPos'),dy=r('Player_Y_Speed'),pad=r('SavedJoypadBits'),source={kr(0x62),kr(0x63),kr(0x64),kr(0x65),kr(0x66),kr(0x67),kr(0x68)},ready=undergroundReady}
   if #entryFirst<8 then entryFirst[#entryFirst+1]=q else entryRecent[#entryRecent+1]=q;if #entryRecent>16 then table.remove(entryRecent,1)end end
   print('KARNOV_UNDERGROUND_ENTRY '..encode(q))
  end
  for _,h in ipairs(helpers)do if h.world==r('WorldNumber')+1 and h.stage==r('LevelNumber')+1 and r('Enemy_Flag',h.slot)==1 and r('Enemy_ID',h.slot)==37 and r('Enemy_State',h.slot)==65 and r('Enemy_X_Position',h.slot)+256*r('Enemy_PageLoc',h.slot)==h.left and r('PlatformCollisionFlag',h.slot)==h.slot then h.carries=h.carries+1 end end
  if kr(0xc0)==128 then armed=true end;if kr(0xc0)>=129 then blastSeen=true end
  if not bootsUsed and #pickups>=3 and kr(0x65)&128~=0 then bootsUsed=state()end
  if STOP_AFTER and #pickups>=STOP_AFTER then finish(true,'requested-natural-pickups');return end
  if #pickups>=4 and armed and blastSeen and kr(0xc0)==0 then finish(true,'naturally-earned-and-used-bomb');return end
  if frame%120==0 then trace[#trace+1]=state();if #trace>16 then table.remove(trace,1)end;print('KARNOV_NATURAL_PROGRESS '..encode(state()))end
  if epoch>18000 then finish(false,'route-bound')end
 end
 if frame>24000 then finish(false,'physical-bound')end
end,emu.eventType.endFrame)
