-- Read-only committed OAM and physical sprite-bank evidence for Roll.
return function(cfg)
 local frame,prepared,dma=0,nil,nil
 local expectedVisible=false
 local folder=cfg.out or OUTPUT
 local stream=assert(io.open(folder..'roll-body.csv','w'))
 local displacements=assert(io.open(folder..'roll-player-writes.csv','w'))
 displacements:write('frame,pc,bank,oldX,newX,y,state,blockAttack\n')
 stream:write('frame,pose,outline,facing,x,y,yHigh,star,banks,oam,palette\n')
 local pages={};local count=0
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(a)return emu.convertAddress(a).address//8192 end
 local function active()return r('SelectedCharacter')==9 and r('RlVariant')==1 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
 local function hex(start,n,kind)local s={}for i=0,n-1 do s[#s+1]=string.format('%02x',emu.read(start+i,kind))end;return table.concat(s)end
 emu.addMemoryCallback(function(_,v)
  if not active()then return end
  local old=r('Player_X_Position');local delta=(v-old+128)%256-128
  if math.abs(delta)>4 then
   local pc=emu.getState()['cpu.pc'];local physical=emu.convertAddress(pc)
   displacements:write(table.concat({frame,pc,physical.address//8192,old,v,r('Player_Y_Position'),r('Player_State'),r('MmBlockAttack')},',')..'\n');displacements:flush()
  end
 end,emu.callbackType.write,L.Player_X_Position)
 emu.addMemoryCallback(function()
  if bank(0xa000)==B.DrawAllMetasprites then
   prepared=nil
   expectedVisible=active()and r('ObjectMetasprite')~=0
  end
 end,emu.callbackType.exec,L.DrawAllMetasprites)
 local function observeBody(expectedBank)
  if not active()or bank(0xa000)~=expectedBank or bank(0xc000)~=B.RlArtBegin then return end
  local pointer=r('R0')+256*r('R1')
  if pointer<0xc000 then return end -- Private shots use a clipped RAM record.
  assert(pointer==r('SmPosePtr')+256*r('SmPosePtr',1),'Roll body uses the current source pose, never the legacy mask cache')
  prepared={r('RlPose'),r('PlayerOutlinesOff')==0 and 1 or 0,r('PlayerFacingDir'),r('R4')+256*r('R5'),r('R6'),r('R7'),r('StarInvincibleTimer')}
 end
 emu.addMemoryCallback(function()observeBody(B.MetaspriteRenderLoop)end,emu.callbackType.exec,L.MetaspriteRenderLoop)
 if L.RlFastRenderLoop then emu.addMemoryCallback(function()observeBody(B.RlFastRenderLoop)end,emu.callbackType.exec,L.RlFastRenderLoop)end
 emu.addMemoryCallback(function(_,page)
  dma=nil
  if not active()then return end
  -- A skipped catch-up may already have computed the next ObjectMetasprite.
  -- Its visibility does not describe the last completed OAM image.
  if expectedVisible then assert(prepared,'A visible Roll body actually reaches the source-pose renderer')end
  if prepared then dma={meta=prepared,oam=hex(page*256,256,emu.memType.nesDebug)}end
 end,emu.callbackType.write,0x4014)
 emu.addEventCallback(function()
  frame=frame+1
  if not dma then return end
  local st=emu.getState();local banks={}
  for i=0,7 do
   local page=assert(st['mapper.chrBanks'..i],'Actual sprite CHR bank')
   banks[#banks+1]=page
   if not pages[page]then
    local f=assert(io.open(folder..'roll-chr-'..page..'.bin','wb'))
    local data={}for a=0,1023 do data[#data+1]=string.char(emu.read(page*1024+a,emu.memType.nesChrRom))end
    f:write(table.concat(data));f:close();pages[page]=true
   end
  end
  stream:write(frame..','..table.concat(dma.meta,',')..','..table.concat(banks,':')..','..dma.oam..','..hex(0x3f00,32,emu.memType.nesPpuDebug)..'\n')
  count=count+1
  if count%60==0 then stream:flush()end
 end,emu.eventType.endFrame)
 return {finish=function()stream:close();displacements:close();assert(count>100,'Roll rendered-frame coverage');return count end}
end
