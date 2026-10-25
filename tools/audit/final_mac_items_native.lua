-- Prepared component fixture. A native pass requires this bound script to finish.
-- Resources are acquired/lost only through actual game code, never fixture stores.
local C=assert(FINAL_MAC_ITEMS)
for n,a in pairs(C.ram)do L[n]=a end
assert(C.mode_value==0 or C.mode_value==1,'Explicit numeric Easy/Hard configuration')
local wall,updates,age,index=0,0,0,0
local entered,done,writeBoundary=false,false,false
local phase,menuPhase='menu',C.mode_value==1 and'focus'or'start'
local current,deathStarted,respawnX=nil,false,nil
local results,captures={},{}
local injuryCount,pickups,starFrames,dmaFrames,sounds=0,0,0,0,{}
local forbidden={PlayerStatus=true,LmHealth=true,LmStars=true,LmHearts=true,
 LmAttack=true,LmSuper=true,LmHurt=true,LmInvul=true,LmReady=true,LmLife=true,
 LmRest=true,LmPrevious=true,LmFresh=true,InjuryTimer=true,StarInvincibleTimer=true,
 SelectedCharacter=true,PowerUpType=true,InvPickup=true,LmStamp=true,MmDeathFlag=true,
 CheatInvincible=true,NumberofLives=true}
for _,n in ipairs({'TimerControl','GameTimerDisplay'})do forbidden[n]=true end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)
 assert(writeBoundary and not forbidden[n],'Disclosed world/motion setup only: '..n)
 emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function json(v)
 if type(v)=='table'then
  local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
  for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function bank(pc)return emu.convertAddress(pc).address//8192 end
