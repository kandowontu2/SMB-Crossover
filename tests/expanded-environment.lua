-- Native 1-1 pipes with enemy suppression, followed by explicit signature-
-- ability fixtures. This is not a controller-only level-clear recording.
local c=assert(EXPANDED_CHARACTER)
local frame,pipe,jumpAge=0,1,-1
local pipes={448,608,736,912}
local high=255
local stopped=false
local wallStart
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
-- V3-MIGRATION-HELPER-BEGIN: controller-only native-pipe observations.
-- Normal-air/climb source hTop=Y+7: Up tests Y+17; top jump tests Y+2.
-- Source Ground intervals include both endpoints; no game state is changed.
local ryuPipeHold=0
local function ryuPipeSolid(wx,yy)
 local function cell(py)
  if py<32 or py>=208 then return false end
  local off=(wx//256)%2*208+((py-32)//16)*16+(wx%256)//16
  local tile=r('Block_Buffer_1',off)
  if tile==0 or tile==0x23 or tile==0x26 or tile==0x5f or tile==0x60 or tile==0x1c or tile==0x6b then return false end
  return r('MTileAttribute',tile)&3==1
 end
 return cell(math.floor(yy)) or (yy%16==0 and cell(math.floor(yy)-1))
end
local function ryuPipeReady()
 local side=r('PlayerFacingDir')
 local wx
 if L.RyWallSide and r('RyWallSide')~=0 then
  side=r('RyWallSide');wx=r('RyWallEdge')+256*r('RyWallPage')-(side==2 and 1 or 0)
 else
  -- The four authored pipes are approached from the left. The mirrored form
  -- is retained for clarity, but no new mirror assertion is introduced here.
  wx=(x()+(side==1 and 15 or 1))//16*16
 end
 local py=r('Player_Y_Position')+(r('MmYFraction')+256*r('MmYFraction',1))/65536
 local headX=x()+8
 return not ryuPipeSolid(wx,py+17) and not ryuPipeSolid(wx,py+2)
  and not ryuPipeSolid(headX,r('Player_Y_Position')+3)
  and r('SavedJoypadBits')&128==0 and r('PreviousA_B_Buttons')&128==0
  and r('RgPreviousButtons')&128==0
end
-- V3-MIGRATION-HELPER-END
local function fixture(px,py,state,power)
 for i=0,415 do w('Block_Buffer_1',0,i) end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 w('Player_X_Position',px);w('Player_PageLoc',0);w('Player_Y_Position',py);w('Player_Y_HighPos',1);w('Player_State',state);w('Player_Y_Speed',0)
 w('PlayerStatus',power or 0);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('XgWall',0);w('XgWallLock',0);w('XgCeiling',0);w('XgDash',0);w('XgRise',0);w('XgJumpUsed',0);w('XgHover',8)
 w('XgWallContact',0);w('PlayerFacingDir',1)
 w('XgHoverActive',0)
 -- V4-SEEDED-RYU-RESET-BEGIN: the native pipe phase is untouched.
 -- This fixture explicitly relocates Ryu/terrain at2050. Discard all persistent
 -- source-wall receipts from the preceding real-pipe traversal, just as the
 -- same fixture already discards XgWall/Contact/Lock and motion fractions.
 if c==10 then
  for _,n in ipairs({'RyWallEdge','RyWallPage','RyWallSide','RyWallResolved','RyWallBlocked','RyWallSupported','RyWallWasGround','RyWallOldHeight','RyWallOldX','RyWallOldPage','RyWallOldXFine','RyWallOldXFrac','RyWallOldY','RyWallOldYFine','RyWallOldYFrac','RyWallScanY','RyWallScanLast'})do
   if L[n]then w(n,0)end
  end
 end
 -- V4-SEEDED-RYU-RESET-END
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 w('MmXFraction',0);w('MmXFraction',0,1);w('MmYFraction',0);w('MmYFraction',0,1)
end
emu.addEventCallback(function()
 local right=frame>=620 and frame<1080
 local a=false;local up=false;local down=c~=8 and frame==80
 if frame>=1080 and frame<2000 then
  while pipes[pipe] and x()>pipes[pipe]+32 do pipe=pipe+1;jumpAge=-1 end
  right=x()<980
  if pipes[pipe] then
   if r('Player_State')==0 and x()>=pipes[pipe]-42 then jumpAge=0 end
   if jumpAge>=0 and jumpAge<36 then a=true end
   if c==9 and jumpAge==17 then a=false end
   up=c==10 and x()>=pipes[pipe]-20
  end
 end
 -- V3-MIGRATION-INPUT-BEGIN: preserve other characters' exact controls.
 if c==10 and frame>=1080 and frame<2000 then
  if ryuPipeHold>0 then
   a=true;ryuPipeHold=ryuPipeHold-1
  elseif pipes[pipe] and r('XgWall')~=0 then
   -- Release the original ground-jump hold until native input history really
   -- contains the release; then a fresh A uses source topJumpPos at the cap.
   a=false
   if ryuPipeReady()then a=true;ryuPipeHold=7 end
  end
 end
 -- V3-MIGRATION-INPUT-END
 if frame>=2050 then
  if c==9 then down=frame==2060;a=frame==2060 or frame==2100 or frame==2118
  elseif c==10 then right=frame>=2060 and frame<2090;up=frame>=2060 and frame<2080;a=frame==2080
  elseif c==11 then up=frame>=2050 and frame<2065;right=frame>=2060 and frame<2075;a=frame==2080 or (frame>=2130 and frame<2160)
  elseif c==8 then a=frame>=2060 and frame<2110;right=frame>=2130 and frame<2150
  elseif c==6 then up=frame==2060;a=frame==2100
  elseif c==7 then right=frame>=2060 and frame<2075 end
 end
 emu.setInput({select=c==8 and frame==180,down=down,left=c==10 and frame>=2080 and frame<2085,right=((c~=8 and frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0) or right) and not (c==10 and frame>=2080 and frame<2085),start=frame==240,a=a,up=up,
 b=(c==6 and (frame==2060 or frame==2080 or frame==2090)) or (c==7 and frame==2060)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=590 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if jumpAge>=0 then jumpAge=jumpAge+1 end
 if frame>=1000 and frame<=1080 then
  -- The independent original-Mario control holds at434. Native contact may
  -- stop Luigi a pixel farther out; neither coordinate can move into the pipe.
  assert(x()>=433 and x()<=(c==8 and 434 or 433),'Character '..c..' cannot creep through the first pipe: '..x());stopped=true
 end
 if frame>=1080 and frame<2000 then high=math.min(high,r('Player_Y_Position')) end
 if frame==2000 then
  assert(stopped and pipe>4 and x()>960,'Character '..c..' clears all four native pipes using its own abilities: x='..x()..', pipe='..pipe..', high='..high)
  print('PASS added character '..c..' solid pipe sides and traversal of all four native 1-1 pipes')
 end
 if frame==2050 then
  fixture(c==10 and 97 or c==11 and 120 or 40,c==10 and 150 or c==11 and 136 or 176,(c==10 or c==11) and 1 or 0,c==11 and 2 or 0)
  if c==10 then for row=8,10 do for col=7,8 do w('Block_Buffer_1',0x54,row*16+col) end end end
  if c==11 then w('InvOwnedLo',0x69,11);for col=7,10 do w('Block_Buffer_1',0x51,96+col) end end
 end
 if frame==2060 then wallStart=r('Player_Y_Position') end
 if frame==2068 then
  if c==9 then assert(r('XgDash')>0 and r('MmVX',2)==2,'Bass dashes without crawling')
  elseif c==10 then assert(r('XgWall')==1 and r('Player_Y_Position')<wallStart,'Ryu clings to and climbs a wall')
  elseif c==11 then assert(r('XgCeiling')==1,'Upgraded Sophia attaches to a solid ceiling') end
 end
 if frame==2084 and c==10 then assert(r('XgWallLock')>0 and r('MmVX',2)>=128 and r('MmVY',2)>=128,'Ryu wall-jumps away from the wall') end
 if frame==2084 and c==11 then assert(r('XgCeiling')==0,'Sophia can release the ceiling with A') end
 if frame==2120 then
  if c==9 then assert(r('XgJumpUsed')==1 and r('MmVY',2)>=128,'Bass receives exactly one second jump')
  elseif c==11 then fixture(40,120,1,1)
  elseif c==8 then assert(high<112,'Luigi can reach the tall pipe') end
 end
 if frame==2150 and c==8 then stopped=x() end
 if frame==2158 then
  if c==8 then assert(x()>stopped,'Luigi coasts after direction is released')
  elseif c==11 then assert(r('XgHover')<8 and r('Player_Y_Position')<120,'Sophia hover consumes one unit per 300ms and lifts the vehicle') end
 end
 if frame==2200 then
  print('PASS added character '..c..' signature movement ability and stable gameplay');emu.stop(0)
 end
end,emu.eventType.endFrame)
