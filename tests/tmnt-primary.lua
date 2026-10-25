-- TMNT NW native component arena. Cold actual menus select one identity/mode.
-- After entry only, player/terrain-actor health/item RAM is seeded for bounded
-- primary/food/contact/death components. Not a route or natural collection proof.
-- Equipment is never seeded here and no equipment collection is claimed.
local C=assert(TMNT_CFG);local f=0;local phase=C.mode=='hard'and'options-focus'or'start';local entry=nil
local base=nil;local current=nil;local cases={};local killCount=0;local sounds=0;local healed=0;local deathFrame=nil;local initialLives=nil
local expected={{0x90,0x99,0x96,0x93},{0x91,0x9a,0x97,0x94},{0x92,0x9b,0x98,0x95}}
local damage={7,10,9,9,7,12,15,16}
for hpIndex,hp in ipairs({128,32})do for d=0,2 do for face=1,2 do cases[#cases+1]={hp=hp,d=d,face=face,air=false,expected=damage[C.variant*2+hpIndex],seen=false,hit=false,killed=false,spawned=false}end end end
for d=0,2 do for face=1,2 do cases[#cases+1]={hp=128,d=d,face=face,air=true,expected=damage[C.variant*2+1],seen=false,hit=false,killed=false,spawned=false}end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function k(a)return emu.read(a,emu.memType.nesDebug)end
local function put(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function screen(n)local h=assert(io.open(TEST_DIR..n..'.png','wb'));h:write(emu.takeScreenshot());h:close()end
local out=assert(io.open(TEST_DIR..'native.csv','w'));out:write('frame,age,case,variant,mode,hp,bodyseq,weaponseq,phase,pose,attack,hurt,enemyhp,enemyflag,enemystate,engine,lives,gear,ammo\n')
local function actualBank(pc)local p=emu.convertAddress(pc,emu.memType.nesMemory);return p and p.address and math.floor(p.address/8192)or-1 end
emu.addMemoryCallback(function()if current and actualBank(L.TnWeapons)==B.TnWeapons and k(0x5c0d)>0 then current.killed=true;killCount=killCount+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function(a,v)if base and v==0x20 then sounds=sounds+1 end end,emu.callbackType.write,L.Square2SoundQueue)
emu.addMemoryCallback(function()if base and actualBank(L.TnHeal)==B.TnHeal then healed=healed+1 end end,emu.callbackType.exec,L.TnHeal)
local function menu()
 if f<60 or f%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2
 if row~=2 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end
local function arena(hp,air,face)
 for a=0x5c00,0x5cff do put(a,0)end
 put(0x5c70,0x80);put(0x5c74,6);put(0x5c76,9);put(0x5c07,8);put(0x5c0b,0xff);put(0x5c10,120)
 w('TnHealth',hp,C.variant);w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',air and 128 or 176);w('Player_Y_HighPos',1)
 w('Player_State',air and 2 or 0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',face);w('InjuryTimer',0);w('GameEngineSubroutine',8);w('TimerControl',0)
 for i=0,5 do w('Enemy_Flag',0,i)end
end
local function target(c)
 w('Enemy_Flag',1,0);w('Enemy_ID',0,0);w('Enemy_State',0,0);w('Enemy_BoundBoxCtrl',9,0)
 local x=k(0x5c20)+256*k(0x5c21)-8
 w('Enemy_X_Position',x%256,0);w('Enemy_PageLoc',math.floor(x/256),0);w('Enemy_Y_Position',k(0x5c22)-8,0);w('Enemy_Y_HighPos',1,0)
 w('Enemy_X_Speed',0,0);w('Enemy_Y_Speed',0,0);w('Enemy_CollisionBits',0,0);w('Enemy_MovingDir',2,0)
 c.spawned=true
end
local function contact(hp)
 arena(hp,false,1);put(0x5c10,0);put(0x5c11,0)
 w('Enemy_Flag',1,0);w('Enemy_ID',6,0);w('Enemy_State',0,0);w('Enemy_X_Position',84,0);w('Enemy_PageLoc',0,0);w('Enemy_Y_Position',184,0);w('Enemy_Y_HighPos',1,0)
 w('Enemy_X_Speed',0,0);w('Enemy_Y_Speed',0,0);w('Enemy_BoundBoxCtrl',9,0);w('Enemy_MovingDir',2,0);w('Enemy_CollisionBits',0,0)
end
local function food(kind,hp)
 arena(hp,false,1)
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5);w('Enemy_X_Position',84,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('PowerUpType',kind,5);w('InvPickup',0xfc,5);w('InvRisePhase',0,5)
end
emu.addEventCallback(function()
 if not base then emu.setInput(entry and{}or menu(),0);return end
 local n=(f-base)//64+1;local a=(f-base)%64;local c=cases[n]
 emu.setInput({b=c and a==4,up=c and c.d==0,down=c and c.d==2},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if not entry and r('SelectedCharacter')==19 and r('GameEngineSubroutine')==8 and r('OperMode')==1 and r('OperMode_Task')==3 then
  assert(r('TnVariant')==C.variant,'actual cold-menu identity');assert(r('CrossoverBehaviorVersion')==(C.mode=='hard'and 1 or 0),'actual cold-menu mode')
  entry=f;initialLives=r('NumberofLives');screen('cold-entry')
 end
 if entry and not base and f>=entry+30 then base=f end
 if base then
  local age=f-base;local n=age//64+1;local a=age%64;local c=cases[n]
  if c then
   if a==0 then
    if current then assert(current.seen and current.hit and current.spawned,'previous real primary contact')end
    current=c;arena(c.hp,c.air,c.face)
   end
   if r('TnAttack')>0 and r('TnSeq')==expected[c.d+1][C.variant+1]then c.seen=true;assert(r('TnSeq',1)==r('TnSeq')+12,'native paired weapon sequence')end
   if not c.spawned and k(0x5c77)>0 and k(0x5c73)>=2 then target(c)end
   if not c.hit and (k(0x5c0e)&1)~=0 then
    c.hit=true;assert(k(0x5c25)==c.expected,'identity/health source damage')
    if c.expected<14 then assert(k(0x5c30)==14-c.expected,'actual native target HP subtraction')else assert(c.killed,'actual native ShellOrBlockDefeat')end
    screen('primary-'..n)
   end
  else
   current=nil;local h=age-#cases*64
   if h==0 then for _,q in ipairs(cases)do assert(q.seen and q.hit and q.spawned,'all primary cases')end;food(0,64)end
   if h==20 then assert(r('TnHealth',C.variant)==96,'physical seeded mushroom heals32');food(1,96)end
   if h==40 then assert(r('TnHealth',C.variant)==128,'physical seeded flower heals64 capped128');food(1,128)end
   if h==60 then assert(r('TnHealth',C.variant)==128 and sounds>=3 and healed>=3,'physical capped food and pickup SFX queues');contact(128)end
   if h==70 then assert(r('TnHealth',C.variant)==112 and r('TnHurt')>0,'native real contact damage16 and protection');screen('contact-protection')end
   if h==95 then assert(r('TnHealth',C.variant)==112,'protection holds HP')end
   if h==110 then contact(16)end
   if h>=110 and not deathFrame and r('GameEngineSubroutine')==11 then deathFrame=f;assert(r('TnHealth',C.variant)==0,'native health death');screen('death')end
   if deathFrame and r('NumberofLives')==initialLives-1 and r('GameEngineSubroutine')==8 then
    assert(r('TnHealth',C.variant)==128,'native life loss/respawn restores selected turtle');screen('respawn')
    out:close();local z=assert(io.open(TEST_DIR..'result.json','w'));z:write(string.format('{"passed":true,"variant":%d,"mode":%q,"entry":%d,"frame":%d,"primary_cases":%d,"food_handler_calls":%d,"pickup_sound_queues":%d,"native_kills":%d,"death_frame":%d,"respawn_hp":128,"scope":"Explicit component arena after real menu. No equipment collection or campaign-clear claim."}\n',C.variant,C.mode,entry,f,#cases,healed,sounds,killCount,deathFrame));z:close();print('PASS identity-specific TMNT primary/food/contact/protection/death/respawn native components');emu.stop(0);return
   end
  end
  out:write(table.concat({f,age,n,C.variant,C.mode,r('TnHealth',C.variant),r('TnSeq'),r('TnSeq',1),r('TnPhase',1),r('TnPose',1),r('TnAttack'),r('TnHurt'),k(0x5c30),r('Enemy_Flag'),r('Enemy_State'),r('GameEngineSubroutine'),r('NumberofLives'),r('TnEquipment',C.variant),r('TnAmmo',C.variant)},',')..'\n')
 end
 assert(f<3200,'bounded component runtime')
end,emu.eventType.endFrame)
