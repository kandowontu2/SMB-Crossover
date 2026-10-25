-- Cold controller entry; seed solid terrain, never inject a death flag.
-- Observe actual animation calls, body records and completed DMA/CHR/palette.
local wall,t,entered,death,respawn,kills=0,0,false,false,false,0
local respawnAt,respawnY,respawnUpdates=nil,nil,0
local prepared,dma;local checks,bad,calls=0,0,0;local poses,pages,captured={},{},{}
local shotPose,shotAge=nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function hex(a,n,kind)local d={}for i=0,n-1 do d[#d+1]=string.format('%02x',emu.read(a+i,kind))end;return table.concat(d)end
local pending={}
local first=({122,68,236})[PN_VARIANT]
local last=({126,70,240})[PN_VARIANT]
local function w(n,v,i)pending[#pending+1]={assert(L[n],n)+(i or 0),v&255}end
local trace=assert(io.open(OUTPUT..'native-animation.csv','w'));trace:write('frame,animation,pose,delay,cursor\n')
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=B.Pnc98a or r('MmDeathFlag')==0 then return end
 calls=calls+1
 trace:write(table.concat({wall,r('PnAnimation'),r('PnFrame'),r('PnAnimDelay'),r('PnAnimCursor')},',')..'\n')
end,emu.callbackType.exec,L.Pnc98a)
emu.addMemoryCallback(function()
 if bank(0xa000)~=B.PnNativeFrameReady or not entered then return end
 if respawn then respawnUpdates=respawnUpdates+1 end
 for _,p in ipairs(pending)do emu.write(p[1],p[2],emu.memType.nesDebug)end;pending={}
end,emu.callbackType.exec,L.PnNativeFrameReady)
emu.addMemoryCallback(function()if entered and r('SelectedCharacter')==18 and r('GameEngineSubroutine')==8 then kills=kills+1 end end,emu.callbackType.exec,L.KillPlayer)
emu.addMemoryCallback(function()if bank(0xa000)==B.DrawAllMetasprites then prepared=nil end end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not entered or r('GameEngineSubroutine')~=11 or bank(0xa000)~=B.MetaspriteRenderLoop then return end
 local ptr=r('R0')+256*r('R1')
 if ptr~=r('SmPosePtr')+256*r('SmPosePtr',1)then return end
 local pose;for p=first,last do if ptr==L['PnDeathPose'..p]then pose=p end end
 assert(pose,'Death must use the original Parodius explosion record')
 local n=emu.read(ptr,emu.memType.nesDebug)
 prepared={pose=pose,record=hex(ptr,n+1,emu.memType.nesDebug),x=r('R4'),y=r('R6'),attr=r('R3')}
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function(_,page)
 dma=nil;if prepared then dma={meta=prepared,oam=hex(page*256,256,emu.memType.nesDebug)}end
end,emu.callbackType.write,0x4014)
local out=assert(io.open(OUTPUT..'death.csv','w'));out:write('frame,pose,bank,x,y,attr,record,oam,palette\n')
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
  else assert(wall<1600,'Real menu entry');return end
 end
 t=t+1
 if t==1 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
  w('PnX',80);w('PnY',96);w('PnXF',0);w('PnYF',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('ScrollLock',1);w('CheatInvincible',0);w('Block_Buffer_1',0x54,101)
 end
 if r('GameEngineSubroutine')==11 then death=true end
 if dma and r('GameEngineSubroutine')==11 then
  local page=emu.getState()['mapper.chrBanks0'];checks=checks+1;poses[dma.meta.pose]=true
  if page~=({892,956,1020})[PN_VARIANT]then bad=bad+1 end
  if not pages[page]then
   local f=assert(io.open(OUTPUT..'death-chr-'..page..'.bin','wb'));local d={}
   for i=0,1023 do d[#d+1]=string.char(emu.read(page*1024+i,emu.memType.nesChrRom))end
   f:write(table.concat(d));f:close();pages[page]=true
  end
  local m=dma.meta
  if shotPose==m.pose then shotAge=shotAge+1 else shotPose=m.pose;shotAge=0 end
  out:write(table.concat({wall,m.pose,page,m.x,m.y,m.attr,m.record,dma.oam,hex(0x3f00,32,emu.memType.nesPpuDebug)},',')..'\n')
  if shotAge>=2 and not captured[m.pose]then
   local f=assert(io.open(OUTPUT..'burst-'..m.pose..'.png','wb'));f:write(emu.takeScreenshot());f:close();captured[m.pose]=true
  end
 end
 if death and r('GameEngineSubroutine')==8 and not respawn then respawn=true;respawnAt=wall;respawnY=r('Player_Y_Position')end
 if respawn and wall-respawnAt>=60 then
  for p=first,last do assert(poses[p],'All native character death records must be drawn')end
  assert(kills==1 and checks>80 and calls>100,'Actual terrain death, native animation calls and sustained burst')
  assert(respawnUpdates>10 and r('Player_Y_Position')~=respawnY,'Actual post-respawn movement updates')
  assert(r('MmDeathFlag')==0 and r('PnActive')==128 and r('PnSkin')==PN_VARIANT,'Respawn restores live state: flag '..r('MmDeathFlag')..' active '..r('PnActive')..' skin '..r('PnSkin'))
  local colors=PN_VARIANT==1 and{0x15,0x08,0x21}or{0x30,0x21,0x03}
  for i,v in ipairs(colors)do assert(emu.read(0x3f10+i,emu.memType.nesPpuDebug)==v,'Respawn restores the live private palette')end
  out:close();trace:close()
  local f=assert(io.open(OUTPUT..'death-proof.json','w'));f:write(string.format('{"passed":%s,"variant":%d,"nativeTerrainKills":%d,"renderedFrames":%d,"mismatches":%d,"respawn":true}',tostring(bad==0),PN_VARIANT,kills,checks,bad));f:close()
  assert(bad==0,'Original death tiles must be committed with the corresponding body')
  print('PASS original character death poses, terrain death and movable respawn');emu.stop(0)
 end
 assert(t<1800,'Bounded death and respawn')
end,emu.eventType.endFrame)
