-- Read-only matching of the last constructed player OAM and hardware CHR.
return function(cfg)
 local folder=cfg.out or OUTPUT
 local target=cfg.character or TARGET_CHARACTER
 local frame,prepared,displayed,inside=0,nil,nil,nil
 local returns={};local rows,bad,draws=0,0,0
 local f=assert(io.open(folder..'chr-commit.csv','w'))
 f:write('frame,pose,expected0,actual0,expected6,actual6,expected7,actual7,newDraw,bad\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(a)return emu.convertAddress(a).address//8192 end
 local function active()return r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==target end
 local function physical(window)
  local mode=r('X5ChrMode',window)
  if mode&128~=0 then return r('CurrentCHRBank',window)+256*(mode&3)end
  -- Samus remains a legacy logical CHR consumer. This is the frozen actual
  -- ChrPhysicalMap used by both legacy and mixed-wide publication paths.
  return assert(cfg.legacy_map[r('CurrentCHRBank',window)+1])
 end
 emu.addMemoryCallback(function()
  if bank(0xa000)==B.DrawAllMetasprites then prepared=nil end
 end,emu.callbackType.exec,L.DrawAllMetasprites)
 emu.addMemoryCallback(function()
  if not active()or bank(0xa000)~=B.DrawMetasprite then return end
  local state=emu.getState();if state['cpu.y']~=0 then return end
  local sp=state['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  inside={pc=pc,sp=(sp+2)%256}
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if inside and inside.pc==pc and emu.getState()['cpu.sp']==inside.sp then inside=nil end
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,L.DrawMetasprite)
 emu.addMemoryCallback(function()
  if not active()or not inside or bank(0xa000)~=B.MetaspriteRenderLoop then return end
  assert(r('CurrentCHRBank')==r('SmChrBank'),'Player publishes its matching physical page before building body sprites')
  local pose=r('SmPosePtr')+256*r('SmPosePtr',1)
  prepared={pose=pose,bank0=physical(0),bank6=-1,bank7=-1,draw=draws}
  if target==18 and r('VvVariant')~=0 then prepared.bank6=physical(6);prepared.bank7=physical(7)end
  draws=draws+1
 end,emu.callbackType.exec,L.MetaspriteRenderLoop)
 emu.addMemoryCallback(function(_,page)
  displayed=nil
  if not active()or not prepared then return end
  local body=false
  for slot=0,63 do
   local at=page*256+slot*4;local y=emu.read(at,emu.memType.nesDebug);local tile=emu.read(at+1,emu.memType.nesDebug)
   if y>=31 and y<239 and tile<64 and tile&1==0 then body=true;break end
  end
  if body then displayed=prepared end
 end,emu.callbackType.write,0x4014)
 local lastDraw=-1
 emu.addEventCallback(function()
  frame=frame+1
  if not active()or not displayed then return end
  local state=emu.getState();local a,b,c=state['mapper.chrBanks0'],state['mapper.chrBanks6'],state['mapper.chrBanks7']
  local wrong=a~=displayed.bank0 or(displayed.bank6>=0 and(b~=displayed.bank6 or c~=displayed.bank7))
  local new=displayed.draw~=lastDraw;lastDraw=displayed.draw
  rows=rows+1;if wrong then
   bad=bad+1
   if bad<=8 then local out=assert(io.open(folder..'mismatch-'..frame..'.png','wb'));out:write(emu.takeScreenshot());out:close()end
  end
  f:write(table.concat({frame,displayed.pose,displayed.bank0,a,displayed.bank6,b,displayed.bank7,c,new and 1 or 0,wrong and 1 or 0},',')..'\n')
 end,emu.eventType.endFrame)
 return{failure=function()return bad>0 and'Player CHR differs from last constructed OAM image'or nil end,finish=function()
  f:close();assert(rows>40 or bad>0,'Actual committed player-frame coverage')
  local out=assert(io.open(folder..'chr-commit.json','w'))
  out:write(string.format('{"passed":%s,"frames":%d,"mismatched_frames":%d,"body_constructions":%d,"scope":"Read-only actual hardware CHR pages versus last DMA player image. Bounded natural controller movement, no full-level or pixel-comparison claim."}',tostring(bad==0),rows,bad,draws));out:close()
 end}
end
