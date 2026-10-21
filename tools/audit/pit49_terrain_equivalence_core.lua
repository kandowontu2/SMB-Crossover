-- Deliberately seeded terrain components through the real ExpandedWeapons.
-- No emulated registers, PC, stack or serialized states are changed.
local c=assert(PIT_TERRAIN_TEST)
local frame,index,depth,irqCycles,irqStart=0,0,0,0,nil
local regs,selector,mode={},0,0
local function rd(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n,i)return rd(assert(c.ram[n],n)+(i or 0))end
local function w(n,v,i)emu.write(assert(c.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function clock()return emu.getState()['cpu.cycleCount']end
if c.mapper=='mmc3'then
 emu.addMemoryCallback(function(_,v)selector=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if selector>=6 then regs[selector]=v&63 end end,emu.callbackType.write,0x8001)
else
 for a=0x5114,0x5117 do emu.addMemoryCallback(function(_,v)regs[a-0x510e]=v&63 end,emu.callbackType.write,a)end
end
local function bank(pc)
 if pc>=0xe000 then return 63 end
 if c.mapper=='mmc5'then return regs[pc>=0xc000 and 8 or pc>=0xa000 and 7 or 6]or-1 end
 if pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)end
 if pc>=0xa000 then return regs[7]or-1 end
 return mode==0 and(regs[6]or-1)or 62
end
local function guard(h)
 if bank(h.address)~=h.physical_bank then return false end
 for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Actual native terrain hook '..h.label)end
 return true
end
for _,pair in ipairs({{'NMI','NMIEnd'},{'IRQ','IRQEnd'}})do
 local a,b=c.hooks[pair[1]],c.hooks[pair[2]]
 emu.addMemoryCallback(function()if guard(a)then if depth==0 then irqStart=clock()-7 end;depth=depth+1 end end,emu.callbackType.exec,a.address)
 emu.addMemoryCallback(function()if guard(b)then depth=depth-1;assert(depth>=0,'Balanced terrain fixture interrupts');if depth==0 then irqCycles=irqCycles+clock()+6-assert(irqStart);irqStart=nil end end end,emu.callbackType.exec,b.address)
end
local output=assert(io.open(c.out..'outcomes.csv','w'))
output:write('case,map,health,solid,coin,coinStartLo,coinStartHi,fields,shots,audio\n')
local perf=assert(io.open(c.out..'timing.csv','w'))
perf:write('case,foregroundCycles,totalCycles,interruptCycles\n')
local active,returns=nil,{}
local audio={}
for name,address in pairs(c.audio)do
 emu.addMemoryCallback(function(_,v)if active and depth==0 then audio[#audio+1]=name..':'..v end end,emu.callbackType.write,address)
end
local function hash(name)
 local h=2166136261
 for i=0,415 do h=((h~r(name,i))*16777619)&0xffffffff end
 return h
end
local function resetShot(i)
 for _,n in ipairs({'RgShotType','RgShotImpact','RgShotAge','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotFracX','RgShotFracY','RgShotHits','RgShotHitsNow'})do w(n,0,i)end
 w('RgShotX',100,i);w('RgShotPage',0,i);w('RgShotY',100,i);w('RgShotYHigh',1,i);w('RgShotDir',1,i)
end
local function done()
 output:close();perf:close()
 local f=assert(io.open(c.out..'result.json','w'));f:write('{"completed":'..#c.cases..',"expected":'..#c.cases..',"passed":true}');f:close()
 print('PASS actual Pit terrain differential components '..#c.cases);emu.stop(0)
end
emu.addMemoryCallback(function()
 local h=c.hooks.Weapons
 if frame<550 or depth~=0 or not guard(h)then return end
 assert(not active,'No overlapping component setup')
 index=index+1
 local item=c.cases[index]
 if not item then done();return end
 assert(r('SelectedCharacter')==6,'Actual Pit selected before component seeding')
 w('CrossoverBehaviorVersion',item.mode);w('TimerControl',0);w('GameEngineSubroutine',8);w('Player_State',0);w('PlayerStatus',item.power)
 w('Player_X_Position',72);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('PlayerFacingDir',item.dir);w('PlayerSize',0);w('CrouchingFlag',0);w('Player_Y_Speed',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
 w('SavedJoypadBits',0);w('A_B_Buttons',0);w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0)
 w('RgCooldown',0);w('RgAttack',0);w('RgShootPose',0);w('RgSfx',0);w('RgCrouch',0)
 w('InvSelected',0,6);w('InvOwnedLo',1,6);w('InvOwnedHi',0,6)
 w('CoinTallyFor1Ups',0);w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0);w('AreaType',item.area)
 w('MmWorldTime',0);w('MmWorldTime',0,1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i);w('Block_State',0,i);w('Block_RepFlag',0,i)end
 for i=0,6 do w('PseudoRandomBitReg',i+1,i)end
 for name in pairs(c.audio)do w(name,0)end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i)end
 for i=0,415 do
  w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i);w('MmCoinHits',0,i);w('MmCoinStartLo',0,i);w('MmCoinStartHi',0,i)
 end
 for i=0,9 do resetShot(i)end
 w('RgShotType',1);w('RgShotX',item.x&255);w('RgShotPage',(item.x>>8)&255);w('RgShotY',item.y);w('RgShotDir',item.dir)
 for _,tile in ipairs(item.tiles)do
  w('Block_Buffer_1',tile.value,tile.offset);w('MmSolidTerrain',tile.solid,tile.offset);w('MmBrickHealth',tile.health,tile.offset)
 end
 local sp=emu.getState()['cpu.sp']
 local pc=(rd(0x100+((sp+1)&255))+256*rd(0x100+((sp+2)&255))+1)&65535
 audio={};active={sp=(sp+2)&255,pc=pc,clock=clock(),irq=irqCycles}
 if not returns[pc]then
  returns[pc]=true
  emu.addMemoryCallback(function()
   if not active or depth~=0 or emu.getState()['cpu.sp']~=active.sp or bank(h.address)~=h.physical_bank then return end
   local v=active;active=nil
   local fields={}
   for _,field in ipairs(c.fields)do fields[#fields+1]=field.name..':'..r(field.name,field.index)end
   local shots={}
   for i=0,9 do
    local a={}
    for _,n in ipairs({'RgShotType','RgShotX','RgShotPage','RgShotY','RgShotYHigh','RgShotDir','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotImpact','RgShotFracX','RgShotFracY'})do a[#a+1]=r(n,i)end
    shots[#shots+1]=table.concat(a,':')
   end
   output:write(table.concat({index,hash('Block_Buffer_1'),hash('MmBrickHealth'),hash('MmSolidTerrain'),hash('MmCoinHits'),hash('MmCoinStartLo'),hash('MmCoinStartHi'),table.concat(fields,';'),table.concat(shots,';'),table.concat(audio,';')},',')..'\n')
   local total=clock()-v.clock;local irq=irqCycles-v.irq
   perf:write(table.concat({index,total-irq,total,irq},',')..'\n')
  end,emu.callbackType.exec,pc)
 end
end,emu.callbackType.exec,c.hooks.Weapons.address)
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==240,down=frame==80},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
