-- Controller-only purposeful roof-contact probe after the genuine five-stage
-- prefix. Read-only receipts; this bounded diagnostic is not a level clear.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=assert(dofile(root..'/tools/playthroughs/luigi34_water_contact_observer.lua'))
local frame,stopAt=0,nil
local out=assert(io.open(ROSTER_CONFIG.out..'purposeful-corner-contact.csv','w'))
out:write('frame,x,y,vy,footLeft,footRight,nibble,pc\n')
local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 if r('CurrentBank')%128~=1 or r('WorldNumber')~=1 or r('LevelNumber')~=1
  or x<2080 or x>2144 or r('Player_Y_Position')<32 or r('Player_Y_Position')>63 then return end
 out:write(table.concat({frame+1,x,r('Player_Y_Position'),r('Player_Y_Speed'),r('R1'),r('R0'),r('R4'),emu.getState()['cpu.pc']},',')..'\n');out:flush()
 if not stopAt then stopAt=frame+4 end
end,emu.callbackType.exec,assert(L.GuestFootContactSide))
emu.addEventCallback(function()
 frame=frame+1
 if stopAt and frame>=stopAt then
  assert(r('GameEngineSubroutine')==8 and r('InjuryTimer')==0,'Purposeful native corner contact stays healthy/playable')
  out:close();print('PASS genuine controller-only water roof contact; bounded diagnostic only');emu.stop(0)
 end
end,emu.eventType.endFrame)
return function(c)
 if c.world==1 and c.level==1 and c.x>=2000 and c.x<2200 then
  return{right=true,b=true,a=c.poll%8<4}
 end
 return normal(c)
end
