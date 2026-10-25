SelectEasyRules() -- Reproduce the ordinary Easy Bill recording.

local frame,seeded,coin,consumed,guard=0,false,0,false,0
local expected={0,0x55,0xaa,0xff,0,0x50,5}
local address={0x23cb,0x23d3,0x23db,0x23e3,0x23eb,0x23f3,0x23fb}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function seed()
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for row=8,10 do for col=1,4 do w('Block_Buffer_1',0xc2,row*16+col)end end
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmVX',0);w('MmVX',0,1);w('MmVX',0,2);w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('VRAM_Buffer1_Offset',0);w('VRAM_Buffer1',0)
 for i,a in ipairs(address)do
  w('VRAM_Buffer2',a//256,(i-1)*4);w('VRAM_Buffer2',a%256,(i-1)*4+1)
  w('VRAM_Buffer2',1,(i-1)*4+2);w('VRAM_Buffer2',expected[i],(i-1)*4+3)
 end
 w('VRAM_Buffer2',0,28);w('VRAM_Buffer2_Offset',28);w('VRAM_Buffer_AddrCtrl',6)
 w('NmiSkipped',r('NmiSkipped')+1);seeded=true
end
emu.addMemoryCallback(function()if frame>=600 and not seeded then seed()end end,emu.callbackType.exec,L.PauseSkip)
emu.addMemoryCallback(function()if seeded and r('CurrentBank')%128==B.RemoveCoin_Axe then coin=coin+1 end end,emu.callbackType.exec,L.RemoveCoin_Axe)
if L.TerrainCatchupPending then emu.addMemoryCallback(function()if seeded and r('VRAM_Buffer_AddrCtrl')==6 then guard=guard+1 end end,emu.callbackType.exec,L.TerrainCatchupPending)end
emu.addMemoryCallback(function()
 if not seeded or consumed or r('NmiR0')+256*r('NmiR1')~=L.VRAM_Buffer2 then return end
 for i,a in ipairs(address)do
  assert(r('VRAM_Buffer2',(i-1)*4)==a//256 and r('VRAM_Buffer2',(i-1)*4+1)==a%256 and r('VRAM_Buffer2',(i-1)*4+2)==1 and r('VRAM_Buffer2',(i-1)*4+3)==expected[i],'Coin collection must preserve the complete attribute column until physical NMI publication')
 end
 consumed=true
end,emu.callbackType.exec,L.UpdateScreen)
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==240,right=frame==80 or frame==100 or frame==120},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if seeded and consumed and coin>0 then
  for i,a in ipairs(address)do assert(emu.read(a,emu.memType.nesPpuDebug)==expected[i],'Every authored attribute reaches the actual PPU and survives coin collection')end
  assert(guard>0,'The actual pending-terrain catch-up path was exercised')
  print('PASS native queued attributes, physical PPU colors and real coin erase; guards='..guard..' coins='..coin)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-terrain-coin-publication.json','w'));f:write('{"passed":true,"guards":'..guard..',"coin_erases":'..coin..',"frame":'..frame..'}\n');f:close();emu.stop(0)
 end
 if frame>=850 then assert(false,'Fixture must actually publish attributes and collect a coin')end
end,emu.eventType.endFrame)
