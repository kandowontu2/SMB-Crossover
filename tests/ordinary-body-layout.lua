-- Independent immutable30 pose/CHR reference. Explicit art inputs only;
-- compare the completed DMA composite before scanline selection. Ordinary
-- controller crowd/first-eight pressure is measured separately.
local ref=dofile(TEST_DIR..'fixtures/ordinary-body-composite-v30.lua')
local char=LAYOUT_CHARACTER or 9
local frame,ci,interruptDepth=0,0,0
local c,pending,drawn,helperCall,helperResult,unfilteredPtr
local checks,selectedChecks,fallbackChecks=0,0,0
local cases={}
local locations={{16,176},{15,176},{224,176},{225,176},{96,16},{96,15},{96,207},{96,208},{96,-10},{96,256},{16,176,240},{15,176,240},{224,176,240},{225,176,240}}
local roles=char==9 and{'bass'}or{'bill','lance'}
local poses=char==9 and{1,3,13}or{2}
local function append(role,pose,power,dir,off,star,loc)
 cases[#cases+1]={role=role,pose=pose,power=power,dir=dir,off=off,star=star,x=loc[1],y=loc[2],camera=loc[3]or 0}
end
for _,role in ipairs(roles)do for _,pose in ipairs(poses)do for power=0,2 do for _,dir in ipairs({1,2})do for off=0,1 do for star=0,1 do for _,loc in ipairs(locations)do append(role,pose,power,dir,off,star,loc)end end end end end
 for _,dir in ipairs({1,2})do for off=0,1 do
  for x=0,5 do append(role,pose,1,dir,off,0,{x,176})end
  for y=-25,-1 do append(role,pose,1,dir,off,0,{96,y})end
 end end
end end
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function side()return c.dir==1 and'Right'or'Left'end
local function optimized()
 return(c.role=='bass'or c.role=='bill'and c.power<2)and c.x>=16 and c.x<=224 and c.y>=16 and c.y<=207
end
local function artInputs()
 local world=256+c.camera+c.x
 w('Player_X_Position',world);w('Player_PageLoc',math.floor(world/256));w('Player_Y_Position',c.y);w('Player_Y_HighPos',1+math.floor(c.y/256))
 w('ScreenLeft_X_Pos',c.camera);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',c.camera+255);w('ScreenRight_PageLoc',1+math.floor((c.camera+255)/256))
 w('PlayerFacingDir',c.dir);w('PlayerStatus',c.power);w('BillVariant',c.role=='lance'and 1 or 0);w('PlayerOutlinesOff',c.off)
 w('RgPose',c.pose);w('StarInvincibleTimer',c.star==1 and 12 or 0)
 helperCall=nil;helperResult=nil;unfilteredPtr=nil
end
local function setup()
 pending=nil;drawn=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('FloateyNum_Control',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i);w('InvDropKind',0,i)end
 w('InvSelected',0,char);w('SsHeld',0);w('SsFreeze',0);w('SsBodyStop',0);w('RgShootPose',0)
 w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0);w('InjuryTimer',0);w('TimerControl',0)
 w('GameEngineSubroutine',8);w('ScrollLock',1);w('AreaParserTaskNum',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0);w('MmDeathFlag',0)
end
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=math.max(0,interruptDepth-1)end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()
 if c and interruptDepth==0 and r('CurrentBank')%128==(char==9 and 30 or 22)then artInputs()end
end,emu.callbackType.exec,char==9 and L.ExpandedPose or L.RosterPose)
emu.addMemoryCallback(function()
 if c and interruptDepth==0 and r('CurrentBank')%128==10 then local s=emu.getState();helperCall={x=s['cpu.x'],y=s['cpu.y'],offset=r('ObjectOffset')}end
end,emu.callbackType.exec,L.OrdinaryLowPressurePose)
local function helperEnd(selected)
 if not c or interruptDepth~=0 or r('CurrentBank')%128~=10 then return end
 local s=emu.getState();assert(helperCall,'Helper has an actual entry')
 assert(s['cpu.x']==helperCall.x and s['cpu.y']==helperCall.y and r('ObjectOffset')==helperCall.offset,'Layout helper preserves X/Y/ObjectOffset')
 assert(selected==optimized(),'Exact conservative guard decision')
 if selected then assert(s['cpu.a']==r('SmPosePtr',1),'Selected helper returns real pointer high in A after PLY/PLX')end
 helperResult=selected
