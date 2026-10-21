-- Actual pause+Select returns Bill to Normal; ordinary input only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_highplant_cross.lua'))
local phase=0
local frame=0
local log=assert(io.open(ROSTER_CONFIG.out..'late-shot-model.csv','w'));log:write('frame,slot,type,age,x,y,yHigh,vxLo,vxHi,vyLo,vyHi,crouch,state,weapon,angle,anchorY\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if frame>=22750 and frame<=23200 and r('WorldNumber')==1 and r('LevelNumber')==0 then
  for i=0,9 do
   if r('RgShotType',i)>0 then log:write(table.concat({frame,i,r('RgShotType',i),r('RgShotAge',i),r('RgShotX',i)+256*r('RgShotPage',i),r('RgShotY',i),r('RgShotYHigh',i),r('RgShotVXLo',i),r('RgShotVXHi',i),r('RgShotVYLo',i),r('RgShotVYHi',i),r('RgCrouch'),r('Player_State'),r('InvSelected',3),r('SsMode',i),r('SsHidden',i)},',')..'\n')end
  end;log:flush()
 end
end,emu.eventType.endFrame)
return function(c)
 if c.char==3 and c.world==1 and c.level==0 and c.x>=2470 and c.x<2660 then
  local paused=(c.r('GamePauseStatus')&1)~=0
  if phase==0 then
   if paused then phase=1 else return {start=true}end
  end
  if phase==1 then
   if c.r('InvSelected',3)==0 then phase=2 else return {select=true}end
  end
  if phase==2 then
   if c.r('GamePauseTimer')==0 then phase=3 else return{}end
  end
  if phase==3 then
   if paused then return {start=true}else phase=4 end
  end
  if phase==4 then
   local active=false
   for i=0,5 do
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==6 and c.r('Enemy_State',i)<32 and c.r('Enemy_Y_Position',i)>=144 and x>c.x-32 and x<2750 then active=true end
   end
   if active then
    if c.r('PlayerFacingDir')~=1 then return {right=true}end
    return {down=true,b=c.poll%8<3}
   end
   phase=5
  end
 end
 return base(c)
end
