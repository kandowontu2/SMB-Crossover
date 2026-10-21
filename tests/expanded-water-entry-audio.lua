-- Real menu/entrance execution. The room fixture selects 2-2 before Start;
-- all decoder observations are read-only. In v11 guest palette setup left
-- X=12 at SetupBubble, writing Bubble_Y_Position+12 over XgAudioPtr+1.
local c=assert(WATER_AUDIO_CHARACTER)
local frame,depth,checks,bubbles=0,0,0,0
local written={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function p(n)return r(n)+256*r(n,1)end
local function audioBank()return depth>0 and r('CurrentBankC')%128==38 end
emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()depth=depth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function(addr)
 if frame>240 and depth==0 then
  assert(false,'Water entrance must preserve decoder zero page: $'..string.format('%04x',addr)..' PC='..string.format('%04x',emu.getState()['cpu.pc']))
 end
end,emu.callbackType.write,L.XgAudioPtr,L.XgAudioZeroPageEnd-1)
emu.addMemoryCallback(function()
 if frame>240 and depth==0 and r('CurrentBank')%128==0 then
  assert(emu.getState()['cpu.x']<3,'Entrance bubble must use one of three valid slots')
  assert(r('R7')<2,'Bubble drift-table index must be valid')
  bubbles=bubbles+1
 end
end,emu.callbackType.exec,L.SetupBubble)
emu.addMemoryCallback(function()if audioBank()then written={}end end,emu.callbackType.exec,L.ResetLz)
emu.addMemoryCallback(function()
 if audioBank()then
  local pos=p('XgLzPosition')
  assert(pos>=L.XgLzHistory and pos<L.XgLzHistory+2048,'History destination stays in its allocated ring')
  written[pos]=true
 end
end,emu.callbackType.exec,L.WriteHistory)
emu.addMemoryCallback(function()
 if audioBank()then assert(written[p('XgLzCopy')],'Compressed match references an already decoded byte')end
end,emu.callbackType.exec,L.CopyLz)
emu.addMemoryCallback(function()
 if audioBank()then assert(false,'Water music must never reach corrupt-stream stop')end
end,emu.callbackType.exec,L.StopCorruptStream)
emu.addMemoryCallback(function()
 if frame>550 then
  checks=checks+1
  assert(r('XgAudioEvent')~=3,'Swimming stage music remains active')
  if r('XgAudioDepth')>0 then assert(p('XgAudioPtr')>=0xc000 and p('XgAudioPtr')<0xe000,'Macro pointer stays in its code bank')end
 end
end,emu.callbackType.exec,L.ExpandedAudioDecoded)
emu.addEventCallback(function()
 local slot=c==12 and 8 or c
 emu.setInput({down=frame==80,right=frame>=100 and frame<100+(slot-6)*20 and(frame-100)%20==0,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then
  emu.write(L.WorldNumber,1,emu.memType.nesDebug)
  emu.write(L.LevelNumber,1,emu.memType.nesDebug)
  emu.write(L.AreaNumber,2,emu.memType.nesDebug)
 end
 if frame==550 then assert(r('SelectedCharacter')==c and r('AreaType')==0 and r('SwimmingFlag')==1,'Real selected-character water entrance')end
 if frame==1300 then
  assert(checks>700 and bubbles>0 and r('XgAudioSong')>0,'Water entrance and continuing decoder exercised')
  print('PASS guest '..c..' valid water-entry bubble slots, untouched decoder RAM, initialized song counter and uninterrupted compressed music')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
