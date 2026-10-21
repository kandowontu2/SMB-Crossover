-- The REAL native bonus-room parser builds every tested tile and protection
-- flag. Only the actor/weapon fixture is reset; controller B throws the disk.
local frame=0
local map,terrain={},{}
local cases={{0,9,2},{4,9,1},{5,9,1},{6,9,1},{7,9,1},{8,9,1},{9,9,1},{10,9,1},{4,0,1},{4,11,1},{15,8,1}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame>=240 and frame<400 and r('SelectedCharacter')==7 and r('OperMode_Task')==0 then w('AreaPointer',0xc2) end
end,emu.callbackType.exec,L.GetAreaDataAddrs)
local function player(s)
 w('Player_X_Position',s[1]==0 and 32 or s[1]*16-32);w('Player_PageLoc',0)
 w('Player_Y_Position',32+s[2]*16);w('Player_Y_HighPos',1);w('Player_State',1);w('Player_Y_Speed',0)
 w('PlayerFacingDir',s[3]);w('GameEngineSubroutine',8);w('TimerControl',0);w('MmDeathFlag',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
end
emu.addEventCallback(function()
 local n=math.floor((frame-550)/60)+1;local t=(frame-550)%60
 emu.setInput({down=frame==80,right=frame==100,start=frame==240,b=n>=1 and n<=#cases and t==3},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n=math.floor((frame-550)/60)+1;local t=(frame-550)%60
 if frame==550 then
  assert(r('AreaType')==2 and r('GameEngineSubroutine')==8,'Native underground bonus room loaded')
  for i=0,415 do map[i]=r('Block_Buffer_1',i);terrain[i]=r('MmSolidTerrain',i) end
  for col=4,10 do for row=8,10 do assert(map[row*16+col]==0x52 and terrain[row*16+col]==0,'Every native middle-platform brick is breakable') end end
  for col=0,15 do assert(map[176+col]==0x54 and terrain[176+col]==1,'Foundation is protected') end
 end
 if n>#cases then print('PASS native bonus-room left stack, all seven middle-platform columns, ceiling masonry, protected ground and pipe; actual controller Diskarmor throws');emu.stop(0);return end
 local s=cases[n];local target=s[2]*16+s[1]
 if t==0 then
  for i=0,415 do w('Block_Buffer_1',map[i],i);w('MmSolidTerrain',terrain[i],i);w('MmBrickHealth',0,i);w('RgMeleeBlocks',0,i) end
  for i=0,9 do w('RgShotType',0,i) end
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
  w('PlayerStatus',2);w('RgPreviousButtons',0);w('RgCooldown',0);w('RgShootPose',0);w('BlockBounceTimer',0)
 end
 if t==35 then
  if n<=9 then assert(r('Block_Buffer_1',target)~=0x52,'Native brick case '..n..' breaks')
  else assert(r('Block_Buffer_1',target)==map[target],'Ground/pipe case '..n..' remains solid') end
  for col=0,15 do assert(r('Block_Buffer_1',176+col)==0x54,'All foundation cells survive') end
 end
 for i=0,5 do w('Enemy_Flag',0,i) end
 player(s)
end,emu.eventType.endFrame)