end
emu.addMemoryCallback(function()helperEnd(true)end,emu.callbackType.exec,L.OrdinaryPoseSelected)
emu.addMemoryCallback(function()helperEnd(false)end,emu.callbackType.exec,L.OrdinaryPoseOriginal)
emu.addMemoryCallback(function()
 if c and interruptDepth==0 and r('CurrentBank')%128==4 and emu.getState()['cpu.y']==0 then drawn=true end
end,emu.callbackType.exec,L.DrawMetasprite)
emu.addMemoryCallback(function()
 if c and drawn and interruptDepth==0 and r('CurrentBank')%128==10 then unfilteredPtr=r('R0')+256*r('R1')end
end,emu.callbackType.exec,L.PlayerRemoveOutlines)
emu.addMemoryCallback(function()
 if not c or not drawn or interruptDepth~=0 or r('CurrentBank')%128~=4 then return end
 drawn=false;local ptr=r('R0')+256*r('R1');local wanted
 if optimized()then
  local n=c.role=='bill'and'OrdBillWalk2'or(c.pose==3 and'OrdBassWalk3'or'OrdBassWalk1')
  wanted=L[n..side()];selectedChecks=selectedChecks+1
  assert(helperResult==true,'Optimized pose used its successful helper receipt')
  assert(r('PlayerChrBank')==(c.role=='bill'and 0x1d or(c.pose==3 and 0xe1 or 0x83)),'Selected actual player CHR bank')
 else
  local prefix=c.role=='bass'and'XgBASS'or(c.role=='bill'and'RgBILL'or'RgLANCE')
  local stride=c.role=='bass'and 84 or 48;local i=c.power*stride+c.pose
  wanted=emu.read(L[prefix..side()..'Lo']+i,emu.memType.nesDebug)+256*emu.read(L[prefix..side()..'Hi']+i,emu.memType.nesDebug)
  assert(r('PlayerChrBank')==ref[c.role][c.power][c.pose][side()].bank,'Exact original fallback CHR bank')
  assert(c.role=='lance'and helperCall==nil or c.role~='lance'and helperResult==false,'Lance excluded before helper; normal fallback returns carry clear')
  fallbackChecks=fallbackChecks+1
 end
 local filtered=c.off==1 and emu.read(L.PlayerOutlineCharacters+char,emu.memType.nesDebug)~=0
 assert((filtered and unfilteredPtr==wanted and ptr==L.OutlinePoseBuffer)or(not filtered and ptr==wanted),'Exact selected/fallback original pointer before optional outline filtering case'..ci..' got'..ptr..' expected'..wanted..' source'..tostring(unfilteredPtr)..' pose'..c.pose..' power'..c.power..' selected'..tostring(optimized()))
 assert(r('R4')+256*r('R5')==c.x and r('R6')+256*(r('R7')-1)==c.y,'Actual renderer origin matches authored viewport case '..ci..' got '..r('R4')..','..r('R5')..','..r('R6')..','..r('R7'))
 pending={case=ci,reference=ref[c.role][c.power][c.pose][side()],x=c.x,y=c.y,off=c.off,optimized=optimized()}
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
-- Keep one ordinary buster alive across every body-bank transition, including
-- new83, originalE0/E1 and clipped fallback. This is an isolated art fixture;
-- native draw dispatch, allocation, CHR mapping and completed DMA stay live.
emu.addMemoryCallback(function()
 if char~=9 or not c or interruptDepth~=0 or r('CurrentBank')%128~=4 then return end
 for i=0,9 do w('RgShotType',0,i)end
 local x=256+c.camera+160
 w('RgShotType',4);w('RgShotX',x);w('RgShotPage',math.floor(x/256));w('RgShotY',160);w('RgShotYHigh',1);w('RgShotAge',0);w('RgShotImpact',0);w('RgShotDir',1)
end,emu.callbackType.exec,L.ExpandedDrawShots)
local committed
emu.addMemoryCallback(function()if c then committed=pending end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 interruptDepth=math.max(0,interruptDepth-1)
 if not committed or not c or committed.case~=ci then return end
 local p=committed;committed=nil;local s=mmc5 and emu.getState()or nil;local cache={}
 local function chr(a)if cache[a]==nil then cache[a]=mmc5 and emu.read(s['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)end;return cache[a]end
 local actual={}
 for o=0,252,4 do
  local y,t,a,x=emu.read(o,emu.memType.nesSpriteRam),emu.read(o+1,emu.memType.nesSpriteRam),emu.read(o+2,emu.memType.nesSpriteRam),emu.read(o+3,emu.memType.nesSpriteRam)
  if y<240 then for dy=0,15 do for dx=0,7 do
   local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx;local at=(t&1)*4096+(t&254)*16+(row//8)*16+row%8
   local color=((chr(at)>>col)&1)+2*((chr(at+8)>>col)&1);local key=(y+1+dy)*256+x+dx
   if color~=0 and x+dx<256 and y+1+dy<240 and actual[key]==nil then actual[key]=emu.read(16+(a&3)*4+color,emu.memType.nesPaletteRam)&63 end
  end end end
 end
 local want={};local parts=p.reference.parts
 for i=#parts,1,-1 do local q=parts[i];local x,y=p.x+q.x,p.y+q.y
  if not(p.off==1 and q.a&4~=0)and x>=0 and x<256 and y>=0 and y<256 then
   for yy,row in ipairs(q.rows)do for xx=1,#row do local color=tonumber(row:sub(xx,xx));local px,py=x+xx-1,y+yy
    if color~=0 and px<256 and py<240 then local key=py*256+px;if want[key]==nil then want[key]=emu.read(16+(q.a&3)*4+color,emu.memType.nesPaletteRam)&63 end end
   end end
  end
 end
 if char==9 then for _,q in ipairs(ref.buster)do
  for yy,row in ipairs(q.rows)do for xx=1,#row do local color=tonumber(row:sub(xx,xx));if color~=0 then local key=(160+q.y+yy)*256+160+q.x+xx-1;assert(want[key]==nil,'Separate normal buster does not overlap the body oracle');want[key]=emu.read(16+(q.a&3)*4+color,emu.memType.nesPaletteRam)&63 end end end
 end end
 for key,color in pairs(want)do
  if actual[key]~=color then
   print('DIAG case '..ci..' playerbank '..r('PlayerChrBank')..' reload '..r('ReloadCHRBank')..' RgRotation '..r('RgOamRotation'))
   print('DIAG map '..emu.read(L.ChrPhysicalMap+r('PlayerChrBank'),emu.memType.nesDebug))
   for tile=2,18,2 do local bytes={};for k=0,31 do bytes[#bytes+1]=string.format('%02x',chr(0x1000+tile*16+k))end;print('DIAG CHR '..tile..' '..table.concat(bytes))end
   for o=0,252,4 do local yy=emu.read(o,emu.memType.nesSpriteRam);if yy<240 then print('DIAG OAM '..o..' y '..yy..' t '..emu.read(o+1,emu.memType.nesSpriteRam)..' a '..emu.read(o+2,emu.memType.nesSpriteRam)..' x '..emu.read(o+3,emu.memType.nesSpriteRam))end end
  end
  assert(actual[key]==color,'Immutable30 DMA composite char'..char..' case'..ci..' role'..c.role..' pose'..c.pose..' X'..c.x..' Y'..c.y..' pixel'..key..' expected'..color..' got'..tostring(actual[key]))
 end
 for key in pairs(actual)do assert(want[key]~=nil,'No added opaque source pixel case'..ci..' key'..key)end
 checks=checks+1;ci=ci+1;c=cases[ci]
 if not c then print('PASS ordinary low-pressure immutable30 DMA composites '..checks..' cases, '..selectedChecks..' optimized/'..fallbackChecks..' exactfallback render decisions; forms/directions/outlines/star, Lance/fire exclusions, guard and clipping/page seams');emu.stop(0)end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 emu.setInput({down=char==9 and frame==80,right=char==3 and(frame==80 or frame==100 or frame==120)or char==9 and(frame==100 or frame==120 or frame==140),start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==char,'Actual character select');ci=1;c=cases[ci];setup()end
 -- Restore ordinary safe physics inputs after each isolated render request.
 w('Player_X_Position',96);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmLastXSpeed',0);w('Player_CollisionBits',3)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 assert(frame<12000,'Bounded art fixture completes')
end,emu.eventType.endFrame)
