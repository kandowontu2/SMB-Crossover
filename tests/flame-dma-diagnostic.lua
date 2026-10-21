-- Read-only observations of DMA/PPU state after an explicit native1-2 arena
-- setup. Controller B creates all seeds; no OAM/CHR/PPU or CPU patches.
local frame,age=0,0
local drawing,parts,ready,dma=false,{},nil,false
local total,bad,shots,visible=0,0,0,0
local csv=assert(io.open(OUTPUT..ROM_NAME..'-flame-dma.csv','w'))
csv:write('frame,phase,dma,parts,chr_errors,oam_errors,ss_active,ss_physical,nt_changes,shots,arts\n')
local binary=assert(io.open(OUTPUT..ROM_NAME..'-flame-dma.bin','wb'))
local previousNt
local screenshots=0
local sampled={}
local samples={}
local screenshotPending=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
local mmc5=ROM_NAME:find('mmc5')~=nil
local function ppu(a,state)
 if mmc5 and a<8192 then return emu.read(assert(state['mapper.chrBanks'..(a//1024)])*1024+a%1024,emu.memType.nesChrRom)end
 return emu.read(a,emu.memType.nesPpuDebug)
end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or(frame>=550 and age<180),left=frame>=550 and age>=180 and age<220,
  start=frame==200,b=frame>=550 and age%12<6},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<550 or r('CurrentBank')%128~=60 then return end
 drawing=true;parts={}
 -- SsChrPhysical is captured after the actual runtime family selection.
end,emu.callbackType.exec,L.SpecialDrawShots)
emu.addMemoryCallback(function()
 if not drawing or r('CurrentBank')%128~=4 then return end
 local slot=r('RgSlot');local typ=r('RgShotType',slot)
 if typ~=15 and typ~=16 then return end
 local ptr=r('R0')+256*r('R1');local count=emu.read(ptr,emu.memType.nesDebug)
 local start=r('CurrentOAMOffset');if start+count>=256 then return end
 local art=r('SsArt',slot);if art==0 then return end
 local expectedBank=r('SsChrPhysical')
 local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 local x=r('R4')+256*r('R5');if x>=32768 then x=x-65536 end
 local y=r('R6')+256*(r('R7')-1)
 for i=0,count//4-1 do
  local p=ptr+1+(count//4-1-i)*4 -- Generic renderer consumes source pieces backwards.
  local tile=emu.read(p,emu.memType.nesDebug)
  local attr=emu.read(p+1,emu.memType.nesDebug)
  local py=y+signed(emu.read(p+2,emu.memType.nesDebug))
  local px=x+signed(emu.read(p+3,emu.memType.nesDebug))
  if px>=0 and px<256 and py>=0 and py<240 then
   parts[#parts+1]={o=(start+rotation+i*4)%256,t=tile,a=attr,y=py,x=px,bank=expectedBank,art=art,slot=slot}
  end
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==60 then drawing=false end end,emu.callbackType.exec,L.SpecialDrawFinish)
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==4 then ready=parts end
end,emu.callbackType.exec,L.RosterOamReady)
emu.addMemoryCallback(function()if frame>=550 then dma=true end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 if not dma or not ready then return end
 dma=false;total=total+1
 local state=mmc5 and emu.getState()or nil
 local chrErrors,oamErrors=0,0
 local arts={}
 for _,p in ipairs(ready)do
  arts[#arts+1]=p.art
  if emu.read(p.o,emu.memType.nesSpriteRam)~=p.y or emu.read(p.o+1,emu.memType.nesSpriteRam)~=p.t
   or emu.read(p.o+2,emu.memType.nesSpriteRam)~=p.a or emu.read(p.o+3,emu.memType.nesSpriteRam)~=p.x then oamErrors=oamErrors+1 end
  local address=(p.t&1)*4096+(p.t&254)*16
  local expectedAddress=(p.bank+(mmc5 and 0 or 1))*1024+(p.t&62)*16
  for b=0,31 do if ppu(address+b,state)~=emu.read(expectedAddress+b,emu.memType.nesChrRom)then chrErrors=chrErrors+1 end end
  visible=visible+1
 end
 local nt={};local changes=0
 for i=0,2047 do local v=ppu(0x2000+i,state);nt[#nt+1]=string.char(v);if previousNt and previousNt[i+1]~=v then changes=changes+1 end end
 previousNt={};for i=1,#nt do previousNt[i]=nt[i]:byte()end
 local count=0;for i=0,9 do if r('RgShotType',i)>0 then count=count+1 end end
 csv:write(table.concat({frame,age,total,#ready,chrErrors,oamErrors,r('SsChrActive'),r('SsChrPhysical'),changes,count,table.concat(arts,'|')},',')..'\n')
 local sample=false
 for _,p in ipairs(ready)do if p.art>=23 and p.art<=37 and not sampled[p.art]then sample=true;sampled[p.art]=true end end
 if chrErrors>0 or oamErrors>0 then bad=bad+1;screenshotPending=true end
 if sample then
  local entry={frame=frame,phase=age,parts=ready,screen=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),shots={}}
  for i=0,9 do entry.shots[i]={x=r('RgShotX',i)+256*r('RgShotPage',i),y=r('RgShotY',i),mode=r('SsMode',i),art=r('SsArt',i),typ=r('RgShotType',i)}end
  samples[#samples+1]=entry
  if age>25 then screenshotPending=true end
 end
 if chrErrors>0 or oamErrors>0 or sample then
  binary:write(string.pack('<I4I2I2',frame,chrErrors,oamErrors))
  for i=0,255 do binary:write(string.char(emu.read(i,emu.memType.nesSpriteRam)))end
  for i=0,8191 do binary:write(string.char(ppu(i,state)))end
  binary:write(table.concat(nt));for i=0,31 do binary:write(string.char(emu.read(i,emu.memType.nesPaletteRam)))end
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',0);w('LevelNumber',1);w('AreaNumber',2)end
 if frame==550 then
  assert(r('AreaType')==2 and r('SelectedCharacter')==1,'Native1-2 MM')
  w('PlayerStatus',1);w('InvOwnedLo',65,1);w('InvSelected',6,1);w('InvAmmo',112,22);w('InvDirty',1)
  -- Flat collision arena, with unmodified native nametable/PPU presentation.
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  return
 end
 if frame>=550 then
  age=age+1
  if FLAME_STAR_AT and age==FLAME_STAR_AT then w('StarInvincibleTimer',32)end
  for i=0,5 do w('Enemy_Flag',0,i)end
  if screenshotPending and screenshots<3 then
   screenshots=screenshots+1;screenshotPending=false
   local f=assert(io.open(OUTPUT..ROM_NAME..'-flame-dma-error-'..screenshots..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  if age==300 then
   csv:close();binary:close()
   local f=assert(io.open(OUTPUT..ROM_NAME..'-flame-samples.lua','w'));f:write('return {\n')
   for _,e in ipairs(samples)do
    f:write('{frame='..e.frame..',phase='..e.phase..',screen='..e.screen..',parts={')
    for _,p in ipairs(e.parts)do f:write(string.format('{o=%d,t=%d,a=%d,x=%d,y=%d,bank=%d,art=%d,slot=%d},',p.o,p.t,p.a,p.x,p.y,p.bank,p.art,p.slot))end
    f:write('},shots={')
    for i=0,9 do local p=e.shots[i];f:write(string.format('[%d]={x=%d,y=%d,mode=%d,art=%d,typ=%d},',i,p.x,p.y,p.mode,p.art,p.typ))end
    f:write('}},\n')
   end
   f:write('}\n');f:close()
   assert(bad==0,'No completed-DMA pattern-bank or OAM contract mismatches')
   print('PASS diagnostic observed '..total..' completed DMA, '..visible..' flame parts; mismatch frames '..bad);emu.stop(0)
  end
 end
end,emu.eventType.endFrame)
