-- Real menu/input, legal staged pickup/shot actors, production dispatch only.
local C=assert(SAMUS_SOURCE_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done=false,false
local current=nil
local results,violations={},{}
local minSP,stackWrites=255,0
local phase='menu'
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function world()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)return bank(C.hooks[n].address)==C.hooks[n].physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n)end end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
end
local function problem(message,data,known)
 local st=emu.getState();local q={wall=wall,case=index,age=age,phase=phase,message=message,data=data,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),sp=st['cpu.sp']}
 violations[#violations+1]=q
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close()
 capture('failure-'..index..'-'..age..'-'..#violations)
 if C.diagnostic~=1 or not known then assert(false,message)end
end
local log=assert(io.open(OUTPUT..'updates.csv','w'));log:write('wall,case,age,phase,playerY,state,lives,marker,hp,equipment,ammo\n')
local writes=assert(io.open(OUTPUT..'first-writes.csv','w'));writes:write('wall,case,age,phase,pc,bank,address,old,new\n')
local returns,installed={},{}
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp'];minSP=math.min(minSP,sp)
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret
 returns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installed[key]then installed[key]=true;emu.addMemoryCallback(function()
  local q=returns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
  returns[key]=nil;q.fn()
 end,emu.callbackType.exec,ret)end
end
local savedNmi=nil
local nmiWindows={}
local function storeAt(pc,target)
 return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256
end
local function bankWindow(pc,target,shadow)
 if storeAt(pc,target)then
  return storeAt(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and storeAt(pc-5,shadow))
 end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and storeAt(pc+2,target)and storeAt(pc-3,shadow)
end
emu.addMemoryCallback(function(address,value)
 if entered and not done then assert(false,'Native stack crosses the end of copied SMC code')end
end,emu.callbackType.write,C.stack_guard)
emu.addMemoryCallback(function()
 if not entered then return end
 bind('NonMaskableInterrupt')
 savedNmi={a=bank(0xa000),c=bank(0xc000),fields={},sp=emu.getState()['cpu.sp']}
 savedNmi.cpu_a=emu.getState()['cpu.a']
 savedNmi.shadow_a=r('CurrentBank')&127;savedNmi.shadow_c=r('CurrentBankC')&127
 local sp=savedNmi.sp
 savedNmi.resume=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 savedNmi.resume_bank=bank(savedNmi.resume);savedNmi.code={}
 for i=-8,8 do savedNmi.code[#savedNmi.code+1]=emu.read(savedNmi.resume+i,emu.memType.nesDebug)end
 savedNmi.a_window=savedNmi.a~=savedNmi.shadow_a and bankWindow(savedNmi.resume,0x5115,L.CurrentBank)
 savedNmi.c_window=savedNmi.c~=savedNmi.shadow_c and bankWindow(savedNmi.resume,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do savedNmi.fields[#savedNmi.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1;minSP=math.min(minSP,savedNmi.sp)
end,emu.callbackType.exec,C.hooks.NonMaskableInterrupt.address)
emu.addMemoryCallback(function()
 if not savedNmi then return end
 local wantA=savedNmi.a_window and savedNmi.shadow_a or savedNmi.a
 local wantC=savedNmi.c_window and savedNmi.shadow_c or savedNmi.c
 if bank(0xa000)~=wantA or bank(0xc000)~=wantC then
  local q=savedNmi;q.after_a=bank(0xa000);q.after_c=bank(0xc000)
  problem('NMI restores foreground A/C banks',q)
 end
 assert((r('CurrentBank')&127)==savedNmi.shadow_a and(r('CurrentBankC')&127)==savedNmi.shadow_c,'NMI restores foreground bank shadows')
 assert(emu.getState()['cpu.a']==savedNmi.cpu_a,'NMI restores foreground A before resumed mapper store')
 if savedNmi.a_window or savedNmi.c_window then nmiWindows[#nmiWindows+1]={wall=wall,case=index,age=age,resume=savedNmi.resume,
  a=savedNmi.a,shadow_a=savedNmi.shadow_a,c=savedNmi.c,shadow_c=savedNmi.shadow_c,code=savedNmi.code}end
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==savedNmi.fields[i],'NMI preserves five SMC operands')end
 assert(emu.getState()['cpu.sp']==savedNmi.sp,'NMI stack balanced before RTI');savedNmi=nil
end,emu.callbackType.exec,C.hooks.NmiReturn.address)



local chr=dofile(C.chr_observer)({character=2,out=OUTPUT,legacy_map=C.legacy_chr})
local dma=nil
local function sw(n,v,s)w(n,v,s)end
local function clear()
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('InvPickup',252,i)end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('SmShotImpact',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GuestHurtTicks','GuestHurtKind','InvPrevious','InvFresh','SmBall','SmCrouch','SmPreviousDirections','SmFlip','A_B_Buttons','PreviousA_B_Buttons','Player_X_Speed','Player_Y_Speed','Player_X_Scroll','Player_X_MoveForce','Player_Y_MoveForce','CheatInvincible','GamePauseStatus','GamePauseTimer'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
local function seed(q)
 clear();age=0;current={name=q.name,mode=q.mode,direction=q.direction,face=q.face,checks=0,positions={},crossings=0,spawn=0,grant=0,hardware=0}
 w('CrossoverBehaviorVersion',q.mode);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 local x=q.center-(q.face==1 and 10 or 6)
 if q.direction~=3 then x=q.center-(q.face==1 and 21 or -5)end
 w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',q.face);w('Player_MovingDir',q.face);w('Player_CollisionBits',255);w('PlayerSize',0)
 w('SmWavePolarity',1-q.polarity)
 if q.mode==0 then w('PlayerStatus',2);w('InvOwnedLo',0,2);phase='release';current.release_age=0
 else
  w('PlayerStatus',1);w('InvOwnedLo',129,2);w('InvOwnedHi',0,2)
  local s=5
  w('Enemy_Flag',1,s);w('Enemy_ID',C.power_id,s);w('Enemy_State',128,s);w('PowerUpType',1,s);w('Enemy_X_Position',x%256,s);w('Enemy_PageLoc',x//256,s);w('Enemy_Y_Position',184,s);w('Enemy_Y_HighPos',1,s);w('Enemy_BoundBoxCtrl',3,s)
  w('Enemy_X_Speed',0,s);w('Enemy_Y_Speed',0,s);w('Enemy_X_MoveForce',0,s);w('Enemy_Y_MoveForce',0,s);w('Enemy_MovingDir',1,s);w('Enemy_SprAttrib',0,s);w('InvPickup',4,s);w('InvPickupOwner',2,s);w('InvRisePhase',0,s)
  phase='pickup'
 end
 print('SAMUS_WAVE_SEED '..json({case=index,wall=wall,name=q.name,phase=phase}))
end
emu.addMemoryCallback(function()
 if not entered or done or not valid('InventoryGrant')then return end
 assert(phase=='pickup'and emu.getState()['cpu.a']==4,'Real Hard Wave item collision and grant')
 current.grant=current.grant+1
 onReturn('wave-grant',function()
  assert(r('InvOwnedLo',2)==145,'Hard Wave physically collected with Long retained')
  phase='release';current.release_age=age
 end)
end,emu.callbackType.exec,C.hooks.InventoryGrant.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('SamusWeapons::Spawn')or phase~='fire'then return end
 onReturn('spawn',function()
  local s=r('SmSlot');assert(r('SmShotType',s)==3,'Actual B creates native Wave Beam')
  current.slot=s;current.spawn=current.spawn+1;current.center=r('SmShotX',s)+256*r('SmShotPage',s);current.centerY=r('SmShotY',s);current.polarity=r('SmShotPolarity',s);current.lastPage=r('SmShotPage',s)
  print('SPAWN '..json({center=current.center,want=C.cases[index].center,dir=r('SmShotDir',s),wantdir=C.cases[index].direction,held=r('SavedJoypadBits'),player=world(),face=r('PlayerFacingDir')}))
  assert(current.center==C.cases[index].center and r('SmShotDir',s)==C.cases[index].direction,'Actual muzzle and held Up own source direction')
  current.spawn_age=age;phase='flight'
 end)
end,emu.callbackType.exec,C.hooks['SamusWeapons::Spawn'].address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('SamusWeapons::Move')or phase~='flight'or emu.getState()['cpu.x']~=current.slot then return end
 local s=current.slot;local n=r('SmShotAge',s);local off=C.wave[n];if off>=128 then off=off-256 end;if current.polarity==0 then off=-off end
 local expected=current.direction==3 and current.center+off or nil
 current.pending_expected=expected;current.pending_age=n;current.inside_move=true
 onReturn('wave-move',function()
  current.inside_move=false
  local got=r('SmShotX',s)+256*r('SmShotPage',s);local live=r('SmShotType',s)~=0;local sc=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
  local visible=not expected or(expected>=sc and expected<sc+256)
  if expected and got~=expected then
   if not current.bad then current.bad=true;problem('Upward Wave loses its world page',{center=current.center,age=n,expected=expected,actual=got,live=live,scroll=sc,first_wrong_erase=current.first_wrong_erase},true)end
  elseif visible and not live and r('SmShotY',s)>=32 and not current.bad then current.bad=true;problem('Visible source Wave disappears',{expected=expected,y=r('SmShotY',s),age=n,first_wrong_erase=current.first_wrong_erase},true)end
  if live then
   current.checks=current.checks+1
   if r('SmShotPage',s)~=current.lastPage then current.crossings=current.crossings+1;capture('case-'..index..'-cross-'..n)end
   current.lastPage=r('SmShotPage',s)
  end
  current.positions[#current.positions+1]={age=n,x=got,y=r('SmShotY',s),expected=expected or-1,live=live}
  if n==6 or n==12 then capture('case-'..index..'-age-'..n)end
 end)
end,emu.callbackType.exec,C.hooks['SamusWeapons::Move'].address)
emu.addMemoryCallback(function(at,value)
 if not entered or done or phase~='flight'or not current.slot or current.first_wrong_terrain then return end
 local st=emu.getState();local slot=current.slot
 if at==L.SmShotImpact+slot and value==3 and r('SmShotType',slot)==3 and r('GuestEnemyMask')==0 and bank(st['cpu.pc'])==C.hooks['SamusWeapons::Impact'].physical_bank and st['cpu.pc']==C.hooks['SamusWeapons::Impact'].address+8 then
  current.first_wrong_terrain={pc=st['cpu.pc'],bank=bank(st['cpu.pc']),address=at,old=r('SmShotImpact',slot),new=value,age=r('SmShotAge',slot)}
  writes:write(table.concat({wall,index,age,phase,st['cpu.pc'],bank(st['cpu.pc']),at,r('SmShotImpact',slot),value},',')..'\n');writes:flush()
  if not current.bad then current.bad=true;problem('Wave enters terrain collision through a different pool slot',current.first_wrong_terrain,true)end
 end
end,emu.callbackType.write,L.SmShotImpact,L.SmShotImpact+2)
emu.addMemoryCallback(function(address,value)
 if not entered or done or phase~='flight'or not current.inside_move or not current.pending_expected then return end
 local s=current.slot;if address~=L.SmShotType+s or value~=0 or current.first_wrong_erase then return end
 local want=current.pending_expected;local sc=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 if want>=sc and want<sc+256 and r('SmShotY',s)>=32 then
  local st=emu.getState();current.first_wrong_erase={pc=st['cpu.pc'],bank=bank(st['cpu.pc']),address=address,old=r('SmShotType',s),new=value,age=current.pending_age,expected=want}
  writes:write(table.concat({wall,index,age,phase,st['cpu.pc'],bank(st['cpu.pc']),address,r('SmShotType',s),value},',')..'\n');writes:flush()
 end
end,emu.callbackType.write,L.SmShotType,L.SmShotType+2)
emu.addMemoryCallback(function()
 if not valid('PauseSkip')or not native()or r('SelectedCharacter')~=2 then return end
 if not entered then if world()<244 then return end;entered=true;index=1;seed(C.cases[index]);return end
 if done then return end
 age=age+1
 if phase~='pickup'then for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end end
 assert(age<90,'Bounded pickup and actual Wave shot')
 if phase=='release'and age-current.release_age>=2 then
  local q=C.cases[index];local x=q.center-(q.direction==3 and(q.face==1 and 10 or 6)or(q.face==1 and 21 or -5))
  w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('PlayerFacingDir',q.face)
  for i=0,2 do w('MmVX',0,i)end;for i=0,1 do w('MmXFraction',0,i)end;w('Player_X_Speed',0)
  phase='fire'
 end
 if phase=='flight'and age-current.spawn_age>=18 then
  assert(current.spawn==1 and(current.grant==1 or current.mode==0),'One source shot per actual equipment fixture')
  print('ENDCASE '..json(current))
  if not current.bad then assert(current.checks>=18 and(current.direction~=3 or current.crossings>0),'Live actual Wave traversal and page crossing')end
  capture('case-'..index..'-result');results[#results+1]=current;index=index+1
  if index>#C.cases then done=true else seed(C.cases[index])end
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
emu.addMemoryCallback(function(_,value)
 if not entered or done then return end;dma={case=index,bytes={}};for i=0,255 do dma.bytes[i+1]=emu.read(value*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if native()then b.right=true;w('CheatInvincible',1)
  elseif wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=C.menu_target then b[C.menu_moves[r('CrossoverMenuIndex')+1]]=true else b.a=true end
  end
 elseif not done and phase=='fire'then b.b=true;if C.cases[index].direction==3 then b.up=true end end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<2400,'Bounded native source audit')
 if entered and not done and dma and dma.case==index then
  for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma.bytes[i+1],'Exact committed DMA reaches hardware OAM')end
  current.hardware=current.hardware+1
 end
 if done then
  chr.finish();assert(not chr.failure(),'Native hardware CHR matches published player image')
  local p={passed=#violations==0,cases=results,violations=violations,nmis=nmis,min_sp_sampled=minSP,nmi_mapper_store_windows=nmiWindows,wall_frames=wall,scope='Cold real selection/navigation; explicit legal power/equipment/player staging. Hard Wave is collected through actual item collision/InventoryGrant; Easy wave tier is seeded. Actual Up+B/B spawn and full source-shot updates; no injected CPU calls. NMI/5SMC/bank/SP sentinel, committed hardware OAM/CHR and raw PPU frames. No full route, natural item emergence, audio fidelity or performance claim.'}
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json(p));f:close();log:close();writes:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
