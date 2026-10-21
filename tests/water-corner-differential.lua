-- Explicit single-ball collision arenas. Every ordinary orbit sample places
-- one masonry/question/foundation tile at an exact canonical radius-4 corner. The
-- complete native outcome CSV can be compared before/after optimization.
local frame,case=0,0
local xs={3,12,252,256,511,0}
local ys={35,60,96,172,214,232}
local tiles={0x51,0x52,0x54,0xc0,0xc1,0xc4,0x23}
local total=#xs*#ys*#tiles*8
local current
local interruptDepth=0
local out=assert(io.open(OUTPUT..ROM_NAME..'-water-corner-differential.csv','w'))
out:write('case,x,y,angle,tile,cell,after,type,health,spawn,itemx,itemy\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 then return end
 if not current then case=case+1 end
 if case>total then out:close();print('PASS Water exact native corner outcomes captured: '..total..' page/seam/height/tile cases');emu.stop(0);return end
 local n=case-1;local angle=(n%8)*32;n=math.floor(n/8)
 local tile=tiles[n%#tiles+1];n=math.floor(n/#tiles)
 local cy=ys[n%#ys+1];n=math.floor(n/#ys);local cx=xs[n+1]
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i);w('MmCoinHits',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i);w('InvPickup',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i)end
 w('BlockBounceTimer',0);w('VRAM_Buffer1_Offset',0);w('VRAM_Buffer1',0)
 w('Player_X_Position',cx-8);w('Player_PageLoc',math.floor((cx-8)/256))
 w('Player_Y_Position',cy-20);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',1);w('InvOwnedLo',129,9);w('InvOwnedHi',0,9);w('InvSelected',7,9)
 w('InvViewedLo',0,9);w('InvViewedHi',0,9);w('InvStoredLo',0,9);w('InvStoredHi',0,9)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('MmDeathFlag',0)
 w('InvFresh',0);w('SsWaterExpand',0);w('SsBodyStop',0);w('SsFreeze',0)
 w('PseudoRandomBitReg',0,1);w('PseudoRandomBitReg',0,2)
 local bx=(cx+signed(r('SsCircle',(angle+64)%256)))%65536
 local by=(cy+signed(r('SsCircle',angle)))%256
 local tx=(bx+4)%65536;local ty=by+4
 if ty>=240 then ty=by-4 end
 if ty<32 then ty=32 end
 local cell=math.floor(tx/256)%2*208+math.floor((ty-32)/16)*16+math.floor(tx%256/16)
 w('Block_Buffer_1',tile,cell)
 w('RgShotType',17);w('RgShotAge',19);w('RgShotImpact',0);w('RgShotDir',1)
 w('SsAngleLo',0);w('SsAngleHi',angle);w('SsHidden',0);w('SsHitTimer',0);w('RgShotHits',0)
 current={cx=cx,cy=cy,angle=angle,tile=tile,cell=cell}
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 or not current then return end
 local c=current;local spawn,itemx,itemy=0,-1,-1
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
  spawn=r('InvPickup',i);itemx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i);itemy=r('Enemy_Y_Position',i)
 end end
 out:write(table.concat({case,c.cx,c.cy,c.angle,c.tile,c.cell,r('Block_Buffer_1',c.cell),r('RgShotType'),r('MmBrickHealth',c.cell),spawn,itemx,itemy},',')..'\n')
 current=nil
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
