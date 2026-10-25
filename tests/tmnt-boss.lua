-- Seeded native boss-defeat component; equipment/projectiles here are injected.
-- This proves native hit/defeat counter policy, never equipment collection.
local C=assert(TMNT_CFG);local f=0;local phase=C.mode=='hard'and'options-focus'or'start';local entry=nil;local base=nil;local defeated=false;local hit=false;local done=0;local spawned=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function k(a)return emu.read(a,emu.memType.nesDebug)end
local function put(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local out=assert(io.open(TEST_DIR..'boss.csv','w'));out:write('frame,case,age,hit,kind,counter,enemyState,bowserHP\n')
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

emu.addMemoryCallback(function()if base and bank(L.TnAllWeapons)==B.TnAllWeapons then hit=true end end,emu.callbackType.exec,L.HandleEnemyFBallCol)
local function target(x,y)
 w('Enemy_Flag',1);w('Enemy_ID',0x2d);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',y);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_MovingDir',2);put(0x5c38,0x2e);put(0x5c30,1);w('BowserHitPoints',1);w('DuplicateObj_Offset',3)
end
emu.addEventCallback(function()
 if not entry then emu.setInput(menu(),0);return end
 local n=base and (f-base)//80 or -1;local a=base and (f-base)%80 or -1
 emu.setInput({b=n==0 and a==4},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if not entry and r('SelectedCharacter')==19 and r('GameEngineSubroutine')==8 and r('OperMode')==1 and r('OperMode_Task')==3 then entry=f;assert(r('TnVariant')==C.variant,'identity')end
 if entry and not base and f>=entry+30 then base=f end
 if base then
  local n=(f-base)//80;local a=(f-base)%80
  if n>=5 then assert(done==5,'all five real native boss defeats');out:close();local h=assert(io.open(TEST_DIR..'result.json','w'));h:write(string.format('{"passed":true,"variant":%d,"mode":"%s","native_defeats":%d,"seeded_boss_projectile_components":true}',C.variant,C.mode,done));h:close();print('PASS native boss counter');emu.stop(0);return end
  if a==0 then arena(128,false,1);w('TnDropCounter',23);hit=false;spawned=false;defeated=false end
  if n==0 and not spawned and r('TnAttack')>0 and k(0x5c77)>0 and k(0x5c73)>=2 then target(k(0x5c20)-8,k(0x5c22)-8);spawned=true end
  if n>0 and a==2 then target(112,176);w('TnShotKind',n);w('TnShotX',120);w('TnShotPage',0);w('TnShotY',184);put(0x5c80,1);spawned=true end
  if hit and r('TnDropCounter')==0 and r('BowserHitPoints')==0 and(r('Enemy_State')&0x20)~=0 then defeated=true end
  if a==65 then
   assert(hit and spawned,'actual native Bowser handler reached');assert(defeated and r('TnDropCounter')==0 and r('BowserHitPoints')==0,'actual mapped boss defeat/reset');for i=0,3 do assert(r('TnDropKind',i)==0,'boss gives no ordinary drop')end;done=done+1
  end
  out:write(table.concat({f,n,a,hit and 1 or 0,n,r('TnDropCounter'),r('Enemy_State'),r('BowserHitPoints')},',')..'\n');out:flush()
 end
 assert(f<1400,'boss component timeout')
end,emu.eventType.endFrame)
