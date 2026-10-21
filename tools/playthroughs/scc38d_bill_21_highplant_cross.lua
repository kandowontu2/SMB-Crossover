-- Cross a fully retracted plant from real upper-bank support; no RAM writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_middle_edge.lua'))
local phase,start=0,nil
local log=assert(io.open(ROSTER_CONFIG.out..'actual-mask-writes.csv','w'));log:write('frame,x,y,value,mirror,pc,bank\n')
local frame,last=0,nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addMemoryCallback(function(_,v)
 if frame>18500 and r('WorldNumber')==1 and r('LevelNumber')==0 and v~=last then
  local st=emu.getState();log:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),v,r('Mirror_PPUMASK'),st['cpu.pc'],r('CurrentBank')},',')..'\n');log:flush();last=v
 end
end,emu.callbackType.write,0x2001)
return function(c)
 if c.char==3 and c.world==1 and c.level==0 and c.x>=2028 and c.x<2200 then
  local shot=c.poll%8<3
  if phase==0 then
   local plant
   for i=0,5 do
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==13 and x>c.x and x<c.x+100 then plant=i end
   end
   if not plant or(c.grounded and c.r('Enemy_Y_Position',plant)>=c.r('PiranhaPlantDownYPos',plant)and c.r('PiranhaPlant_MoveFlag',plant)==0 and c.r('EnemyFrameTimer',plant)>=48)then phase=1 end
   return {right=phase==1,b=shot}
  elseif phase==1 then
   if c.grounded and c.y>=80 and c.x>=2090 and c.x<2112 and(c.r('PreviousA_B_Buttons')&128)==0 then phase=2;start=c.poll end
   return {right=true,b=shot,a=phase==2}
  end
  local e=c.enemy()
  return {right=true,b=shot,a=c.poll-start<32,down=not c.grounded and e and e.y>c.y+12}
 end
 return base(c)
end
