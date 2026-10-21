-- Actual impact, completed DMA, mapped CHR and PPU colors compared with raw
-- pinned2.02 white masks. These explicit arenas are not traversal evidence.
local ref=dofile(TEST_DIR..'fixtures/megaman-bass-injury-source-pixels.lua')
local pickup=dofile(TEST_DIR..'fixtures/bass-pickup-pixels.lua')[3]
local char=HURT_CHARACTER or 1
local theme=HURT_THEME or 2
local themes={{1,1,2},{0,0,0},{0,1,2},{0,3,4}}
local frame,phase,age=0,0,0
local started,drawing,expected,calls,parts,ready,dma,caseSeen
local images,pieces,pickupImages,recoveryFrames=0,0,0,0
local recoveryReturn=false
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
local function ppu(a,s)
 if mmc5 and a<8192 then return emu.read(s['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)end
 return emu.read(a,emu.memType.nesPpuDebug)
end
local function setup()
 age=0;started=false;caseSeen={};parts={};ready=nil;dma=nil;drawing=false
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local py=phase<4 and 176 or 64
 w('Player_X_Position',96);w('Player_PageLoc',1);w('Player_Y_Position',py);w('Player_Y_HighPos',1)
 if phase>=4 then w('MmYFraction',192,1)end
 w('Player_State',phase<4 and 0 or 2);w('PlayerStatus',1);w('PlayerSize',0);w('PlayerFacingDir',phase%4<2 and 1 or 2)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmLastXSpeed',0);w('Player_CollisionBits',3)
 w('PlayerOutlinesOff',phase%2);w('SavedJoypadBits',0);w('A_B_Buttons',0);w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('GuestPowerupActive',0);w('MmDeathFlag',0)
 w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('MmSliding',0);w('XgDash',0);w('SsFreeze',0);w('SsBodyStop',0)
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',104);w('Enemy_PageLoc',1);w('Enemy_Y_Position',py+8);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 -- A static, distant Super Arm icon must coexist with every injury image.
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',128,5);w('PowerUpType',1,5)
 w('Enemy_X_Position',160,5);w('Enemy_PageLoc',1,5);w('Enemy_Y_Position',88,5);w('Enemy_Y_HighPos',1,5);w('Enemy_SprAttrib',0,5)
 w('InvPickup',1,5);w('InvPickupOwner',char,5)
end
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==10 then started=true end end,emu.callbackType.exec,L.MegaManHurtStart)
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==10 then recoveryReturn=true end end,emu.callbackType.exec,L.MegaManHurtEnd)
emu.addMemoryCallback(function()
 if recoveryReturn and r('CurrentBank')%128==10 then
  recoveryReturn=false
  assert(r('PlayerChrBank')==(char==1 and 64 or 224),'End event restores the ordinary buster/body window before any recovery shot')
 end
end,emu.callbackType.exec,L.MegaManHurtReturned)
emu.addMemoryCallback(function()
 if frame<550 or r('CurrentBank')%128~=10 then return end
 drawing=true;parts={};expected={};calls=0
 local ticks=r('GuestHurtTicks')
 if ticks==0 then
  assert(r('PlayerChrBank')~=0x81 and r('PlayerChrBank')~=0x82,'No private hurt bank survives the recovery event')
  recoveryFrames=recoveryFrames+1;return
 end
 local t=27-ticks
 local visible=(math.floor(t*5/21)%2)==0
 assert((r('GuestHurtVisible')~=0)==visible,'Source70ms retained flicker phase')
 local x=r('Player_X_Position')+256*(r('Player_PageLoc')-r('ScreenLeft_PageLoc'))-r('ScreenLeft_X_Pos')
 local y=r('Player_Y_Position')+256*(r('Player_Y_HighPos')-1)
 local fraction=(r('MmYFraction')+256*r('MmYFraction',1))/65536
 local feet=y+32
 if not visible then expected[#expected+1]={art=0,x=x+8,y=math.floor(feet+fraction-ref.displayHeight/2)}end
 if t<24 then
  local art=1+math.floor(t*5/39)
  for _,p in ipairs({{-12,-4},{0,-7},{12,-4}})do expected[#expected+1]={art=art,x=x+8+p[1],y=math.floor(feet+fraction-ref.displayHeight+p[2])}end
 end
end,emu.callbackType.exec,L.MegaManHurtDraw)
emu.addMemoryCallback(function()
 if not drawing or r('CurrentBank')%128~=4 then return end
 calls=calls+1;local e=assert(expected[calls],'No extra effect outside source splash/spark lifetime')
 assert(r('SmTemp')==e.art,'Exact130ms source spark frame')
 local x=r('R4')+256*r('R5');if x>=32768 then x=x-65536 end
 local y=r('R6')+256*(r('R7')-1)
 assert(x==e.x and y==e.y,'Source effect follows actual body center/head, independently of facing')
 local ptr=r('R0')+256*r('R1');local count=emu.read(ptr,emu.memType.nesDebug)
 local start=r('CurrentOAMOffset');assert(start+count<256,'Injury effect fits the actual OAM reservation')
 local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 local rec={x=x,y=y,art=e.art,phase=phase,parts={}}
 for i=0,count//4-1 do
  local p=ptr+1+(count//4-1-i)*4
  rec.parts[#rec.parts+1]={o=(start+rotation+i*4)%256,t=emu.read(p,emu.memType.nesDebug),a=emu.read(p+1,emu.memType.nesDebug),x=x+signed(emu.read(p+3,emu.memType.nesDebug)),y=y+signed(emu.read(p+2,emu.memType.nesDebug))}
 end
 parts[#parts+1]=rec
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==10 and drawing then assert(calls==#expected,'Every live splash/spark is emitted');drawing=false end
end,emu.callbackType.exec,L.MegaManHurtDrawFinish)
emu.addMemoryCallback(function()if frame>=550 and r('CurrentBank')%128==4 then ready={parts=parts,phase=phase,ticks=r('GuestHurtTicks')}end end,emu.callbackType.exec,L.RosterOamReady)
emu.addMemoryCallback(function()if frame>=550 then dma=ready end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 if not dma then return end
 local committed=dma;dma=nil;if committed.phase~=phase then return end
 local s=mmc5 and emu.getState()or nil;local cache={}
 local function chr(a)if cache[a]==nil then cache[a]=ppu(a,s)end;return cache[a]end
 local function glyph(t,a)
  local pixels={};local base=(t&1)*4096+(t&254)*16
  for dy=0,15 do for dx=0,7 do
   local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx
   local off=base+(row//8)*16+row%8;local c=((chr(off)>>col)&1)+2*((chr(off+8)>>col)&1)
   if c>0 then pixels[dy*8+dx]=emu.read(16+(a&3)*4+c,emu.memType.nesPaletteRam)&63 end
  end end;return pixels
 end
 for _,rec in ipairs(committed.parts)do
  local actual={}
  for _,p in ipairs(rec.parts)do
   local y,t,a,x=emu.read(p.o,emu.memType.nesSpriteRam),emu.read(p.o+1,emu.memType.nesSpriteRam),emu.read(p.o+2,emu.memType.nesSpriteRam),emu.read(p.o+3,emu.memType.nesSpriteRam)
   assert(y==p.y and t==p.t and a==p.a and x==p.x,'Completed DMA preserves injury sprite data')
   for k,v in pairs(glyph(t,a))do actual[(y+k//8-rec.y)*128+x+k%8-rec.x]=v end
   pieces=pieces+1
  end
  local pic=ref.pictures[rec.art];local want={}
  for yy,row in ipairs(pic.rows)do for xx=1,#row do if row:sub(xx,xx)~='.'then want[(pic.y+yy-1)*128+pic.x+xx-1]=48 end end end
  for k,v in pairs(want)do assert(actual[k]==v,'Exact source white injury pixels char'..char..' theme'..theme..' art'..rec.art..' key'..k..' actual'..tostring(actual[k]))end
  for k in pairs(actual)do assert(want[k],'No extra non-source injury pixels')end
  caseSeen[rec.art]=true;images=images+1
 end
 if committed.ticks>0 then
  local icon={};for i=1,256 do icon[i]=255 end
  for o=252,0,-4 do
   local y,t,a,x=emu.read(o,emu.memType.nesSpriteRam),emu.read(o+1,emu.memType.nesSpriteRam),emu.read(o+2,emu.memType.nesSpriteRam),emu.read(o+3,emu.memType.nesSpriteRam)
   if x<176 and x+8>160 and y<112 and y+16>96 then
    for k,v in pairs(glyph(t,a))do local px,py=x+k%8,y+k//8;if px>=160 and px<176 and py>=96 and py<112 then icon[(py-96)*16+px-160+1]=v end end
   end
  end
  for i,v in ipairs(pickup)do
   if icon[i]~=v then
    print('PICKUP diagnostic age'..age..' sourceY'..r('Enemy_Y_Position',5)..' flag'..r('Enemy_Flag',5)..' private'..r('InvPickup',5)..' owner'..r('InvPickupOwner',5)..' bank'..r('SsChrPhysical')..' active'..r('SsChrActive'))
    for o=0,252,4 do local px=emu.read(o+3,emu.memType.nesSpriteRam);if px>=152 and px<184 then print('OAM '..o..' y'..emu.read(o,emu.memType.nesSpriteRam)..' t'..emu.read(o+1,emu.memType.nesSpriteRam)..' a'..emu.read(o+2,emu.memType.nesSpriteRam)..' x'..px)end end
   end
   assert(icon[i]==v,'Private pickup source pixels coexist with player-window injury FX frame'..frame..' tick'..committed.ticks..' index'..i..' expected'..v..' actual'..icon[i])
  end
  pickupImages=pickupImages+1
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 emu.setInput({down=char==9 and frame==80,right=(char==1 and frame==80)or(char==9 and(frame==100 or frame==120 or frame==140)),start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then local p=themes[theme+1];w('WorldNumber',p[1]);w('LevelNumber',p[2]);w('AreaNumber',p[3])end
 if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==char and r('AreaType')==theme,'Actual selected character and loaded native theme');setup();return end
 age=age+1;if started then w('Enemy_Flag',0)end
 if age==100 then
  assert(started,'Actual body injury');for i=0,3 do assert(caseSeen[i],'All raw source injury frames reach actual DMA')end
  phase=phase+1
  if phase==8 then
   assert(images>400 and pickupImages>=140 and recoveryFrames>=200,'Meaningful source/DMA/pickup/recovery coverage')
   print('PASS injury source pixels char'..char..' theme'..theme..' both directions/outlines, ground/air fractional anchors: '..images..' DMA images, '..pieces..' hardware parts, '..pickupImages..' concurrent pickup images and '..recoveryFrames..' clean recovery frames');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
