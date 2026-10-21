-- Read-only causal observation over a genuine controller run. The policy
-- supplies ordinary inputs; this observer never writes emulated state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=assert(dofile(root..'/tools/playthroughs/scrooge_native_policy.lua'))
local frame=0
local pending={}
local out=assert(io.open(ROSTER_CONFIG.out..'real-pogo-bumps.csv','w'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
out:write('frame,world,level,tile,slot,beforeX,beforeY,tileTop,expectedSupportY,afterX,afterY,pogo,vyHigh,blockState,mapTile\n')
emu.addMemoryCallback(function()
 if r('CurrentBank')%128~=8 or r('SelectedCharacter')~=12 or r('ScPogo')==0 or r('MmBlockAttack')~=1 or r('MmVY',2)>=128 then return end
 local x=r('MmSavedPlayer')+256*r('MmSavedPlayer',1)
 local y=r('MmSavedPlayer',2)
 if r('MmBulletX')+256*r('MmBulletPage')~=x+8 or r('MmBulletY')~=y+32 then return end
 local slot=r('SprDataOffset_Ctrl')
 pending[#pending+1]={world=r('WorldNumber'),level=r('LevelNumber'),tile=r('R5'),slot=slot,x=x,y=y,support=r('Block_Orig_YPos',slot)}
end,emu.callbackType.exec,L.BumpBlock)
emu.addEventCallback(function()
 frame=frame+1
 for _,c in ipairs(pending)do
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  local address=L.Block_Buffer_1+r('Block_BBuf_Low',c.slot)+r('Block_Orig_YPos',c.slot)
  out:write(table.concat({frame,c.world,c.level,c.tile,c.slot,c.x,c.y,c.support+32,c.support,x,r('Player_Y_Position'),r('ScPogo'),r('MmVY',2),r('Block_State',c.slot),emu.read(address,emu.memType.nesDebug)},',')..'\n')
 end
 if #pending>0 then out:flush();pending={}end
end,emu.eventType.endFrame)
return normal
