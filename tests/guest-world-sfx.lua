local frame=0
local character=assert(SFX_CHARACTER)
local actual={};local expansion={};local checked={};local writes=0
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function(a,v)
 actual[a-0x4000]=v;writes=writes+1
end,emu.callbackType.write,0x4000,0x400f)
local master=0
local expansionMaster=0
emu.addMemoryCallback(function(a,v) master=v end,emu.callbackType.write,0x4015)
emu.addMemoryCallback(function(a,v) expansion[a-0x5000]=v end,emu.callbackType.write,0x5000,0x5007)
emu.addMemoryCallback(function(a,v) expansionMaster=v end,emu.callbackType.write,0x5015)
emu.addEventCallback(function()
 emu.setInput({down=character>=6 and frame==80,
   right=character>=6 and (frame>=100 and frame<100+20*(character-6) and (frame-100)%20==0) or
     (character<6 and frame>=80 and frame<80+20*character and (frame-80)%20==0),start=frame==200},0)
end,emu.eventType.inputPolled)
local cues={{frame=550,queue='Square1SoundQueue',value=2,bit=1,channel=0,name='block bump'},
 {frame=620,queue='Square2SoundQueue',value=1,bit=2,channel=1,name='coin'},
 {frame=700,queue='Square2SoundQueue',value=2,bit=2,channel=1,name='power-up reveal'},
 {frame=760,queue='NoiseSoundQueue',value=1,bit=8,channel=3,name='brick shatter'},
 {frame=830,queue='Square1SoundQueue',value=64,bit=1,channel=0,name='flagpole over muted music',silence=true}}
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 for index,cue in ipairs(cues) do
  if frame==cue.frame then
   if cue.silence then w('EventMusicQueue',128) end
   w(cue.queue,cue.value)
  end
  if frame==cue.frame+3 then
   assert((r('GuestMixMask')&cue.bit)>0,cue.name..' owns its APU channel')
   local base=cue.channel*4
   if mmc5 and cue.channel<2 then
    assert(expansion[base]==r('GuestExpansionApu',base),cue.name..' reaches MMC5 envelope register')
    assert(expansion[base+2]==r('GuestExpansionApu',base+2),cue.name..' reaches MMC5 period register')
    assert((expansionMaster&cue.bit)>0,cue.name..' enables its expansion channel')
    assert(actual[base]==r('GuestNativeApu',base) and actual[base+2]==r('GuestNativeApu',base+2),cue.name..' leaves the native music voice intact')
   else
    assert(actual[base]==r('GuestFxApu',base),cue.name..' reaches the real APU volume/envelope register')
    assert(actual[base+2]==r('GuestFxApu',base+2),cue.name..' reaches the real APU period register')
    assert((master&cue.bit)>0,cue.name..' keeps the effect channel enabled')
   end
   checked[index]=true
  end
  if frame==cue.frame+(cue.silence and 70 or 60) then
   assert((r('GuestMixMask')&cue.bit)==0,cue.name..' releases its channel')
   if mmc5 and cue.channel<2 then assert((expansionMaster&cue.bit)==0,cue.name..' silences its expansion channel') end
   local base=cue.channel*4
   assert(actual[base]==r('GuestNativeApu',base),cue.name..' restores native music/effect envelope')
   assert(actual[base+2]==r('GuestNativeApu',base+2),cue.name..' restores native music/effect pitch')
   print('PASS character '..character..' '..cue.name..', hardware APU output, and native channel restoration')
  end
 end
 if mmc5 and frame==560 then
  assert(r('GuestSweepPeriod')~=r('GuestFxApu',2) or r('GuestSweepPeriod',1)~=(r('GuestFxApu',3)&7),'Bump has a software pitch sweep on MMC5')
 end
 if frame==930 then
  w('AreaMusicQueue',1);w('Square1SoundQueue',2);w('Square2SoundQueue',1);w('NoiseSoundQueue',1)
 end
 if frame==934 then
  assert(r('GuestMixMask')==11,'Independent pulse and noise world effects overlap')
  if mmc5 then
   assert(expansionMaster==3 and (master&15)==15,'Both expansion pulses coexist with all four native voices')
   for base=0,4,4 do
    assert(actual[base]==r('GuestNativeApu',base) and actual[base+2]==r('GuestNativeApu',base+2),'Simultaneous effects retain native pulse music')
   end
  end
 end
 if frame==936 then w('GamePauseStatus',1) end
 if frame==940 then
  assert(master==0 and (not mmc5 or expansionMaster==0),'Pause silences native and expansion voices')
  w('GamePauseStatus',0)
 end
 if frame==950 then assert((master&15)>0,'Unpause resumes native voices') end
 if frame==960 then
  assert(#checked==5 and writes>200,'All world effects and ongoing native audio exercised the physical APU')
  print('PASS guest world effects mix over original music without disabling the other channels');emu.stop(0)
 end
end,emu.eventType.endFrame)
