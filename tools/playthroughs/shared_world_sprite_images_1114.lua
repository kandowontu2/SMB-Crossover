-- Ordinary controls; actual mapper/OAM/palette observations, two in-memory PNGs.
local frame,polls,entries,completed,commits,epoch=0,0,0,0,0,0
local pad,stopped,menuDone=0,false,CPU_CONTROLLER_OPENING or false
local pendingMain,first,birth,lastCommit
local phase,changedAt='settle',0
local shots,events,inputs={}, {}, {}
local upper,chrMode,ppuCtrl=0,-1,-1
local spriteBanks,writeCounts={},{}
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(name,i)return read(assert(C.ram[name],name)+(i or 0))end
local function source(at,bank)return emu.read((bank or 2)*8192+at,emu.memType.nesWorkRam)end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function state()
 return{frame=frame,polls=polls,Main_entries=entries,Main_returns=completed,original_commits=commits,route_epoch=epoch,
  phase=phase,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),y_high=r('Player_Y_HighPos'),
  native_state=r('Player_State'),engine=r('GameEngineSubroutine'),lives=r('NumberofLives'),power=r('PlayerStatus'),
  scroll=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),world=r('WorldNumber'),level=r('LevelNumber'),
  action=source(0x616),pose=source(0x617),facing=source(0x615),mode=source(0x618),lock=source(0x6c0),
  foot=source(0x84)+256*source(0x85),prince_hp=source(0x6cf)}
end
local function actor(i)
 return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i),kind=r('PowerUpType',i),
  x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),y_high=r('Enemy_Y_HighPos',i),
  attribute=r('Enemy_SprAttrib',i),metasprite=r('EnemyMetasprite',i)}
end
local function actors()local a={};for i=0,5 do local q=actor(i);if q.flag~=0 then a[#a+1]=q end end;return a end
local function identity()
 assert(r('SelectedCharacter')==C.owner,'Actual selected owner')
 assert(C.role<0 or r('FmGroups')&7==C.role,'Actual selected WWF role')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Normal uncheated input')
 if C.key=='prince'then for bank=2,3 do for i,v in ipairs(C.prince_cookie)do assert(source(0x1fe0+i-1,bank)==v,'Complete current Prince cookie')end end end
end
local function finish(ok,why)
 if stopped then return end;stopped=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity=C.key,compiled_name=C.name,
  physical_frames=frame,input_polls=polls,Main_entries=entries,Main_returns=completed,original_commits=commits,
  shots=shots,first=first,mushroom_birth=birth,events=events,input_changes=inputs,terminal=state(),
  normal_controller_only=true,gameplay_seeds=0,output_files=0,images_in_memory=#shots,
  scope='Existing graphics observation only; no correct-art, collision, full-stage, performance or pixel-visibility acceptance.'}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function setPad(bits)
 if bits~=pad and#inputs<48 then inputs[#inputs+1]={frame=frame,completed=completed,epoch=epoch,phase=phase,bits=bits}end;pad=bits
