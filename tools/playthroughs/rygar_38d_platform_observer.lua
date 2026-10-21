-- Owned read-only native-platform route receipt; no emulated writes.
local cfg=assert(ROSTER_CONFIG);local root=assert(cfg.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/rygar_38d_policy.lua'))
local frame=0;local f=assert(io.open(cfg.out..'platforms.csv','w'))
f:write('frame,playerX,playerY,playerYHigh,playerState,playerVY,camera,slot,id,flag,x,y,yHigh,state,contact,enemyVX\n')
local function r(n,i)return L[n] and emu.read(L[n]+(i or 0),emu.memType.nesDebug) or -1 end
emu.addEventCallback(function()
 frame=frame+1
 if frame<5920 or frame>6035 or r('WorldNumber')~=0 or r('LevelNumber')~=1 then return end
 if frame%2==0 then
  for slot=0,5 do
   local flag=r('Enemy_Flag',slot);local id=r('Enemy_ID',slot)
   if flag>0 then
    f:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_Y_Speed'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),slot,id,flag,r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot),r('Enemy_Y_HighPos',slot),r('Enemy_State',slot),r('PlatformCollisionFlag',slot),r('Enemy_X_Speed',slot)},',')..'\n')
   end
  end
  f:flush()
 end
 if frame==5970 or frame==5978 or frame==5986 then local p=assert(io.open(cfg.out..'platform-frame-'..frame..'.png','wb'));p:write(emu.takeScreenshot());p:close() end
end,emu.eventType.endFrame)
return base
