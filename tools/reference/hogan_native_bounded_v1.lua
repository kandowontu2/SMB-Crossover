-- Cold controller entry and real source attacks. Read-only observations only.
local P=assert(HOGAN_ARGS)
local frame,age,updates,step=0,0,0,1
local phase,done='title',false
local plan={'right','right','right','right','up'} -- slot28 in the four-row grid
local pad={}
local counters={construct=0,movement=0,source=0,draw=0,damage=0,defeat=0,nmi=0,irq=0,vectors=0}
local body,ui,lastMain,isrs=nil,{},nil,{}
local pages,upper={},0
local minSP=255
local startX,startY,lives,minimumY,maximumX,maximumCamera
local jumped,landed=false,false
local idleX=nil
local attacks,poses={},{}
local livesFirst,registers,scrollSamples=nil,{},{}
local csv=assert(io.open(OUTPUT..'updates.csv','w'))
csv:write('frame,Main,X,Y,camera,state,input,source_action,source_group,body_DMA,source_damage,native_defeat\n')
local screenshots=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function peek(a)return emu.read(a,emu.memType.nesDebug)end
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function signed(v)return v>=128 and v-256 or v end
local function raw(pc)
 if pc>=0xa000 and pc<0xc000 then return r('CurrentBank')end
 if pc>=0xc000 and pc<0xe000 then return r('CurrentBankC')end
 return pc<0xa000 and 254 or 255
end
local function active()return phase=='game'and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function image()local t={}for a=0x15a,0x17a do t[#t+1]=peek(a)end;return table.concat(t,',')end
local function json(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
 for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function shot(n)
 screenshots=screenshots+1;assert(screenshots<=4,'Four PNG cap')
 local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function finish(ok,reason)
 if done then return end;done=true;shot('endpoint');csv:close()
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=ok==true,frontend_diagnostic=P.frontend_only,ROM_sha256=P.sha256,reason=reason,frames=frame,main_updates=updates,counters=counters,minimum_ISR_SP=minSP,jumped=jumped,landed=landed,maximum_X=maximumX,maximum_camera=maximumCamera,start_X=startX,start_Y=startY,minimum_Y=minimumY,attack_actions=attacks,poses=poses,body_DMA=ui,lives_scroll=scrollSamples,scope='Controller-only observations; frontend-only is diagnostic, not playable admission. ISR entry stack samples plus danger-zone write guard. No RAM writes, full1-1, upgrades, original audio or60Hz claim.'})..'\n');f:close()
 print('HOGAN_NATIVE '..tostring(ok)..' '..reason);emu.stop(ok and 0 or 1)
