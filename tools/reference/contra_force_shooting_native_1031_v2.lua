-- Root launches the exact bound packet. Controller input and passive reads only.
local P=assert(COLD_ARGS)
local frame,age,phase,step,done=0,0,'title',1,false
local updates=0
local routePad={};local jumpUntil=-4
local combatPhase,shootSince,earned,contactPending='approach',0,nil,nil
local nativeDefeats,nativeScores,sourceImpacts,sourceImpactCommits=0,0,0,0
local maxCamera,nativeEnemies,parserCalls,scrollCalls=0,0,0,0
local terrainInitial,terrainChanged=nil,false
local plan={};local col,row=P.slot%8,P.slot//8
for i=1,(col<=4 and col or 8-col)do plan[#plan+1]=col<=4 and'right'or'left'end
for i=1,(row<=2 and row or 4-row)do plan[#plan+1]=row<=2 and'down'or'up'end
for i=1,P.selects do plan[#plan+1]='select'end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
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
local standingDMA=nil
local enemyDesc=nil
local enemyDMAs,enemyPixelFrames,enemyLastPixels=0,0,0
local combatFile=assert(io.open(OUTPUT..'native-contact.csv','w'));combatFile:write('frame,Main,kind,enemy_slot,enemy_id,enemy_state,shot_slot,shot_kind,radius_index,shot_worldX,shot_Y,input,score,SFX\n')
local enemyFile=assert(io.open(OUTPUT..'native-enemy-DMA.csv','w'));enemyFile:write('frame,source_frame,parts,admitted_pixels,window1,window2,window3,P3\n')
emu.addMemoryCallback(function()
 if phase~='game'or bank(L.NativeGoombaRender)~=B.NativeGoombaRender or r('SelectedCharacter')~=31 then return end
 enemyDesc=nil
 if r('R5')~=0 or r('R7')~=1 or r('R4')>=248 or r('R6')>=224 then return end
 local ptr=r('R0')+256*r('R1')
 if not P.goomba_records[ptr]then return end
 assert(peek(ptr)==8,'Genuine original complete two-part Goomba descriptor')
 local parts={}
 for _,at in ipairs({5,1})do
  parts[#parts+1]={tile=peek(ptr+at),attr=((peek(ptr+at+1)|r('R3'))&0xf3)&0xe7,y=(r('R6')+peek(ptr+at+2))%256,x=(r('R4')+peek(ptr+at+3))%256}
 end
 enemyDesc={frame=frame,parts=parts}
end,emu.callbackType.exec,L.NativeGoombaRender)
local uiChecks={selected=0,lives=0,game=0};local renderedUI,lastUI,RGB={},{},{}
local bodyChecks,shotRecords,groundShots,airShots,epochBoth,epochs,authA2=0,0,0,0,0,0,0
local sourceFresh,sourceMain,sourceMove,sourceEnd,sourceAudio,vectorGuards=0,0,0,0,0,0
local lastBoth,guardOK=nil,false
local uiFile=assert(io.open(OUTPUT..'body-DMA.csv','w'));uiFile:write('frame,stage,class,page,parts,admitted_pixels,P0,P1,Last,descriptor_age\n')
local recordFile=assert(io.open(OUTPUT..'source-record.csv','w'));recordFile:write('frame,context,mode,task,screen,engine,rawA,rawC,class,sourceframe,PlayerY,anchorX,anchorY,source_page,source_parts\n')
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
 local context=r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and'game'or'lives'
 local q={frame=frame,parts={},page=(r('X5ChrMode')&3)*256+r('CurrentCHRBank'),context=context,nativeY=r('Player_Y_Position'),nativeX=r('Player_X_Position')+256*r('Player_PageLoc'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),x=r('CfRenderXLo'),y=r('CfRenderYLo'),start=r('CurrentOAMOffset'),rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0}
 for k=0,size-1,4 do q.parts[#q.parts+1]={dy=signed(peek(ptr+k)),dx=signed(peek(ptr+k+1)),tile=peek(ptr+k+2),attr=peek(ptr+k+3)}end
 sourceDesc=q
 recordFile:write(table.concat({frame,context,r('OperMode'),r('OperMode_Task'),r('ScreenRoutineTask'),r('GameEngineSubroutine'),r('CurrentBank'),r('CurrentBankC'),class(),peek(L.CfState+0x31a),r('Player_Y_Position'),q.x,q.y,q.page,#q.parts},',')..'\n')
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
 if stage~='game'and lastUI[stage]and frame-lastUI[stage].frame<8 then return end
 local rows,body,enemy={},{ },{};local sourceY,anchorY,sourceX,dmaCamera=nil,nil,nil,nil
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
  local desc=assert(sourceDesc,'Real mapped source record observed')
  sourceY,anchorY,sourceX,dmaCamera=desc.nativeY,desc.y,desc.nativeX,desc.camera
  assert(desc.context==stage,'Source descriptor belongs to the current native scene')
  if stage=='game'then assert(frame-desc.frame<=8,'Recent original gameplay source body')end
  assert(chr[0]==desc.page,'Current hardware body page matches the actual source emission')
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
 if stage=='game'then
  assert(chr[1]==16 and chr[2]==17 and chr[3]==18,'Native world windows1..3, no stale portrait pages')
  for i=1,3 do assert(ppu(0x3f1c+i)==P.native_P3[i],'Native Goomba P3 colors preserved')end
  if enemyDesc and enemyDesc.frame==sourceDesc.frame and frame-enemyDesc.frame<=8 then
   for _,p in ipairs(enemyDesc.parts)do
    if p.x<248 and p.y<224 then
     local found=nil
     for _,row in ipairs(rows)do
      if row.x==p.x and row.y==p.y and row.tile==p.tile and row.attr==p.attr then found=row;break end
     end
     assert(found,'Every complete source-native Goomba part reaches the actual DMA')
     assert(found.page==17,'Goomba A2/A4 uses genuine native physical17')
     local original=assert(P.native_patterns[found.tile],'Actual native Goomba tile')
     for k=0,31 do assert(found.pattern[k]==original[k+1],'Actual hardware Goomba pattern equals untouched native CHR')end
     enemy[found.oam]=true
    end
   end
  end
 end
 -- Build actual normal-eight-sprite winners. Crowded body cells not admitted
 -- by hardware are excluded; unrelated world/weapon sprites remain visible.
 local admitted={};for y=0,239 do local n=0;admitted[y]={};for _,row in ipairs(rows)do if row.y+1<=y and y<row.y+17 then n=n+1;if n<=8 then admitted[y][row.oam]=true end end end end
 local expected={};local count=0
 for _,row in ipairs(rows)do
  for yy=0,15 do local y=row.y+1+yy;if y<240 and admitted[y][row.oam]then
   for xx=0,7 do local x=row.x+xx;if x<256 then local pix=value(row.pattern,xx,yy,row.attr);local pos=y*256+x
    if pix~=0 and expected[pos]==nil then expected[pos]={nes=ppu(0x3f10+(row.attr&3)*4+pix),body=body[row.oam]or false,enemy=enemy[row.oam]or false,behind=row.attr&32~=0}end
   end end
  end end
 end
 local pixels,enemyPixels={},{};local top,bottom=240,-1
 for pos,v in pairs(expected)do if v.body and not v.behind then pixels[pos]=v.nes;count=count+1;local py=pos//256;top=math.min(top,py);bottom=math.max(bottom,py)end end
 for pos,v in pairs(expected)do if v.enemy and not v.behind then enemyPixels[pos]=v.nes end end
 local en=0;for _ in pairs(enemyPixels)do en=en+1 end
 if en>0 then enemyDMAs=enemyDMAs+1;enemyLastPixels=en;enemyFile:write(table.concat({frame,enemyDesc.frame,2,en,chr[1],chr[2],chr[3],ppu(0x3f1d)..':'..ppu(0x3f1e)..':'..ppu(0x3f1f)},',')..'\n')end
 assert(count>=(stage=='game'and 16 or 40),'Actual hardware-admitted original body pixels')
 lastUI[stage]={frame=frame,pixels=pixels,opaque=count,sourceY=sourceY,anchorY=anchorY,sourceX=sourceX,camera=dmaCamera,top=top,bottom=bottom,enemy_pixels=enemyPixels,enemy_opaque=en};uiChecks[stage]=uiChecks[stage]+1
 uiFile:write(table.concat({frame,stage,P.variant,chr[0],#rows,count,ppu(0x3f11)..':'..ppu(0x3f12)..':'..ppu(0x3f13),ppu(0x3f15)..':'..ppu(0x3f16)..':'..ppu(0x3f17),r('SmFreezeLastBlue'),sourceDesc and frame-sourceDesc.frame or-1},',')..'\n')
end
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=31 or class()~=P.variant then return end
 if phase=='browse'and step>#plan and age>=8 and r('CrossoverMenuState')==2 then dma('selected',page)
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then dma('lives',page)
 elseif phase=='game'and r('GameEngineSubroutine')==8 then
  -- The parser may publish engine8 before its first controlled GameLoop.
  -- Never count a retained lives descriptor as a gameplay body.
  if not sourceDesc or sourceDesc.context~='game'then assert(updates==0,'Completed gameplay Main must emit its own body');return end
  dma('game',page)
 end
end,emu.callbackType.write,0x4014)
local function stable(stage)local q=lastUI[stage];return q and frame-q.frame>=(stage=='game'and 1 or 2)and frame-q.frame<=7 end
local function rendered(stage)
 local q=assert(lastUI[stage]);assert(stable(stage),'Completed actual DMA before image')
 local screen=emu.getScreenBuffer();assert(#screen==61440);local used={}
 for at,nes in pairs(q.pixels)do local rgb=screen[at+1]&0xffffff;if RGB[nes]then assert(RGB[nes]==rgb,'Original hardware source color/opaque pixel '..stage)else RGB[nes]=rgb end;used[rgb]=true end
 if stage=='game'and q.enemy_opaque>=16 then
  for at,nes in pairs(q.enemy_pixels)do local rgb=screen[at+1]&0xffffff;if RGB[nes]then assert(RGB[nes]==rgb,'Actual complete native enemy opaque pixel')else RGB[nes]=rgb end end
  enemyPixelFrames=enemyPixelFrames+1
 end
 local n=0;for _ in pairs(used)do n=n+1 end;assert(n>=2,'Readable real original sprite');renderedUI[stage]={frame=frame,pixels=q.opaque,colors=n}
end
local shots=0
local function shot(name)shots=shots+1;assert(shots<=4,'Four PNG bound');local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local csv=assert(io.open(OUTPUT..'trace.csv','w'));csv:write('frame,phase,age,mode,task,engine,raw,x,y,state,lives,main_updates,nmi_skipped,main_last_cpu,camera,scroll_pos,scroll_amount,enemy_observations,parser_calls,scroll_calls\n')
local cycles=assert(io.open(OUTPUT..'main-cycles.csv','w'));cycles:write('frame,elapsed,interrupt_cpu,foreground_cpu,x,y\n')
local activeFrames,minSP,lastCPU=0,255,0
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
 if done then return end;done=true;shot('endpoint');csv:close();cycles:close();uiFile:close();epochFile:close();recordFile:close();enemyFile:close();combatFile:close()
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=ok,reason=reason,ROM_sha256=P.sha256,variant=P.variant,frames=frame,gameplay_frames=activeFrames,main_updates=updates,walked=startX and maxX-startX or 0,maximum_worldX=maxX,maximum_camera=maxCamera,native_enemy_observations=nativeEnemies,native_enemy_DMAS=enemyDMAs,native_enemy_pixel_frames=enemyPixelFrames,native_enemy_last_opaque=enemyLastPixels,actual_parser_calls=parserCalls,actual_scroll_calls=scrollCalls,terrain_changed=terrainChanged,earned=earned,native_defeats=nativeDefeats,native_score_calls=nativeScores,source_impact_calls=sourceImpacts,source_impact_commits=sourceImpactCommits,combat_phase=combatPhase,rise=startY and startY-apex or 0,jumped=jumped,landed=landed,standing_DMA=standingDMA,source_construct=sourceFresh,source_Main=sourceMain,source_body_steps=sourceMove,source_projectile_records=shotRecords,ground_projectile_observations=groundShots,air_projectile_observations=airShots,auth_A2_entries=authA2,epochs=epochs,both_owner_epochs=epochBoth,body_checks=gameBodyChecks,actual_DMA=uiChecks,rendered=renderedUI,background_checks=backgroundChecks,timing=timing,minimum_SP=minSP,vector_guards=vectorGuards,frame_completion_histogram=frameHistogram,scope='Real cold controller menu/lives and up to1000physical advancing gameplay. Actual worldX/camera page crossing, new native terrain/enemy parser, controller-earned original pistol/native Goomba contact. Original body/DMA/palette/stack/ISR guards. No earned pickups/full1-1/60Hz claim.'})..'\n');f:close();print('CF_COLD '..tostring(ok)..' '..reason..' frame='..frame);emu.stop(ok and 0 or 1);return
end
local function terrain()
 local q={};for i=0,415 do q[#q+1]=string.char(peek(L.Block_Buffer_1+i))end;return table.concat(q)
end
local function routeAfterMain()
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc');maxCamera=math.max(maxCamera,camera)
 local near=false
 for i=0,5 do
  local flag,id,st=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
  if flag>0 and flag<128 and id<21 and st&32==0 then
   nativeEnemies=nativeEnemies+1
   local ex=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)
   if id==6 and ex-x>18 and ex-x<100 and r('Player_State')==0 then near=true end
  end
 end
 if terrainInitial and updates%16==0 and terrain()~=terrainInitial then terrainChanged=true end
 if earned then
  assert(earned.original_impact_verified,'Mapped original impact commit must precede native Main return')
  if not earned.completed_Main then earned.completed_Main=updates;earned.completed_raw_C=r('CurrentBankC')end
  combatPhase='advance';routePad={right=true}
 elseif combatPhase=='approach'and near then
  combatPhase='shoot';shootSince=updates
 end
 if combatPhase=='approach'then routePad={right=true}
 elseif combatPhase=='shoot'then
  local settle=P.variant==2 and 0 or 4;local n=updates-shootSince
  routePad={down=true};if n>=settle and(n-settle)%8<2 then routePad.b=true end
  assert(n<100,'Bounded genuine fresh-B attack must earn a native defeat')
 end
 if x>=369 and camera>=257 then routePad={}end
end
for _,n in ipairs({'ScrollHandler','AreaParserTaskHandler','ProcessEnemyData'})do
 emu.addMemoryCallback(function()
  if phase=='game'and bank(L[n])==B[n]then if n=='ScrollHandler'then scrollCalls=scrollCalls+1 else parserCalls=parserCalls+1 end end
 end,emu.callbackType.exec,L[n])
end
@@TIMING@@
local function contact(stage,q)
 combatFile:write(table.concat({frame,updates+1,stage,q.enemy_slot,q.enemy_id,r('Enemy_State',q.enemy_slot),q.shot_slot,peek(L.CfState+0x382+q.shot_slot),peek(L.CfState+0x420+q.shot_slot),q.worldX,q.Y,r('SavedJoypadBits'),r('FloateyNum_Control',q.enemy_slot),r('Square1SoundQueue')},',')..'\n')
end
emu.addMemoryCallback(function()
 if not active()or r('CurrentBank')~=3 or r('CurrentBankC')~=2 then return end
 local slot=r('CfShotSlot');local foe=r('CfEnemySlot')
 assert(slot>=10 and slot<22 and foe<6,'Actual source projectile/native enemy slots')
 assert(peek(L.CfState+0x382+slot)==1 and peek(L.CfState+0x420+slot)==6,'Genuine starting pistol kind and original6/8 radius')
 assert(r('Enemy_ID',foe)==6 and r('Enemy_Flag',foe)>0 and r('Enemy_State',foe)&32==0,'Live naturally parsed Goomba before earned source shot')
 assert(r('SavedJoypadBits')&64~=0 or shotRecords>0,'Controller/source shot history observed')
 contactPending={frame=frame,Main=updates+1,shot_slot=slot,enemy_slot=foe,enemy_id=r('Enemy_ID',foe),worldX=peek(L.CfState+0x34e+slot)+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),Y=peek(L.CfState+0x368+slot),input=r('SavedJoypadBits'),source_input=peek(L.CfState+0x4aa),native_calls=0,score_calls=0}
 contact('source-contact',contactPending)
end,emu.callbackType.exec,L.CfOrdinaryDefeat)
emu.addMemoryCallback(function()
 if not active()or not contactPending or bank(L.ShellOrBlockDefeat)~=B.ShellOrBlockDefeat then return end
 local q=contactPending;assert(emu.getState()['cpu.x']==q.enemy_slot and r('ObjectOffset')==q.enemy_slot,'Real native defeat receives actual actor X/origin')
 q.native_calls=q.native_calls+1;nativeDefeats=nativeDefeats+1;contact('native-defeat',q)
end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function()
 if not active()or not contactPending or bank(L.SetupFloateyNumber)~=B.SetupFloateyNumber then return end
 local q=contactPending;local state=emu.getState();assert(state['cpu.x']==q.enemy_slot and state['cpu.a']==1,'Genuine native score writer origin/code')
 q.score_calls=q.score_calls+1;nativeScores=nativeScores+1;contact('native-score',q)
end,emu.callbackType.exec,L.SetupFloateyNumber)
emu.addMemoryCallback(function()
 if not active()or r('CurrentBank')~=3 or r('CurrentBankC')~=2 then return end
 local q=assert(contactPending,'Source impact follows actual native defeat')
 assert(q.native_calls==1 and q.score_calls==1 and r('Enemy_State',q.enemy_slot)&32~=0,'Native defeat/state and real score happen before original source impact')
 assert(r('FloateyNum_Control',q.enemy_slot)==1 and r('Square1SoundQueue')==P.native_defeat_sound,'Native earned score and SFX')
 assert(peek(L.CfState+0x382+q.shot_slot)==1 and peek(L.CfState+0x420+q.shot_slot)==6,'Unchanged original shot before genuine impact action')
 sourceImpacts=sourceImpacts+1;assert(not earned,'One earned first-Goomba result');earned=q;contact('source-impact',q);contactPending=nil
end,emu.callbackType.exec,L.CfSourceImpact)
emu.addMemoryCallback(function()
 if not active()or r('CurrentBank')~=3 or r('CurrentBankC')~=2 or not earned or earned.original_impact_verified then return end
 local q=earned
 assert(q.Main==updates+1 and r('CfShotSlot')==q.shot_slot,'Same genuine source shot/active Main at post-call boundary')
 assert(peek(L.CfState+0x382+q.shot_slot)==6,'Original source shot transitions to impact kind6')
 sourceImpactCommits=sourceImpactCommits+1;assert(sourceImpactCommits==1,'Single actual source impact commit')
 q.original_impact_verified=true;q.post_kind=6;q.post_PC=L.CfContactDone;q.post_frame=frame;q.post_raw_A=r('CurrentBank');q.post_raw_C=r('CurrentBankC')
 contact('impact-committed',q)
end,emu.callbackType.exec,L.CfContactDone)

emu.addEventCallback(function()
 if done then return end;local b={}
 if phase=='open'and age<6 or phase=='launch'and age<4 then b.start=true
 elseif phase=='browse'and age<4 and plan[step]then b[plan[step]]=true
 elseif phase=='game'then
  b=routePad
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 local mode,task,engine=r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine');local x,y=r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position')
 csv:write(table.concat({frame,phase,age,mode,task,engine,r('SelectedCharacter'),x,y,r('Player_State'),r('NumberofLives'),updates,r('NmiSkipped'),lastCPU,r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),r('Player_Pos_ForScroll'),r('ScrollAmount'),nativeEnemies,parserCalls,scrollCalls},',')..'\n')
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
   assert(renderedUI.lives and sourceFresh==1,'Visible cold lives and genuine sole construction');phase='game';age=0;startX,startY,lives,maxX,apex=x,y,r('NumberofLives'),x,y;terrainInitial=terrain()
  elseif age>400 then finish(false,'Cold native launch bound');return end
 elseif phase=='game'then
  if lastUI.game and frame-lastUI.game.frame==1 then rendered('game');gameBodyChecks=gameBodyChecks+1 end
  local body=lastUI.game
  if not standingDMA and body and body.sourceY==startY and age<80 then standingDMA={frame=body.frame,sourceY=body.sourceY,anchorY=body.anchorY,top=body.top,bottom=body.bottom}end
  if active()then
   assert(r('AreaType')==1 and ppu(0x3f00)==0x22 and ppu(0x3f10)==0x22,'Actual original blue world backdrop');backgroundChecks=backgroundChecks+1
   activeFrames=activeFrames+1;maxX=math.max(maxX,x);apex=math.min(apex,y)
   if y<startY-12 then jumped=true end
   if earned and earned.original_impact_verified and not renderedUI.earned and body and stable('game')then
    rendered('game');shot('earned-shot');renderedUI.earned={frame=frame,DMA_frame=body.frame,sourceY=body.sourceY,anchorY=body.anchorY,opaque=body.opaque}
   end
   if jumped and r('Player_State')==0 then landed=true end
   local now=r('NmiSkipped');if lastLag then timing.lag_counter_delta=timing.lag_counter_delta+(now-lastLag)%256 end;lastLag=now
  end
  if engine==11 or r('NumberofLives')~=lives then finish(false,'Native death/life loss');return end
  if maxX>=369 and maxCamera>=257 and nativeEnemies>0 and parserCalls>0 and scrollCalls>0 and terrainChanged and lastUI.game and lastUI.game.sourceX>=369 and lastUI.game.camera>=257 and stable('game')and not main then
   finish(updates>=200 and sourceMain==updates and sourceMove==updates and sourceEnd==updates and vectorGuards>60 and sourceAudio>0 and sourceFresh==1 and earned and earned.original_impact_verified and nativeDefeats==1 and nativeScores==1 and sourceImpacts==1 and sourceImpactCommits==1 and groundShots>0 and shotRecords>0 and renderedUI.earned and gameBodyChecks>=20 and enemyDMAs>=4 and enemyPixelFrames>=4 and renderedUI.jump and epochs>0 and authA2>0,'Controller-earned original CF pistol defeats a naturally parsed Goomba with native score/SFX/source impact; camera/page and original body/world checks; no1-1 clear claim');return
  end
  if age>=1000 and not main then finish(false,'1000gamephysical advancing-camera smoke bound');return end
 end
 if frame>=1800 then finish(false,'1800physical frame bound');return end
end,emu.eventType.endFrame)
