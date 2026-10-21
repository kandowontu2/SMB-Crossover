-- Synthetic contact isolation ONLY. Replays ordinary Luigi inputs, but selects
-- native Mario0 solely inside SamusStopAtWall and restores Luigi at its return.
-- No position/velocity/terrain writes. This is never an accepted route proof.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local policy=assert(dofile(root..'/tools/playthroughs/luigi33_water_position_probe.lua'))
local frame,active,restorePC,entrySP=0,false,nil,nil
local out=assert(io.open(ROSTER_CONFIG.out..'synthetic-contact-overrides.csv','w'))
out:write('frame,event,pc,sp,character,x,y\n')
local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
local function log(event)
 local s=emu.getState()
 out:write(table.concat({frame+1,event,s['cpu.pc'],s['cpu.sp'],r('SelectedCharacter'),
  r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position')},',')..'\n');out:flush()
end
emu.addMemoryCallback(function()
 if frame<15245 or frame>15265 then return end
 assert(not active,'Single isolated wall-dispatch call')
 assert(r('SelectedCharacter')==8,'The ordinary prefix remains Luigi outside this explicit fixture')
 local sp=emu.getState()['cpu.sp'];entrySP=sp
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 if not restorePC then
  restorePC=pc
  emu.addMemoryCallback(function()
   if not active or emu.getState()['cpu.sp']~=entrySP+2 then return end
   log('native-return');emu.write(L.SelectedCharacter,8,emu.memType.nesDebug);active=false;log('restore-luigi')
  end,emu.callbackType.exec,pc)
 end
 assert(pc==restorePC,'Stable actual shared collision return site')
 log('before-override');emu.write(L.SelectedCharacter,0,emu.memType.nesDebug);active=true;log('native-control')
end,emu.callbackType.exec,assert(L.SamusStopAtWall))
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return policy