end
local function switch(name,bits)
 assert(#events<32,'Bounded route phase events');phase,changedAt=name,epoch
 events[#events+1]={phase=name,state=state()};setPad(bits)
end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function floor(s)return s.y_high==1 and math.abs(s.y-176)<=2 and s.foot>=207 and s.foot<=211 end
local function nearGoomba(s)
 local best
 for i=0,5 do local a=actor(i);local dx=a.x-s.x
  if a.flag>0 and a.flag<128 and a.id==6 and a.state&32==0 and a.y_high==1 and dx>=-16 and(not best or dx<best.gap)then a.gap=dx;best=a end
 end;return best
end
local function drive()
 if not menuDone or not active()then return end
 identity();local s=state();first=first or s
 assert(s.lives==2 and s.world==0 and s.level==0,'Living actual1-1')
 assert(C.key~='prince'or s.prince_hp>0,'Living Prince')
 if C.key=='prince'then if commits==lastCommit then return end;lastCommit=commits end
 epoch=epoch+1;assert(epoch<1600,'Natural two-spot route bound1600')
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 then assert(a.kind==0,'First native kind0 mushroom');birth=birth or{state=s,actor=a}end end
 local e=nearGoomba(s);local age=epoch-changedAt
 if C.key=='prince'then
  if phase=='settle'and age>=4 then switch('approach',1)
  elseif phase=='approach'and e and e.gap>=115 and e.gap<=136 and s.action==1 and s.mode==1 and s.pose>=6 and s.pose<14 and s.lock==0 and s.native_state==0 then switch('evade',129)
  elseif phase=='evade'then
   if s.action==4 then setPad(1)end
   if age>=16 and s.action==1 and s.mode==1 and floor(s)then switch('runout',1)end
  elseif phase=='runout'and s.x>=390 then switch('backtrack',2)
  elseif phase=='backtrack'and s.action==1 and s.native_state==0 and s.facing==0 and s.x<=365 then switch('settle-jump',0)
  elseif phase=='settle-jump'and s.action==0 and s.native_state==0 and s.pose==15 and s.mode==0 and s.lock==0 then switch('turn',1)
  elseif phase=='turn'then
   if s.facing==255 then setPad(0)end
   if age>4 and s.facing==255 and s.action==0 and s.mode==0 and s.pose==15 and s.lock==0 then switch('jump',8)end
  elseif phase=='jump'and age>80 then setPad(0)end
 else
  if birth then setPad(0)
  elseif phase=='settle'then if age>=4 then switch('approach',1)end
  elseif phase=='jump'then setPad(age<18 and 128 or 0)
  elseif e and e.gap>0 and e.gap<=(C.key=='donkey_kong'and 100 or 40)then setPad(epoch%18<2 and(C.key=='honky'and 68 or 64)or 0)
  elseif s.x>=328 then switch('jump',128)
  else setPad(1)end
 end
end
local function hook(h,fn)
 emu.addMemoryCallback(guard(function()
  local q=emu.convertAddress(h.pc)
  if not q or q.memType~=emu.memType.nesPrgRom or q.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact current native hook')end;fn()
 end),emu.callbackType.exec,h.pc)
end
hook(C.hooks.GameLoop,function()
 assert(not pendingMain,'Prior Main returns')
 local sp=emu.getState()['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.GameLoopReturn0.pc or pc==C.hooks.GameLoopReturn1.pc,'Actual IdleLoop Main caller')
 pendingMain={pc=pc,sp=(sp+2)&255};entries=entries+1
end)
for i=0,1 do local h=C.hooks['GameLoopReturn'..i];hook(h,function()
 assert(pendingMain and pendingMain.pc==h.pc and pendingMain.sp==emu.getState()['cpu.sp'],'Actual completed Main PC/SP')
 pendingMain=nil;completed=completed+1;drive()
end)end
if C.key=='prince'then emu.addMemoryCallback(guard(function()
 local q=emu.convertAddress(0xb37c)
 if r('SelectedCharacter')==38 and q and q.memType==emu.memType.nesWorkRam and q.address==3*8192+(0xb37c&8191)then commits=commits+1 end
end),emu.callbackType.exec,0xb37c)end
for _,at in ipairs({0x2000,0x5101,0x5130,0x5120,0x5121,0x5122,0x5123,0x5124,0x5125,0x5126,0x5127})do
 emu.addMemoryCallback(guard(function(address,value)
  writeCounts[address]=(writeCounts[address]or 0)+1
  if address==0x2000 then ppuCtrl=value elseif address==0x5101 then chrMode=value
  elseif address==0x5130 then upper=value&3 else spriteBanks[address-0x5120]=(upper<<8)|value end
 end),emu.callbackType.write,at)
end
local function png64(bytes)
 local out={};for i=1,#bytes,3 do local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
  out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1);local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1);j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1)or'=';j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1)or'='end;return table.concat(out)
