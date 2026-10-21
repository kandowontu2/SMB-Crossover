-- Explicit flat Goomba arenas. After setup, only ordinary idle/Right controls
-- run. This diagnostic reads completed hardware OAM, actual mapped CHR and
-- palettes; it does not patch rendering, physics, timers or controller outcomes.
local char=VIS_CHARACTER or 1
local frame,ci,age,interruptDepth=0,0,0,0
local cases={}
for _,off in ipairs({0,1})do for _,walk in ipairs({false,true})do for _,n in ipairs({0,1,2,4})do cases[#cases+1]={off=off,walk=walk,n=n}end end end
local c,stats,submitted,lastActor,lastMetrics,committed,rows
local drew,dma=false,false
rows={}
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
local function setup()
 age=0;submitted={};lastMetrics=nil;committed=nil;drew=false;dma=false
 stats={samples=0,draws=0,dmas=0,total_oam_max=0,scanline_max=0,scanline_overflow_frames=0,missing_oam_parts=0,not_submitted_actor_frames=0,player={},enemy={},actors={}}
 for a=0,c.n do stats.actors[a]={visible_frames=0,whole_hidden_frames=0,partial_frames=0,longest_hidden_streak=0,current_hidden_streak=0}end
 for _,group in ipairs({'player','enemy'})do stats[group]={ideal_pixels=0,correct_pixels=0,wrong_color_pixels=0,hidden_pixels=0,whole_hidden_frames=0,partial_frames=0,parts=0,scanline_hidden_parts=0}end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,23 do w('ObjectMetasprite',0,i)end
 for i=0,5 do
  w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('Enemy_CollisionBits',0,i);w('ObjectVerticalFlip',0,i+1)
  w('FloateyNum_Control',0,i);w('InvPickup',0,i);w('MmEnemyFlash',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)
 end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i);w('InvDropKind',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Player_X_Position',16);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmLastXSpeed',0);w('Player_CollisionBits',3);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('PlayerSize',0);w('CrouchingFlag',0);w('RgCrouch',0);w('MmSliding',0);w('XgDash',0);w('MmOnVine',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0);w('TimerControl',0);w('GameEngineSubroutine',8);w('InjuryTimer',0);w('StarInvincibleTimer',0)
 w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0);w('MmDeathFlag',0);w('PlayerOutlinesOff',c.off)
 w('InvSelected',0,char);w('SsFreeze',0);w('SsBodyStop',0);w('SavedJoypadBits',0);w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0)
 for i=0,c.n-1 do
  w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i)
  w('Enemy_X_Position',128+i*24,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',184,i);w('Enemy_Y_HighPos',1,i)
  w('Enemy_X_Speed',8,i);w('Enemy_Y_Speed',0,i);w('Enemy_MovingDir',1,i);w('Enemy_SprAttrib',0,i)
 end
end
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=math.max(0,interruptDepth-1)end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()
 if not c or interruptDepth~=0 or r('CurrentBank')%128~=4 then return end
 submitted={};lastActor=nil;drew=true
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if c and interruptDepth==0 and r('CurrentBank')%128==4 then lastActor=emu.getState()['cpu.y']end
end,emu.callbackType.exec,L.DrawMetasprite)
emu.addMemoryCallback(function()
 if not c or interruptDepth~=0 or r('CurrentBank')%128~=4 or lastActor==nil then return end
 local actor=lastActor;lastActor=nil
 if actor>c.n then return end
 local ptr=r('R0')+256*r('R1');local count=emu.read(ptr,emu.memType.nesDebug)
 local base=r('CurrentOAMOffset');local rejected=base+count>=256
 local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 local x=r('R4')+256*r('R5');if x>=32768 then x=x-65536 end
 local y=r('R6')+256*(r('R7')-1)
 for i=0,count//4-1 do
  local p=ptr+1+(count//4-1-i)*4
  local px,py=x+signed(emu.read(p+3,emu.memType.nesDebug)),y+signed(emu.read(p+2,emu.memType.nesDebug))
  if px>=0 and px<256 and py>=0 and py<240 then
   submitted[#submitted+1]={actor=actor,o=(base+rotation+i*4)%256,x=px,y=py,t=emu.read(p,emu.memType.nesDebug),missing=rejected}
  end
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()if c then dma=true;committed=submitted end end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()
 interruptDepth=math.max(0,interruptDepth-1)
 if not c or not dma or not committed then return end
 local state=mmc5 and emu.getState()or nil;local cache={};local ownership={};local missing=0
 for _,p in ipairs(committed)do
  if p.missing then missing=missing+1 else
   assert(emu.read(p.o,emu.memType.nesSpriteRam)==p.y and emu.read(p.o+3,emu.memType.nesSpriteRam)==p.x and emu.read(p.o+1,emu.memType.nesSpriteRam)==p.t,'Completed OAM actor attribution remains exact')
   ownership[p.o]=p.actor
  end
 end
 local function chr(a)
  if cache[a]==nil then
   cache[a]=mmc5 and emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)
  end
  return cache[a]
 end
 local hardware,ideal,pixelByPart={},{},{}
 local visibleCount,total,maxLine,overflow=0,0,0,false
 local selected={}
 -- Selection uses sprite Y alone. Transparent CHR rows consume a slot too.
 for y=0,239 do
  local n=0;selected[y]={}
  for o=0,252,4 do local sy=emu.read(o,emu.memType.nesSpriteRam)+1
   if sy<=y and y<sy+16 then n=n+1;if n<=8 then selected[y][o]=true end end
  end
  maxLine=math.max(maxLine,n);if n>8 then overflow=true end
 end
 for o=0,252,4 do
  local sy,t,a,sx=emu.read(o,emu.memType.nesSpriteRam)+1,emu.read(o+1,emu.memType.nesSpriteRam),emu.read(o+2,emu.memType.nesSpriteRam),emu.read(o+3,emu.memType.nesSpriteRam)
  if sy<240 then
   total=total+1;local actor=ownership[o];local partPixels,partSurviving=0,0
   for dy=0,math.min(15,239-sy)do for dx=0,math.min(7,255-sx)do
    local row=a&128~=0 and 15-dy or dy;local col=a&64~=0 and dx or 7-dx
    local off=(t&1)*4096+(t&254)*16+(row//8)*16+row%8
    local color=((chr(off)>>col)&1)+2*((chr(off+8)>>col)&1)
    if color~=0 then
     local key=(sy+dy)*256+sx+dx;local rgb=emu.read(16+(a&3)*4+color,emu.memType.nesPaletteRam)&63
     if actor~=nil then
      ideal[actor]=ideal[actor]or{};if not ideal[actor][key]then ideal[actor][key]=rgb end
      partPixels=partPixels+1
     end
     if selected[sy+dy][o]then
      if not hardware[key]then hardware[key]={actor=actor,color=rgb}end
      if actor~=nil then partSurviving=partSurviving+1 end
     end
    end
   end end
   if actor~=nil then pixelByPart[#pixelByPart+1]={actor=actor,pixels=partPixels,surviving=partSurviving}end
  end
 end
 local result={total=total,maxLine=maxLine,overflow=overflow,missing=missing,player={},enemy={},actors={},notSubmitted=0}
 for _,g in ipairs({'player','enemy'})do result[g]={ideal_pixels=0,correct_pixels=0,wrong_color_pixels=0,hidden_pixels=0,whole_hidden_frames=0,partial_frames=0,parts=0,scanline_hidden_parts=0}end
 for actor=0,c.n do
  local image=ideal[actor]or{};local n,correct,wrong,visible=0,0,0,0
  for key,color in pairs(image)do
   n=n+1;local h=hardware[key]
   if h and h.actor==actor then visible=visible+1;if h.color==color then correct=correct+1 else wrong=wrong+1 end end
  end
  local group=result[actor==0 and'player'or'enemy']
  result.actors[actor]={n=n,correct=correct,visible=visible}
  if n==0 then result.notSubmitted=result.notSubmitted+1 end
  group.ideal_pixels=group.ideal_pixels+n;group.correct_pixels=group.correct_pixels+correct;group.wrong_color_pixels=group.wrong_color_pixels+wrong;group.hidden_pixels=group.hidden_pixels+n-visible
  if n>0 and visible==0 then group.whole_hidden_frames=group.whole_hidden_frames+1 end
  if correct<n then group.partial_frames=group.partial_frames+1 end
 end
 for _,p in ipairs(pixelByPart)do local g=result[p.actor==0 and'player'or'enemy'];g.parts=g.parts+1;if p.pixels>0 and p.surviving==0 then g.scanline_hidden_parts=g.scanline_hidden_parts+1 end end
 lastMetrics=result
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 local b={}
 if frame<540 then
  b={down=char==9 and frame==80,right=(char==1 and frame==80)or(char==2 and(frame==80 or frame==100))or(char==3 and(frame==80 or frame==100 or frame==120))or(char==9 and(frame==100 or frame==120 or frame==140)),start=frame==200}
 elseif c then b={right=c.walk}end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==char,'Ordinary character select');ci=1;c=cases[ci];setup();return end
 age=age+1
 if age>8 then
  assert(r('GameEngineSubroutine')==8 and r('GuestHurtTicks')==0 and r('InjuryTimer')==0,'Ordinary unhurt walking/idle arena')
  for i=0,c.n-1 do assert(r('Enemy_Flag',i)~=0 and r('Enemy_Y_Position',i)==184,'Every actual Goomba remains live and supported for the full measurement')end
  assert(lastMetrics,'At least one actual completed OAM DMA')
  stats.samples=stats.samples+1;if drew then stats.draws=stats.draws+1 end;if dma then stats.dmas=stats.dmas+1 end
  local m=lastMetrics;stats.total_oam_max=math.max(stats.total_oam_max,m.total);stats.scanline_max=math.max(stats.scanline_max,m.maxLine);if m.overflow then stats.scanline_overflow_frames=stats.scanline_overflow_frames+1 end
  stats.missing_oam_parts=stats.missing_oam_parts+m.missing
  stats.not_submitted_actor_frames=stats.not_submitted_actor_frames+m.notSubmitted
  for _,g in ipairs({'player','enemy'})do for k,v in pairs(m[g])do stats[g][k]=stats[g][k]+v end end
  for a,v in pairs(m.actors)do
   local s=stats.actors[a]
   if v.visible>0 then s.visible_frames=s.visible_frames+1;s.current_hidden_streak=0
   else s.whole_hidden_frames=s.whole_hidden_frames+1;s.current_hidden_streak=s.current_hidden_streak+1;s.longest_hidden_streak=math.max(s.longest_hidden_streak,s.current_hidden_streak)end
   if v.correct<v.n then s.partial_frames=s.partial_frames+1 end
  end
 end
 drew=false;dma=false
 if age==72 then
  stats.character=char;stats.outlines_off=c.off;stats.walk=c.walk;stats.goombas=c.n;rows[#rows+1]=stats
  print('VIS '..char..' outlineOff'..c.off..' walk'..tostring(c.walk)..' goombas'..c.n..' DMA'..stats.dmas..'/'..stats.samples..' OAMmax'..stats.total_oam_max..' rowMax'..stats.scanline_max..' bodyPartial'..stats.player.partial_frames..' enemyWholeHidden'..stats.enemy.whole_hidden_frames)
  ci=ci+1;c=cases[ci]
  if c then setup()else
   local f=assert(io.open(OUTPUT..ROM_NAME..'-ordinary-visibility-'..char..'.jsonl','w'))
   local function json(v)
    if type(v)=='table'then local p={};for k,x in pairs(v)do p[#p+1]='"'..k..'":'..json(x)end;return'{'..table.concat(p,',')..'}'end
    if type(v)=='boolean'then return v and'true'or'false'end;return tostring(v)
   end
   for _,row in ipairs(rows)do f:write(json(row)..'\n')end;f:close()
   print('PASS ordinary completed-DMA first-eight physical sprite audit '..#rows..' arenas char'..char);emu.stop(0)
  end
 end
end,emu.eventType.endFrame)
