local frame,index=0,0
local cases={171,172,173,174,175}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<=160 and (frame-80)%20==0,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame>=550 and (frame-550)%15==0 then
  if index>0 then assert(r('Player_Y_Position')==176 and r('Player_State')==0,'Fast fall lands on the top ground row from Y='..cases[index]..', got '..r('Player_Y_Position')) end
  index=index+1
  if not cases[index] then print('PASS Simon lands above the ground at every phase of his seven-pixel fall step');emu.stop(0);return end
  w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',cases[index]);w('Player_Y_HighPos',1)
  w('Player_State',2);w('Player_Y_Speed',7);w('Player_X_Speed',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',i==2 and 7 or 0,i) end
  for i=0,1 do w('MmYFraction',0,i);w('MmXFraction',0,i) end
 end
end,emu.eventType.endFrame)
