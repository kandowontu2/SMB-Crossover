-- Controller-created Flame Blast seeds against real native map cells.
-- Ceiling case gives that real seed an explicit upward test velocity;
-- the other faces use its unmodified source launch/acceleration.
local frame,age,phase=0,0,0
local appeared,flame,updates=0,nil,0
local cases={{face=0,x=64,page=0,y=208},{face=3,x=128,page=0,y=176},
 {face=1,x=16,page=1,y=176},{face=2,x=80,page=0,y=144}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 local c=cases[phase+1]
 w('Player_X_Position',phase==1 and 64 or phase==2 and 64 or 32);w('Player_PageLoc',phase==2 and 1 or 0)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',phase==2 and 2 or 1)
 w('ScreenLeft_X_Pos',phase==2 and 192 or 0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',phase==2 and 191 or 255);w('ScreenRight_PageLoc',phase==2 and 1 or 0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('PlayerStatus',1);w('InvOwnedLo',65,9);w('InvSelected',6,9);w('InvAmmo',112,150);w('InvDirty',1)
 w('SsBodyStop',0);w('SsFreeze',0)
 if phase==1 then for row=9,10 do w('Block_Buffer_1',0x61,row*16+8)end
 elseif phase==2 then for row=9,10 do w('Block_Buffer_1',0x61,208+row*16)end
 elseif phase==3 then w('Block_Buffer_1',0x61,6*16+5)end
 age=0;appeared=0;flame=nil;updates=0
end
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==60 and flame and r('RgShotType',flame)==16 then updates=updates+1 end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=550 and age>=10 and age<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 for i=0,9 do
  if phase==3 and r('RgShotType',i)==15 and appeared==0 then
   -- Isolate source ceiling collision independently of launch direction.
   w('RgShotX',80,i);w('RgShotPage',0,i);w('RgShotY',160,i);w('RgShotVXLo',0,i);w('RgShotVXHi',0,i);w('RgShotVYLo',0,i);w('RgShotVYHi',-4,i);appeared=1
  end
  if r('RgShotType',i)==16 and not flame then
   flame=i;appeared=age
   assert(r('SsMode',i)==cases[phase+1].face,'Flame orientation matches the contacted surface: '..phase..'/'..r('SsMode',i))
   if phase==0 then assert(r('RgShotY',i)==208,'Floor flame sits on the top surface')
   elseif phase==1 then assert(r('RgShotX',i)==128 and r('RgShotPage',i)==0,'Left-pointing flame sits at wall left')
   elseif phase==2 then assert(r('RgShotX',i)==16 and r('RgShotPage',i)==1,'Right-pointing flame sits at wall right across page parity')
   else assert(r('RgShotY',i)==144,'Ceiling flame sits at the bottom surface')end
  end
 end
 if flame and age==appeared+8 then
  local expected=phase==0 and L.SS_ART_FLAME25 or phase==1 and L.SS_ART_FLAME27025 or phase==2 and L.SS_ART_FLAME9025 or L.SS_ART_FLAME18025
  assert(r('SsArt',flame)>=expected and r('SsArt',flame)<expected+15,'Flame uses rotated source artwork')
  local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-flame-face-'..phase..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if age==100 then
  assert(flame and updates==45,'Flame appears and completes exactly fifteen 50ms animation frames: '..tostring(flame)..'/'..updates)
  phase=phase+1
  if phase==4 then print('PASS Flame Blast source pivot, all four contact orientations, rotated art and 45-update lifetime');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
