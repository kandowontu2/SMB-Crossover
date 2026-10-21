-- A bomb overlaps nine cells. Every non-brick cell must retain its original
-- collision tile throughout the explosion, not merely after bounce cleanup.
local frame=0
local cases={0x54,0x69,0x61,0x62,0x10,0x11,0x14,0x15,0xc4,0x52}
local cells={150,151,152,166,167,168,182,183,184}
local active
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or frame==100,start=frame==140},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if active then
    for _,cell in ipairs(cells) do
      assert(r('Block_Buffer_1',cell)==cases[active],
        'Bomb changed solid tile '..string.format('%02x',cases[active])..' at cell '..cell..', frame '..frame)
    end
  end
  if frame>=500 and frame<=860 and (frame-500)%40==0 then
    active=(frame-500)/40+1
    for _,cell in ipairs(cells) do
      w('Block_Buffer_1',cases[active],cell)
      w('MmSolidTerrain',cases[active]==0x52 and 1 or 0,cell)
    end
    for i=0,2 do w('SmBombAge',0,i);w('SmShotType',0,i) end
    w('SmBombAge',57);w('SmBombX',120);w('SmBombPage',0);w('SmBombY',200)
    w('SmBombHits',0);w('SmBombBoosted',0);w('SmBombBlocksDone',0)
  end
  if frame==890 then
    active=nil
    print('PASS bombs preserve ground, water/castle terrain, stairs, pipes, used blocks and underground terrain in all nine cells')
    for _,cell in ipairs(cells) do w('Block_Buffer_1',0,cell);w('MmSolidTerrain',0,cell) end
    w('Block_Buffer_1',0x52,167)
    w('SmBombAge',57);w('SmBombX',120);w('SmBombY',200);w('SmBombPage',0)
    w('SmBombBlocksDone',0);w('BlockBounceTimer',0)
  end
  if frame==895 then
    assert(r('Block_Buffer_1',167)~=0x52,'A genuine underground brick still breaks')
    assert(r('Player_X_Position')==40,'Bomb block processing preserves the player')
    print('PASS shared underground tile ID distinguishes breakable bricks from protected terrain')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
