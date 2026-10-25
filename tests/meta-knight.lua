-- Legacy NH health/block regression, updated to reject the removed flight.
-- New source moves/physical-food fixtures provide native-boundary coverage.
-- Controller selection followed by explicit component arenas. Not a level run.
local frame,wall=0,0
local selected,menuSeen=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function shot(tag)local f=assert(io.open(OUTPUT..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local trace=assert(io.open(OUTPUT..'components.csv','w'))
trace:write('frame,variant,health,action,age,float,x,y,pose,enemy,state,sfx\n')
local swordHits,pickups,nmis=0,0,0
local active,context=false,nil
local function actual(a)return emu.convertAddress(a).address//8192 end
emu.addMemoryCallback(function()
 context={a=actual(0xa000),c=actual(0xc000)};nmis=nmis+1
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 assert(context and actual(0xc000)==context.c,'NMI restores C graphics ownership')
 assert(actual(0xa000)==r('CurrentBank')%128,'NMI restores A ownership');context=nil
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if active and actual(0xa000)==B.MkWeapons then swordHits=swordHits+1 end
end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function(_,v)if active and v==0x20 then pickups=pickups+1 end end,emu.callbackType.write,L.Square2SoundQueue)
local function arena(y)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for _,name in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','StarInvincibleTimer','GuestInvulTicks','GuestHurtTicks','GuestHurtKind','PlayerChangeSizeFlag','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','Player_X_Speed','Player_Y_Speed','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer','KbFloat','KbHurt','KbHurtMove','KbAction','KbActionAge'})do w(name,0)end
 w('ScrollLock',1);w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',y or 176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_CollisionBits',3);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('GameEngineSubroutine',8);w('OperMode',1)
end
local function enemy(x,y)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',y or 184);w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',1);w('Enemy_X_Speed',0);w('Enemy_CollisionBits',0)
end
local function pickup(kind)
 arena();w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5);w('PowerUpType',kind,5);w('Enemy_BoundBoxCtrl',3,5);w('Enemy_X_Position',128,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
end
emu.addEventCallback(function()
 if not selected then
  local buttons={}
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then buttons.start=true
   elseif r('CrossoverMenuIndex')~=12 then buttons.down=true
   elseif r('KbVariant')~=1 then buttons.select=true
   elseif menuSeen then buttons.a=true end
  end
  emu.setInput(buttons,0);return
 end
 emu.setInput({start=frame==60,down=frame==90 or frame==110 or(frame>=1030 and frame<1050),select=frame==140,
 a=frame==210 or(frame>=940 and frame<950)or(frame>=970 and frame<1010),
 b=(frame>=660 and frame<715)or(frame>=750 and frame<775)or(frame>=830 and frame<850),
 right=frame>=1110 and frame<1190},0)
end,emu.eventType.inputPolled)
local floatSeen,healSeen=false,false
emu.addEventCallback(function()
 wall=wall+1
 if not selected then
  if r('CrossoverMenuState')==2 and r('SelectedCharacter')==13 and r('KbVariant')==1 then
   local text={}
   for i=0,15 do local t=emu.read(L.X5MenuNameAddress+i,emu.memType.nesPpuDebug);text[#text+1]=t>=10 and t<=35 and string.char(65+t-10)or' 'end
   if table.concat(text):find('META KNIGHT',1,true)then
    if not menuSeen then menuSeen=wall
    elseif wall-menuSeen>=3 then shot('menu')end
   end
  end
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then selected=true;frame=589
  else assert(wall<1800,'Controller entry timeout');return end
 end
 frame=frame+1
 if frame==175 then assert(r('SelectedCharacter')==13 and r('KbVariant')==1,'Select picks Meta Knight');shot('menu')end
 if frame==350 then shot('lives')end
 if frame==590 then assert(r('SelectedCharacter')==13 and r('KbVariant')==1 and r('GameEngineSubroutine')==8,'Controller starts Meta Knight');active=true end
 if frame==630 then shot('entry')end
 if frame==650 then arena();enemy(156)end
 if frame==672 then shot('sword')end
 if frame==725 then assert(swordHits>=1,'Sword defeats real Goomba');assert(r('KbMouth')==0 and r('KbCopy')==0,'Sword never inhales/copies')end
 if frame==740 then arena(112);w('Player_State',2);w('Block_Buffer_1',0xc1,121);w('Block_Buffer_1',0x54,122)end
 if frame==795 then assert(r('Block_Buffer_1',121)==0xc4,'Sword activates question block');assert(r('Block_Buffer_1',122)==0x54,'Adjacent protected terrain untouched');shot('block')end
 if frame==820 then arena();w('Block_Buffer_1',0x54,169)end
 if frame==870 then assert(r('Block_Buffer_1',169)==0x54,'Sword preserves ground/solid terrain')end
 if frame==880 then w('KbHealth',2);pickup(0)end
 if frame==892 then assert(r('KbHealth')==4 and r('KbCopy')==0 and r('Enemy_Flag',5)==0,'Mushroom heals two, no tier/copy')end
 if frame==900 then pickup(1)end
 if frame==915 then assert(r('KbHealth')==6 and r('KbCopy')==0,'Flower caps six health');assert(pickups>=2,'Both food pickups sound');healSeen=true end
 if frame==930 then arena()end
 if frame>=975 and frame<1010 and r('KbFloat')==1 then floatSeen=true end
 if frame==995 then shot('jump-no-flight')end
 if frame==1060 then assert(not floatSeen and r('KbFloat')==0,'Fresh air A cannot initiate flight');assert(r('KbMouth')==0 and r('KbCopy')==0,'Jump never inflates/copies')end
 if frame==1100 then arena()end
 if frame==1160 then shot('walk')end
 if frame%2==0 and frame>=590 then trace:write(table.concat({frame,r('KbVariant'),r('KbHealth'),r('KbAction'),r('KbActionAge'),r('KbFloat'),r('Player_X_Position'),r('Player_Y_Position'),r('KbPose'),r('Enemy_Flag'),r('Enemy_State'),r('Square1SoundQueue')},',')..'\n')end
 for hit=1,6 do
  local at=1240+(hit-1)*135
  if frame==at then if hit==1 then w('KbHealth',6)end;arena();enemy(132)end
  if frame==at+8 then
   assert(r('KbHealth')==6-hit,'Native health damage step '..hit)
   if hit==6 then assert(r('GameEngineSubroutine')==11,'Sixth health hit kills')
   else assert(r('GameEngineSubroutine')==8,'Nonlethal health damage stays playable');w('Enemy_Flag',0)end
  end
 end
 if frame==1940 then assert(healSeen and nmis>600,'Healing and sustained NMI coverage');trace:close();print('PASS Meta Knight: controller Select/name/preview, sword enemy and block contacts, protected terrain, health food/SFX, six-hit death, no flight, bank restoration');emu.stop(0)end
end,emu.eventType.endFrame)
