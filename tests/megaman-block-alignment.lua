-- Block-map/projectile fixtures check the native bounce sprite and the actual
-- OAM coordinates on every bounce frame, including tile and page crossings.
local frame=0
local current
local cases={
  {name='normal right edge',kind=1,dir=1,x=122,y=150,tx=128,ty=144},
  {name='normal left edge',kind=1,dir=2,x=132,y=150,tx=112,ty=144},
  {name='full charge right edge',kind=3,dir=1,x=119,y=150,tx=128,ty=144},
  {name='fire charge left edge',kind=6,dir=2,x=136,y=150,tx=112,ty=144},
  {name='right edge across page',kind=1,dir=1,x=250,y=150,tx=256,ty=144,camera=200},
  {name='left edge across page',kind=1,dir=2,x=261,y=150,tx=240,ty=144,camera=200},
  {name='charge top edge',kind=3,dir=1,x=124,y=164,tx=128,ty=144},
  {name='fire charge bottom edge',kind=6,dir=1,x=119,y=140,tx=128,ty=144},
  {name='mushroom box right edge',kind=1,dir=1,x=122,y=150,tx=128,ty=144,item=true},
}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function blockOffset(x,y)
  return (math.floor(x/256)%2)*208+math.floor((y-32)/16)*16+math.floor((x%256)/16)
end
local function begin(c)
  c.frames=0;c.camera=c.camera or 0
  for i=0,5 do w('Enemy_Flag',0,i) end
  for i=0,8 do w('Misc_State',0,i) end
  for i=0,3 do w('MmBulletType',0,i);w('Block_State',0,i);w('BlockMetasprite',0,i) end
  for i=0,1 do w('Block_RepFlag',0,i) end
  w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
  for dx=-16,16,16 do for dy=-16,16,16 do
    w('Block_Buffer_1',0,blockOffset(c.tx+dx,c.ty+dy))
  end end
  c.offset=blockOffset(c.tx,c.ty)
  w('Block_Buffer_1',c.item and 0xc1 or 0xc0,c.offset)
  w('ScreenLeft_X_Pos',c.camera%256);w('ScreenLeft_PageLoc',math.floor(c.camera/256))
  w('ScreenRight_X_Pos',(c.camera+255)%256);w('ScreenRight_PageLoc',math.floor((c.camera+255)/256))
  w('Player_X_Position',(c.camera+40)%256);w('Player_PageLoc',math.floor((c.camera+40)/256))
  w('MmBulletType',c.kind);w('MmBulletX',c.x%256);w('MmBulletPage',math.floor(c.x/256))
  w('MmBulletY',c.y);w('MmBulletDir',c.dir);w('MmBulletAge',0)
  w('MmBulletFracLo',0);w('MmBulletFracHi',0)
  current=c
end
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
  if r('CurrentBank')%128==4 and current and r('BlockMetasprite')==L.METASPRITE_MISC_BLOCK then
    local c=current
    local bx=r('Block_X_Position')+256*r('Block_PageLoc')
    assert(bx==c.tx,c.name..': bouncing block moved horizontally; expected '..c.tx..', got '..bx)
    assert(r('Block_PageLoc2')==math.floor(c.tx/256),c.name..': saved page matches the struck block')
    assert(r('Block_Y_Position')<=c.ty+4 and r('Block_Y_Position')>=c.ty-12,
      c.name..': bounce starts on the struck row; expected '..c.ty..', got '..r('Block_Y_Position')..', probe '..r('MmProbeY'))
    local tile=emu.read(4*0x2000+(L.MetaspriteData_MISC_BLOCK_RIGHT+1)%0x2000,emu.memType.nesPrgRom)
    local seen=0
    for offset=0,255,4 do
      if r('Sprite_Tilenumber',offset)==tile and r('Sprite_Y_Position',offset)<240 then
        local sx=r('Sprite_X_Position',offset)
        assert(sx==c.tx-r('ScreenLeft_X_Pos') or sx==c.tx-r('ScreenLeft_X_Pos')+8,
          c.name..': rendered block must stay aligned with its background cell')
        seen=seen+1
      end
    end
    assert(seen==2,c.name..': both halves of the bouncing block are visible')
    if c.frames==0 then
      if c.item then
        local found=false
        for i=0,5 do
          if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
            assert(r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)==c.tx,'Power-up spawns in the struck column')
            found=true
          end
        end
        assert(found,'Question box releases its mushroom')
      else
        local i=r('JumpCoinMiscOffset')
        assert(r('Misc_X_Position',i)+256*r('Misc_PageLoc',i)==c.tx+5,'Coin spawns over the struck block')
      end
    end
    c.frames=c.frames+1
  end
end,emu.callbackType.exec,L.RosterOamReady)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=500 and (frame-500)%45==0 then
    if current then
      assert(current.frames>=5,current.name..': checked the full animated bounce')
      assert(r('Block_Buffer_1',current.offset)==0xc4,current.name..': used tile returns to the same map cell')
      assert(r('Player_X_Position')+256*r('Player_PageLoc')==current.camera+40,'Block activation preserves the player position')
      print('PASS aligned block bounce, OAM and reward: '..current.name)
    end
    local index=1+(frame-500)/45
    if cases[index] then begin(cases[index]) else emu.stop(0) end
  end
end,emu.eventType.endFrame)
