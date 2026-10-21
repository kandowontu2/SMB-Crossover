-- Explicit flat arenas in four actual loaded area themes. Ordinary B creates
-- every seed; completed hardware DMA, mapped CHR and actual PPU colors are
-- compared to raw pinned SWF bitmap/mask pixels, independently of CHR packing.
local ref=dofile(TEST_DIR..'fixtures/flame-source-pixels.lua')
local char=FLAME_CHARACTER or 1
local theme=FLAME_THEME or 2
local themes={{1,1,2,0},{0,0,0,1},{0,1,2,2},{0,3,4,3}}
local frame,age,phase=0,0,0
local drawing,parts,ready,dma=false,{},nil,false
local checks,chrParts,starChecks,seedChecks,recoveryChecks=0,0,0,0,0
local seen,allSeen={},{}
local born,flame,updates=0,nil,0
local mmc5=ROM_NAME:find('mmc5')~=nil
local cases={{face=0},{face=3},{face=1},{face=2}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
local function ppu(a,state)
 if mmc5 and a<8192 then return emu.read(assert(state['mapper.chrBanks'..(a//1024)])*1024+a%1024,emu.memType.nesChrRom)end
 return emu.read(a,emu.memType.nesPpuDebug)
end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 local face=phase%4
 w('Player_X_Position',face==1 and 64 or face==2 and 64 or 32);w('Player_PageLoc',face==2 and 1 or 0)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',face==2 and 2 or 1)
 w('ScreenLeft_X_Pos',face==2 and 192 or 0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',face==2 and 191 or 255);w('ScreenRight_PageLoc',face==2 and 1 or 0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('PlayerStatus',math.max(1,phase//4));w('PlayerSize',0);w('InvOwnedLo',65,char);w('InvSelected',6,char);w('InvAmmo',112,char*16+6);w('InvDirty',1)
 w('SsBodyStop',0);w('SsFreeze',0);w('SsLastPalette',0);w('StarInvincibleTimer',0)
 w('TimerControl',0);w('GuestPowerupActive',0)
 if face==1 then for row=9,10 do w('Block_Buffer_1',0x61,row*16+8)end
 elseif face==2 then for row=9,10 do w('Block_Buffer_1',0x61,208+row*16)end
 elseif face==3 then w('Block_Buffer_1',0x61,6*16+5)end
 age=0;seen={};born=0;flame=nil;updates=0;parts={};ready=nil;dma=false
end
emu.addEventCallback(function()
 emu.setInput({down=char==9 and frame==80,right=(char==1 and frame==80)or(char==9 and(frame==100 or frame==120 or frame==140)),start=frame==200,b=frame>=550 and age>=10 and age<16},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==60 and flame and r('RgShotType',flame)==16 then updates=updates+1 end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if frame<550 or r('CurrentBank')%128~=60 then return end
 drawing=true;parts={}
end,emu.callbackType.exec,L.SpecialDrawShots)
emu.addMemoryCallback(function()
 if not drawing or r('CurrentBank')%128~=4 then return end
 local slot=r('RgSlot');local typ=r('RgShotType',slot)
 if typ~=15 and typ~=16 then return end
 local ptr=r('R0')+256*r('R1');local count=emu.read(ptr,emu.memType.nesDebug)
 local start=r('CurrentOAMOffset');if start+count>=256 then return end
 local art=r('SsArt',slot);if not ref[art]then return end
 local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 local x=r('R4')+256*r('R5');if x>=32768 then x=x-65536 end
 local y=r('R6')+256*(r('R7')-1)
 local shot={x=x,y=y+1,art=art,dir=r('RgShotDir',slot),parts={},star=r('StarInvincibleTimer')>0,phase=phase}
 for i=0,count//4-1 do
  local p=ptr+1+(count//4-1-i)*4
  local py=y+signed(emu.read(p+2,emu.memType.nesDebug));local px=x+signed(emu.read(p+3,emu.memType.nesDebug))
  if px>=0 and px<256 and py>=0 and py<240 then
   shot.parts[#shot.parts+1]={o=(start+rotation+i*4)%256,t=emu.read(p,emu.memType.nesDebug),a=emu.read(p+1,emu.memType.nesDebug),y=py,x=px}
  end
 end
 if #shot.parts>0 then parts[#parts+1]=shot end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==60 then drawing=false end end,emu.callbackType.exec,L.SpecialDrawFinish)
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==4 then ready=parts end end,emu.callbackType.exec,L.RosterOamReady)
emu.addMemoryCallback(function()if frame>=550 then dma=ready end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 if not dma then return end
 local committed=dma;dma=false
 local state=mmc5 and emu.getState()or nil;local cache={}
 local function chr(a)if cache[a]==nil then cache[a]=ppu(a,state)end;return cache[a]end
 for _,shot in ipairs(committed)do
  if shot.phase==phase then
   local actual={}
   table.sort(shot.parts,function(a,b)return a.o>b.o end)
   for _,p in ipairs(shot.parts)do
    local o=p.o
    local y,t,a,x=emu.read(o,emu.memType.nesSpriteRam),emu.read(o+1,emu.memType.nesSpriteRam),emu.read(o+2,emu.memType.nesSpriteRam),emu.read(o+3,emu.memType.nesSpriteRam)
    assert(y==p.y and t==p.t and a==p.a and x==p.x,'Flame completed DMA matches renderer OAM contract')
    local address=(t&1)*4096+(t&254)*16
    for dy=0,15 do for dx=0,7 do
     local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx
     local off=address+(row//8)*16+row%8
     local color=((chr(off)>>col)&1)+2*((chr(off+8)>>col)&1)
     if color>0 then actual[(y+1+dy-shot.y)*128+x+dx-shot.x]=emu.read(16+(a&3)*4+color,emu.memType.nesPaletteRam)&63 end
    end end
    chrParts=chrParts+1
   end
   local expected={};local pic=ref[shot.art];local colors={b=15,r=22,o=39}
   for y,row in ipairs(pic.rows)do for x=1,#row do
    local c=colors[row:sub(x,x)]
    if c then local px=pic.x+x-1;if shot.dir==2 then px=-px-1 end;expected[(pic.y+y-1)*128+px]=c end
   end end
   for k,v in pairs(expected)do assert(actual[k]==v,string.format('Source Flame pixels char%d theme%d power%d face%d art%d star%s frame%d key%d expected%02x got%s',char,theme,phase//4,phase%4,shot.art,tostring(shot.star),frame,k,v,tostring(actual[k])))end
   for k in pairs(actual)do assert(expected[k],'No extra non-source Flame pixels at '..frame..' art'..shot.art..' key'..k)end
   seen[shot.art]=true;allSeen[shot.art]=true;checks=checks+1
   if shot.star then starChecks=starChecks+1 elseif age>=45 then recoveryChecks=recoveryChecks+1 end
   if shot.art==22 then seedChecks=seedChecks+1 end
  end
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then local t=themes[theme+1];w('WorldNumber',t[1]);w('LevelNumber',t[2]);w('AreaNumber',t[3])end
 if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==char and r('AreaType')==theme,'Actual menu character and native theme');setup();return end
 age=age+1
 for i=0,5 do w('Enemy_Flag',0,i)end
 if age==26 then w('StarInvincibleTimer',6)end
 if age==45 then w('StarInvincibleTimer',0)end
 for i=0,9 do
  -- Power0 cannot launch specials. A controller-created live projectile is
  -- retained while this explicit fixture changes the player's power form.
  if phase<4 and r('RgShotType',i)==15 then w('PlayerStatus',0)end
  if phase%4==3 and r('RgShotType',i)==15 and born==0 then
   w('RgShotX',80,i);w('RgShotPage',0,i);w('RgShotY',160,i);w('RgShotVXLo',0,i);w('RgShotVXHi',0,i);w('RgShotVYLo',0,i);w('RgShotVYHi',-4,i);born=1
  end
  if r('RgShotType',i)==16 and not flame then flame=i;assert(r('SsMode',i)==cases[phase%4+1].face,'Source contact orientation')end
 end
 if age==100 then
  assert(flame and updates==45,'All15 source frames complete45 updates; char'..char..' theme'..theme..' phase'..phase..' slot'..tostring(flame)..' updates'..updates)
  local first=phase%4==0 and 23 or phase%4==1 and 100 or phase%4==2 and 70 or 85
  for art=first,first+14 do assert(seen[art],'Every source phase reaches actual DMA, art'..art..' phase'..phase)end
  assert(seen[22],'Seed source colors checked before contact, phase'..phase)
  phase=phase+1
  if phase==12 then
   assert(checks>300 and starChecks>100 and seedChecks>=12 and recoveryChecks>=12,'Meaningful completed DMA/source/star coverage: '..checks..'/'..starChecks..'/'..seedChecks..'/'..recoveryChecks)
   local n=0;for _ in pairs(allSeen)do n=n+1 end;assert(n==61,'All61 raw source frames checked')
   print(string.format('PASS Flame source colors/pixels char%d nativeTheme%d all3powerforms all4surfaces staron/off: %d DMA images, %d hardware parts, %d invincibility images, %d recovery images, all61 source frames',char,theme,checks,chrParts,starChecks,recoveryChecks));emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
