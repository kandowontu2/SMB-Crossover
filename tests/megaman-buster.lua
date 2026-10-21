local frame=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function clearShots() for i=0,3 do w('MmBulletType',0,i) end end
local function enemy()
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
  w('Enemy_X_Position',112);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',9)
  w('MmEnemyHealthLo',0);w('MmEnemyHealthHi',0)
end
local function bullet(kind,x,y,slot)
  slot=slot or 0
  w('MmBulletType',kind,slot);w('MmBulletX',x,slot);w('MmBulletPage',0,slot)
  w('MmBulletY',y,slot);w('MmBulletDir',1,slot)
  w('MmBulletFracLo',0,slot);w('MmBulletFracHi',0,slot);w('MmBulletAge',0,slot)
end
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120,
    b=frame==500 or frame==520 or frame==540 or frame==560 or
      (frame>=740 and frame<789) or (frame>=820 and frame<910)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==490 then enemy() end
  if frame>490 and frame<580 and r('Enemy_State')<32 then
    w('Enemy_X_Position',112);w('Enemy_X_Speed',0)
  end
  if frame==515 or frame==535 or frame==555 then
    local expected=50-25*((frame-515)/20)
    assert(r('MmEnemyHealthLo')==expected,'Goomba health '..r('MmEnemyHealthLo')..' expected '..expected)
    if frame<555 then assert(r('Enemy_State')<32,'Goomba survives until the third normal shot') end
  end
  if frame==575 then
    assert(r('Enemy_State')>=32 or r('Enemy_Flag')==0,'25-damage buster defeats the 75-HP 2.02 Goomba')
    print('PASS reference Goomba health and three-hit normal buster')
  end
  if frame==600 then
    for i=0,5 do w('Enemy_Flag',0,i) end
    clearShots();w('BlockBounceTimer',0)
    w('Block_Buffer_1',0x51,167)
    bullet(1,110,194)
  end
  if frame==604 then
    assert(r('MmBrickHealth',167)==9,'Brick has 9 of 34 health after one normal shot')
    assert(r('Block_Buffer_1',167)==0x51,'First shot leaves brick intact')
  end
  if frame==620 then bullet(1,110,194) end
  if frame==625 then
    assert(r('Block_Buffer_1',167)~=0x51,'Second normal shot shatters brick')
    assert(r('Player_X_Position')==40,'Shooting a block preserves player position')
    print('PASS two-hit brick destruction and restored player coordinates')
  end
  if frame==650 then
    clearShots();w('BlockBounceTimer',0);w('Block_Buffer_1',0xc0,167)
    bullet(1,110,194)
  end
  if frame==655 then
    assert(r('Block_Buffer_1',167)~=0xc0,'Buster activates question block from the side')
    assert(r('CoinTallyFor1Ups')>0,'Question coin block awards coin')
    print('PASS projectile activation of question block')
  end
  if frame==690 then
    clearShots();enemy();w('MmEnemyHealthLo',75);w('Block_Buffer_1',0,167)
    bullet(3,88,194)
  end
  if frame==699 then
    assert(r('Enemy_State')>=32 or r('Enemy_Flag')==0,'Full charge kills weakened enemy')
    assert(r('MmBulletType')==3,'Full charge pierces a killed enemy')
    print('PASS 75-damage full charge and piercing')
  end
  if frame==730 then
    clearShots();w('PlayerStatus',1)
    for i=0,5 do w('Enemy_Flag',0,i) end
  end
  if frame==791 then
    local weak=false
    for i=0,3 do if r('MmBulletType',i)==2 then weak=true end end
    assert(weak,'800ms charge release emits weak charge')
  end
  if frame==912 then
    local full=false
    for i=0,3 do if r('MmBulletType',i)==3 then full=true end end
    assert(full,'1450ms charge release emits full charge')
    local f=assert(io.open(OUTPUT..ROM_NAME..'-hosted-buster.png','wb'));f:write(emu.takeScreenshot());f:close()
    print('PASS mushroom charge thresholds and independent charge shot')
  end
  if frame==920 then
    clearShots();w('BlockBounceTimer',0);w('Block_Buffer_1',0x58,167)
    w('MmCoinHits',0,167)
  end
  if frame>=930 and frame<=1190 and (frame-930)%20==0 then
    bullet(1,110,194)
  end
  if frame==1210 then
    assert(r('MmCoinHits',167)==14,'Hosted multi-coin brick permits fourteen hits')
    assert(r('Block_Buffer_1',167)==0xc4,'Fourteenth coin leaves an empty block')
    print('PASS per-brick fourteen-coin limit')
    w('BlockBounceTimer',0);w('Block_Buffer_1',0x58,167);w('MmCoinHits',0,167)
    bullet(1,110,194)
  end
  if frame==1240 then
    w('MmWorldTime',r('MmWorldTime',1)+2,1)
    bullet(1,110,194)
  end
  if frame==1270 then
    assert(r('Block_Buffer_1',167)==0xc4,'Six-second coin window expires independently of the native timer')
    print('PASS per-brick six-second coin window')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
