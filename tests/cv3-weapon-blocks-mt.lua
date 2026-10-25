-- Controller menu/attack inputs; collision-buffer arena is explicitly injected.
local frame,phase,entered,arenaAt=0,0,nil,nil
local variant=CV3_VARIANT
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local stage=0;local chunks={};local noise={};local bumped={};local emerging=false;local spawnAt
local ctx;local nmis=0
local function bank(a)return emu.convertAddress(a).address//8192 end
emu.addMemoryCallback(function()ctx=bank(0xc000);nmis=nmis+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()assert(ctx and bank(0xc000)==ctx and r('CurrentBankC')%128==ctx);assert(bank(0xa000)==r('CurrentBank')%128);ctx=nil end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()chunks[stage]=(chunks[stage]or 0)+1 end,emu.callbackType.exec,L.SpawnBrickChunks)
emu.addMemoryCallback(function(_,v)if v~=0 then noise[stage]=true end end,emu.callbackType.write,L.NoiseSoundQueue)
local function arena(tile,foundation,nextTile)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i)end
 for i=0,3 do emu.write(0x5c20+i,0,emu.memType.nesDebug)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerStatus',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for _,n in ipairs({'InjuryTimer','StarInvincibleTimer','TimerControl','AreaParserTaskNum','ScrollThirtyTwo'})do w(n,0)end
 w('ScrollLock',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 emu.write(0x5c08,0,emu.memType.nesDebug);emu.write(0x5cc0,0,emu.memType.nesDebug)
 w('Block_Buffer_1',tile,167);w('MmSolidTerrain',foundation,167);w('Block_Buffer_1',nextTile,168)
end
emu.addEventCallback(function()
 local b={}
 if phase==0 then b.start=frame==60;if r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and frame%12==0 then
  if r('CrossoverMenuIndex')~=5 then b.right=true
  elseif r('Cv3Variant')~=variant then b.select=true
  else b.a=true;phase=2 end
 elseif arenaAt then local t=frame-arenaAt;b.b=t==20 or t==100 or t==200 or t==280 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=frame;phase=3 end
 if entered and not arenaAt and frame-entered==20 then arenaAt=frame;stage=1;arena(0x51,0,0xc1)end
 if arenaAt then
  local t=frame-arenaAt;local cell=r('Block_Buffer_1',167)
  if cell==0x23 then bumped[stage]=true end
  assert(r('Player_X_Position')==96 and r('Player_PageLoc')==0,'Attacks preserve native player X/page')
  if t==70 then
   assert(cell==0 and r('Block_Buffer_1',168)==0xc1,'Closest brick breaks; adjacent question stays intact')
   assert((chunks[1]or 0)>0 and noise[1],'Native brick debris and SFX execute')
   stage=2;arena(0xc1,0,0x51)
  end
  if stage==2 then for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
   if not spawnAt then spawnAt=t end
   if t==spawnAt+10 then assert(r('Enemy_State',i)<128 and r('PlayerStatus')==0,'Question produces an emerging physical item');emerging=true end
  end end end
  if t==175 then
   assert(bumped[2] and cell~=0x23 and cell~=0xc1 and emerging,'Question becomes native used cell and mushroom emerges')
   assert(r('Block_Buffer_1',168)==0x51,'Question activation does not destroy adjacent brick')
   stage=3;arena(0x52,1,0xc1)
  end
  if t==255 then
   assert(cell==0x52 and r('Block_Buffer_1',168)==0xc1,'Foundation rejects attack and protects block behind it')
   stage=4;arena(0x52,0,0xc1)
  end
  if t==345 then
   assert(cell==0 and r('Block_Buffer_1',168)==0xc1,'Ordinary underground brick breaks without affecting adjacent question')
   assert((chunks[4]or 0)>0 and noise[4],'Underground brick keeps native debris/SFX')
   assert(nmis>500,'Native interrupt rendering exercised')
   local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"passed":true,"variant":%d,"frames":%d,"nmis":%d,"debrisCalls":%d,"questionEmergence":true,"foundationProtected":true}\n',variant,frame,nmis,(chunks[1]or 0)+(chunks[4]or 0)));f:close()
   print('PASS CV3 variant'..variant..' controller attacks, precise bricks/questions, native debris/SFX and protected foundation');emu.stop(0)
  end
 end
 if frame>1800 then error('Menu/attack fixture timed out')end
end,emu.eventType.endFrame)

