-- Two live on-screen targets prove that selection uses missile distance,
-- independently of NES enemy slot order. No input/memory patch is a route clear.
local frame=0
local cases={{100,220,0},{220,100,1},{150,220,0},{220,150,1}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/80),(frame-550)%80 end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',0x85,11);w('InvSelected',2,11);w('InvAmmo',20,178);w('InvPrevious',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do
  w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_X_Position',cases[n+1][i+1],i);w('Enemy_PageLoc',0,i)
  w('Enemy_Y_Position',176,i);w('Enemy_Y_HighPos',1,i);w('Enemy_BoundBoxCtrl',9,i);w('EnemyOffscrBitsMasked',0,i);w('MmEnemyHealthLo',255,i);w('MmEnemyHealthHi',127,i)
 end
 w('AvStopwatch',200)
end
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=n>=0 and n<#cases and t>=12 and t<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==#cases then print('PASS source homing target selection follows missile distance in both enemy-slot orders');emu.stop(0);return end
 if t==0 then fixture(n)end
 if t==25 then
  local found=false
  for i=0,9 do if r('RgShotType',i)==45 then
   assert(r('SsMode',i)==cases[n+1][3],'Nearest live target independently of slot order: case '..n..' target '..r('SsMode',i))
   found=true
  end end
  assert(found,'Actual Select produces the tested homing missile')
 end
end,emu.eventType.endFrame)
