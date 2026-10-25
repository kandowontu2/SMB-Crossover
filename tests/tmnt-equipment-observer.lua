-- Read-only observer; the separate equipment fixture explicitly seeds arenas.
local frame=0;local prepared={};local completed=nil;local dma=nil;local rows=0;local drawRows=0
local o=assert(io.open(TEST_DIR..'world-oam.bin','wb'));local p=assert(io.open(TEST_DIR..'world-palettes.bin','wb'));local f=assert(io.open(TEST_DIR..'world-draws.csv','w'));f:write('row,wall,pose,face,x,y,attribute,count,offset,rotation,first\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function bytes(page)local s={};for i=0,255 do s[#s+1]=string.char(emu.read(page*256+i,emu.memType.nesDebug))end;return table.concat(s)end
local function active()return r('SelectedCharacter')==19 and r('GameEngineSubroutine')==8 and r('OperMode')==1 end
local poses={};for _,n in ipairs({60,61,62,63,72,73,74,75,76,80,81,82,83})do for _,face in ipairs({'R','L'})do poses[L['TnWorld'..n..face]]={pose=n,face=face=='L'and 2 or 1}end end
emu.addMemoryCallback(function()if active()and bank(L.DrawAllMetasprites)==B.DrawAllMetasprites then prepared={}end end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not active()or bank(L.TnWorldDraw)~=B.TnWorldDraw then return end
 local ptr=r('R0')+256*r('R1');local pose=assert(poses[ptr],'source world pointer')
 prepared[#prepared+1]={pose=pose.pose,face=pose.face,x=r('R4')+256*r('R5'),y=r('R6')+256*r('R7')-256,attr=r('R3'),count=emu.read(ptr,emu.memType.nesDebug)//4,off=r('CurrentOAMOffset'),rot=r('RgOamRotation'),first=r('RgOamFirst')}
end,emu.callbackType.exec,L.TnWorldDraw)
emu.addMemoryCallback(function()
 if active()and bank(L.RosterOamReady)==B.RosterOamReady then completed={bytes=bytes(2),draws=prepared}end
end,emu.callbackType.exec,L.RosterOamReady)
emu.addMemoryCallback(function(_,page)
 dma=nil;if active()and completed and bytes(page)==completed.bytes then dma=completed end
end,emu.callbackType.write,0x4014)
local physical=false
emu.addEventCallback(function()
 frame=frame+1;if not dma then return end;local q=dma;dma=nil
 local s={};for i=0,255 do s[#s+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end;local raw=table.concat(s);assert(raw==q.bytes,'DMA exact native OAM')
 rows=rows+1;o:write(raw);s={};for i=0,31 do s[#s+1]=string.char(emu.read(0x3f00+i,emu.memType.nesPpuDebug))end;p:write(table.concat(s))
 local state=emu.getState();if #q.draws>0 then assert(state['mapper.chrBanks4']==628,'actual equipment physical page628')end
 if not physical and #q.draws>0 then physical=true;s={};for i=0,1023 do s[#s+1]=string.char(emu.read(628*1024+i,emu.memType.nesChrRom))end;local h=assert(io.open(TEST_DIR..'physical-628.bin','wb'));h:write(table.concat(s));h:close()end
 for _,d in ipairs(q.draws)do drawRows=drawRows+1;f:write(table.concat({rows,frame,d.pose,d.face,d.x,d.y,d.attr,d.count,d.off,d.rot,d.first},',')..'\n')end;f:flush()
end,emu.eventType.endFrame)
return function()o:close();p:close();f:close();assert(rows>100 and drawRows>100,'native equipment observer coverage')end
