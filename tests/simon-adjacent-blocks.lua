local frame,index=0,0
local current
-- Explicit map/player fixtures exercise a real B-button whip across more
-- cells than SMB's two block-animation slots can hold at once.
local cases={{power=0,dir=1},{power=1,dir=1},{power=2,dir=1},{power=0,dir=2},{power=1,dir=2},{power=2,dir=2}}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function cell(x) return 160+math.floor(x/16) end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<180 and (frame-80)%20==0,start=frame==200,b=frame>=560 and (frame-560)%120<4},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do if r('Enemy_ID',i)~=0x2e then w('Enemy_Flag',0,i) end end end
 if current then
  assert(emu.read(0x3f19,emu.memType.nesPpuDebug)==0x16 and
    emu.read(0x3f1a,emu.memType.nesPpuDebug)==0x30 and
    emu.read(0x3f1b,emu.memType.nesPpuDebug)==0x27,
    'Simon preserves red/white/tan world colors while whipping adjacent blocks')
  for i=0,5 do
   if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then current.reward=true end
  end
  if frame==current.start+85 and current.power==0 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-simon-mushroom-'..current.dir..'.png','wb'))
   f:write(emu.takeScreenshot());f:close()
  end
 end
 if frame>=550 and (frame-550)%120==0 then
  if current then
   assert(r('Block_Buffer_1',cell(current.q))==0xc4,'Whip preserves the used question block beside shattered bricks, power '..current.power..', direction '..current.dir..': '..r('Block_Buffer_1',cell(current.q)))
   local address=0x2000+24*32+math.floor(current.q/8)
   for i,offset in ipairs({0,1,32,33}) do
    assert(emu.read(address+offset,emu.memType.nesPpuDebug)==({0xae,0xaf,0xbe,0xbf})[i],
      'Used question block remains rendered in its original background cell')
   end
   local brick=r('Block_Buffer_1',cell(128))
   assert(brick==0,'Adjacent brick is destroyed and its logical map cell is committed: '..brick)
   if current.power==2 then
    assert(r('Block_Buffer_1',cell(current.dir==1 and 112 or 144))==0,'Long whip commits both shattered brick cells')
   end
   assert(current.reward,'Question block still releases its power-up')
   print('PASS adjacent question block survives whip power '..current.power..', direction '..current.dir)
  end
  index=index+1;current=cases[index]
  if not current then print('PASS Simon adjacent question/brick transactions');emu.stop(0);return end
  current.start=frame
  for i=0,415 do w('Block_Buffer_1',0,i);w('RgMeleeBlocks',0,i) end
  for i=0,5 do w('Enemy_Flag',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
  current.q=current.dir==1 and 144 or 112
  w('Block_Buffer_1',0xc1,cell(current.q));w('Block_Buffer_1',0x51,cell(128))
  if current.power==2 then w('Block_Buffer_1',0x51,cell(current.dir==1 and 112 or 144)) end
  w('PlayerStatus',current.power);w('RgAttack',0);w('RgAttackKind',0)
  -- A previous case's mushroom can be collected late in its window. Each
  -- independent collision arena starts outside that transformation freeze.
  w('GuestPowerupActive',0);w('TimerControl',0);w('GameEngineSubroutine',8);w('PlayerChangeSizeFlag',0);w('PlayerSize',0)
  -- Each explicit tier arena starts with its own source inventory: basic whip,
  -- common starting item, and Flame Whip only for tier two.
  w('InvOwnedLo',current.power==2 and 3 or 1,5);w('InvOwnedHi',2,5);w('InvSelected',0,5)
  -- Source leather/morning-star rectangles have identical reach. Flame adds
  -- fifteen NES pixels; keep all three populated cells inside that rectangle.
  local x=current.dir==1 and ({104,104,88})[current.power+1] or ({156,156,164})[current.power+1]
  w('PlayerFacingDir',current.dir);w('Player_X_Position',x);w('Player_PageLoc',0)
  w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('BlockBounceTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
end,emu.eventType.endFrame)
