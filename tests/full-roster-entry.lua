-- Cold controller-only front-end and bounded ordinary1-1 movement.
-- Target constants are supplied by the roster runner; no gameplay RAM injection.
local frame,phase,entered=0,0,nil
local ctx;local smc;local nmis,irqs,visible,publicationWindows=0,0,0,0
local startx,maxx,miny=nil,0,255
local logic,lastLogic=0,nil
local livesPending,livesSaved=0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function actual(a)return emu.convertAddress(a).address//8192 end
local function shared()local t={}for a=L.__SMCCODE_RUN__,L.__SMCCODE_RUN__+32 do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end
local function shot(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
if L.X5PortraitRender then
 emu.addMemoryCallback(function()
  if actual(0xa000)==99 and r('OperMode')==1 and r('CrossoverMenuState')==0 and not livesSaved and livesPending==0 then livesPending=5 end
 end,emu.callbackType.exec,L.X5PortraitRender)
end
local function variant()return TARGET_VARIANT_ADDRESS==0 and 0 or emu.read(TARGET_VARIANT_ADDRESS,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 assert(not ctx,'NMI nesting')
 local st=emu.getState();ctx=r('CurrentBankC')%128
 if actual(0xc000)~=ctx then
  -- BankPRGC publishes its logical shadow before the hardware write. A lag
  -- interrupt can fall between them; NMI correctly restores that shadow.
  -- Admit only the actual decoded tail of this exact bank-publication macro.
  local sp=st['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
  local function byte(a)return emu.read(a,emu.memType.nesDebug)end
  local op=byte(pc);local value
  if op==0xa9 then value=byte(pc+1);pc=pc+2
  elseif op==0xa5 then value=byte(byte(pc+1));pc=pc+2
  elseif op==0xad then value=byte(byte(pc+1)+256*byte(pc+2));pc=pc+3 end
  op=byte(pc)
  if not value then value=op==0x8d and st['cpu.a']or(op==0x8e and st['cpu.x']or st['cpu.y'])end
  assert((op==0x8d or op==0x8e or op==0x8c)and byte(pc+1)==0x16 and byte(pc+2)==0x51 and value%128==ctx,'C mismatch is a verified in-progress publication')
  publicationWindows=publicationWindows+1
 end
 smc=shared();nmis=nmis+1
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 assert(ctx and smc==shared(),'NMI preserves shared farcall operands')
 assert(actual(0xa000)==r('CurrentBank')%128,'A window restored')
 assert(actual(0xc000)==ctx and r('CurrentBankC')%128==ctx,'C window restored')
 ctx=nil
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()irqs=irqs+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addEventCallback(function()
 local b={}
 if phase==0 then
  -- Power-on CPU/PPU alignment can move the first accepted title input.
  -- Pulse Start until the actual selection screen opens.
  b.start=frame>=60 and frame%12==0
  -- Do not interpret uninitialized power-on RAM as an already-open menu.
  if frame>=60 and r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and frame%12==0 then
  local index=r('CrossoverMenuIndex')
  local row=index<12 and index//6 or 2
  local wanted=TARGET_SLOT<12 and TARGET_SLOT//6 or 2
  if row~=wanted then b.down=true
  elseif index~=TARGET_SLOT then b.right=true
  elseif variant()~=TARGET_VARIANT then b.select=true
  else
   local name={}
   for i=0,15 do
    local tile=emu.read((L.X5MenuNameAddress or 0x2308)+i,emu.memType.nesPpuDebug)
    name[#name+1]=(tile>=10 and tile<=35)and string.char(65+tile-10)or(tile<=9 and string.char(48+tile)or' ')
   end
   assert(table.concat(name):match('^%s*(.-)%s*$')==TARGET_MENU_NAME,'Highlighted name matches identity beyond the first256-byte table page')
   shot('selection');b.a=true;phase=2
  end
 elseif entered then
  local t=frame-entered
  b.right=t>=15 and t<125
  b.b=t>=15 and t<125
  b.a=(t>=30 and t<65)or(t>=95 and t<113)
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if livesPending>0 then
  livesPending=livesPending-1
  if livesPending==0 then shot('lives');livesSaved=true end
 end
 if phase==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==TARGET_CHARACTER and variant()==TARGET_VARIANT,'Selected identity survives actual new-game initialization')
  assert(r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Cold defaults Easy/outlinesOff')
  entered=frame;phase=3;startx=r('Player_X_Position')+256*r('Player_PageLoc');lastLogic=r('FrameCounter');shot('entry')
 end
 if entered then
  local t=frame-entered
  local fc=r('FrameCounter');logic=logic+(fc-lastLogic)%256;lastLogic=fc
  assert(r('MmDeathFlag')==0,'Character survives bounded ordinary1-1 input')
  maxx=math.max(maxx,r('Player_X_Position')+256*r('Player_PageLoc'));miny=math.min(miny,r('Player_Y_Position'))
  local n=0
  for i=0,63 do if emu.read(0x200+i*4,emu.memType.nesDebug)<240 then n=n+1 end end
  if n>0 then visible=visible+1 end
  if t==100 then shot('movement')end
  if t==140 then
   assert(maxx>=startx+16,'Normal controls advance in native level')
   assert(visible>60 and nmis>200 and irqs>100,'Visible sprites and native interrupts exercised')
   local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(string.format('{"passed":true,"name":"%s","character":%d,"variant":%d,"slot":%d,"frames":%d,"nmis":%d,"irqs":%d,"startX":%d,"maxX":%d,"minY":%d,"visibleFrames":%d,"logicUpdates":%d,"verifiedPublicationWindows":%d,"scope":"Controller-only cold menu, alternate, lives/level entry and140video frames in ordinary1-1; NMI restores logical bank shadow, with decoded publication windows checked; no full-level or video review claim"}\n',TARGET_NAME,TARGET_CHARACTER,TARGET_VARIANT,TARGET_SLOT,frame,nmis,irqs,startx,maxx,miny,visible,logic,publicationWindows));f:close()
   print('PASS '..TARGET_NAME..' cold selection, alternate persistence, ordinary movement and interrupt ownership');emu.stop(0)
  end
 end
 if frame>1800 then
  shot('timeout')
  error('Cold roster entry timed out; phase='..phase..' menu='..r('CrossoverMenuState')..' index='..r('CrossoverMenuIndex')..' character='..r('SelectedCharacter')..' variant='..variant()..' mode='..r('OperMode')..' engine='..r('GameEngineSubroutine'))
 end
end,emu.eventType.endFrame)
