-- Passive startup-only state/probe/Arrow-slot accounting. No inputs/state writes.
return function(out,C)
 local f=assert(io.open(out..'darkwing-resources.csv','w'))
 f:write('event,frame,poll,cycle,pc,bank,x,y,state,vx,previous,fresh,saved,gas,adaptor,mode,near,far,shot_kind,slot,value,arrows\n')
 local frame,poll,rows,launches,debits=0,0,0,0,0
 local lastGas,closed=nil,false
 local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or-1 end
 local function owner()return r('SelectedCharacter')==12 and r('DarkwingVariant')==1 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('WorldNumber')==0 and r('LevelNumber')==0 end
 local function cell(x,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',x//256%2*208+(y-32)//16*16+x%256//16)
 end
 local function arrows()
  local z={}
  for i=0,9 do
   local t=r('RgShotType',i)
   if t==5 or t==6 or(t==8 and r('RgShotImpact',i)==2)then
    local actor=r('RgShotImpact',i)-1
    local valid=t==6 and actor>=0 and actor<=5 and r('Enemy_Flag',actor)==1
     and r('Enemy_ID',actor)==0x26 and(r('Enemy_State',actor)&0x7f)==(0x20|i)
    -- Colon fields: slot/type/age/dir/shotX/shotY/impact/SsMode,
    -- validated actor slot/X/Y/state/collision flag. -1 means not validated.
    z[#z+1]=table.concat({i,t,r('RgShotAge',i),r('RgShotDir',i),
     r('RgShotX',i)+256*r('RgShotPage',i),r('RgShotY',i),r('RgShotImpact',i),r('SsMode',i),
     valid and actor or-1,valid and(r('Enemy_X_Position',actor)+256*r('Enemy_PageLoc',actor))or-1,
     valid and r('Enemy_Y_Position',actor)or-1,valid and r('Enemy_State',actor)or-1,
     valid and r('PlatformCollisionFlag',actor)or-1},':')
   end
  end
  return table.concat(z,';')
 end
 local function log(kind,value)
  if not owner()then return end
  local x=r('Player_X_Position')+256*r('Player_PageLoc');if x<450 or x>2400 then return end
  rows=rows+1;assert(rows<=20000,'Bounded passive Darkwing resource rows')
  local s=emu.getState();local y=r('Player_Y_Position')
  f:write(table.concat({kind,frame,poll,s['cpu.cycleCount'],s['cpu.pc'],bank(s['cpu.pc']),x,y,r('Player_State'),r('Player_X_Speed'),r('DwPrevious'),r('ScFresh'),r('SavedJoypadBits'),r('DwGas'),r('DwAdaptor'),r('DwMode'),cell(x+16,y-20),cell(x+32,y-20),r('RgTemp'),s['cpu.x'],value or 0,arrows()},',')..'\n')
 end
 local function hook(name,fn)
  local h=assert(C.hooks[name],name)
  emu.addMemoryCallback(function()
   if bank(h.pc)~=h.bank then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Passive actual hook '..name)end
   if owner()then fn()end
  end,emu.callbackType.exec,h.pc)
 end
 hook('launch',function()launches=launches+1;log('launch-before')end)
 hook('shot_init',function()debits=debits+1;log('successful-debit-before-init')end)
 hook('movement',function()if(r('DwPrevious')~r('SavedJoypadBits'))&160~=0 then log('movement-before-A-Select-fresh')end end)
 emu.addMemoryCallback(function(_,v)log('gas-write',v);lastGas=v end,emu.callbackType.write,C.ram.DwGas)
 emu.addMemoryCallback(function(_,v)log('mode-write',v)end,emu.callbackType.write,C.ram.DwMode)
 emu.addEventCallback(function()poll=poll+1;log('actual-input-poll')end,emu.eventType.inputPolled)
 emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
 return function()assert(not closed);closed=true;f:close();return{kind='passive-darkwing-resource-arrow-observer-v2',rows=rows,polls=poll,launch_entries=launches,successful_shot_inits=debits,last_observed_gas=lastGas,passive=true,no_input_or_state_writes=true}end
end
