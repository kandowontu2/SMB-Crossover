-- Typed mature pickup scenes; all health/owned stock and attacks are native.
local C=assert(CURRENT_MAC_MIKE_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot
local csv=assert(io.open(OUTPUT..'components.csv','w'))
csv:write('event,wall,update,case,phase,age,hp,capacity,stock,selected,injury,hurt,x,y,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function hp()return r(C.mac and'LmHealth'or'JnHealth')end
local function stock()return r(C.mac and'LmStars'or'JnOwnedTier')end
local function pool()if C.mac then return 0 end;local v=0;for i=0,5 do if r('JnShotKind',i)~=0 then v=v+1 end end;return v end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,index,phase,age,hp(),r(C.mac and'LmHearts'or'JnMaxHearts'),stock(),C.mac and r('LmSuper')or r('JnSelected'),r('InjuryTimer'),r(C.mac and'LmHurt'or'JnHurt'),r('Player_X_Position'),r('Player_Y_Position'),value or 0},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local yes=false;for _,b in ipairs(h.banks)do if bank(h.pc)==b then yes=true end end;if not yes then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only native GameLoop+5 typed setup')
 assert(C.setup_allowed[n]and not C.resource_bans[n],'No health/tier/owned/ammo/attack/hurt/RNG/outcome seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)assert(not writing and not nmi and not irq and r('NmiDisable')==255);writing=true;fn();writing=false;event('typed-scene-setup')end
local function tile(page,col,row,id)
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)assert(writing and not nmi and not irq);emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function quiet()
 return r('Player_State')==0 and r('InjuryTimer')==0 and r(C.mac and'LmAttack'or'JnAttack')==0 and r(C.mac and'LmHurt'or'JnHurt')==0 and(not C.mac or r('LmInvul')==0)and pool()==0
end
local function arena(face)
 assert(quiet(),'Wait native landing/attack/projectiles and BOTH protections')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',face);w('Player_MovingDir',face);w('Player_CollisionBits',255)
end
local function actor(x,y,kind,slot)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',kind},{'Enemy_State',kind==46 and 128 or 0},{'Enemy_BoundBoxCtrl',kind==46 and 3 or 9},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_SprAttrib',0},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0}})do w(a[1],a[2],slot)end
end
local function pickup(task)
 actor(112,184,46,5);w('InvPickupOwner',C.character,5)
 if C.mac then w('PowerUpType',task.pickup,5);w('LmStamp',task.pickup==0 and 0xe0 or 0xe1,5);w('InvPickup',task.pickup==0 and 0xe0 or 0xe1,5)
 else
  local kind=1
  if task.pickup==1 then
   if r('JnOwnedTier')<3 then kind=r('JnOwnedTier')+1
   else local i=0;while i<10 and r('JnAmmo',i)~=0 do i=i+1 end;if i==10 then i=math.max(0,r('JnSelected')-1)end;kind=i+4 end
  end
  assert(kind==task.item,'Typed mature stamp agrees with actual source prepare policy')
  w('PowerUpType',1,5);w('InvPickup',0x80+kind,5)
 end
end
local function drop(kind)
 assert(not C.mac and r('JnDropKind',0)==0,'Previous physical restoration pickup consumed')
 w('JnDropKind',kind,0);w('JnDropX',112,0);w('JnDropPage',0,0);w('JnDropY',192,0);w('JnDropAge',0,0)
end
local function target(task,contact)
 if contact then actor(112,184,6,0)
 elseif task.weapon==7 then actor(160,184,C.mirror_target,0);actor(188,184,6,1)
 else actor(task.face==2 and 88 or 140,184,6,0)end
