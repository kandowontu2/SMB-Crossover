-- Explicit accepted-property arenas, never gameplay traversal evidence.
-- Ordinary controller B/Select creates each attack. Existing target effects
-- are seeded at the actual collision boundary to test replacement ordering.
local character=assert(SOURCE_EFFECT_CHARACTER)
local frame,depth,index,age=0,0,1,-1
local attempted,accepted,stopChecked=false,false,false
local cases={}
for _,spec in ipairs({
 {name='ordinary',id=6}, {name='armored',id=2,immune=true},
 {name='hostile-projectile',id=12,immune=true},
 {name='Lakitu-STOP-resistance',id=17,resist=true},
 {name='Bowser-STOP-resistance',id=45,resist=true},
 {name='killed-removes-effects',id=6,hp=50,killed=true},
 {name='new-valid-attack-during-FLASH',id=6,flash=16},
})do cases[#cases+1]=spec end
if character~=10 then for _,spec in ipairs({
 {name='replace-short-STOP',id=6,seed=8,flash=6,freeze=true},
 {name='reject-equal-STOP',id=6,seed=24,flash=6,freeze=true},
 {name='reject-shorter-STOP',id=6,seed=100,flash=6,freeze=false},
})do cases[#cases+1]=spec end end
if character==4 then
 for _,spec in ipairs({
  {name='boomerang-ordinary',id=6,boom=true},
  {name='boomerang-pierces-armor',id=2,boom=true},
  {name='boomerang-excludes-projectile',id=12,boom=true,immune=true},
  {name='boomerang-Lakitu-resistance',id=17,boom=true,resist=true},
  {name='boomerang-Bowser-resistance',id=45,boom=true,resist=true},
  {name='boomerang-replaces-freeze-removes-FLASH',id=6,boom=true,seed=24,flash=6,freeze=true},
  {name='boomerang-equal-STOP-preserves-FLASH',id=6,boom=true,seed=180,flash=6,freeze=false},
  {name='boomerang-shorter-STOP-preserves-FLASH',id=6,boom=true,seed=200,flash=6,freeze=false},
 })do cases[#cases+1]=spec end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced property-fixture interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()
 local c=cases[index]
 local choosing=character<6 and frame>=80 and frame<80+20*character and frame%20==0 or character==10 and frame>=100 and frame<180 and frame%20==0
 local attack=age>=10 and age<14
 emu.setInput({right=choosing,down=character==10 and(frame==80 or age>=0),start=frame==240,b=attack and not c.boom,select=attack and c.boom or false},0)
end,emu.eventType.inputPolled)
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('RgEnemyStun',0,i);w('MmEnemyFlash',0,i);w('LsrFrozenPose',0,i)end
 for i=0,9 do w('RgShotType',0,i);w('RgShotHits',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('Player_State',0);w('PlayerStatus',1);w('PlayerSize',0);w('InvOwnedLo',1,character);w('InvOwnedHi',0,character);w('InvSelected',0,character)
 w('PlayerFacingDir',1);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('InjuryTimer',255)
 w('RgAttack',0);w('RgAttackAge',0);w('RgAttackKind',0);w('RgMeleeHits',0);w('RgThrust',0);w('RgThrustReset',0);w('RgCrouch',0);w('RgPreviousButtons',r('SavedJoypadBits'));w('RgCooldown',0);w('AvSlash',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestPowerupActive',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 local c=cases[index];local hp=c.hp or 500
 w('Enemy_Flag',1);w('Enemy_ID',c.id);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',c.boom and 132 or 116);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0);w('Enemy_MovingDir',1)
 w('EnemyFrameTimer',90);w('EnemyIntervalTimer',11)
 w('MmEnemyHealthLo',hp%256);w('MmEnemyHealthHi',hp//256)
 if c.id==45 then
  w('DuplicateObj_Offset',5);w('Enemy_Flag',0x80,5);w('Enemy_ID',45,5);w('Enemy_Y_HighPos',1,5)
  w('BowserOrigXPos',116);w('BowserFireBreathTimer',255);w('BowserBodyControls',0);w('BowserMovementSpeed',0);w('BowserFeetCounter',32)
 end
 age=0;attempted=false;accepted=false;stopChecked=false
end
emu.addMemoryCallback(function()
 if age<10 or not bank(8)or r('MmEnemySlot')~=0 then return end
 local c=cases[index]
 assert(not attempted,'Exactly one actual collision enters the property arena: '..c.name)
 attempted=true
 -- These are isolated property-boundary initial conditions, not ROM/CPU or
 -- controller patches. They model an already active target status effect.
 w('RgEnemyStun',c.seed or 0);w('MmEnemyFlash',c.flash or 0)
 w('LsrFrozenPose',c.freeze and assert(L.METASPRITE_GOOMBA_WALKING_1)or 0)
end,emu.callbackType.exec,assert(L.DamageEnemy))
emu.addMemoryCallback(function()
 if not attempted or not bank(61)then return end
 local c=cases[index];local duration=c.boom and 3000/(1000/60)or 400/(1000/60)
 local replace=(c.seed or 0)<duration
 assert(not c.resist and not c.immune and not c.killed,'Only a susceptible surviving target reaches completed STOP application')
 assert(r('RgEnemyStun')==(replace and duration or c.seed),'Source strictly-greater STOP replacement: '..c.name)
 assert(r('MmEnemyFlash')==(replace and 0 or(c.flash or 0)),'Accepted STOP removes old FLASH; rejected STOP preserves it: '..c.name)
 assert((r('LsrFrozenPose')~=0)==(replace and not c.boom or not replace and(c.freeze or false)),'STOP stopAnim property is replaced independently: '..c.name)
 stopChecked=true
end,emu.callbackType.exec,assert(L.LsrEffectsApplyStopFinish))
emu.addMemoryCallback(function()
 if attempted and bank(B.LsrEffectsAcceptedHitFinish)then accepted=true end
end,emu.callbackType.exec,assert(L.LsrEffectsAcceptedHitFinish))
local finish=character==10 and L.ExpandedWeaponsFinish or L.RosterWeaponsFinish
emu.addMemoryCallback(function()
 if not attempted or not bank(character==10 and 37 or 8)then return end
 local c=cases[index];local sourceStop=character==10 and 0 or(c.boom and 180 or 24)
 local stop=sourceStop
 -- Spell out property acceptance instead of deriving the oracle from ROM.
 if c.immune or c.resist or c.killed then stop=0 elseif c.seed and c.seed>=sourceStop then stop=c.seed end
 local flash
 if c.immune or c.killed then flash=0
 elseif c.boom or character==5 then
  local replaced=not c.resist and(c.seed or 0)<sourceStop
  flash=replaced and 0 or(c.flash or 0)
 else flash=24 end
 assert(r('RgEnemyStun')==stop,'Final source STOP property '..c.name..': '..r('RgEnemyStun')..' expected'..stop)
 assert(r('MmEnemyFlash')==flash,'Final source FLASH property '..c.name..': '..r('MmEnemyFlash')..' expected'..flash)
 assert(accepted==(not c.immune and not c.boom and not c.killed),'Only surviving pierced damage dispatches DEFAULT_PROPS: '..c.name)
 if not c.resist and not c.immune and not c.killed and character~=10 then assert(stopChecked,'STOP replacement ordering was independently observed: '..c.name)end
 if c.killed then assert(r('Enemy_State')&32~=0 or r('Enemy_Flag')==0,'Killed enemy removes all effects')
 else
  local expectedHP=(c.hp or 500)-((c.immune or c.boom)and 0 or 75)
  assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==expectedHP,'Actual source damage/piercing: '..c.name)
 end
 print('PASS effect property c'..character..' '..c.name)
 w('Enemy_Flag',0);w('Enemy_Flag',0,5) -- End the explicit arena before native boss AI.
 index=index+1;age=-1;attempted=false
 if not cases[index]then print('PASS '..#cases..' source accepted-effect, armor, resistance, replacement, flash admission and death arenas c'..character);emu.stop(0)end
end,emu.callbackType.exec,assert(finish))
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==character,'Real menu launches property fixture character'..character);setup()
 elseif frame>550 then
  if age<0 then setup()else
   age=age+1
   if not attempted then
    local c=cases[index]
    -- Stationary authored contact target; natural weapons and their hitboxes
    -- still have to reach it. Bowser/Lakitu AI is outside this effect arena.
    w('Enemy_X_Position',c.boom and 132 or 116);w('Enemy_Y_Position',176)
    w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
   end
   assert(age<90,'Actual controller attack reaches source property arena: '..cases[index].name..' engine'..r('GameEngineSubroutine')..' id'..r('Enemy_ID')..' flag'..r('Enemy_Flag')..' state'..r('Enemy_State')..' player'..r('Player_X_Position')..'/'..r('Player_Y_Position')..' crouch'..r('RgCrouch')..' attack'..r('RgAttack'))
  end
 end
 assert(frame<2600,'All bounded effect-property arenas complete')
end,emu.eventType.endFrame)
