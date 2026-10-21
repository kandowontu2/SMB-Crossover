local frame=0
local oldestBeforeFourth
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function clear()
  for i=0,5 do w('Enemy_Flag',0,i) end
  for i=0,2 do w('SmShotType',0,i);w('SmShotImpact',0,i);w('SmShotAge',0,i);w('SmBombAge',0,i) end
end
local function enemy(id,x,y)
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',id);w('Enemy_State',0)
  w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',y);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',9)
  w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
end
local function beam(kind,x,y)
  w('SmShotType',kind,0);w('SmShotX',x,0);w('SmShotY',y,0);w('SmShotPage',0,0)
  w('SmShotAge',0,0);w('SmShotFraction',0,0);w('SmShotDir',1,0);w('SmShotImpact',0,0)
end
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or frame==100,start=frame==140,
    down=frame==780 or(frame>=782 and frame<785),up=frame>=842 and frame<848,
    b=(frame>=500 and frame<504)or(frame>=520 and frame<524)or(frame>=540 and frame<544)
      or(frame>=800 and frame<804)or(frame>=808 and frame<812)
      or(frame>=816 and frame<820)or(frame>=824 and frame<828)
      or(frame>=870 and frame<875)or(frame>=882 and frame<887)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==490 then w('InvOwnedLo',2,2);w('PlayerStatus',1); clear();enemy(6,90,168) end
  if frame>490 and frame<560 and r('Enemy_State')<32 then
    w('Enemy_X_Position',90);w('Enemy_Y_Position',168)
    w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
  end
  if frame==515 then assert(r('MmEnemyHealthLo')==60,'Short beam deals 40 damage') end
  if frame==535 then assert(r('MmEnemyHealthLo')==20,'Second beam leaves 20 HP') end
  if frame==555 then
    assert(r('Enemy_State')>=32 or r('Enemy_Flag')==0,'Third beam defeats a 100-HP enemy')
    print('PASS source 40-damage beams and multi-hit enemy health')
  end
  if frame==600 then
    clear();w('BlockBounceTimer',0);w('Block_Buffer_1',0x51,167)
    beam(1,110,194)
  end
  if frame==605 then assert(r('Block_Buffer_1',167)~=0x51,'One beam breaks a 34-HP brick') end
  if frame==630 then
    clear();w('BlockBounceTimer',0);w('Block_Buffer_1',0xc0,167)
    beam(1,110,194)
  end
  if frame==635 then
    assert(r('Block_Buffer_1',167)~=0xc0 and r('CoinTallyFor1Ups')>0,'Beam activates question block and reward')
    print('PASS Samus brick destruction and question-block activation')
  end
  if frame==680 then
    clear();enemy(0,120,184);w('MmEnemyHealthLo',125);w('Block_Buffer_1',0,167)
    w('SmBombAge',1);w('SmBombX',120);w('SmBombPage',0);w('SmBombY',194)
    w('SmBombHits',0);w('SmBombBoosted',0);w('SmBombBlocksDone',0)
  end
  if frame>680 and frame<760 then
    w('Enemy_X_Position',120);w('Enemy_Y_Position',184)
    w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
  end
  if frame==736 then
    assert(r('SmBombAge')==57,'Bomb stays armed for 950 ms')
    assert(r('MmEnemyHealthLo')==125,'Bomb cannot hit before its fuse ends')
  end
  if frame==740 or frame==750 then
    assert(r('MmEnemyHealthLo')==25 and r('MmEnemyHealthHi')==0,'Bomb deals 100 damage only once to this enemy')
    assert(r('SmBombHits')==1,'Explosion remembers the enemy hit')
  end
  if frame==765 then
    assert(r('SmBombAge')==0,'Explosion expires after its animation')
    clear()
    print('PASS 57-frame bomb fuse, 100 damage and one hit per explosion')
  end
  if frame==790 then
    w('SmShotType',2,0);w('SmShotX',32,0);w('SmShotY',100,0);w('SmShotDir',1,0)
    w('SmShotType',2,1);w('SmShotX',48,1);w('SmShotY',100,1);w('SmShotDir',1,1)
    w('SmShotType',2,2);w('SmShotX',64,2);w('SmShotY',100,2);w('SmShotDir',1,2)
  end
  if frame==823 then oldestBeforeFourth=r('SmBombAge',2)end
  if frame==832 then
    for i=0,2 do
      assert(r('SmBombAge',i)>0,'Morph Ball permits three bombs even with three beams')
      assert(r('SmShotType',i)==2,'All three beams remain live alongside the three bombs')
    end
    assert(oldestBeforeFourth and r('SmBombAge',2)>oldestBeforeFourth,'Fourth bomb press cannot replace a live bomb')
    print('PASS independent three-bomb pool and three-beam pool')
  end
  if frame==860 then clear();w('PlayerStatus',2);w('InvOwnedLo',0x92,2) end
  if frame==890 then
    for _,i in ipairs({1,2}) do
      assert(r('SmShotType',i)==3,'Flower fires wave beams')
      local age=r('SmShotAge',i)
      local offset=math.floor(math.sin((age-1)*25/60)*15+0.5)
      if r('SmShotPolarity',i)==0 then offset=-offset end
      assert(r('SmShotY',i)==(r('SmShotCenter',i)+offset)%256,'Reference sine-wave path')
      assert(r('SmShotX',i)>=61+math.floor(age*400/120)-1,'Reference wave speed')
    end
    assert(r('SmShotPolarity',1)~=r('SmShotPolarity',2),'Successive wave shots alternate polarity')
    print('PASS flower wave beam speed, sine amplitude and alternating polarity')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
