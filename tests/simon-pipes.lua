local frame=0
local jumpAge=-1
local pipe=1
local secondJumps=0
local pipes={448,608,736,912}
local high=255
local trace=assert(io.open(OUTPUT..ROM_NAME..'-simon-pipes.csv','w'))
trace:write('frame,x,y,state,vy,double,age,pipe\n')
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
 local a=false
 if frame>=550 then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  while pipes[pipe] and x>pipes[pipe]+32 do pipe=pipe+1;jumpAge=-1 end
  if pipes[pipe] then
   if r('Player_State')==0 and x>=pipes[pipe]-48 then a=true;jumpAge=0
   elseif jumpAge==18 then a=true;secondJumps=secondJumps+1 end
  end
 end
 emu.setInput({right=(frame>=80 and frame<=160 and (frame-80)%20==0) or frame>=550,start=frame==200,a=a},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if jumpAge>=0 then jumpAge=jumpAge+1 end
 if pipe==3 then high=math.min(high,r('Player_Y_Position')) end
 if frame>=550 then trace:write(table.concat({frame,r('Player_PageLoc')*256+r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('MmVY',2),r('RgDoubleJump'),jumpAge,pipe},',')..'\n') end
 if frame==1500 then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  trace:close()
  assert(pipe>4 and x>960,'Simon clears all four native 1-1 pipes with double jumps: '..x)
  assert(secondJumps>=4 and high<112,'Second jump reaches above the tallest pipe: '..high)
  print('PASS Simon double jumps over every 1-1 pipe, including both four-block pipes');emu.stop(0)
 end
end,emu.eventType.endFrame)
