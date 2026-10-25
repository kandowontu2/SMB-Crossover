-- Cold menus, then explicitly seeded RPG state. No fabricated UI renderer.
local frame,phase,entered=0,0,nil
local captures,restores,opens=0,0,0
local before,oldchr,oldmode
local otherRecords={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function snapshot()
 local t={}
 for a=0x2000,0x27ff do t[#t+1]=emu.read(a,emu.memType.nesPpuDebug)end
 for a=0x3f00,0x3f0f do t[#t+1]=emu.read(a,emu.memType.nesPpuDebug)end
 for a=0x200,0x2ff do t[#t+1]=emu.read(a,emu.memType.nesDebug)end
 return t
end
local function image(tag)
 local st=emu.getState();local buf=emu.getScreenBuffer();assert(#buf==61440)
 local f=assert(io.open(OUTPUT..tag..'.rgba','wb'))
 for i=1,#buf,8 do f:write(string.pack('<I4I4I4I4I4I4I4I4',table.unpack(buf,i,i+7)))end
 f:close();captures=captures+1
end
emu.addMemoryCallback(function()
 if emu.convertAddress(L.Z2PanelTick).address//8192~=B.Z2PanelTick then return end
 if r('GamePauseStatus')&1~=0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==1 and r('Mirror_PPUMASK')&0x18==0 and r('VRAM_Buffer1_Offset')==0 and r('VRAM_Buffer_AddrCtrl')==0 then
  before=snapshot();oldchr=r('CurrentCHRBank',11);oldmode=r('X5ChrMode',11);opens=opens+1
 end
end,emu.callbackType.exec,L.Z2PanelTick)
emu.addMemoryCallback(function(_,value)
 if value~=0 or not before then return end
 local after=snapshot()
 for i=1,#before do assert(before[i]==after[i],'Pause restore byte '..i..' '..before[i]..'/'..after[i])end
 assert(r('CurrentCHRBank',11)==oldchr and r('X5ChrMode',11)==oldmode,'Original background CHR ownership restored')
 before=nil;restores=restores+1
end,emu.callbackType.write,L.Z2PanelActive)
emu.addEventCallback(function()
 local b={}
 if phase==0 then
  b.start=frame>=60 and frame%12==0
  if frame>=60 and r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and frame%12==0 then
  local i=r('CrossoverMenuIndex')
  if i~=4 then b.right=true
  elseif r('Z2Variant')~=1 then b.select=true
  else b.a=true;phase=2 end
 elseif entered then
  local t=frame-entered
  b.start=t==20
  b.down=t==36 or t==66
  b.right=t==46
  b.a=t==78 or t==192
  b.b=t==112 or t==152
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==4 and r('Z2Variant')==1)
  entered=frame;phase=3
 end
 if entered then
  local t=frame-entered
  if t==10 then
   w('Z2ExpLo',0);w('Z2ExpHi',0);w('Z2ExpPendingLo',0);w('Z2ExpPendingHi',0)
   w('Z2LearnedSpells',5);w('Z2Selection',0);w('Z2UiCursor',0)
   for i=0,127 do otherRecords[i]=(i*37+19)%256;emu.write(0x5e80+i,otherRecords[i],emu.memType.nesDebug)end
  end
  if t==32 then assert(r('GamePauseStatus')&1==1 and r('Z2PanelActive')==1,'Start opens full panel');image('upgrades')end
  if t==42 then assert(r('Z2UiCursor')==1,'Down selects Magic')end
  if t==60 then assert(r('Z2UiState')&1==0,'Right switches to spell page');image('spells')end
  if t==72 then assert(r('Z2Selection')&7==2,'Spell navigation skips locked Jump');image('life-selected')end
  if t==90 then
   assert(r('GamePauseStatus')&1==0 and restores==1,'A confirms spell and restores world')
   image('resumed')
   w('Z2ExpLo',50)
  end
  if t==106 then assert(r('GamePauseStatus')&1==1 and r('Z2UiCursor')==2,'EXP50 offers Life');image('life-upgrade')end
  if t==130 then
   assert(r('GamePauseStatus')&1==0 and r('Z2DeferredMask')==4 and restores==2,'Cancel advances from50to100 without permanently suppressing upgrades')
   w('Z2ExpLo',100)
  end
  if t==146 then assert(r('GamePauseStatus')&1==1 and r('Z2UiCursor')==1,'EXP100 offers Magic after deferral');image('magic-upgrade')end
  if t==170 then
   assert(r('GamePauseStatus')&1==0 and r('Z2DeferredMask')==6 and restores==3,'Second cancellation advances to Attack200')
   w('Z2ExpLo',200)
  end
  if t==186 then assert(r('GamePauseStatus')&1==1 and r('Z2UiCursor')==0,'EXP200 offers Attack');image('attack-upgrade')end
  if t==210 then
   for i=0,127 do assert(emu.read(0x5e80+i,emu.memType.nesDebug)==otherRecords[i],'Pause leaves other character records untouched at '..i)end
   assert(r('GamePauseStatus')&1==0 and restores==4 and r('Z2LevelsLo')&7==1 and r('Z2ExpLo')==0 and r('Z2DeferredMask')==0,'Purchase deducts200, raises Attack and resets deferrals')
   local f=assert(io.open(OUTPUT..'proof.json','w'))
   f:write(string.format('{"passed":true,"cold_menu":true,"seeded_RPG":true,"opens":%d,"exact_world_restores":%d,"physical_images":%d,"frames":%d}\n',opens,restores,captures,frame));f:close()
   print('PASS full Zelda II pause panel, stats/spell navigation, lock skipping and exact PPU/OAM/CHR restoration');emu.stop(0)
  end
 end
 if frame>1800 then error('Z2 pause timeout '..phase)end
end,emu.eventType.endFrame)
