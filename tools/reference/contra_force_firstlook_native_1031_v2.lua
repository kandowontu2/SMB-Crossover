-- Root launches the exact bound packet. Controller input and passive reads only.
local P=assert(COLD_ARGS)
local frame,age,phase,step,done=0,0,'title',1,false
local plan={};local col,row=P.slot%8,P.slot//8
for i=1,(col<=4 and col or 8-col)do plan[#plan+1]=col<=4 and'right'or'left'end
for i=1,(row<=2 and row or 4-row)do plan[#plan+1]=row<=2 and'down'or'up'end
for i=1,P.selects do plan[#plan+1]='select'end
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function peek(a)return emu.read(a,emu.memType.nesDebug)end
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or-1 end
local function signed(v)return v>=128 and v-256 or v end
local function json(v)
 if type(v)=='table'then local z={};if#v>0 then for _,x in ipairs(v)do z[#z+1]=json(x)end;return'['..table.concat(z,',')..']'end
 for k,x in pairs(v)do z[#z+1]=string.format('%q',k)..':'..json(x)end;table.sort(z);return'{'..table.concat(z,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function class()return(r('FmGroups')>>3)&3 end
local chr,upper={},0
for i=0,11 do chr[i]=-1 end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
for i=0,11 do emu.addMemoryCallback(function(_,v)chr[i]=upper+v end,emu.callbackType.write,0x5120+i)end
local function pattern(tile)
 local at=(tile&1)*4096+(tile&254)*16;local page=assert(chr[at//1024]);assert(page>=0,'Observed actual sprite CHR mapping')
 local q={};for i=0,31 do q[i]=emu.read(page*1024+at%1024+i,emu.memType.nesChrRom)end;return q,page
end
local function value(q,x,y,attr)
 local yy=attr&128~=0 and 15-y or y;local xx=attr&64~=0 and x or 7-x
 local a=(yy//8)*16+yy%8;return((q[a]>>xx)&1)|(((q[a+8]>>xx)&1)<<1)
end
local sourceDesc,prelate=nil,nil
local uiChecks={selected=0,lives=0,game=0};local renderedUI,lastUI,RGB={},{},{}
local bodyChecks,shotRecords,groundShots,airShots,epochBoth,epochs,authA2=0,0,0,0,0,0,0
local sourceFresh,sourceMain,sourceMove,sourceEnd,sourceAudio,vectorGuards=0,0,0,0,0,0
local lastBoth,guardOK=nil,false
local uiFile=assert(io.open(OUTPUT..'body-DMA.csv','w'));uiFile:write('frame,stage,class,page,parts,admitted_pixels,P0,P1,Last,descriptor_age\n')
local epochFile=assert(io.open(OUTPUT..'epochs.csv','w'));epochFile:write('frame,visible,choice,Turn,Last,Pending,native_hidden,CF_hidden\n')
local function cookie(base)for i=0,15 do assert(peek(base+i)==P.cookie[i+1],'Full original CF24KB cookie')end end
emu.addMemoryCallback(function()if bank(L.CfGuardReturn)==B.CfOrBtCheck then guardOK=assert(emu.getState()['cpu.ps'],'Actual CPU status register')&1~=0 end end,emu.callbackType.exec,L.CfGuardReturn)
emu.addMemoryCallback(function(_,v)if r('CurrentBank')==2 and v==0 then guardOK=false end end,emu.callbackType.write,0xbfe0)
emu.addMemoryCallback(function()
 if r('CurrentBank')~=2 or r('SelectedCharacter')~=31 then return end
 assert(guardOK,'Actual ROM auth before first A2 router');cookie(0xbfe0);authA2=authA2+1
end,emu.callbackType.exec,L.CfA2Router)
emu.addMemoryCallback(function()
 if r('CurrentBank')~=3 or r('CurrentBankC')~=2 or r('SelectedCharacter')~=31 then return end
 cookie(0xdfe0);assert(class()==P.variant and peek(L.CfState+0xb1)==P.variant,'Original class and source identity')
 local slot=r('CfRenderSlot')
 if slot~=0 then shotRecords=shotRecords+1;return end
 local ptr=peek(L.CfPointers)+256*peek(L.CfPointers+1);local size=r('CfRenderRemaining')
 assert(size>=4 and size<=48 and size%4==0,'Complete source body record')
 local q={frame=frame,parts={},page=chr[0],x=r('CfRenderXLo'),y=r('CfRenderYLo'),start=r('CurrentOAMOffset'),rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0}
 for k=0,size-1,4 do q.parts[#q.parts+1]={dy=signed(peek(ptr+k)),dx=signed(peek(ptr+k+1)),tile=peek(ptr+k+2),attr=peek(ptr+k+3)}end
 sourceDesc=q
 local shots=0;for i=10,21 do if peek(L.CfState+0x382+i)~=0 and peek(L.CfState+0x334+i)==28 then shots=shots+1 end end
 if phase=='game'and shots>0 and r('SavedJoypadBits')&64~=0 then if r('Player_State')==0 then groundShots=groundShots+1 else airShots=airShots+1 end end
end,emu.callbackType.exec,L.CfRecordReady)
emu.addMemoryCallback(function()
 if r('CurrentBank')~=3 or r('SelectedCharacter')~=31 then return end
 prelate={};for at=0,252,4 do prelate[at]={peek(512+at),peek(513+at),peek(514+at),peek(515+at)}end
end,emu.callbackType.exec,L.CfP1Late)
emu.addMemoryCallback(function(_,v)
 if phase~='game'or r('SelectedCharacter')~=31 or r('CurrentBank')~=1 or(v~=0x80 and v~=0xc0)then return end
 local visible,choice=peek(L.CfState+0x2fa),peek(L.CfState+0x2fb);local last=r('SmFreezeLastBlue')
 assert(last==0xc0+choice and v==(choice==1 and 0x80 or 0xc0),'Complete source owner validity published last')
 if visible==3 then if lastBoth~=nil then assert(choice~=lastBoth,'Fair alternation only when both complete owners are present')end;lastBoth=choice;epochBoth=epochBoth+1 end
 local nh,ch=0,0
 assert(prelate,'Genuine complete native OAM before late filter')
 for at=0,252,4 do
  local before=prelate[at];local tag=before[3]&24;local hidden=tag==8 and choice==0 or tag==16 and choice==1
  assert(peek(514+at)==before[3]&0xe7,'Strip every temporary OAM tag')
  assert(peek(513+at)==before[2]and peek(515+at)==before[4],'Preserve source patterns/positions')
  assert(peek(512+at)==(hidden and 248 or before[1]),'Whole CF/native object filtering')
  if hidden and tag==8 then ch=ch+1 elseif hidden then nh=nh+1 end
 end
 epochs=epochs+1;epochFile:write(table.concat({frame,visible,choice,r('SmFreezeTurn'),last,v,nh,ch},',')..'\n')
end,emu.callbackType.write,L.SmFreezePalettePending)
local function nativeP1()
 local n=r('SmFreezePaletteControl');if n==8 then n=2 end
 if n<1 or n>4 then n=r('AreaType')<4 and r('AreaType')+1 or 2 end
 return({{16,48,39},{26,48,39},{28,54,23},{28,54,23}})[n]
end
local function dma(stage,page)
 if lastUI[stage]and frame-lastUI[stage].frame<8 then return end
 local rows,body={},{}
 for at=0,252,4 do
  local row={y=peek(page*256+at),tile=peek(page*256+at+1),attr=peek(page*256+at+2),x=peek(page*256+at+3),oam=at}
  if row.y<240 then row.pattern,row.page=pattern(row.tile);rows[#rows+1]=row end
 end
 if stage=='selected'then
  assert(#rows==5,'Authentic fivepart CF ready preview')
  for i,row in ipairs(rows)do local p=P.menu[i];assert(row.y==p[1]and row.tile==p[2]and row.attr==p[3]and row.x==p[4],'Exact original in-game CF menu OAM');assert(row.page>=700 and row.page<=703,'Own menu700..703 pages');body[row.oam]=true end
  for i=1,7 do assert(ppu(0x3f10+i)==P.menu_palette[i],'Original two-role menu palette')end
 else
  assert(chr[0]>=959 and chr[0]<968,'Actual original CF body window0')
  local desc=assert(sourceDesc,'Real mapped source record observed');assert(frame-desc.frame<=8,'Recent original source body')
  for i,p in ipairs(desc.parts)do
   local at=(desc.start+desc.rotation+(i-1)*4)%256;local found=nil
   for _,row in ipairs(rows)do if row.oam==at then found=row;break end end
   assert(found and found.y==(desc.y+p.dy)%256 and found.x==(desc.x+p.dx)%256 and found.tile==p.tile and found.attr==p.attr,'Every software source body cell in its actual rotated DMA slot')
   body[at]=true
  end
  for i,v in ipairs({55,18,15})do assert(ppu(0x3f10+i)==v,'Original CF body P0')end
  for i,v in ipairs({22,48,39})do assert(ppu(0x3f18+i)==v,'Native/source shared worldP2 untouched')end
  if stage=='lives'then assert(ppu(0x3f00)==15,'Native black lives BG')else
   local want=r('SmFreezeLastBlue')==0xc1 and{32,56,22}or nativeP1()
   for i=1,3 do assert(ppu(0x3f14+i)==want[i],'Paired completed CF/native P1 at DMA')end
  end
 end
 -- Build actual normal-eight-sprite winners. Crowded body cells not admitted
 -- by hardware are excluded; unrelated world/weapon sprites remain visible.
 local admitted={};for y=0,239 do local n=0;admitted[y]={};for _,row in ipairs(rows)do if row.y+1<=y and y<row.y+17 then n=n+1;if n<=8 then admitted[y][row.oam]=true end end end end
 local expected={};local count=0
 for _,row in ipairs(rows)do
  for yy=0,15 do local y=row.y+1+yy;if y<240 and admitted[y][row.oam]then
   for xx=0,7 do local x=row.x+xx;if x<256 then local pix=value(row.pattern,xx,yy,row.attr);local pos=y*256+x
    if pix~=0 and expected[pos]==nil then expected[pos]={nes=ppu(0x3f10+(row.attr&3)*4+pix),body=body[row.oam]or false,behind=row.attr&32~=0}end
   end end
  end end
 end
 local pixels={};for pos,v in pairs(expected)do if v.body and not v.behind then pixels[pos]=v.nes;count=count+1 end end
 assert(count>=(stage=='game'and 16 or 40),'Actual hardware-admitted original body pixels')
 lastUI[stage]={frame=frame,pixels=pixels,opaque=count};uiChecks[stage]=uiChecks[stage]+1
 uiFile:write(table.concat({frame,stage,P.variant,chr[0],#rows,count,ppu(0x3f11)..':'..ppu(0x3f12)..':'..ppu(0x3f13),ppu(0x3f15)..':'..ppu(0x3f16)..':'..ppu(0x3f17),r('SmFreezeLastBlue'),sourceDesc and frame-sourceDesc.frame or-1},',')..'\n')
end
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=31 or class()~=P.variant then return end
 if phase=='browse'and step>#plan and age>=8 and r('CrossoverMenuState')==2 then dma('selected',page)
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then dma('lives',page)
 elseif phase=='game'and r('GameEngineSubroutine')==8 then dma('game',page)end
end,emu.callbackType.write,0x4014)
local function stable(stage)local q=lastUI[stage];return q and frame-q.frame>=(stage=='game'and 1 or 2)and frame-q.frame<=7 end
local function rendered(stage)
 local q=assert(lastUI[stage]);assert(stable(stage),'Completed actual DMA before image')
 local screen=emu.getScreenBuffer();assert(#screen==61440);local used={}
 for at,nes in pairs(q.pixels)do local rgb=screen[at+1]&0xffffff;if RGB[nes]then assert(RGB[nes]==rgb,'Original hardware source color/opaque pixel '..stage)else RGB[nes]=rgb end;used[rgb]=true end
 local n=0;for _ in pairs(used)do n=n+1 end;assert(n>=2,'Readable real original sprite');renderedUI[stage]={frame=frame,pixels=q.opaque,colors=n}
end
local shots=0
local function shot(name)shots=shots+1;assert(shots<=4,'Four PNG bound');local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local csv=assert(io.open(OUTPUT..'trace.csv','w'));csv:write('frame,phase,age,mode,task,engine,raw,x,y,state,lives,main_updates,nmi_skipped,main_last_cpu\n')
local cycles=assert(io.open(OUTPUT..'main-cycles.csv','w'));cycles:write('frame,elapsed,interrupt_cpu,foreground_cpu,x,y\n')
local updates,activeFrames,minSP,lastCPU=0,0,255,0
local backgroundChecks,gameBodyChecks=0,0
local main,isrs=nil,{}
local frameHistogram={}
local function image()local z={}for i=0x15a,0x17a do z[#z+1]=peek(i)end;return table.concat(z,',')end
local timing={minimum=10000000,maximum=0,total=0,nmi=0,lag_nmi=0,irq=0,lag_counter_delta=0}
local startX,startY,lives,maxX,apex,lastLag
local jumped,landed=false,false
local function active()return phase=='game'and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
for _,item in ipairs({{'CfHostConstruct',3,function()sourceFresh=sourceFresh+1 end},{'CfHostMovement',3,function()if main then sourceMain=sourceMain+1 end end},{'CfNativeBody',1,function()if main then sourceMove=sourceMove+1 end end}})do
 emu.addMemoryCallback(function()if r('CurrentBank')==item[2]and r('SelectedCharacter')==31 then item[3]()end end,emu.callbackType.exec,L[item[1]])
end
emu.addMemoryCallback(function()if bank(L.AudioUpdate)==B.AudioUpdate then sourceAudio=sourceAudio+1 end end,emu.callbackType.exec,L.AudioUpdate)
local function finish(ok,reason)
 if done then return end;done=true;shot('endpoint');csv:close();cycles:close();uiFile:close();epochFile:close()
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=ok,reason=reason,ROM_sha256=P.sha256,variant=P.variant,frames=frame,gameplay_frames=activeFrames,main_updates=updates,walked=startX and maxX-startX or 0,rise=startY and startY-apex or 0,jumped=jumped,landed=landed,source_construct=sourceFresh,source_Main=sourceMain,source_body_steps=sourceMove,source_projectile_records=shotRecords,ground_projectile_observations=groundShots,air_projectile_observations=airShots,auth_A2_entries=authA2,epochs=epochs,both_owner_epochs=epochBoth,body_checks=gameBodyChecks,actual_DMA=uiChecks,rendered=renderedUI,background_checks=backgroundChecks,timing=timing,minimum_SP=minSP,vector_guards=vectorGuards,frame_completion_histogram=frameHistogram,scope='Real cold controller menu/lives/360physical gameplay. Normal8sprite visible-winner pixel proof, source motion and ground/air B. Fair complete P1 epochs when both present; no1-1/powerup/60Hz claim.'})..'\n');f:close();print('CF_COLD '..tostring(ok)..' '..reason..' frame='..frame);emu.stop(ok and 0 or 1);return
end
@@TIMING@@
emu.addEventCallback(function()
 if done then return end;local b={}
 if phase=='open'and age<6 or phase=='launch'and age<4 then b.start=true
 elseif phase=='browse'and age<4 and plan[step]then b[plan[step]]=true
 elseif phase=='game'then
  if age>=20 and age<70 then b.right=true end
  if age>=80 and age<145 then b.a=true end
  if age>=20 and age<50 or age>=90 and age<150 then b.b=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 local mode,task,engine=r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine');local x,y=r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position')
 csv:write(table.concat({frame,phase,age,mode,task,engine,r('SelectedCharacter'),x,y,r('Player_State'),r('NumberofLives'),updates,r('NmiSkipped'),lastCPU},',')..'\n')
 if phase=='title'and frame==100 then assert(mode==0 and r('CrossoverMenuState')==0,'Cold native title');phase='open';age=0
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2,'Controller Start opens menu');phase='browse';age=0
 elseif phase=='browse'and age>=24 then
  if step<=#plan then step=step+1;age=0 elseif stable('selected')then
   assert(r('CrossoverMenuIndex')==30 and r('SelectedCharacter')==31 and class()==P.variant,'Real selected CF class')
   for i=0,15 do assert(ppu(0x2328+i)==P.menu_tiles[i+1],'Full source class name without star')end
   rendered('selected');shot('selected');phase='launch';age=0
  end
 elseif phase=='launch'then
  if not renderedUI.lives and stable('lives')then rendered('lives');shot('lives')end
  if mode==1 and task==3 and engine==8 then
   assert(renderedUI.lives and sourceFresh==1,'Visible cold lives and genuine sole construction');phase='game';age=0;startX,startY,lives,maxX,apex=x,y,r('NumberofLives'),x,y
  elseif age>400 then finish(false,'Cold native launch bound');return end
 elseif phase=='game'then
  if lastUI.game and frame-lastUI.game.frame==1 then rendered('game');gameBodyChecks=gameBodyChecks+1 end
  if active()then
   assert(r('AreaType')==1 and ppu(0x3f00)==0x22 and ppu(0x3f10)==0x22,'Actual original blue world backdrop');backgroundChecks=backgroundChecks+1
   activeFrames=activeFrames+1;maxX=math.max(maxX,x);apex=math.min(apex,y)
   if y<startY-12 then jumped=true;if not renderedUI.jump and stable('game')then rendered('game');shot('jump');renderedUI.jump=true end end
   if jumped and r('Player_State')==0 and y>=startY-2 then landed=true end
   local now=r('NmiSkipped');if lastLag then timing.lag_counter_delta=timing.lag_counter_delta+(now-lastLag)%256 end;lastLag=now
  end
  if engine==11 or r('NumberofLives')~=lives then finish(false,'Native death/life loss');return end
  if age>=360 and not main then
   finish(updates>=60 and sourceMain==updates and sourceMove==updates and sourceEnd==updates and vectorGuards>60 and sourceAudio>0 and sourceFresh==1 and maxX-startX>=16 and jumped and landed and gameBodyChecks>=20 and renderedUI.jump and shotRecords>0 and groundShots>0 and airShots>0 and epochs>0 and authA2>0,'Bounded original CF cold/lives/body/motion/ground-air attacks/paired epochs');return
  end
 end
 if frame>=1200 then finish(false,'1200physical frame bound');return end
end,emu.eventType.endFrame)
