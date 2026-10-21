-- Extra read-only support observations for the eventual final34 fixed replay.
-- This is not a legality assertion: Morph exits and edge/platform contacts
-- require the logged movement/terrain context to be reviewed.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/scc34_samus21_tail.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'samus-jump-support.csv','w'))
log:write('frame,world,level,x,y,yHigh,crouch,ball,face,feetTiles,platforms,springAnimation\n')
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function block(x,y)
 if y<32 or y>=240 then return -1 end
 return r('Block_Buffer_1',(math.floor(x/256)%2)*208+math.floor((y-32)/16)*16+math.floor((x%256)/16))
end
emu.addMemoryCallback(function()
 if r('CurrentBank')%128~=10 or r('SelectedCharacter')~=2 or r('GameEngineSubroutine')~=8 then return end
 if r('Player_State')~=0 or(r('A_B_Buttons')&128)==0 or(r('PreviousA_B_Buttons')&128)~=0 then return end
 local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position')
 local feet={}
 for _,dx in ipairs({4,8,12})do feet[#feet+1]=table.concat({x+dx,y+32,block(x+dx,y+32),block(x+dx,y+31)},':')end
 local platforms={}
 for i=0,5 do
  local id=r('Enemy_ID',i)
  if r('Enemy_Flag',i)>0 and((id>=0x24 and id<=0x2c)or id==0x32)then
   platforms[#platforms+1]=table.concat({i,id,r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('PlatformCollisionFlag',i)},':')
  end
 end
 -- The callback occurs in the physical frame after the previous endFrame.
 log:write(table.concat({frame+1,r('WorldNumber'),r('LevelNumber'),x,y,r('Player_Y_HighPos'),r('SmCrouch'),r('SmBall'),r('PlayerFacingDir'),table.concat(feet,';'),table.concat(platforms,';'),r('JumpspringAnimCtrl')},',')..'\n');log:flush()
end,emu.callbackType.exec,assert(L.SamusMovement))
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return choose
