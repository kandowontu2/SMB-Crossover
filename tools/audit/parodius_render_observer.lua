-- Passive actual body records, committed DMA, CHR pages and palette.
return function(cfg)
 local folder=cfg.out or OUTPUT
 local frame,prepared,dma,updates,draws,count=0,nil,nil,0,0,0
 local pages={};local lastLag
 local f=assert(io.open(folder..'parodius-body.csv','w'))
 local hud=assert(io.open(folder..'parodius-hud.csv','w'));hud:write('frame,variant,world,level,dirty,tiles\n')
 f:write('frame,variant,pose,pool,x,y,yHigh,attr,updates,draws,lagNmis,banks,record,oam,palette\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(a)return emu.convertAddress(a).address//8192 end
 local function active()return r('SelectedCharacter')==18 and r('VvVariant')>0 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
 local function hex(a,n,kind)local s={}for i=0,n-1 do s[#s+1]=string.format('%02x',emu.read(a+i,kind))end;return table.concat(s)end
 emu.addMemoryCallback(function()
  if active()and bank(0xa000)==B.PnNativeFrameReady then updates=updates+1 end
 end,emu.callbackType.exec,L.PnNativeFrameReady)
 emu.addMemoryCallback(function()
  if bank(0xa000)==B.DrawAllMetasprites then prepared=nil;if active()then draws=draws+1 end end
 end,emu.callbackType.exec,L.DrawAllMetasprites)
 emu.addMemoryCallback(function()
  if not active()or bank(0xa000)~=B.MetaspriteRenderLoop then return end
  local ptr=r('R0')+256*r('R1')
  if ptr<0xc000 or ptr~=r('SmPosePtr')+256*r('SmPosePtr',1)then return end
  local length=emu.read(ptr,emu.memType.nesDebug)
  assert(length>0 and length%4==0,'Actual body record length')
  prepared={r('VvVariant'),r('PnFrame'),r('PnPool'),r('R4')+256*r('R5'),r('R6'),r('R7'),r('R3')}
  prepared.record=hex(ptr,length+1,emu.memType.nesDebug)
 end,emu.callbackType.exec,L.MetaspriteRenderLoop)
 emu.addMemoryCallback(function(_,page)
  dma=nil
  if active()and prepared then dma={meta=prepared,oam=hex(page*256,256,emu.memType.nesDebug)}end
 end,emu.callbackType.write,0x4014)
 emu.addEventCallback(function()
  frame=frame+1
  local lag=r('NmiSkipped');local increment=lastLag and(lag-lastLag)%256 or 0;lastLag=lag
  if active()and dma then
   if frame%60==0 then hud:write(table.concat({frame,r('VvVariant'),r('WorldNumber'),r('LevelNumber'),r('VvHudDirty'),hex(0x2022,28,emu.memType.nesPpuDebug)},',')..'\n')end
   local st=emu.getState();local banks={}
   for i=0,7 do
    local page=assert(st['mapper.chrBanks'..i]);banks[#banks+1]=page
    if not pages[page]then
     local out=assert(io.open(folder..'parodius-chr-'..page..'.bin','wb'))
     local data={}for a=0,1023 do data[#data+1]=string.char(emu.read(page*1024+a,emu.memType.nesChrRom))end
     out:write(table.concat(data));out:close();pages[page]=true
    end
   end
   f:write(frame..','..table.concat(dma.meta,',')..','..updates..','..draws..','..increment..','..table.concat(banks,':')..','..dma.meta.record..','..dma.oam..','..hex(0x3f00,32,emu.memType.nesPpuDebug)..'\n')
   count=count+1
  end
  updates,draws=0,0
 end,emu.eventType.endFrame)
 return{finish=function()f:close();hud:close();assert(count>100,'Actual body-frame coverage')end}
end
