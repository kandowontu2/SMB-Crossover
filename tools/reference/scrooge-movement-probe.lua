-- Unmodified DuckTales reference: ordinary controller input and read-only RAM/OAM.
-- Bounded CSV/binary telemetry and eight selected screenshots; no state patches.
local frame=0
local base=OUTPUT..'native-scrooge-movement'
local motion=assert(io.open(base..'.csv','w'))
local ram=assert(io.open(base..'.bin','wb'))
local velocity=assert(io.open(base..'-velocity.csv','w'))
velocity:write('frame,address,value,pc\n')
emu.addMemoryCallback(function(a,v)
 if(frame>=398 and frame<=403)or(frame>=880 and frame<=885)then
  velocity:write(frame..','..a..','..v..','..emu.getState()['cpu.pc']..'\n')
 end
end,emu.callbackType.write,0x7b0,0x7c0)
motion:write('frame,phase,y,oam\n')
local shots={[300]=true,[430]=true,[650]=true,[900]=true,[1100]=true,[1300]=true,[1450]=true,[1600]=true}
local function phase()
 if frame<400 then return 'settle' elseif frame<510 then return 'jump'
 elseif frame<600 then return 'settle' elseif frame<780 then return 'ground-pogo'
 elseif frame<850 then return 'settle' elseif frame<1110 then return 'air-pogo'
 elseif frame<1250 then return 'settle' elseif frame<1350 then return 'crouch-right'
 elseif frame<1450 then return 'right' elseif frame<1550 then return 'crouch' else return 'settle' end
end
emu.addEventCallback(function()
 emu.setInput({start=frame>=60 and frame<66,
  a=(frame>=150 and frame<156)or(frame>=400 and frame<440)or(frame>=850 and frame<862),
  down=(frame>=600 and frame<780)or(frame>=865 and frame<1110)or(frame>=1250 and frame<1350)or(frame>=1450 and frame<1550),
  b=(frame>=600 and frame<780)or(frame>=865 and frame<1110),
  right=frame>=1250 and frame<1450},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=300 then
  local o={}
  for s=0,63 do
   local b=s*4;local y=emu.read(b,emu.memType.nesSpriteRam)
   if y<240 then o[#o+1]=string.format('%d:%d:%d:%d',y,emu.read(b+1,emu.memType.nesSpriteRam),emu.read(b+2,emu.memType.nesSpriteRam),emu.read(b+3,emu.memType.nesSpriteRam))end
  end
  motion:write(frame..','..phase()..','..emu.read(0x640,emu.memType.nesDebug)..','..table.concat(o,' ')..'\n')
  for a=0,0x7ff do ram:write(string.char(emu.read(a,emu.memType.nesDebug)))end
 end
 if shots[frame]then local f=assert(io.open(base..'-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
 if frame==1300 then
  for _,q in ipairs({{'.chr',8192,emu.memType.nesPpuDebug},{'.pal',32,emu.memType.nesPaletteRam},{'.oam',256,emu.memType.nesSpriteRam}})do
   local f=assert(io.open(base..'-1300'..q[1],'wb'))
   for a=0,q[2]-1 do f:write(string.char(emu.read(a,q[3])))end
   f:close()
  end
 end
 if frame==1650 then motion:close();ram:close();velocity:close();print('PASS native DuckTales controller-only movement reference, no emulated writes');emu.stop(0)end
end,emu.eventType.endFrame)
