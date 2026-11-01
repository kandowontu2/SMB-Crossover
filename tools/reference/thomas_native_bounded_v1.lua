-- Cold UI and controller-only Thomas route. Game memory is read-only.
local P=assert(THOMAS_ARGS)
local frame,age,updates,step=0,0,0,1
local phase,done='title',false
local plan={'right','right','down','select','select'}
local pad,ui,pages,isrs={},{},{},{}
local upper,minSP,screenshots=0,255,0
local body,lastMain,livesFirst,initialLives=nil,nil,nil,nil
local counters={source=0,movement=0,defeat=0,nmi=0,irq=0,vectors=0,lifts=0}
local target,routeState,runup,hop,previous=1,'approach',0,0,nil
local targets={{400,176},{560,160},{688,144},{864,144}}
local clears,poses={},{}
local maxX,maxCamera=0,0
local csv=assert(io.open(OUTPUT..'updates.csv','w'))
csv:write('frame,Main,X,Y,camera,route_state,pipe,input,defeats,lift_Y,platform_contact\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function peek(a)return emu.read(a,emu.memType.nesDebug)end
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function raw(pc)
 if pc>=0xa000 and pc<0xc000 then return r('CurrentBank')end
 if pc>=0xc000 and pc<0xe000 then return r('CurrentBankC')end
 return pc<0xa000 and 254 or 255
end
local function selected()return r('SelectedCharacter')==10 and r('FmAlts')&68==64 end
local function active()return phase=='game'and selected()and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
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
 f:write(json({passed=ok,reason=reason,ROM_sha256=P.sha256,frames=frame,Main=updates,counters=counters,
 minimum_ISR_SP=minSP,pipe_clears=clears,maximum_X=maxX,maximum_camera=maxCamera,poses=poses,body_DMA=ui,
 scope='Cold controller-only native run; original staged CHR/pixels, real interrupts and native moving-platform crossings. No RAM writes, full1-1, audio, every upgrade or60Hz claim.'})..'\n');f:close()
 print('THOMAS_NATIVE '..tostring(ok)..' '..reason);emu.stop(ok and 0 or 1)
end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
for i=0,7 do emu.addMemoryCallback(function(_,v)pages[i]=upper+v end,emu.callbackType.write,0x5120+i)end
local function sample(page,record,stage)
 if ui[stage]and frame-ui[stage].frame<16 then return end
 local parts,expected,anchor={},{},nil
 for _,z in ipairs(record)do
  local found=nil
  for at=0,252,4 do
   local a=page*256+at;local y,t,attr,x=peek(a),peek(a+1),peek(a+2),peek(a+3)
   if y<240 and t==z[1]and attr&3==z[2]&3 and attr&192==z[2]&192 and(not anchor or(x-z[4])%256==anchor[1]and(y-z[3])%256==anchor[2])then
    found={y=y,t=t,attr=attr,x=x};anchor={(x-z[4])%256,(y-z[3])%256};break
   end
  end
  if not found then return end
  parts[#parts+1]=found
 end
 local count=0
 for _,z in ipairs(parts)do
  local start=(z.t&1)*4096+(z.t&254)*16;local physical=assert(pages[start//1024],'Actual CHR latch')
  assert(physical>=434 and physical<442,'Granted original Thomas art')
  for dy=0,15 do
   local at=(start&1023)+(dy//8)*16+dy%8
   local lo=emu.read(physical*1024+at,emu.memType.nesChrRom)
   local hi=emu.read(physical*1024+at+8,emu.memType.nesChrRom)
   assert(lo==P.chr[(physical-434)*1024+at+1]and hi==P.chr[(physical-434)*1024+at+9],'Original pattern bytes')
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
 local q=ui[stage];if not q or frame-q.frame<2 or frame-q.frame>15 then return false end
 local screen=emu.getScreenBuffer();local colors={}
 for at,nes in pairs(q.expected)do
  local rgb=screen[at+1]&0xffffff
  if colors[nes]and colors[nes]~=rgb then return false end;colors[nes]=rgb
 end
 local distinct={};for _,rgb in pairs(colors)do distinct[rgb]=true end
 local count=0;for _ in pairs(distinct)do count=count+1 end
 return count>=2 and r('DisableScreenFlag')==0 and r('Mirror_PPUMASK')&24==24
end
emu.addMemoryCallback(function()
 if not active()or raw(L.ThNaturalDrawDone)~=3 or r('CurrentBankC')~=2 then return end
 assert(peek(L.ThReady)==167,'Actual cold constructor completed')
 local pose=peek(L.ThPoseIndex);assert(pose<42,'Original pose index');poses[tostring(pose)]=true
 body=P.records[pose+1]
end,emu.callbackType.exec,L.ThNaturalDrawDone)
emu.addMemoryCallback(function(_,page)
 if not selected()then return end
 if phase=='browse'and step>#plan and age>=8 then sample(page,P.idle,'selected')
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then
  livesFirst=livesFirst or frame;sample(page,P.idle,'lives')
 elseif active()and body then sample(page,body,'game')end
end,emu.callbackType.write,0x4014)
for _,entry in ipairs({{'ThMovement',3,'movement'},{'ThomasC2AcceptedFrame',3,'source'},{'ThLiftTick',3,'lifts'}})do
 emu.addMemoryCallback(function()if active()and raw(L[entry[1]])==entry[2]then counters[entry[3]]=counters[entry[3]]+1 end end,emu.callbackType.exec,L[entry[1]])
end
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
   assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')
   counters.vectors=counters.vectors+1
  end
 end,emu.callbackType.exec,leave)
end
emu.addMemoryCallback(function()if active()then assert(emu.getState()['cpu.sp']>0x7a,'Stack overlaps SMC')end end,emu.callbackType.write,0x100,0x17a)
local function route()
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local py=r('Player_Y_Position')
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera)
 local lift,pipeTop=targets[target][1],targets[target][2]
 local slot,ly,contact=nil,nil,nil
 local near=false
 for i=0,5 do
  if r('Enemy_Flag',i)==1 and r('Enemy_ID',i)==37 and r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)==lift then slot=i;ly=r('Enemy_Y_Position',i);contact=r('PlatformCollisionFlag',i)end
  if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)==6 and r('Enemy_State',i)&32==0 then
   local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x
   if dx>0 and dx<=38 and math.abs(r('Enemy_Y_Position',i)-py)<=24 then near=true end
  end
 end
 if near then pad={down=true,b=updates%24<6}
 elseif routeState=='approach'then pad={right=true};if x>=lift-24 then routeState='wait';pad={}end
 elseif routeState=='wait'then pad={};if ly and ly>=188 and(not previous or ly>=previous)then routeState='runup';runup=0 end
 elseif routeState=='runup'then pad={right=true};runup=runup+1;if runup>=6 then routeState='hop';hop=0 end
 elseif routeState=='hop'then pad={right=true,up=hop<3};hop=hop+1;if x>=lift+14 then routeState='ride'end
 elseif routeState=='ride'then pad={};if py+32<=pipeTop-16 then routeState='cross';hop=0 end
 else pad={right=true,up=hop>=6 and hop<9};hop=hop+1 end
 csv:write(table.concat({frame,updates,x,py,camera,routeState,target,r('SavedJoypadBits'),counters.defeat,ly or-1,contact or-1},',')..'\n');csv:flush()
 previous=ly
 if target==1 and routeState=='ride'and slot~=nil and contact==slot and not ui.platform_shot and visible('game')then shot('platform');ui.platform_shot=true end
 if x>=lift+96 then
  if#clears<target then clears[#clears+1]={pipe_X=lift+48,Main=updates,X=x};print('THOMAS_PIPE '..json(clears[#clears]))end
  if#clears>=P.pipes then
   if visible('game')then finish(counters.defeat>0 and counters.source==counters.movement and counters.vectors>100,'Native moving-platform pipe crossings and source melee defeat');return end
  else target=target+1;routeState='approach';previous=nil end
 end
end
emu.addMemoryCallback(function()if active()and raw(L.GameLoop)==254 then assert(not lastMain,'No recursive Main');lastMain={sp=emu.getState()['cpu.sp']}end end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if lastMain and raw(P.main_return)==254 and emu.getState()['cpu.sp']==lastMain.sp then updates=updates+1;lastMain=nil;route()end
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
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2,'Start opens roster');phase='browse';age=0
 elseif phase=='browse'and age>=24 then
  if step<=#plan then step=step+1;age=0
  elseif visible('selected')then assert(r('CrossoverMenuIndex')==10 and selected(),'Actual Thomas Select alternate');shot('selected');phase='launch';age=0 end
 elseif phase=='launch'then
  if not ui.lives_shot and livesFirst and frame-livesFirst>=24 and visible('lives')then shot('lives');ui.lives_shot=true end
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(ui.lives_shot,'Visible lives sprite');phase='game';age=0;initialLives=r('NumberofLives')
  end
 elseif phase=='game'then
  if r('GameEngineSubroutine')==11 or r('NumberofLives')~=initialLives then finish(false,'Natural death during route');return end
  if updates>=4500 and not lastMain then finish(false,'4500 Main route bound');return end
 end
 if frame>=10000 then finish(false,'10000 physical frame bound')end
end,emu.eventType.endFrame)