end
local function capture(tag,target)
 assert(#shots<C.maximum_images,'Two image maximum')
 assert(ppuCtrl>=0 and chrMode>=0,'Actual PPUCTRL and MMC5 mode writes observed')
 local png=emu.takeScreenshot();assert(type(png)=='string'and png:sub(1,8)=='\137PNG\13\10\26\10','Actual PNG header');assert(#png<=C.maximum_PNG_bytes,'PNG <=64KB')
 local oam,patterns,palette,shadow,software={}, {}, {}, {}, {}
 local height=ppuCtrl&32~=0 and 16 or 8
 for i=0,11 do software[#software+1]={window=i,bank=r('CurrentCHRBank',i),mode=r('X5ChrMode',i)}end
 for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end
 for slot=0,63 do
  local at=slot*4;local y=emu.read(at,emu.memType.nesSpriteRam)
  if y<240 then
   local tile=emu.read(at+1,emu.memType.nesSpriteRam);local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
   local pattern=height==16 and((tile&1)*4096+(tile&254)*16)or((ppuCtrl&8~=0 and 4096 or 0)+tile*16)
   local window=pattern//1024;local bank=assert(spriteBanks[window],'Actual sprite-bank latch')
   local key=tostring(bank)..'/'..tostring(pattern%1024)..'/'..height
   if not patterns[key]then local bytes={};for j=0,(height==16 and 31 or 15)do bytes[#bytes+1]=emu.read(bank*1024+pattern%1024+j,emu.memType.nesChrRom)end;patterns[key]=bytes end
   oam[#oam+1]={slot=slot,x=x,y=y,tile=tile,attributes=attr,palette=attr&3,behind_background=attr&32~=0,
    pattern=pattern,window=window,physical_bank=bank,pattern_key=key}
  end
  local base=0x200+at;if read(base)<240 then shadow[#shadow+1]={slot=slot,y=read(base),tile=read(base+1),attributes=read(base+2),x=read(base+3)}end
 end
 local scanlines={};local top=math.max(0,target.y-8);local bottom=math.min(239,target.y+31)
 for y=top,bottom do local eligible={};for _,p in ipairs(oam)do if y>=p.y+1 and y<p.y+1+height then eligible[#eligible+1]=p.slot end end
  if#eligible>0 then local first8={};for i=1,math.min(8,#eligible)do first8[i]=eligible[i]end;scanlines[#scanlines+1]={y=y,count=#eligible,first8=first8}end
 end
 local banks,counts={},{};for i=0,7 do banks[#banks+1]=spriteBanks[i]or-1 end;for at,count in pairs(writeCounts)do counts[at]=count end
 shots[#shots+1]={tag=tag,bytes=#png,state=state(),target=target,actors=actors(),actual_OAM=oam,shadow_OAM=shadow,
  ppu_control=ppuCtrl,ppu_control_shadow=r('Mirror_PPUCTRL'),sprite_height=height,MMC5_CHR_mode=chrMode,
  actual_sprite_banks=banks,software_CHR=software,wide_active=r('X5WideChrActive'),palette=palette,
  physical_pattern_bytes=patterns,scanline_candidates=scanlines,register_write_counts=counts}
 print('SMB_NATIVE_IMAGE '..png64(png))
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)setPad(bits);frames(4);setPad(0);frames(10)end
local function ready(fn)for _=1,1000 do if fn()then return end;coroutine.yield()end;error('Cold frontend readiness bound')end
local task=coroutine.create(function()
 if not CPU_CONTROLLER_OPENING then
  ready(function()return frame>=90 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
  press(16);ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
  assert(r('CrossoverMenuIndex')==0,'Actual initial Mario slot')
  for _,bits in ipairs(C.navigation)do press(bits)end
  assert(r('CrossoverMenuIndex')==C.slot and r('SelectedCharacter')==C.owner,'Actual compiled roster slot/owner')
  assert(C.role<0 or r('FmGroups')&7==C.role,'Actual compiled WWF role');press(16)
  ready(active)
 end
 menuDone=true;identity()
 while not stopped do coroutine.yield()end
end)
emu.addEventCallback(guard(function()
 polls=polls+1;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;assert(frame<12000,'Physical frame bound12000')
 local ok,why=coroutine.resume(task);assert(ok,why)
 if menuDone and first and not pendingMain and active()then
  local s=state();local target
  if#shots==0 then local e=nearGoomba(s);if e and e.x-s.scroll>=16 and e.x-s.scroll<=224 and e.gap>=50 and e.gap<=145 then target=e;capture('first-live-Goomba',e)end
  elseif#shots==1 then
   for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==0 and a.state>=128 and a.x-s.scroll>=16 and a.x-s.scroll<=224 and a.y<224 then target=a;capture('first-natural-mature-Mushroom',a);break end end
  end
  if#shots==2 then finish(true,'Two ordinary current421 world-sprite observations')end
 end
end),emu.eventType.endFrame)
