-- Controller entry, then a disclosed collision-buffer block fixture.
-- The inserted collision cell has no matching nametable/attribute artwork.
local f,phase,entered,arenaAt=0,0,nil,nil
local who=TARGET=='darkwing' and 12 or 4
local slot=TARGET=='darkwing' and 8 or 4
local variant=TARGET=='darkwing' and 'DarkwingVariant' or 'Z2Variant'
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local spawned,emerging,bumped,replaced=false,false,false,false
local trace=assert(io.open(OUTPUT..'blocks.csv','w'));trace:write('frame,x,y,cell,state0,state1,rep0,rep1,vram,pickupstate,pickupy\n')
emu.addEventCallback(function()
 local b={}
 if phase==0 then b.start=f==60;if r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and f%12==0 then
  if r('CrossoverMenuIndex')//6~=slot//6 then b.down=true
  elseif r('CrossoverMenuIndex')~=slot then b.right=true
  elseif r(variant)~=1 then b.select=true
  else b.a=true;phase=2 end
 elseif arenaAt then local t=f-arenaAt;b.a=t>=20 and t<58 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if phase==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then phase=3;entered=f end
 if entered and not arenaAt and f-entered==20 then
  arenaAt=f
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerStatus',0)
  w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  for _,n in ipairs({'InjuryTimer','StarInvincibleTimer','TimerControl','AreaParserTaskNum','ScrollThirtyTwo'})do w(n,0)end
  w('ScrollLock',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
  w('Block_Buffer_1',0xc1,134);w('MmSolidTerrain',1,134)
 end
 if arenaAt then
  local t=f-arenaAt;local cell=r('Block_Buffer_1',134)
  if cell==0x23 then bumped=true end
  if bumped and cell~=0x23 and cell~=0xc1 then replaced=true end
  local state,y=-1,-1
  for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
   state=r('Enemy_State',i);y=r('Enemy_Y_Position',i)
   if not spawned then spawned=t end
   if t==spawned+10 then assert(state<128 and r('PlayerStatus')==0,'Head bump produces an emerging physical item, not auto-pickup');emerging=true end
  end end
  assert(r('Player_X_Position')==96,'Head hit preserves world X')
  trace:write(table.concat({f,96,r('Player_Y_Position'),cell,r('Block_State'),r('Block_State',1),r('Block_RepFlag'),r('Block_RepFlag',1),r('VRAM_Buffer1_Offset'),state,y},',')..'\n')
  if t==180 then
   assert(spawned and emerging,'Physical mushroom emerges')
   assert(bumped and replaced,'Native deferred replacement clears bumped cell')
   assert(r('Block_RepFlag')==0 and r('Block_RepFlag',1)==0,'No permanently pending block replacement')
   trace:close();print('PASS '..TARGET..' head block publishes, mushroom emerges and player X is stable');emu.stop(0)
  end
 end
 if f>1600 then error('Menu/arena timed out')end
end,emu.eventType.endFrame)
