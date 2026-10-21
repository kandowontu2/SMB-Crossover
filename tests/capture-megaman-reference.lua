local frame=0
emu.addEventCallback(function()
  emu.setInput({start=frame==120 or frame==600,left=frame>=1605 and frame<1627,a=frame>=1650 and frame<1690,b=frame==1740},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==1600 or frame==1619 or frame==1625 or frame==1660 or frame==1742 then
    local out=assert(io.open(OUTPUT..'megaman-'..frame..'.oam','wb'))
    for i=0,255 do out:write(string.char(emu.read(i,emu.memType.nesSpriteRam))) end
    out:close()
  end
  if frame==1760 then
    local f=assert(io.open(OUTPUT..'megaman-reference.png','wb'));f:write(emu.takeScreenshot());f:close()
    for _,region in ipairs({{'chr',emu.memType.nesChrRam,8192},{'oam',emu.memType.nesSpriteRam,256},{'pal',emu.memType.nesPaletteRam,32}}) do
      local out=assert(io.open(OUTPUT..'megaman-reference.'..region[1],'wb'))
      for i=0,region[3]-1 do out:write(string.char(emu.read(i,region[2]))) end
      out:close()
    end
    emu.stop(0)
  end
end,emu.eventType.endFrame)