end
local function beginCase()
 local t=assert(C.plan[index]);assert(hp()==t.health,'Real carried health before '..t.name)
 rec={name=t.name,kind=t.kind,health=hp(),stock=stock(),hearts=C.mac and r('LmHearts')or r('JnMaxHearts'),hits=0,grants=0,contacts=0,debits=0,births=0,reflects=0,splits=0,drops=0,toggles=0,started=updates}
 if not C.mac then rec.remainder=r('JnStars')&7;assert(rec.remainder<5,'Actual source star remainder0..4');rec.ammo={};for i=0,9 do rec.ammo[i+1]=r('JnAmmo',i)end end
 records[#records+1]=rec;phase=t.kind;age=0
 transaction(function()arena(t.face or 1);if phase=='pickup'then pickup(t)elseif phase=='contact'then target(t,true)elseif phase=='weapon'then target(t,false)elseif phase=='drop'then drop(t.drop)end end);event('case-start')
end
local function complete()
 rec.completed=updates;rec.afterHP=hp();rec.afterStock=stock();rec.updates=age;event('case-complete');index=index+1
 if index>#C.plan then done=true;phase='complete'else phase='setup'end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then if r('CrossoverMenuState')~=4 then return{}end;if r('CrossoverOptionsFocus')~=1 then return{down=true}end;if r('CrossoverBehaviorVersion')~=C.mode then menuPhase='back';return{a=true}end;menuPhase='back'end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i~=C.menu then local key=assert(C.navigation[i+1]);assert(key~='');return{[key]=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual cold Hard owner/menu');entered=true;phase='settle';age=0 end
 updates=updates+1;age=age+1;assert(updates<4000,'Bounded Main updates')
 assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual identity/Hard retained')
 if phase=='settle'and age>=30 then
  if C.mac then assert(hp()==96 and r('LmHearts')==20 and r('LmStars')==0,'Actual cold Mac resources')else assert(hp()==6 and r('JnMaxHearts')==3 and r('JnOwnedTier')==1 and r('JnSelected')==0,'Actual cold Mike resources');for i=0,9 do assert(r('JnAmmo',i)==0,'Actual unowned Mike specials')end end
  beginCase()
 elseif phase=='setup'and quiet()then beginCase()
 elseif rec and phase=='contact'then
  if rec.remove then transaction(function()w('Enemy_Flag',0,0);w('Enemy_CollisionBits',0,0)end);rec.remove=false;rec.separated=updates end
  if rec.rearm and quiet()and updates>rec.separated then transaction(function()arena(1);target(C.plan[index],true)end);rec.rearm=false end
 elseif rec and phase=='pickup'and rec.again then transaction(function()pickup(C.plan[index])end);rec.again=false
 elseif rec and phase=='drop'and rec.again then transaction(function()drop(C.plan[index].drop)end);rec.again=false end
end)
hook('Collect',function(s)
 if not entered then return end
 local valid=r('InvPickupOwner',s['cpu.x'])==C.character and(C.mac and r('LmStamp',s['cpu.x'])>=0xe0 or not C.mac and r('InvPickup',s['cpu.x'])>=0x81 and r('InvPickup',s['cpu.x'])<=0x8d)
 if not valid then return end
 assert(phase=='pickup'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Actual physical mature pickup before source grant')
 local t=C.plan[index];assert(not rec.pendingGrant,'One source grant at a time')
 rec.pendingGrant={hp=hp(),stock=stock(),hearts=C.mac and r('LmHearts')or r('JnMaxHearts')};rec.grants=rec.grants+1;event('actual-collection-entry',t.pickup)
end)
hook('Injury',function()
 if not entered or not rec or r(C.mac and'LmInvul'or'JnHurt')~=0 then return end
 assert(phase=='contact'and r('Enemy_ID',0)==6 and r('Enemy_Flag',0)~=0 and not rec.pendingHit,'Actual planned native body contact')
 rec.pendingHit={hp=hp()-(C.mac and 8 or 2),stock=stock(),hearts=C.mac and r('LmHearts')or r('JnMaxHearts')};event('actual-contact-injury')
end)
hook('Defeat',function(s)
 if entered and rec then assert(phase=='weapon'and s['cpu.x']==(C.plan[index].weapon==7 and 1 or 0),'Actual intended weapon defeat source');rec.contacts=rec.contacts+1;event('actual-source-defeat')end
end)
if not C.mac then
 hook('Reflect',function()if entered and rec then assert(phase=='weapon'and C.plan[index].weapon==7,'Actual Miracle Mirror reflect source');rec.reflects=rec.reflects+1;event('actual-mirror-reflect')end end)
 emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then assert(phase=='weapon','Only native attack phase can birth projectiles');rec.births=rec.births+1;event('native-projectile-birth',v)end end,emu.callbackType.write,C.ram.JnShotKind,C.ram.JnShotKind+5)
 emu.addMemoryCallback(function(a,v)if entered and rec and not writing and phase=='weapon'and v==r('JnAmmo',a-C.ram.JnAmmo)-1 then rec.debits=rec.debits+1;event('native-one-ammo-debit',v)end end,emu.callbackType.write,C.ram.JnAmmo,C.ram.JnAmmo+9)
 hook('DropCollect',function(s)
  if entered and rec and phase=='drop'then assert(s['cpu.x']==0 and r('JnDropKind',0)==C.plan[index].drop and r('JnDropAge',0)>0,'Live native private restoration actor');rec.drops=rec.drops+1;event('actual-restoration-collection')end
 end)
