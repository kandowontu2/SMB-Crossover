-- Cold input only. Four selected PNGs; aggregate actual OAM/CHR/PPU/ISR data.
local P=assert(DOKI_ARGS)
local frame,age,step,updates,shots=0,0,1,0,0
local phase,done='title',false
local plan={'up'};for i=1,P.variant do plan[#plan+1]='select'end
local pad,body,pages,isrs={},{},{},{}
local upper,lastMain=0,nil
local shown,checks,poses={},{},{}
local startX,startY,lives,minY,maxX,maxCamera
local jumped,landed=false,false
local vectors,sourceTicks,damage,defeats,apu=0,0,0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function peek(a)return emu.read(a,emu.memType.nesDebug)end
local function raw(pc)if pc>=0xa000 and pc<0xc000 then return r('CurrentBank')elseif pc>=0xc000 and pc<0xe000 then return r('CurrentBankC')end;return pc<0xa000 and 254 or 255 end
local function active()return phase=='game'and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function json(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
 for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function shot(n)shots=shots+1;assert(shots<=4);local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function finish(ok,why)
 if done then return end;done=true;shot('endpoint')
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=ok,reason=why,ROM_sha256=P.sha256,variant=P.variant,frames=frame,Main=updates,jumped=jumped,landed=landed,minimum_Y=minY,maximum_X=maxX,maximum_camera=maxCamera,ISR_returns=vectors,source_movement=sourceTicks,damage=damage,defeats=defeats,APU_writes=apu,graphics_checks=checks,display=shown,poses=poses,phase=phase,scope='Cold selection/lives, authentic CHR/palette/descriptor DMA, idle/jump/native enemy encounters and opening camera crossing. No RAM writes, full1-1/shortcut/all-powerup or 60Hz claim.'})..'\n');f:close();print('DOKI_NATIVE '..tostring(ok)..' '..why);emu.stop(ok and 0 or 1)
end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
for i=0,7 do emu.addMemoryCallback(function(_,v)pages[i]=upper+v end,emu.callbackType.write,0x5120+i)end
emu.addMemoryCallback(function()apu=apu+1 end,emu.callbackType.write,0x4000,0x4017)
local function capture()
 if r('SelectedCharacter')~=25 or raw(L.S2Meta)~=246 then return end
 local ptr=r('SmPosePtr')+256*r('SmPosePtr',1);local n=peek(ptr)
 assert(n==16 or n==20,'Original four-cell Doki/five-cell USA record')
 body={};for i=1,n,4 do body[#body+1]={peek(ptr+i),peek(ptr+i+1),peek(ptr+i+2),peek(ptr+i+3)}end
 poses[tostring(r('S2Animation'))]=true
end
emu.addMemoryCallback(capture,emu.callbackType.exec,L.S2Meta)
local function sample(page,stage)
 if#body==0 then return end
 local cells,anchor={},nil
 for _,z in ipairs(body)do
  local found
  for at=0,252,4 do
   local a=page*256+at;local y,t,attr,x=peek(a),peek(a+1),peek(a+2),peek(a+3)
   if y<240 and t==z[1]and attr&195==z[2]&195 and(not anchor or(x-z[4])%256==anchor[1]and(y-z[3])%256==anchor[2])then found={x=x,y=y,t=t,attr=attr,offset=at};anchor={(x-z[4])%256,(y-z[3])%256};break end
  end
  if not found then return end;cells[#cells+1]=found
 end
 -- Hardware priority follows actual DMA order, including USA eye overlays.
 table.sort(cells,function(a,b)return a.offset<b.offset end)
 local expected={};local count=0
 for _,z in ipairs(cells)do
  local base=(z.t&1)*4096+(z.t&254)*16;local physical=assert(pages[base//1024],'CHR latch for window '..base//1024)
  assert(physical>=796 and physical<=807,'Owned original art page')
  for y=0,15 do
   local yy=z.attr&128~=0 and 15-y or y
   local off=(base&1023)+(yy//8)*16+yy%8
   local lo=emu.read(physical*1024+off,emu.memType.nesChrRom);local hi=emu.read(physical*1024+off+8,emu.memType.nesChrRom)
   assert(lo==P.chr[(physical-796)*1024+off+1]and hi==P.chr[(physical-796)*1024+off+9],'Exact original CHR bytes')
   for x=0,7 do
    local bit=z.attr&64~=0 and x or 7-x;local v=((lo>>bit)&1)|(((hi>>bit)&1)<<1);local px,py=z.x+x,z.y+y+1
    if v>0 and px<256 and py<240 then local at=py*256+px;if not expected[at]then expected[at]=emu.read(0x3f10+4*(z.attr&3)+v,emu.memType.nesPpuDebug);count=count+1 end end
   end
  end
 end
 checks[stage]=(checks[stage]or 0)+1
 if count>=70 then shown[stage]={frame=frame,opaque=count,cells=#cells,expected=expected,visible=shown[stage]and shown[stage].visible or false,shot=shown[stage]and shown[stage].shot or false}end
end
local function visible(stage)
 local q=shown[stage];if not q or frame-q.frame<1 or frame-q.frame>4 then return false end
 local screen=emu.getScreenBuffer();local colors={}
 for at,nes in pairs(q.expected)do local rgb=screen[at+1]&0xffffff;if colors[nes]and colors[nes]~=rgb then return false end;colors[nes]=rgb end
 local n=0;for _ in pairs(colors)do n=n+1 end
 if n>=2 and r('DisableScreenFlag')==0 and r('Mirror_PPUMASK')&24==24 then q.visible=true;return true end;return false
end
emu.addMemoryCallback(function(_,p)
 if r('SelectedCharacter')~=25 then return end
 if phase=='browse'and step>#plan then sample(p,'selected')elseif phase=='launch'and r('ScreenRoutineTask')==7 then sample(p,'lives')elseif active()then sample(p,'game')end
end,emu.callbackType.write,0x4014)
for _,kind in ipairs({'NMI','IRQ'})do
 local entry=kind=='NMI'and L.NonMaskableInterrupt or L.IrqScrollSplit;local leave=kind=='NMI'and L.NonMaskableInterrupt_RTI or L.IrqScrollSplit_RTI
 emu.addMemoryCallback(function()
  local s=emu.getState();local q=isrs[#isrs];if q and q.kind==kind and q.sp==s['cpu.sp']then return end
  local smc={}for i=0x15a,0x17a do smc[#smc+1]=peek(i)end
  isrs[#isrs+1]={kind=kind,sp=s['cpu.sp'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],smc=table.concat(smc,',')}
 end,emu.callbackType.exec,entry)
 emu.addMemoryCallback(function()
  local s=emu.getState();local q=isrs[#isrs]
  if q and q.kind==kind and q.sp==s['cpu.sp']then
   table.remove(isrs);local smc={}for i=0x15a,0x17a do smc[#smc+1]=peek(i)end
   assert(q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y']and q.smc==table.concat(smc,','),'ISR registers/SMC restored');vectors=vectors+1
  end
 end,emu.callbackType.exec,leave)
end
emu.addMemoryCallback(function()if active()and raw(L.S2Movement)==246 then sourceTicks=sourceTicks+1 end end,emu.callbackType.exec,L.S2Movement)
emu.addMemoryCallback(function()if active()and raw(L.S2InjuryStart)==246 then damage=damage+1 end end,emu.callbackType.exec,L.S2InjuryStart)
emu.addMemoryCallback(function()if active()and raw(L.ShellOrBlockDefeat)==254 then defeats=defeats+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
local function route()
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position');local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 minY=math.min(minY,y);maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera)
 if y<startY-20 then jumped=true end;if jumped and r('S2Air')==0 then landed=true end
 if updates<=40 then assert(x==startX,'No idle drift');pad={}
 elseif updates<=62 then pad={a=true}
 elseif updates<=105 then pad={}
 else
  local near=false
  for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)==6 and r('Enemy_State',i)&32==0 then local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x;if dx>0 and dx<54 then near=true end end end
  pad={right=true,a=near}
 end
 if updates%20==0 then print('DOKI_PROGRESS '..updates..' x='..x..' camera='..camera..' y='..y)end
end
emu.addMemoryCallback(function()if active()and raw(L.GameLoop)==254 then assert(not lastMain,'Recursive Main: previousSP='..tostring(lastMain)..' currentSP='..emu.getState()['cpu.sp']..' frame='..frame..' returnPC='..P.main_return);lastMain=emu.getState()['cpu.sp']end end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()if lastMain and raw(P.main_return)==254 and emu.getState()['cpu.sp']==lastMain then updates=updates+1;lastMain=nil;route()end end,emu.callbackType.exec,P.main_return)
emu.addEventCallback(function()
 local b={};if phase=='open'and age<6 or phase=='launch'and age<4 then b.start=true elseif phase=='browse'and age<4 and plan[step]then b[plan[step]]=true elseif phase=='game'then b=pad end;emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 for _,stage in ipairs({'selected','lives','game'})do visible(stage)end
 if phase=='title'and frame>=100 then assert(r('OperMode')==0);phase='open';age=0
 elseif phase=='open'and age>=36 then assert(r('CrossoverMenuState')==2);phase='browse';age=0
 elseif phase=='browse'and age>=24 then
  if step<=#plan then step=step+1;age=0 elseif shown.selected and shown.selected.visible then assert(r('CrossoverMenuIndex')==24 and r('S2Variant')==P.variant);shot('selected');phase='launch';age=0 end
 elseif phase=='launch'then
  if shown.lives and shown.lives.visible and not shown.lives.shot then shot('lives');shown.lives.shot=true end
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(shown.lives and shown.lives.visible,'Actual visible lives sprite');phase='game';age=0;startX=r('Player_X_Position')+256*r('Player_PageLoc');startY=r('Player_Y_Position');lives=r('NumberofLives');minY=startY;maxX=startX;maxCamera=0
  end
 elseif phase=='game'then
  if r('NumberofLives')~=lives or r('GameEngineSubroutine')==11 then finish(false,'Natural death');return end
  if updates>=35 and shown.game and not shown.game.shot and shown.game.visible then shot('gameplay');shown.game.shot=true end
  if updates>=105 and maxCamera>=257 and jumped and landed and shown.game and shown.game.visible and not lastMain then finish(vectors>100 and sourceTicks>100,'Cold original identity, displayed graphics, real jump/landing and camera crossing');return end
  if updates>=650 and not lastMain then finish(false,'650 Main route bound');return end
 end
 if frame>=2600 then finish(false,'2600 physical frame bound')end
end,emu.eventType.endFrame)