local function save(n,s)local f=assert(io.open(OUTPUT..n,'wb'));f:write(s);f:close()end
local log=assert(io.open(OUTPUT..'events.jsonl','w'))
local trace=assert(io.open(OUTPUT..'updates.csv','w'))
trace:write('wall,update,step,phase,age,x,y,state,hp,hearts,stars,status,injury,invul,hurt,attack,super,lives,death\n')
local function event(kind,data)
 local s=emu.getState();log:write(json({kind=kind,data=data,wall=wall,update=updates,index=index,phase=phase,
  pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']})..'\n');log:flush()
end
local function capture(name)captures[#captures+1]=string.format('%02d-',index)..name end
local function hook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(function()
  if bank(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound native instruction '..n)end
  fn()
 end,emu.callbackType.exec,h.address)
end
local pendingReturns,installedReturns={},{}
local function onReturn(name,fn)
 local s=emu.getState();local sp=s['cpu.sp']
 local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret;pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then
  installedReturns[key]=true
  emu.addMemoryCallback(function()
   local q=pendingReturns[key]
   if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
   pendingReturns[key]=nil;q.fn()
  end,emu.callbackType.exec,ret)
 end
end
local function state()
 local q={};for _,n in ipairs({'PlayerStatus','LmHealth','LmStars','LmHearts','LmAttack','LmSuper',
  'LmHurt','LmInvul','InjuryTimer','NumberofLives','MmDeathFlag','Player_X_Position','Player_Y_Position','Player_State'})do q[n]=r(n)end
 return q
end
local function free()
 return r('LmAttack')==0 and r('LmHurt')==0 and r('LmInvul')==0 and r('InjuryTimer')==0 and r('Player_State')==0
end
local function tile(page,col,row,id)
 local function art(n)local a=C.art[n];return emu.read(a.bank*8192+a.address%8192+id,emu.memType.nesPrgRom)end
 local function put(a,v)assert(writeBoundary);emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*0x400+row*64+col*2
 put(at,art('MTileTopLeft'));put(at+1,art('MTileTopRight'));put(at+32,art('MTileBotLeft'));put(at+33,art('MTileBotRight'))
 local a=0x23c0+page*0x400+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((art('MTileAttribute')>>6)<<shift))
end
local function arena(delivery)
 assert(free(),'Wait both source/native protection, attack and landing before staging')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do for row=11,12 do
  w('Block_Buffer_1',0x54,p*208+row*16+col);w('MmSolidTerrain',1,p*208+row*16+col)
 end end end
 -- Logical row0 begins32 pixels below the nametable origin: screen row=logical+2.
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 if delivery then w('Block_Buffer_1',0xc1,118);w('MmSolidTerrain',1,118);tile(0,6,9,0xc1)end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce',
  'ScrollThirtyTwo','AreaParserTaskNum','EnemyFrenzyBuffer','EnemyFrenzyQueue'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerFacingDir',1)
 assert(r('TimerControl')==0,'Native master timer is free; no timer reset')
end
local function target()
 assert(free()and r('Enemy_Flag')==0,'Separated actor and both protections expired')
 for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',104},
  {'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},
  {'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_BoundBoxCtrl',9},
  {'Enemy_CollisionBits',0},{'EnemyOffscrBitsMasked',0}})do w(q[1],q[2],0)end
 current.contactPending=true;event('explicit-standing-native-goomba',{x=104,y=184,box=9,before=state()})
end
local function hud()
 local hp=r('LmHealth');assert(emu.read(0x2006,emu.memType.nesPpuDebug)==hp//10 and emu.read(0x2007,emu.memType.nesPpuDebug)==hp%10,'Committed actual health digits')
 assert(emu.read(0x200e,emu.memType.nesPpuDebug)==r('LmStars'),'Committed actual earned star digit')
end
local function complete()
 current.after=state();current.finished=updates;event('step-completed',current);capture('complete');phase='cooldown';age=0
end
local function start()
 index=index+1
 if index>#C.plan then done=true;phase='complete';return end
 current={q=C.plan[index],before=state(),started=updates,contacts=0,riseCalls=0,grants=0,artFrames=0};results[#results+1]=current
 writeBoundary=true;arena(current.q.action=='block');writeBoundary=false
 age=0;phase=current.q.action;event('step-started',current);capture('start')
 if phase=='lethal'then current.livesBefore=r('NumberofLives')end
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  assert(r('SelectedCharacter')==15 and r('CrossoverBehaviorVersion')==C.mode_value,'Actual cold character and numeric mode readback')
  assert(r('CheatInvincible')==0,'Cold cheats remain off')
  entered=true;phase='settle';age=0;event('actual-cold-selection',{mode=r('CrossoverBehaviorVersion'),character=r('SelectedCharacter')})
 end
 updates=updates+1;age=age+1
 if current and current.removeEnemy then
  writeBoundary=true;w('Enemy_Flag',0,0);w('Enemy_CollisionBits',0,0);writeBoundary=false
  current.removeEnemy=nil;current.emptySince=updates;event('actual-contact-actor-separated',{})
 end
 if phase=='setup'then start()
 elseif (phase=='damage'or phase=='lethal')and not current.contactPending and current.contacts<current.q.contacts
  and free()and r('Enemy_Flag')==0 and(not current.emptySince or updates-current.emptySince>=4)then
  writeBoundary=true;arena(false);target();writeBoundary=false
 end
end)
hook('LmPrepareGate',function()
 if phase~='block'then return end
 onReturn('prepared',function()
  local slot=emu.getState()['cpu.x'];assert(slot==5 and r('PowerUpType',slot)==current.q.type,'Actual block owns mushroom/flower from naturally earned PlayerStatus')
  current.revealed=updates;current.revealY=r('Enemy_Y_Position',slot);current.stamp=r('LmStamp',slot)
  assert(current.stamp==(current.q.type==0 and 0xe0 or 0xe1),'Native item stamp')
  event('native-physical-reveal',{type=r('PowerUpType',slot),before=state(),stamp=current.stamp});capture('reveal')
 end)
end)
hook('LmRiseGate',function()
 if phase~='block'or not current.revealed or r('Enemy_State',5)>=128 then return end
 current.riseCalls=current.riseCalls+1
 onReturn('rise',function()
  assert(current.grants==0 and r('LmHealth')==current.before.LmHealth and r('LmStars')==current.before.LmStars,'No automatic collection while rising')
  if r('Enemy_State',5)>=128 and not current.mature then
   current.mature=updates;assert(r('Enemy_Y_Position',5)<current.revealY,'Visible actor rises from physical block')
   if current.q.type==1 then assert(current.riseCalls==48,'Source star48-handler-call emergence')end
   event('native-full-rise',{calls=current.riseCalls,y=r('Enemy_Y_Position',5)});capture('mature')
  end
 end)
end)
hook('LmCollectGate',function()
 if not entered or r('LmStamp',emu.getState()['cpu.x'])<0xe0 then return end
 assert(phase=='block'and current.revealed and current.mature and current.grants==0,'Collection follows real head bump, reveal and complete emergence')
 local hp,stars=r('LmHealth'),r('LmStars')
 onReturn('collected',function()
  assert(r('LmHealth')==(current.q.type==0 and math.min(96,hp+24)or hp),'Native mushroom heals24 only')
  assert(r('LmStars')==(current.q.type==1 and math.min(3,stars+1)or stars),'Native flower grants one star, cap3')
  assert(r('PlayerStatus')==1 and r('Square2SoundQueue')&C.powerup_sfx~=0,'Actual collection advances status and queues powerup SFX')
  current.grants=1;current.collected=updates;pickups=pickups+1;event('actual-native-pickup',{beforeHP=hp,beforeStars=stars,after=state()});capture('collected')
 end)
end)
hook('LmInjuryGate',function()
 if not current or not current.contactPending or r('LmInvul')~=0 then return end
 assert(phase=='damage'or phase=='lethal','Only disclosed physical contact plan may damage Mac')
 local before=state()
 onReturn('injured',function()
  local hp=math.max(0,before.LmHealth-8)
  assert(r('LmHealth')==hp,'Actual Goomba contact subtracts8HP, without fixture health write')
  if hp>0 then
   assert(r('LmStars')==math.max(0,before.LmStars-1)and r('LmHearts')==math.max(0,before.LmHearts-3),'Actual contact removes a star and3 stamina')
   assert(r('LmInvul')==64 and r('LmHurt')==16,'Actual native protection starts')
  else assert(phase=='lethal'and before.LmHealth==8,'Death is reached by actual final contact')end
  current.contacts=current.contacts+1;injuryCount=injuryCount+1;current.contactPending=nil;current.removeEnemy=true
  event('actual-native-injury',{before=before,after=state(),contact=current.contacts});capture('injury-'..current.contacts)
 end)
end)
hook('LmDeathStartGate',function()
 if not entered then return end
 assert(phase=='lethal'and current.before.LmHealth==64,'Only final physical damage stage may cause death')
 deathStarted=true;current.deathAt=wall;event('actual-native-death',{before=state()});capture('death')
end)
hook('LmWeaponsGate',function()
 if phase~='super'or current.superStarted or r('LmAttack')~=0 or r('SavedJoypadBits')&0x48~=0x48 then return end
 local before=state()
 onReturn('earned-super',function()
  assert(r('LmStars')==before.LmStars-1 and r('LmHearts')==before.LmHearts-1,'Up+B spends a physically earned star and one stamina')
  assert(r('LmAttack')==88 and r('LmSuper')==1,'Native super-punch starts authentic88-tick animation')
  current.superStarted=updates;event('actual-earned-super',{before=before,after=state()});capture('earned-super')
 end)
end)
hook('finish',function()
 if not entered or done then return end
 if phase=='settle'and age>=30 then
  assert(r('LmHealth')==96 and r('LmHearts')==20 and r('LmStars')==0 and r('PlayerStatus')==0,'Actual cold96HP/default resources')
  phase='setup';age=0
 elseif phase=='damage'and current.contacts==current.q.contacts and free()then
  assert(r('LmHealth')==current.q.hp and r('LmStars')==current.q.stars,'Repeated real contacts establish expected resource state')
  hud();complete()
 elseif phase=='block'then
  for i=0,3 do if r('Block_State',i)~=0 then current.headBlock=true end end
  if current.revealed then assert(current.headBlock,'Physical native head bump, not injected actor')end
  if age>=220 and current.grants==1 and r('Enemy_Flag',5)==0 and free()then
   assert(r('LmHealth')==current.q.hp and r('LmStars')==current.q.stars,'Actual physical item result')
   if current.q.type==1 then assert(current.artFrames>0,'Uploaded original73-pixel white star observed')end
   assert((sounds[index]or 0)>0,'Real pickup powerup sound queued');hud();complete()
  end
 elseif phase=='super'and age>=150 and free()then
  assert(current.superStarted and r('LmStars')==2 and r('LmHealth')==72,'Earned super spends stock without inventing resources')
  hud();complete()
 elseif phase=='cooldown'and age>=32 and free()then phase='setup';age=0
 end
 trace:write(table.concat({wall,updates,index,phase,age,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),
  r('LmHealth'),r('LmHearts'),r('LmStars'),r('PlayerStatus'),r('InjuryTimer'),r('LmInvul'),r('LmHurt'),r('LmAttack'),r('LmSuper'),r('NumberofLives'),r('MmDeathFlag')},',')..'\n')
 local limit=(phase=='damage'or phase=='lethal')and 4000 or 900
 assert(age<limit,'Finite physical step '..phase)
end)
-- Original uploaded73-white-pixel star oracle, paired with its committed OAM.
local sourceRows={'.....#.....','....###....','....###....','...#####...',
 '###########','###########','.#########.','..#######..',
 '..#######..','..###.###..','.###...###.','.##.....##.'}
local upper,banks,pendingStar,published,publishedStar,dma=0,{},nil,nil,nil,nil
local function bytes(at,kind)local t={};for i=0,255 do t[#t+1]=string.char(emu.read(at+i,kind))end;return table.concat(t)end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)banks[a-0x5120]=v+upper*256 end,emu.callbackType.write,0x5120,0x512b)
hook('MetaspriteRenderLoop',function()
 if phase=='block'and current.q.type==1 and r('R0')+256*r('R1')==L.LmStar and bank(0xc000)==C.star_bank then
  pendingStar={index=index,x=r('R4'),y=r('R6'),age=age}
 end
end)
hook('RosterOamReady',function()
 if not entered or done then return end
 published=bytes(L.Sprite_Data,emu.memType.nesDebug);publishedStar=pendingStar;pendingStar=nil
end)
emu.addMemoryCallback(function(_,page)
 dma=nil;if entered and not done and published then
  local image=bytes(page*256,emu.memType.nesDebug)
  if image==published then dma={image=image,star=publishedStar}end
 end
end,emu.callbackType.write,0x4014)
hook('NmiReturn',function()
 if not dma then return end
 local frame=dma;dma=nil;assert(bytes(0,emu.memType.nesSpriteRam)==frame.image,'Committed complete OAM publication reaches actual hardware');dmaFrames=dmaFrames+1
 local p=frame.star;if not p then return end
 local pixels,count,parts={},0,0
 for i=0,63 do
  local at=i*4;local y=emu.read(at,emu.memType.nesSpriteRam);local tile=emu.read(at+1,emu.memType.nesSpriteRam)
  local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
  if y<240 and(tile==1 or tile==3)and(attr&3)==2 and banks[4]==704 then
   parts=parts+1
   for yy=0,15 do for xx=0,7 do
    local sy=(attr&128)~=0 and 15-yy or yy;local sx=(attr&64)~=0 and 7-xx or xx
    local a=4096+(tile&254)*16+(sy//8)*16+sy%8
    local function bit(at)return emu.read(assert(banks[at//1024])*1024+at%1024,emu.memType.nesChrRom)>>(7-sx)&1 end
    local q=bit(a)+2*bit(a+8)
    if q>0 then
     assert(emu.read(0x3f10+(attr&3)*4+q,emu.memType.nesPpuDebug)==48,'Original white star palette')
     local key=(x+xx-p.x)..','..(y+yy-p.y);if not pixels[key]then count=count+1;pixels[key]=true end
    end
   end end
  end
 end
 local correct=parts==2 and count==73
 for y=1,12 do for x=1,11 do if(pixels[(x-1)..','..(y-7)]or false)~=(sourceRows[y]:sub(x,x)=='#')then correct=false end end end
 if results[p.index].artFrames==0 or not correct then
  save('star-'..p.index..'-oam.bin',frame.image)
  local chr={};for i=0,1023 do chr[#chr+1]=string.char(emu.read(704*1024+i,emu.memType.nesChrRom))end
  save('star-'..p.index..'-chr.bin',table.concat(chr));save('star-'..p.index..'-pixels.json',json({correct=correct,parts=parts,opaque=count,x=p.x,y=p.y,age=p.age}));capture('original-star-hardware')
 end
 assert(correct,'Uploaded star matches all73 original white pixels including right points')
 results[p.index].artFrames=results[p.index].artFrames+1;starFrames=starFrames+1
end)
emu.addMemoryCallback(function(_,v)if entered and phase=='block'and v&C.powerup_sfx~=0 then sounds[index]=(sounds[index]or 0)+1 end end,emu.callbackType.write,L.Square2SoundQueue)
for _,n in ipairs({'LmHealth','LmStars','LmHearts','PlayerStatus'})do
 emu.addMemoryCallback(function(_,v)if entered then assert(not writeBoundary,'No fixture resource write');event('actual-native-resource-write',{name=n,before=r(n),value=v})end end,emu.callbackType.write,L[n])
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='focus'then menuPhase='open';return{down=true}end
 if menuPhase=='open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then menuPhase='back';return{a=true}end;menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if r('CrossoverMenuState')==2 then
  local ix=r('CrossoverMenuIndex');if ix==C.menu_target then return{a=true}end
  return{[assert(C.menu_moves[ix+1])]=true}
 end
 return{start=true}
end
emu.addEventCallback(function()
 local b={}
 if not entered then b=menu()
 elseif phase=='block'then
  b.a=age>=20 and age<45
  if current.q.type==0 then b.right=age>=70 and age<155;b.a=b.a or(age>=90 and age<125)
  else b.right=age>=70 and age<96;b.a=b.a or(age>=130 and age<180);b.left=age>=134 and age<180 end
 elseif phase=='super'then b.up=age>=20 and age<24;b.b=b.up
 elseif phase=='respawn'then b.right=age<70 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 for _,name in ipairs(captures)do save(name..'.png',emu.takeScreenshot())end;captures={}
 if phase=='lethal'and deathStarted and r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0 then
  assert(current.contacts==8 and r('NumberofLives')==(current.livesBefore-1)%256,'Eight actual final contacts consume one native life')
  assert(r('LmHealth')==96 and r('LmHearts')==20 and r('LmStars')==0,'Real death initializes healthy96HP/default resources')
  respawnX=r('Player_X_Position');phase='respawn';age=0;event('actual-healthy-respawn',state());capture('respawn')
 elseif phase=='respawn'and age>=70 then
  assert(r('Player_X_Position')>respawnX+8 and r('LmHealth')==96,'Actual healthy respawn responds to controller')
  complete();done=true;phase='complete'
 end
 if done then
  assert(#results==9 and pickups==5 and injuryCount==15 and starFrames>0 and dmaFrames>100,'Entire finite naturally earned Mac resource plan')
  trace:close();log:close()
  save('native-result.json',json({passed=true,goal_complete=false,ROM_sha256=C.ROM_sha256,mode=C.mode_label,actual_mode_readback=r('CrossoverBehaviorVersion'),
   wall=wall,updates=updates,physical_pickups=pickups,real_contacts=injuryCount,star_DMA_frames=starFrames,full_OAM_DMA_frames=dmaFrames,steps=results,
   scope='Cold native menu; explicit aligned world/motion/Goomba setup only. Six real contacts96->48; controller mushroom+24; four physical flowers0->3/cap; earnedUp+B/spend; actual star loss; eight further contacts/death/healthy96HP movable respawn. No resource/PlayerStatus/attack/hurt/invul writes, no injected item or post-rise item placement. Not a campaign certificate.'}))
  emu.stop(0)
 end
 assert(wall<16000,'Bounded naturally earned Mac component lifecycle')
end,emu.eventType.endFrame)
local inheritedAssert=assert
function assert(ok,message,...)
 if not ok then
  local s=emu.getState();local f=io.open(OUTPUT..'first-failure.json','w')
  if f then f:write(json({message=tostring(message),wall=wall,updates=updates,index=index,age=age,phase=phase,current=current,
   pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp'],state=entered and state()or{}}));f:close()end
 end
 return inheritedAssert(ok,message,...)
end