end
hook('GameLoopFinish',function()
 if not entered or done or not rec or phase=='setup'or phase=='settle'then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No hidden death/transition');local t=C.plan[index]
 if rec.pendingHit then local p=rec.pendingHit;assert(hp()==p.hp and(C.mac and r('InjuryTimer')==0 or not C.mac and r('InjuryTimer')>0)and r(C.mac and'LmHurt'or'JnHurt')>0,'Actual family injury/protection contract');if C.mac then assert(stock()==math.max(0,p.stock-1)and r('LmHearts')==math.max(0,p.hearts-3)and r('LmInvul')==64 and r('LmHurt')==16,'Native Mac star/stamina loss and private64/16 protection')end;rec.hits=rec.hits+1;rec.pendingHit=nil;rec.remove=true;rec.rearm=rec.hits<t.hits end
 if rec.pendingGrant then
  local p=rec.pendingGrant
  if C.mac then assert(hp()==(t.pickup==0 and math.min(96,p.hp+24)or p.hp)and stock()==(t.pickup==1 and math.min(3,p.stock+1)or p.stock),'Native Mac heal24/star+1cap3')
  elseif t.item==1 then assert(r('JnMaxHearts')==math.min(22,p.hearts+1)and hp()==r('JnMaxHearts')*2,'Native heart-container growth/full restore')
  elseif t.item<4 then assert(stock()==math.max(p.stock,t.item)and hp()==p.hp,'Native owned primary tier')
  else assert(r('JnAmmo',t.item-4)==C.refills[t.item-3]and r('JnSelected')==t.item-3 and hp()==p.hp,'Native exact weapon stock replacement/autoselect')end
  assert(r('Enemy_Flag',5)==0,'Native mature pickup erase');rec.pendingGrant=nil;if rec.grants<(t.count or 1)then rec.again=true end
 end
 if rec.contacts>0 and(r('Enemy_State',t.weapon==7 and 1 or 0)&32~=0 or r('Enemy_Flag',t.weapon==7 and 1 or 0)==0)then rec.defeatSeen=true end
 if phase=='pickup'and rec.grants==(t.count or 1)and not rec.again and age>=8 then assert(hp()==t.afterHP and stock()==t.afterStock,'Exact carried pickup outcome');if t.picture then screenshot=t.picture end;complete()
 elseif phase=='contact'and rec.hits==t.hits and not rec.remove and quiet()then assert(hp()==rec.health-(C.mac and 8 or 2)*t.hits,'Earned healing deficit');complete()
 elseif phase=='drop'then
  if rec.drops>0 and r('JnDropKind',0)==0 then if rec.drops<(t.count or 1)then rec.again=true else assert(hp()==t.afterHP and r('JnStars')&7==(rec.remainder+(t.drop==2 and(t.count or 1)or 0))%5,'Exact real restoration/star remainder');if t.picture then screenshot=t.picture end;complete()end end
 elseif phase=='select'then
  local s=r('JnSelected');if rec.lastSelect~=nil and s~=rec.lastSelect then rec.toggles=rec.toggles+1 end;rec.lastSelect=s
  if age>=t.edges*10+5 then assert(rec.toggles==t.edges and s==t.selected,'Actual Select edges retain real owned stock');complete()end
 elseif phase=='empty'then if age>=20 then assert(r('LmAttack')==0 and r('LmStars')==0 and r('LmHearts')==rec.hearts,'Empty Mac stars cannot invent super punch');complete()end
 elseif phase=='rest'then if age>=35 then assert(hp()==rec.health and r('LmStars')==0 and rec.hearts==0 and r('LmHearts')==20,'Actual crouch-rest restores20 empty stamina without a refill seed');complete()end
 elseif phase=='weapon'then
  if t.picture and not rec.pictured and(C.mac and r('LmAttack')>0 or not C.mac and pool()>0)then screenshot=t.picture;rec.pictured=true end
  if not C.mac and t.weapon==8 then for i=0,5 do if r('JnShotKind',i)==8 and r('JnShotHit',i)&128~=0 then rec.splits=rec.splits+1 end end end
  if age>=t.wait and quiet()then
   assert(rec.contacts==1 and rec.defeatSeen and hp()==rec.health,'Actual target kill and native attack cleanup without health loss')
   if C.mac then assert(stock()==rec.stock-(t.super and 1 or 0)and r('LmHearts')==rec.hearts,'Actual one heart debit and one hit refund; star cost only for uppercut')
   else for i=0,9 do assert(r('JnAmmo',i)==rec.ammo[i+1]-((t.weapon>=4 and i==t.weapon-4)and 1 or 0),'Exact earned-ammo conservation')end;assert(rec.debits==(t.weapon>=4 and 1 or 0)and rec.births==((t.weapon==7 or t.weapon==8)and 2 or(t.attacks or 1)),'Native projectile count and single debit');if t.weapon==7 then assert(rec.reflects==1,'Mirror really reflected native hostile projectile')elseif t.weapon==8 then assert(rec.splits>0,'Fresh second B really split existing blades without second debit')end end
   complete()
  end
 end
 assert(age<t.limit,'Finite component limit');event('update')
end)
-- Passive additive Mike draw->completed Main image->actual DMA->whole PPU log.
local D=assert(C.render_diagnostic)
local renderLog=assert(io.open(OUTPUT..'live-render.jsonl','w'))
local renderRows,renderBytes,renderDraws,renderDmas,renderFrames=0,0,0,0,0
local drawPending,drawsSinceFinish,lastDma=nil,{},nil
local recentImages={}
local captureStamp={}
local codec=dofile(D.codec)
local capture=codec.install(OUTPUT,{container_bytes=134217728,records=3000},function()return captureStamp end)
local full=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local function stamp()
 local s=emu.getState()
 return{ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']}
end
local function hexbytes(at,kind)
 local t={};for i=0,255 do t[#t+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)
end
local function emit(t)
 t.stamp=stamp();t.wall=wall;t.update=updates;t.case=index;t.phase=phase
 local line=json(t)..'\n';renderRows=renderRows+1;renderBytes=renderBytes+#line
 assert(renderRows<=12000 and renderBytes<=67108864 and #line<=16384,'Bounded passive render diagnostics')
 renderLog:write(line);renderLog:flush()
end
local function slots()
 local out={};for i=0,5 do out[#out+1]={slot=i,kind=r('JnShotKind',i),age=r('JnShotAge',i),hit=r('JnShotHit',i),x=r('JnShotX',i),page=r('JnShotPage',i),y=r('JnShotY',i),vx=r('JnShotVX',i)}end;return out
end
hook('RenderShotCall',function(s)
 if not entered then return end
 assert(not drawPending,'No recursive Mike shot renderer')
 local slot=s['cpu.x'];assert(slot>=0 and slot<6 and r('JnSavedY')==slot,'Actual native shot slot saved by JnDraw')
 local kind,age,vx=r('JnShotKind',slot),r('JnShotAge',slot),r('JnShotVX',slot)
 assert(kind>=1 and kind<=13,'Actual live source projectile kind')
 local pose=kind-1
 if vx>=128 or vx==0 and r('PlayerFacingDir')==2 then pose=pose+13 end
 if age&4~=0 then pose=pose+26 end
 local record=assert(D.records[pose+1]);local ptr=r('R0')+256*r('R1')
 assert(s['cpu.y']==pose and ptr==record.pointer and bank(0xc000)==record.bank,'Actual shot art table, pointer and physical C-bank owner')
 assert(emu.read(ptr,emu.memType.nesDebug)==record.header,'Actual compiled source shot record header')
 drawPending={event='actual-shot-draw',draw=renderDraws+1,case=index,name=C.plan[index].name,update=updates,slot=slot,kind=kind,age=age,pose=pose,record=ptr,record_bank=record.bank,header=record.header,
  x=r('R4'),page=r('R5'),y=r('R6'),cursor_before=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),rotation_active=r('GuestOamRotationActive'),before=hexbytes(0x200),writes={},entry=stamp()}
end)
emu.addMemoryCallback(function(at,value)
 if not drawPending then return end
 assert(#drawPending.writes<256,'At most complete source OAM page per shot draw')
 drawPending.writes[#drawPending.writes+1]={address=at,value=value,pc=emu.getState()['cpu.pc'],bank=bank(emu.getState()['cpu.pc'])}
end,emu.callbackType.write,0x200,0x2ff)
hook('RenderShotReturn',function()
 if not entered or not drawPending then return end -- Next is also the genuine empty-slot branch target.
 local p=drawPending
 assert(p.update==updates,'Same Main shot rendering continuation')
 p.cursor_after=r('CurrentOAMOffset');p.after=hexbytes(0x200);p.completed=stamp()
 renderDraws=renderDraws+1;drawsSinceFinish[#drawsSinceFinish+1]=p;emit(p);drawPending=nil
end)
hook('GameLoopFinish',function()
 if not entered then return end
 assert(not drawPending,'No unfinished shot call at completed Main')
 if #drawsSinceFinish>0 then
  local image={event='completed-Main-image-with-shot-draw',update=updates,source=hexbytes(0x200),draws=drawsSinceFinish,draw_ids={}}
  for _,d in ipairs(drawsSinceFinish)do image.draw_ids[#image.draw_ids+1]=d.draw end
  recentImages[#recentImages+1]=image;if #recentImages>8 then table.remove(recentImages,1)end
  emit({event=image.event,source=image.source,draw_ids=image.draw_ids});drawsSinceFinish={}
 end
end)
hook('DmaComplete',function()
 if not entered or not pending then return end
 assert(pending.writes==256,'Diagnostic records only actual complete256 DMA')
 local raw={};for _,v in ipairs(pending.source)do raw[#raw+1]=string.format('%02x',v)end;local source=table.concat(raw)
 local image
 for i=#recentImages,1,-1 do if recentImages[i].source==source then image=recentImages[i];break end end
 renderDmas=renderDmas+1
 local s=emu.getState();local chr={};for i=0,11 do chr[i+1]=s['mapper.chrBanks'..i]end
 local retained={}
 if image then
  for _,d in ipairs(image.draws)do
   local last={};for _,w in ipairs(d.writes)do last[w.address]=w.value end
   local bytes,match=0,true
   for at,v in pairs(last)do bytes=bytes+1;if pending.source[at-0x200+1]~=v then match=false end end
   retained[#retained+1]={draw=d.draw,case=d.case,kind=d.kind,slot=d.slot,source_written_bytes=bytes,all_written_bytes_retained=match}
  end
 end
 lastDma={event='actual-complete-DMA',epoch=renderDmas,source=source,physical=hexbytes(0,emu.memType.nesSpriteRam),
  completed_Main_update=image and image.update or nil,full_completed_Main_source_match=image~=nil,shots=retained,live_slots=slots(),chr=chr,stamp=stamp()}
 if phase=='weapon'or image then emit(lastDma)end
end)
emu.addEventCallback(function()
 if entered and(phase=='weapon'or lastDma and #lastDma.shots>0)then
  local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual full live-shot PPU image')
  local t={};for i,v in ipairs(screen)do t[i]=string.pack('<I4',v)end
  captureStamp={ppu=stamp(),case=index,phase=phase,last_actual_DMA=lastDma and lastDma.epoch or nil,Main_source_update=lastDma and lastDma.completed_Main_update or nil}
  full:write(table.concat(t));renderFrames=renderFrames+1
  emit({event='captured-whole-PPU',ordinal=renderFrames,last_actual_DMA=lastDma and lastDma.epoch or nil,Main_source_update=lastDma and lastDma.completed_Main_update or nil})
 end
 if done then
  full:close();capture.close()
  emit({event='passive-render-diagnostic-terminal',draws=renderDraws,actual_DMAs=renderDmas,whole_frames=renderFrames,
   limits='Draw emission and exact source-page DMA linkage are observed; opaque pixel/per-shot visibility requires offline whole-PPU analysis. Unmatched completed images are recorded without ownership invention.'})
  renderLog:close()
 end
end,emu.eventType.endFrame)

-- All callback registration is startup-static. No callback adds/removes callbacks.
local function bytes(at,kind)local t={};for i=0,255 do t[i+1]=emu.read(at+i,kind or emu.memType.nesDebug)end;return t end
local function equal(a,b)for i=1,256 do if a[i]~=b[i]then return false end end;return true end
local function smc()local t={};for i,a in ipairs(C.smc)do t[i]=emu.read(a,emu.memType.nesDebug)end;return t end
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function publicationWindow(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
hook('NmiEntry',function(s)
 assert(not nmi,'No recursive NMI')
 local sp=s['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
 nmi={a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],sp=sp,fields=smc(),ba=r('CurrentBank'),bc=r('CurrentBankC'),pa=bank(0xa000),pc=bank(0xc000)}
 nmi.wa=nmi.pa~=(nmi.ba&127)and publicationWindow(pc,0x5115,C.ram.CurrentBank)
 nmi.wc=nmi.pc~=(nmi.bc&127)and publicationWindow(pc,0x5116,C.ram.CurrentBankC);nmis=nmis+1
end)
hook('NmiReturn',function(s)
 assert(nmi and s['cpu.a']==nmi.a and s['cpu.x']==nmi.x and s['cpu.y']==nmi.y and s['cpu.sp']==nmi.sp,'NMI AXY/SP restored')
 for i,v in ipairs(smc())do assert(v==nmi.fields[i],'NMI five SMC operands restored')end
 assert(r('CurrentBank')==nmi.ba and r('CurrentBankC')==nmi.bc,'NMI bank shadows restored')
 assert(bank(0xa000)==(nmi.wa and(nmi.ba&127)or nmi.pa)and bank(0xc000)==(nmi.wc and(nmi.bc&127)or nmi.pc),'Actual foreground banks restored, including verified publication window');nmi=nil
end)
hook('IrqEntry',function()assert(not irq,'No nested IRQ');irq=true;if entered and r('Sprite0HitDetectFlag')~=0 then assert(emu.getState()['ppu.scanline']==31,'Actual HUD IRQ31');irqCount=irqCount+1 end end)
hook('IrqReturn',function()irq=false end)
emu.addMemoryCallback(function(_,v)mask=v end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 assert(not pending and mask&24==0,'Rendering disabled at actual DMA start')
 local s=emu.getState();assert(v==2 and s['cpu.pc']==C.dma_store_return,'Actual native page2 DMA owner')
 assert(s['ppu.spriteRamAddr']==0,'Actual native DMA begins at OAM address zero')
 pending={source=bytes(v*256),writes=0}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 assert(pending and mask&24==0,'Actual DMA byte while rendering disabled')
 local i=pending.writes+1
 assert(i<=256 and v==pending.source[i]and emu.getState()['ppu.spriteRamAddr']==i-1,'All256 raw DMA source/value/destination bytes match')
 pending.writes=i
end,emu.callbackType.write,0x2004)
hook('DmaComplete',function()
 if not pending then return end
 local hw=bytes(0,emu.memType.nesSpriteRam);local same=true
 for i=1,256 do local want=pending.source[i];if(i-1)%4==2 then want=want&0xe3 end;if hw[i]~=want then same=false end end
 assert(pending.writes==256 and mask&24==0 and emu.getState()['ppu.spriteRamAddr']==0 and same,'All256 physical OAM bytes match hardware attribute E3 semantics')
 pending=nil;dmas=dmas+1
end)
emu.addMemoryCallback(function(_,v)
 if entered and nmi and v&24~=0 then
  local s=emu.getState();local line,dot=s['ppu.scanline'],s['ppu.cycle'];enables=enables+1
  local safe=line>=241 and line<=260 or line==-1 and dot<=274
  if not safe then late=late+1 end;assert(safe,'Actual NMI render enable deadline')
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()if entered then assert(emu.getState()['cpu.sp']>=128,'Actual lower stack guard')end end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={};local t=C.plan[index]
 if t and(phase=='weapon'or phase=='empty')then b.b=age>=8 and age<12 or(t.weapon==8 and age>=20 and age<24)or(t.attacks==2 and age>=40 and age<44);b.up=t.super==true or phase=='empty'
 elseif t and phase=='select'then b.select=age>=4 and age<t.edges*10 and(age-4)%10<4 end
 if phase=='rest'and age>=4 then b.down=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 meaningful whole-frame PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<8000,'At most8000 physical frames')
 if done then
  assert(not pending and dmas>100 and nmis>100 and enables>100 and irqCount>100 and late==0,'Actual strict hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,mode=C.mode,records=records,updates=updates,wall=wall,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,PNGs=images,goal_complete=false,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
