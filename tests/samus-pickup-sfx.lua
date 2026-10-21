-- Real pickup collisions from controlled item placement. Assert the sound at
-- the physical APU/MMC5 registers, not merely the transient SMB request queue.
local frame=0
local current
local master,expansionMaster=0,0
local actual,expansion={},{}
local mmc5=ROM_NAME:find('mmc5')~=nil
local cases={{at=560,kind=0,name='mushroom'},{at=680,kind=1,name='flower'},
 {at=800,kind=1,name='flower at full power'},{at=920,kind=2,name='star'},
 {at=1040,kind=3,name='1-up'}}
local lifeQueued,lifeSamples,lifeNotes=false,0,{}
local rawWrites=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function count(t) local n=0;for _ in pairs(t) do n=n+1 end;return n end
emu.addMemoryCallback(function(a,v)
 actual[a-0x4000]=v
 if frame>=550 then
  local pc=emu.getState()['cpu.pc']
  if pc>=0xb200 and pc<0xc000 then rawWrites=rawWrites+1 end
 end
end,emu.callbackType.write,0x4000,0x400f)
emu.addMemoryCallback(function(a,v) expansion[a-0x5000]=v end,emu.callbackType.write,0x5000,0x5007)
emu.addMemoryCallback(function(a,v) master=v end,emu.callbackType.write,0x4015)
emu.addMemoryCallback(function(a,v) expansionMaster=v end,emu.callbackType.write,0x5015)
emu.addMemoryCallback(function(a,v)
 if frame<550 then return end
 if (v&32)>0 and current and not current.collected then current.collected=frame end
 if (v&64)>0 then lifeQueued=true end
end,emu.callbackType.write,L.Square2SoundQueue)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100,start=frame==200},0)
end,emu.eventType.inputPolled)
local function hardwareSound(name,notes)
 assert((r('GuestMixMask')&2)>0,name..' owns the shared pickup voice')
 local regs=mmc5 and expansion or actual
 local expected=mmc5 and 'GuestExpansionApu' or 'GuestFxApu'
 assert(regs[4]==r(expected,4) and regs[6]==r(expected,6),name..' reaches the physical envelope and pitch registers')
 assert(((mmc5 and expansionMaster or master)&2)>0,name..' enables its physical pulse channel')
 assert((regs[4]&15)>0,name..' has audible volume')
 notes[regs[6]+256*(regs[7]&7)]=true
 -- The pickup voice must not overwrite unrelated native music channels.
 assert(actual[0]==r('GuestNativeApu',0) and actual[8]==r('GuestNativeApu',8) and actual[10]==r('GuestNativeApu',10),name..' preserves native pulse-1 and triangle music')
 if mmc5 then
  assert(actual[4]==r('GuestNativeApu',4) and actual[6]==r('GuestNativeApu',6),name..' preserves native pulse-2 music on MMC5')
 end
end
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==2 and r('PlayerStatus')==0,'Unpowered Samus selected')
  for i=0,5 do w('Enemy_Flag',0,i) end
 end
 for _,cue in ipairs(cases) do
  if frame==cue.at then
   current=cue;cue.notes={};cue.samples=0
   for i=0,5 do w('Enemy_Flag',0,i) end
   w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
   w('PowerUpType',cue.kind,5);w('Enemy_BoundBoxCtrl',3,5)
   w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5)
   w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
   w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
  end
  if cue.collected and frame==cue.collected+3 then
   assert((r('Square2SoundBuffer')&32)>0,cue.name..' starts the collected-power-up sound')
   if cue.kind<2 and cue.at<800 then assert(r('GuestPowerupActive')~=0,cue.name..' sounds during the upgrade freeze') end
  end
  if cue.collected and current==cue and (r('Square2SoundBuffer')&32)>0 then
   hardwareSound(cue.name,cue.notes);cue.samples=cue.samples+1
  end
  if frame==cue.at+80 then
   if cue.kind==3 then
    -- The awarded-life fanfare takes priority over the initial pickup cue.
    assert(cue.collected and lifeQueued and lifeSamples>=8 and count(lifeNotes)>=3,'1-up plays its changing multi-note life fanfare')
   else
    assert(cue.collected and cue.samples>=8 and count(cue.notes)>=3,cue.name..' plays a changing multi-note pickup effect')
   end
   assert(r('GuestMixMask')==0,cue.name..' releases the borrowed voice')
   assert(actual[4]==r('GuestNativeApu',4) and actual[6]==r('GuestNativeApu',6),cue.name..' restores native music pitch and envelope')
   if mmc5 then assert(expansionMaster==0,cue.name..' silences the expansion pulse after release') end
   print('PASS Samus '..cue.name..': actual collision, audible hardware pickup effect, music isolation and restoration')
  end
 end
 if frame>=1040 and (r('Square2SoundBuffer')&64)>0 then
  hardwareSound('1-up fanfare',lifeNotes);lifeSamples=lifeSamples+1
 end
 if frame==1140 then
  assert(lifeQueued and lifeSamples>=8 and count(lifeNotes)>=3,'Samus also hears the awarded extra-life fanfare')
  assert(r('NumberofLives')==3,'The green mushroom awards one life')
  assert(r('PlayerStatus')==2 and r('GuestPowerupActive')==0,'Both upgrades commit, repeated pickups preserve the final suit')
  assert(rawWrites==0,'Native Metroid audio remains buffered behind the mixer')
  print('PASS Samus pickup/1-up SFX across all three suit states, with continuous buffered Metroid music');emu.stop(0)
 end
end,emu.eventType.endFrame)