end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
for _,reg in ipairs({0x2000,0x2001,0x2005,0x2006})do
 emu.addMemoryCallback(function(_,v)
  if phase=='launch'then
   local s=emu.getState()
   registers[#registers+1]={frame=frame,register=reg,value=v,pc=s['cpu.pc'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle']}
   if#registers>32 then table.remove(registers,1)end
  end
 end,emu.callbackType.write,reg)
end
for i=0,7 do emu.addMemoryCallback(function(_,v)pages[i]=upper+v end,emu.callbackType.write,0x5120+i)end
local function sample(page,record,stage)
 if ui[stage]and frame-ui[stage].frame<8 then return end
 local parts,expected,anchor={}, {},nil
 for i=1,#record do
  local z=record[i];local found=nil
  for at=0,252,4 do
   local a=page*256+at;local y,t,attr,x=peek(a),peek(a+1),peek(a+2),peek(a+3)
   if y<240 and t==z[1]and attr&3==z[2]&3 and attr&192==z[2]&192 and(not anchor or(x-z[4])%256==anchor[1]and(y-z[3])%256==anchor[2])then
    found={y=y,t=t,attr=attr,x=x};anchor={(x-z[4])%256,(y-z[3])%256};break
   end
  end
  if not found then return end -- complete owner groups can intentionally yield
  parts[#parts+1]=found
 end
 local count=0
 for _,z in ipairs(parts)do
  local start=(z.t&1)*4096+(z.t&254)*16;local physical=assert(pages[start//1024],'Actual sprite CHR latch')
  assert(physical>=546 and physical<563,'Granted original Hogan art page')
  for dy=0,15 do
   local at=(start&1023)+(dy//8)*16+dy%8
   local lo=emu.read(physical*1024+at,emu.memType.nesChrRom)
   local hi=emu.read(physical*1024+at+8,emu.memType.nesChrRom)
   assert(lo==P.chr[(physical-546)*1024+at+1]and hi==P.chr[(physical-546)*1024+at+9],'Original Hogan pattern bytes')
   for dx=0,7 do
    local bit=(z.attr&64~=0)and dx or 7-dx
    local value=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
    local px,py=z.x+dx,z.y+dy+1
    if value>0 and px<256 and py<240 then
     local pos=py*256+px
     if expected[pos]==nil then expected[pos]=ppu(0x3f10+4*(z.attr&3)+value);count=count+1 end
    end
   end
  end
 end
 if count<80 then return end
 ui[stage]={frame=frame,opaque=count,parts=#parts,expected=expected,checks=ui[stage]and ui[stage].checks+1 or 1}
end
local function visible(stage)
 local q=ui[stage];if not q or frame-q.frame<2 or frame-q.frame>7 then return false end
 local screen=emu.getScreenBuffer();local colors={}
 for at,nes in pairs(q.expected)do
  local rgb=screen[at+1]&0xffffff
  if colors[nes]and colors[nes]~=rgb then return false end
  colors[nes]=rgb
 end
 local distinct={};for _,rgb in pairs(colors)do distinct[rgb]=true end
 local count=0;for _ in pairs(distinct)do count=count+1 end
 return count>=2 and r('DisableScreenFlag')==0 and r('Mirror_PPUMASK')&24==24
end
-- Snapshot only while the authenticated selected C2 state is genuinely mapped.
emu.addMemoryCallback(function()
 if not active()or raw(L.WfTagDone)~=224 or r('CurrentBankC')~=2 then return end
 assert(peek(L.WfHostReady)==167,'Real forcedblank constructor completed')
 local size=peek(L.WfRenderBuffer);assert(size>0 and size<=64 and size%4==0,'Bounded original source record')
 local record={}
 for i=0,size-1,4 do record[#record+1]={peek(L.WfRenderBuffer+1+i),peek(L.WfRenderBuffer+2+i),signed(peek(L.WfRenderBuffer+3+i)),signed(peek(L.WfRenderBuffer+4+i))}end
 body={record=record,action=peek(L.WfState+0x3c),group=peek(L.WfState+0x32)}
 attacks[tostring(body.action)]=true;poses[tostring(body.group)]=true
end,emu.callbackType.exec,L.WfTagDone)
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=29 or r('FmGroups')&7~=0 then return end
 if phase=='browse'and step>#plan and age>=8 then sample(page,P.idle,'selected')
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then
  livesFirst=livesFirst or frame;sample(page,P.idle,'lives')
 elseif active()and body then sample(page,body.record,'game')end
end,emu.callbackType.write,0x4014)
for _,entry in ipairs({{'WfConstructCold',224,'construct'},{'WfMovement',224,'movement'},{'WfHostFrame',2,'source'},{'WfDrawBody',224,'draw'}})do
 emu.addMemoryCallback(function()if r('SelectedCharacter')==29 and raw(L[entry[1]])==entry[2]then counters[entry[3]]=counters[entry[3]]+1 end end,emu.callbackType.exec,L[entry[1]])
end
emu.addMemoryCallback(function()
 if active()and raw(L.WfRawProxyCommit)==224 and r('CurrentBankC')==2 and peek(L.WfProxyValid)~=0 and peek(L.WfState+0x7a)<200 then counters.damage=counters.damage+1 end
end,emu.callbackType.exec,L.WfRawProxyCommit)
emu.addMemoryCallback(function()if active()and raw(L.ShellOrBlockDefeat)==254 then counters.defeat=counters.defeat+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
for _,kind in ipairs({'NMI','IRQ'})do
 local entry=kind=='NMI'and L.NonMaskableInterrupt or L.IrqScrollSplit
 local leave=kind=='NMI'and L.NonMaskableInterrupt_RTI or L.IrqScrollSplit_RTI
 emu.addMemoryCallback(function()
  if active()or lastMain or#isrs>0 then
   local s=emu.getState();minSP=math.min(minSP,s['cpu.sp']);local t=isrs[#isrs]
   if t and t.kind==kind and t.sp==s['cpu.sp']then return end
   isrs[#isrs+1]={kind=kind,sp=s['cpu.sp'],smc=image(),a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y']}
   counters[kind=='NMI'and'nmi'or'irq']=counters[kind=='NMI'and'nmi'or'irq']+1
  end
 end,emu.callbackType.exec,entry)
 emu.addMemoryCallback(function()
  if#isrs>0 then local q=table.remove(isrs);local s=emu.getState()
   assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')
   assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Real vector restores SMC and live registers')
   counters.vectors=counters.vectors+1
  end
 end,emu.callbackType.exec,leave)
end
emu.addMemoryCallback(function()
 if active()then local sp=emu.getState()['cpu.sp'];assert(sp>0x7a,'Stack must not overlap SMC code')end
end,emu.callbackType.write,0x100,0x17a)
local function route()
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position')
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 maximumX=math.max(maximumX,x);minimumY=math.min(minimumY,y);maximumCamera=math.max(maximumCamera,camera)
 if y<startY-20 then jumped=true end
 if jumped and r('Player_State')==0 then landed=true end
 if updates<=70 then
  idleX=idleX or x;assert(x==idleX,'No stationary drift');pad={}
 elseif updates<=95 then pad={right=true}
 elseif updates<=113 then pad={a=true}
 elseif updates<=140 then pad={}
 elseif updates<=149 then pad={b=updates>=145}
 else
  local near=false
  for i=0,5 do
   if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)==6 and r('Enemy_State',i)&32==0 then
    local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x
    if dx>0 and dx<=40 then near=true end
   end
  end
  if near then pad={b=updates%18<2}else pad={right=true}end
 end
 csv:write(table.concat({frame,updates,x,y,camera,r('Player_State'),r('SavedJoypadBits'),body and body.action or-1,body and body.group or-1,ui.game and ui.game.checks or 0,counters.damage,counters.defeat},',')..'\n');csv:flush()
end
emu.addMemoryCallback(function()
 if active()and raw(L.GameLoop)==254 then assert(not lastMain,'No recursive Main');lastMain={sp=emu.getState()['cpu.sp']}end
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if lastMain and raw(P.main_return)==254 and emu.getState()['cpu.sp']==lastMain.sp then
  updates=updates+1;lastMain=nil;route()
 end
end,emu.callbackType.exec,P.main_return)
emu.addEventCallback(function()
 if done then return end;local b={}
 if phase=='open'and age<6 or phase=='launch'and age<4 then b.start=true
 elseif phase=='browse'and age<4 and plan[step]then b[plan[step]]=true
 elseif phase=='game'then b=pad end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame==100 then assert(r('OperMode')==0,'Cold title');phase='open';age=0
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2,'Start opens actual roster');phase='browse';age=0
 elseif phase=='browse'and age>=24 then
  if step<=#plan then step=step+1;age=0
  elseif visible('selected')then assert(r('CrossoverMenuIndex')==28 and r('SelectedCharacter')==29,'Actual highlighted Hogan');shot('selected');phase='launch';age=0 end
 elseif phase=='launch'then
  if not ui.lives_shot and livesFirst and frame-livesFirst>=24 and visible('lives')then
   local s=emu.getState();local pp={}
   for k,v in pairs(s)do if k:find('ppu.',1,true)==1 and type(v)~='table'then pp[k]=v end end
   scrollSamples[#scrollSamples+1]={frame=frame,ppu=pp,registers=registers,horizontal=r('HorizontalScroll'),vertical=r('VerticalScroll'),control=r('Mirror_PPUCTRL'),mask=r('Mirror_PPUMASK'),disable=r('DisableScreenFlag')}
   shot('lives');ui.lives_shot=true
  end
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(ui.lives_shot,'Actual visible lives sprite');phase='game';age=0
   startX=r('Player_X_Position')+256*r('Player_PageLoc');startY=r('Player_Y_Position');lives=r('NumberofLives');minimumY=startY;maximumX=startX;maximumCamera=0
  end
 elseif phase=='game'then
  if P.frontend_only and updates>=30 and visible('game')and not lastMain then finish(true,'Short cold frontend diagnostic only');return end
  if r('GameEngineSubroutine')==11 or r('NumberofLives')~=lives then finish(false,'Natural injury/death while attempting original source attack');return end
  if updates>=140 and not ui.jump_shot and visible('game')then shot('gameplay');ui.jump_shot=true end
  if counters.damage>0 and counters.defeat>0 and maximumX>=369 and maximumCamera>=257 and visible('game')and not lastMain then
   finish(jumped and landed and counters.source==counters.movement and counters.vectors>100,'Real cold Hogan, stationary/jump/source attack/native defeat and camera crossing');return
  end
  if updates>=500 and not lastMain then finish(false,'500 Main route bound: require genuine source attack defeat and advancing camera');return end
 end
 if frame>=1800 then finish(false,'1800 physical frame bound');return end
end,emu.eventType.endFrame)
