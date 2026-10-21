local frame=0
local checked=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100,start=frame==200,a=frame>=560 and frame<950 and (frame-560)%130<30},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame>=550 and frame<=810 and (frame-550)%130==0 then
  local status=math.floor((frame-550)/130)
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  w('Block_Buffer_1',0x51,118);w('MmSolidTerrain',0,118)
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
  w('BlockBounceTimer',0);w('PlayerStatus',status);w('SmBall',0)
  w('Player_X_Position',88);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_Y_Speed',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
 if frame>=625 and frame<=885 and (frame-625)%130==0 then
  local status=math.floor((frame-625)/130)
  assert(r('Block_Buffer_1',118)==(status==2 and 0x51 or 0),'Samus head behavior matches the hosted suit rule: '..status..' / '..r('Block_Buffer_1',118))
  checked=checked+1
 end
 if frame==900 then
  assert(checked==3,'All Samus suits tested')
  print('PASS Samus head breaks bricks in her first two suits; wave suit bumps as in the hosted game');emu.stop(0)
 end
end,emu.eventType.endFrame)
