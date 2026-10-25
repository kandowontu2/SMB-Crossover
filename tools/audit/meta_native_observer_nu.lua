-- Read-only observer. The separately loaded component driver seeds explicit
-- terrain/player/enemy arenas; this observer never writes emulated state.
local O=assert(META_AUDIT_OUT);local wall,depth,drawID,rows=0,0,0,0
local inside,prepared,completed,dma=nil,nil,nil,nil;local hooks,seen,physical={},{},{}
local meta=assert(io.open(O..'hardware.csv','w'));meta:write('row,wall,draw,pose,face,combo,tick,originX,originY,attribute,page0,page1,expectedPage,bodyPalette,swordPalette,partCount,logicalStart,first,rotation\n')
local oamFile=assert(io.open(O..'oam.bin','wb'));local paletteFile=assert(io.open(O..'palettes.bin','wb'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function active()return r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==13 and r('KbVariant')==1 end
local function qualified(n)return depth==0 and bank(L[n])==B[n]end
local function bytes()local t={};for i=0,255 do t[#t+1]=string.char(r('Sprite_Data',i))end;return table.concat(t)end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Observer balanced interrupt scope')end,emu.callbackType.exec,assert(pc))end
emu.addMemoryCallback(function()if qualified('DrawAllMetasprites')then prepared=nil end end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not active()or not qualified('DrawMetasprite')or emu.getState()['cpu.y']~=0 then return end
 local sp=emu.getState()['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 inside={pc=pc,sp=(sp+2)%256}
 if not hooks[pc]then hooks[pc]=true;emu.addMemoryCallback(function()if inside and inside.pc==pc and depth==0 and emu.getState()['cpu.sp']==inside.sp then inside=nil end end,emu.callbackType.exec,pc)end
end,emu.callbackType.exec,L.DrawMetasprite)
emu.addMemoryCallback(function()
 if not active()or not inside or not qualified('MetaspriteRenderLoop')then return end
 local pose=r('KbPose');local p=assert(META_POSES[pose],'Native pose in original90pose table')
 if r('R0')+256*r('R1')~=p.pointer then return end
 drawID=drawID+1
 prepared={draw=drawID,pose=pose,face=r('PlayerFacingDir'),combo=r('MkCombo'),tick=r('MkMoveTick'),x=r('R4')+256*r('R5'),y=r('R6')+256*r('R7'),attr=r('R3'),expectedPage=p.page,count=#p.parts,start=r('RgOamPlayerStart'),first=r('RgOamFirst'),rotation=r('RgOamRotation')}
 assert(not(prepared.first>prepared.start and prepared.first<prepared.start+prepared.count*4),'Actual Meta pivot stays outside its logical body span')
 assert(((prepared.start-prepared.first)&255)+prepared.count*4<=256,'Body occupies a contiguous physical OAM span')
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()
 if not active()or not prepared or not qualified('RosterOamReady')then return end
 completed={bytes=bytes(),body=prepared}
end,emu.callbackType.exec,L.RosterOamReady)
emu.addMemoryCallback(function(_,page)
 dma=nil;if not active()or not completed then return end
 local t={};for i=0,255 do t[#t+1]=string.char(emu.read(page*256+i,emu.memType.nesDebug))end
 if table.concat(t)==completed.bytes then dma=completed end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 wall=wall+1;if not dma then return end
 local q=dma;dma=nil;local actual={};for i=0,255 do actual[#actual+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
 local raw=table.concat(actual);assert(raw==q.bytes,'Actual DMA sprite RAM exactly matches complete native list')
 local b=q.body;local st=emu.getState();local page0,page1=st['mapper.chrBanks0'],st['mapper.chrBanks1'];assert(page0==b.expectedPage,'Port body/sword physical page matches constructed pose')
 for _,page in ipairs({page0,page1})do if not physical[page]then
  physical[page]=true;local t={};for i=0,1023 do t[#t+1]=string.char(emu.read(page*1024+i,emu.memType.nesChrRom))end
  local f=assert(io.open(O..'physical-'..page..'.bin','wb'));f:write(table.concat(t));f:close()
 end end
 local pal={};for i=0,31 do pal[#pal+1]=string.char(emu.read(0x3f00+i,emu.memType.nesPpuDebug))end;local colors=table.concat(pal)
 local body=string.format('%02x:%02x:%02x',pal[18]:byte(),pal[19]:byte(),pal[20]:byte());local sword=string.format('%02x:%02x:%02x',pal[26]:byte(),pal[27]:byte(),pal[28]:byte())
 rows=rows+1;oamFile:write(raw);paletteFile:write(colors)
 meta:write(table.concat({rows,wall,b.draw,b.pose,b.face,b.combo,b.tick,b.x,b.y,b.attr,page0,page1,b.expectedPage,body,sword,b.count,b.start,b.first,b.rotation},',')..'\n');meta:flush()
 local key=b.pose..'-'..b.face..'-'..b.combo
 if not seen[key]then seen[key]=true;local f=assert(io.open(O..'pose-'..key..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
end,emu.eventType.endFrame)
local finished=false
return function()
 if finished then return end;finished=true
 meta:close();oamFile:close();paletteFile:close();assert(rows>500,'Independent live port hardware coverage')
 local f=assert(io.open(O..'observer.json','w'));f:write(string.format('{"rows":%d,"body_draws":%d,"read_only_observer":true,"separate_driver_injected_arenas":true}',rows,drawID));f:close()
end
