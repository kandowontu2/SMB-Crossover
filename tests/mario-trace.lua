local frame=0
local file=assert(io.open(OUTPUT..ROM_NAME..'-mario-trace.csv','w'))
local fields={'OperMode','GameEngineSubroutine','Player_State','Player_PageLoc','Player_X_Position','Player_Y_HighPos','Player_Y_Position','Player_X_Speed','Player_X_MoveForce','Player_XSpeedAbsolute','Player_Y_Speed','Player_Y_MoveForce','Player_YMoveForceFractional','VerticalForce','VerticalForceDown','PlayerSize','PlayerStatus','ScreenLeft_PageLoc','ScreenLeft_X_Pos'}
local function r(name) return emu.read(assert(L[name],name),emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({start=frame==120,right=(frame>=500 and frame<640) or (frame>=800 and frame<920),
    left=frame>=650 and frame<710,b=frame>=500 and frame<580,
    a=(frame>=530 and frame<553) or (frame>=820 and frame<826)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  -- Isolate Mario's controller physics from the front end's different title
  -- timing/PRNG history. Enemy combat has its own fixtures and route replays.
  if frame>=480 then
    for i=0,5 do emu.write(L.Enemy_Flag+i,0,emu.memType.nesDebug) end
  end
  if frame>=480 then
    local values={frame}
    for _,name in ipairs(fields) do table.insert(values,r(name)) end
    file:write(table.concat(values,',')..'\n')
  end
  if frame==1000 then file:close(); print('PASS Mario trace captured'); emu.stop(0) end
end,emu.eventType.endFrame)
