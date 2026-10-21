-- Explicit arena fixtures, not a controller-only level clear. Cane and pogo
-- still execute through the real controller and world collision handlers.
local frame=0
local broken,blockSfx,pogoBounce=false,false,false
local rewardSpawned=false
local case=''
local seams={}
for _,dir in ipairs({1,2})do
 for x=0,255 do if x<=8 or x>=232 then seams[#seams+1]={x=x,dir=dir}end end
end
local seamHits={}
local seamIndex=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function reset(tile,terrain)
 case='cane'
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmBrickHealth',0,i);w('MmSolidTerrain',0,i);w('RgMeleeBlocks',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('TimerControl',0)
 w('BlockBounceTimer',0);w('InjuryTimer',0);w('StarInvincibleTimer',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Block_Buffer_1',tile,167);w('MmSolidTerrain',terrain or 0,167)
end
emu.addMemoryCallback(function(a,v)
 if(case=='cane-brick' and a==L.NoiseSoundQueue and(v&1)~=0)
  or(case=='question' and a==L.Square2SoundQueue and(v&2)~=0)then blockSfx=true end
end,emu.callbackType.write,L.NoiseSoundQueue,L.Square1SoundQueue)
emu.addMemoryCallback(function(_,v)
 if case=='question' and v==0x2e then rewardSpawned=true end
end,emu.callbackType.write,L.Enemy_ID,L.Enemy_ID+5)
emu.addMemoryCallback(function(_,v)if case=='cane-brick' and v~=0 then broken=true end end,emu.callbackType.write,L.Block_State,L.Block_State+1)
emu.addMemoryCallback(function(_,v)
 if case~='seam' then return end
 local pc=emu.getState()['cpu.pc']
 if pc~=L.CaneY and pc~=L.CaneY+3 then return end
 local q=assert(seams[seamIndex])
 assert(r('Player_X_Position')==q.x and r('Player_PageLoc')==1 and r('PlayerFacingDir')==q.dir,'Seam probe uses the requested actual player position and direction')
 local target=256+q.x+(q.dir==1 and 24 or -8)
 assert(r('MmBulletX')==target%256 and v==target//256,'Cane keeps the exact 16-bit position across page seams: x='..q.x..' dir='..q.dir..' target='..target..' got='..(256*v+r('MmBulletX')))
 seamHits[seamIndex]=true
end,emu.callbackType.write,L.MmBulletPage)
emu.addEventCallback(function()
 local down=frame==80 or(frame>=1060 and frame<1170)
 local b=(frame>=640 and frame<644)or(frame>=760 and frame<764)or(frame>=880 and frame<884)
  or(frame>=1000 and frame<1004)or(frame>=1060 and frame<1170)
 if frame>=1200 and frame<1200+20*#seams then b=(frame-1200)%20>=4 and(frame-1200)%20<8 end
 emu.setInput({down=down,right=frame==100 or frame==120,start=frame==200,b=b},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==620 then assert(r('SelectedCharacter')==12 and r('GameEngineSubroutine')==8,'Scrooge enters the arena');reset(0x51);case='cane-brick';blockSfx=false end
 if frame==690 then
  assert(r('Block_Buffer_1',167)~=0x51,'Scrooge cane breaks ordinary brick')
  assert(broken and blockSfx,'Cane brick hit emits native fragment state and SFX')
  print('PASS Scrooge cane ordinary brick, fragments and hit sound')
 end
 if frame==740 then reset(0xc1);case='question';blockSfx=false;rewardSpawned=false end
 if frame==810 then
  assert(r('Block_Buffer_1',167)~=0xc1,'Cane activates a question block')
  -- Native20px body contact can collect this adjacent low mushroom once
  -- emergence finishes. Observe its actual spawn instead of requiring the
  -- object to remain uncollected50frames after the hit.
  assert(rewardSpawned and blockSfx,'Cane question hit spawns an actual native power-up with sound')
  print('PASS Scrooge question activation produces native power-up and sound')
 end
 if frame==860 then reset(0x54);case='ground' end
 if frame==930 then assert(r('Block_Buffer_1',167)==0x54,'Cane preserves ground');print('PASS Scrooge cane preserves ground')end
 if frame==980 then reset(0x52,1);case='terrain' end
 if frame==1050 then assert(r('Block_Buffer_1',167)==0x52,'Cane preserves native underground terrain sharing a brick metatile');print('PASS Scrooge cane protected underground masonry')end
 if frame==1060 then
  reset(0);case='pogo';w('Player_X_Position',112);w('Player_Y_Position',112);w('Player_State',2)
  w('Player_Y_Speed',1);w('MmVY',1,2)
 end
 if frame>=1061 and frame<1170 and r('ScPogo')~=0 and r('MmVY',2)>=128 then pogoBounce=true end
 if frame==1170 then assert(pogoBounce,'Holding Down+B pogo bounces from real ground');print('PASS Scrooge Down+B pogo reaches ground and rebounds')end
 if frame==1180 then
  assert(r('ScPogo')==0,'Releasing Down+B cancels pogo')
  assert(r('GameEngineSubroutine')==8,'Scrooge remains playable after cane and pogo interactions')
  print('PASS Scrooge release cancels pogo and gameplay remains active')
 end
 if frame>=1200 and frame<1200+20*#seams and(frame-1200)%20==0 then
  seamIndex=(frame-1200)//20+1
  local q=seams[seamIndex];reset(0);case='seam'
  w('Player_X_Position',q.x);w('Player_PageLoc',1);w('PlayerFacingDir',q.dir)
  local camera=256+q.x-96
  w('ScreenLeft_X_Pos',camera%256);w('ScreenLeft_PageLoc',camera//256)
  w('ScreenRight_X_Pos',(camera+255)%256);w('ScreenRight_PageLoc',(camera+255)//256)
 end
 if frame==1200+20*#seams then
  for i=1,#seams do assert(seamHits[i],'Each seam position/direction actually executes a cane attack: '..i)end
  print('PASS Scrooge cane 66 real attacks across both directions and every x=0..8 /232..255 page seam')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
