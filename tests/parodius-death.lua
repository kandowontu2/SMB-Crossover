-- Actual controller entry, then a solid-terrain component arena. No injected
-- death flags: the native terrain contact must call KillPlayer itself.
local wall,t,entered,death,respawn,kills=0,0,false,false,false,0
local prepared,dma,deathAt;local checks,bad=0,0;local poses={}
local captured={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local pending={}
local function w(n,v,i)pending[#pending+1]={assert(L[n],n)+(i or 0),v&255}end
emu.addMemoryCallback(function()
 if bank(0xa000)~=B.PnNativeFrameReady or not entered then return end
 for _,pair in ipairs(pending)do emu.write(pair[1],pair[2],emu.memType.nesDebug)end
 pending={}
end,emu.callbackType.exec,L.PnNativeFrameReady)
emu.addMemoryCallback(function()if entered and r('SelectedCharacter')==18 and r('GameEngineSubroutine')==8 then kills=kills+1 end end,emu.callbackType.exec,L.KillPlayer)
emu.addMemoryCallback(function()if bank(0xa000)==B.DrawAllMetasprites then prepared=nil end end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not entered or r('GameEngineSubroutine')~=11 or bank(0xa000)~=B.MetaspriteRenderLoop then return end
 local ptr=r('R0')+256*r('R1')
 if ptr==r('SmPosePtr')+256*r('SmPosePtr',1)then
  local pose
  for p=45,48 do if ptr==L['VvPose'..p]then pose=p end end
  assert(pose,'The existing ship death path must select a burst record')
  prepared={bank=256+r('SmChrBank'),pose=pose}
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()dma=prepared end,emu.callbackType.write,0x4014)
local out=assert(io.open(OUTPUT..'death.csv','w'));out:write('frame,elapsedVideo,pose,expected,actual\n')
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
 elseif respawn then b.up=true;b.a=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;t=0
  else assert(wall<1600,'Real Parodius menu entry');return end
 end
 t=t+1
 if t==1 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
  w('PnX',80);w('PnY',96);w('PnXF',0);w('PnYF',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('ScrollLock',1);w('CheatInvincible',0)
  w('Block_Buffer_1',0x54,101)
 end
 if r('GameEngineSubroutine')==11 then death=true;deathAt=deathAt or wall end
 if dma and r('GameEngineSubroutine')==11 then
  local actual=emu.getState()['mapper.chrBanks0'];checks=checks+1;poses[dma.pose]=true
  if actual~=dma.bank then bad=bad+1 end
  out:write(table.concat({wall,wall-(deathAt or wall),dma.pose,dma.bank,actual},',')..'\n')
  if not captured[dma.pose]then
   local shot=assert(io.open(OUTPUT..'burst-'..dma.pose..'.png','wb'));shot:write(emu.takeScreenshot());shot:close();captured[dma.pose]=true
  end
 end
 if death and r('GameEngineSubroutine')==8 then respawn=true end
 if respawn and t>250 then
  local flags={};for p=45,48 do assert(poses[p],'All existing ship burst poses must be drawn');flags[#flags+1]=p end
  assert(kills==1 and checks>20,'Actual native terrain death and rendered burst coverage')
  out:close()
  local result=assert(io.open(OUTPUT..'death-proof.json','w'))
  result:write(string.format('{"passed":%s,"variant":%d,"nativeTerrainKills":%d,"renderedFrames":%d,"mismatches":%d,"respawn":true}',tostring(bad==0),PN_VARIANT,kills,checks,bad));result:close()
  assert(bad==0,'Death burst uses matching graphics instead of live Parodius tiles')
  print('PASS terrain death, four burst poses, matching CHR, respawn');emu.stop(0)
 end
 assert(t<1800,'Bounded death and respawn')
end,emu.eventType.endFrame)
