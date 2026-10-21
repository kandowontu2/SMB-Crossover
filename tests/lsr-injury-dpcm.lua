-- Explicit audio-request arenas; compare the actual hardware sample mapping
-- and initial registers to read-only source NSF captures. No CPU/ROM writes.
local refs=dofile(TEST_DIR..'fixtures/remaining-source-dpcm.lua')
local cases={{id=21},{id=21},{id=22},{id=22},{id=21,switch=true},{id=22}}
local frame,index,age,starts,checks=0,0,0,0,0
local current,registers,started,ended={},{},false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function(address,value)
 if frame<550 then return end
 if address>=0x4010 and address<=0x4013 then registers[address]=value end
 if address~=0x4015 or value&16==0 then return end
 local playing=emu.read(0x4015,emu.memType.nesDebug)&16~=0
 if playing then return end
 assert(current.id,'No unrequested DMC restart from unrelated music status writes')
 assert(not started,'A completed sample cannot restart when later music status writes enable voices')
 local ref=assert(refs[current.id]);started=true;starts=starts+1
 assert(registers[0x4010]==ref.rate and registers[0x4011]==ref.dac,'Exact source DMC rate/noIRQ/noLoop and initial DAC')
 local base=0xc000+64*assert(registers[0x4012])
 local length=16*assert(registers[0x4013])+1
 assert(length==ref.length and base>=0xe000 and base+length<=0x10000,'Complete sample lies in the fixed resident window')
 for i=0,length-1 do
  assert(emu.read(base+i,emu.memType.nesDebug)==tonumber(ref.hex:sub(i*2+1,i*2+2),16),'Actual fixed mapped source sample byte '..current.id..'/'..i)
  checks=checks+1
 end
 assert(r('BassDmcActive')==2,'Source injury uses shared DMC owner2')
end,emu.callbackType.write,0x4010,0x4015)
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 for i=0,5 do w('Enemy_Flag',0,i)end
 if frame==550 or age>=24 then
  if index>0 then assert(started and ended,'Every actual sample plays and releases hardware once')end
  index=index+1;current=cases[index];age=0;started=false;ended=false;registers={}
  if not current then print('PASS '..starts..' source DMC injury requests, '..checks..' actual fixed sample bytes, initial registers, completion/no restart and character-switch release');emu.stop(0);return end
  w('SelectedCharacter',current.id==21 and 4 or 5)
  -- Let the normal character-change reset run before the explicit cue.
 end
 age=age+1
 if age==3 then w('AvAudioRequest',current.id)end
 if current.switch and started and age==5 then w('SelectedCharacter',6)end
 if started and age>=10 then
  assert(emu.read(0x4015,emu.memType.nesDebug)&16==0 and r('BassDmcActive')==0,'Hardware completion/character change stops and releases the shared sample')
  ended=true
 end
 assert(age<40,'Bounded DMC source cue lifecycle')
end,emu.eventType.endFrame)
