-- Real menu entry, native UI calls/returns and NMI. Explicit component staging.
local C=assert(ROBOT_CONFIG)
local wall,updates,nmis,index,age=0,0,0,0,0
local entered,done,active=false,false,false
local results={}
local function json(v)
 if type(v)=='table'then
  local out={}
  if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..json(x)end
  return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function actual(h)
 local p=emu.convertAddress(h.pc)
 return p and p.address//8192==h.bank
end
local function bound(h)
 for i,v in ipairs(h.code)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Native UI opcode binding')end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local saved=nil
emu.addMemoryCallback(function()
 if not entered then return end
 saved={a=emu.convertAddress(0xa000).address//8192,c=emu.convertAddress(0xc000).address//8192,fields={}}
 for _,a in ipairs(C.smc)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1
end,emu.callbackType.exec,C.nmi.pc)
emu.addMemoryCallback(function()
 if not saved then return end
 assert(emu.convertAddress(0xa000).address//8192==saved.a and emu.convertAddress(0xc000).address//8192==saved.c,'UI NMI restores foreground banks')
 for i,a in ipairs(C.smc)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'UI NMI preserves five SMC operands')end
 saved=nil
end,emu.callbackType.exec,C.nmi_return.pc)
local entrySP,minSP=0,255
emu.addMemoryCallback(function()
 if not actual(C.entry)or not native()or r('SelectedCharacter')~=C.character then return end
 bound(C.entry);entered=true;updates=updates+1
 index=(updates-1)//12+1;age=(updates-1)%12
 if index>#C.cases then done=true;return end
 if age~=0 then return end
 local q=C.cases[index]
 -- Stage legal equipment/input and three live pellets at the actual native
 -- UI boundary. No routine/return/mapper/interrupt is simulated or skipped.
 w('CrossoverBehaviorVersion',1);w('PlayerStatus',1);w('GuestHurtTicks',0)
 w('InvRefill',0);w('InvPrevious',0);w('InvOwnedLo',q.owned,C.character)
 w('InvOwnedHi',C.character==1 and 4 or 0,C.character)
 w('InvSelected',q.selected,C.character);w('GamePauseStatus',q.pause)
 -- SavedJoypadBits and SavedJoypad1Bits are the same native byte.
 w('SavedJoypad1Bits',q.button|64)
 w('MmChargeFrames',48);w('MmCharging',1)
 for i=0,3 do
  w('MmBulletType',i==2 and 0 or 1,i)
  local x=r('Player_X_Position')+256*r('Player_PageLoc')+24+i*8
  w('MmBulletX',x%256,i);w('MmBulletPage',x//256,i)
  w('MmBulletY',r('Player_Y_Position')+16,i);w('MmBulletDir',1,i);w('MmBulletAge',0,i)
 end
 entrySP=emu.getState()['cpu.sp'];active=true
end,emu.callbackType.exec,C.entry.pc)
for _,h in ipairs(C.returns)do
 emu.addMemoryCallback(function()
  if not active or not actual(h)then return end
  bound(h);active=false
  local q=C.cases[index];local shots={}
  for i=0,3 do shots[#shots+1]=r('MmBulletType',i)end
  local row={case=index,name=q.name,frame=wall,selected=r('InvSelected',C.character),charge=r('MmChargeFrames'),charging=r('MmCharging'),shots=shots,fresh=r('InvFresh'),previous=r('InvPrevious'),owned=r('InvOwnedLo',C.character),status=r('PlayerStatus'),pause=r('GamePauseStatus')}
  results[#results+1]=row;print('ROBOT_UI '..json(row))
  assert(emu.getState()['cpu.sp']==entrySP,'UI returns at original native stack depth')
  assert(row.selected==q.want,'Expected actual selection')
  assert(row.charge==(q.clear==1 and 0 or 48),'No-op selection retains charge; true switch clears it')
  assert(row.charging==(q.clear==1 and 0 or 1),'No-op selection retains charging')
  for i,v in ipairs(shots)do assert(v==(q.clear==1 and 0 or (i==3 and 0 or 1)),'Live pellet cleanup only for a real switch')end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function()
 if entered then minSP=math.min(minSP,emu.getState()['cpu.sp']);assert(minSP>=0x5b,'Native UI stack floor')end
end,emu.callbackType.write,0x100,0x1ff)
emu.addEventCallback(function()
 local b={}
 if not entered and wall>=120 and wall%12==0 then
  if r('CrossoverMenuState')~=2 then b.start=true
  elseif r('CrossoverMenuIndex')~=C.menu_target then b[C.menu_moves[r('CrossoverMenuIndex')+1]]=true
  elseif C.character==1 and r('ProtoVariant')~=C.proto then b.select=true
  elseif C.character==9 and r('RlVariant')~=0 then b.select=true else b.a=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<1800,'Bounded native UI fixture')
 if done then
  assert(#results==#C.cases and nmis>10,'Every staged native UI case and interrupts executed')
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json({passed=true,cases=results,nmis=nmis,minSP=minSP,staged=true,scope='Real selection and foreground UI entry/return with legal component staging; exact selection/shot/charge and five-SMC/bank NMI invariants. Not natural weapon earning, shot lifetime/contact, PPU/audio fidelity or whole level.'}));f:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
