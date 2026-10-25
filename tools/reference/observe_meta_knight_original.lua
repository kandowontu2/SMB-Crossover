-- Source observation arena: enter the original Meta Knight room through its
-- native room initializer. No sprite/animation/AI/CHR/palette code is replaced.
local f,seeded,started=0,false,nil
local seen={};local snapshots=0
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function w(a,v)emu.write(a,v,emu.memType.nesDebug)end
local function save(n,s)local o=assert(io.open(OUTPUT..n,'wb'));o:write(s);o:close()end
local function bytes(a,n,t)local d={}for i=0,n-1 do d[#d+1]=string.char(emu.read(a+i,t))end;return table.concat(d)end
local rows=assert(io.open(OUTPUT..'native.csv','w'))
rows:write('frame,room,kirbyX,kirbyY,ability,slot,script,pose,x,y,vxLo,vxHi,vyLo,vyHi,var0,var1,var2,var3,tick,chr1,palette\n')
emu.addMemoryCallback(function()
 if seeded or f<60 or emu.convertAddress(0xa000).address//8192~=0x13 then return end
 seeded=true;started=f
 -- Original bank12 boss-entry table 9C4A+5*3 = 6C,00,29.
 w(0x55e,0x6c);w(0x55f,0);w(0x558,5);w(0x559,6)
 w(0x560,0);w(0x561,0x29);w(0x520,7);w(0x51c,3)
 print('Original Meta room seeded at native initializer, frame '..f)
end,emu.callbackType.exec,0xa319)
emu.addEventCallback(function()
 local b={}
 if not seeded then b.start=f>=60 and f%60==0;b.a=f>=60 and f%60==20
 else
  -- Collect the offered sword by walking under it; then remain an AI target.
  local x=r(0x83)+256*r(0x95)
  b.right=x<122;b.left=x>134;b.a=(f-started)>300 and(f-started)%150<28
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if not seeded then return end
 -- Keep the target alive for observation; this does not alter Meta Knight.
 w(0x597,6)
 for slot=2,17 do
  if r(0x6128+slot)==0x42 and r(0x62fc+slot)==0x31 and r(0x61dc+slot)==0xc0 then
   local pose=r(0x62c6+slot)
   if pose<0x7c and not seen[pose]then
    seen[pose]=true;snapshots=snapshots+1
    local stem=string.format('pose-%02x',pose)
    save(stem..'-oam.bin',bytes(0,256,emu.memType.nesSpriteRam))
    save(stem..'-palette.bin',bytes(0,32,emu.memType.nesPaletteRam))
    -- Read physical CHR, not an end-of-frame PPU debug view after HUD banking.
    save(stem..'-chr.bin',bytes(r(0x43)*1024,2048,emu.memType.nesChrRom))
    save(stem..'-state.json',string.format('{"frame":%d,"slot":%d,"pose":%d,"x":%d,"y":%d,"cameraX":%d,"cameraY":%d,"chr":%d}',f,slot,pose,r(0x82+slot)+256*r(0x94+slot),r(0xb8+slot)+256*r(0xca+slot),r(0xdd)+256*r(0xde),r(0xe0)+256*r(0xe1),r(0x43)))
   end
  end
 end
end,emu.eventType.startFrame)
emu.addEventCallback(function()
 f=f+1
 if seeded then
  for slot=2,17 do if r(0x6128+slot)==0x42 then
   local pal={}for i=0,31 do pal[#pal+1]=string.format('%02x',emu.read(i,emu.memType.nesPaletteRam))end
   rows:write(table.concat({f,r(0x55e)+256*r(0x55f),r(0x83),r(0xb9),r(0x5e3),slot,r(0x6128+slot),r(0x62c6+slot),r(0x82+slot),r(0xb8+slot),r(0x60e0+slot),r(0x60f2+slot),r(0x6104+slot),r(0x6116+slot),r(0x61ca+slot),r(0x61dc+slot),r(0x61ee+slot),r(0x6200+slot),r(0x627e+slot)+256*r(0x6290+slot),r(0x43),table.concat(pal)},',')..'\n')
  end end
  if(f-started)%120==0 then save('screen-'..f..'.png',emu.takeScreenshot())end
  if f-started>=2100 then
   rows:close();assert(snapshots>6,'Native Meta Knight visible pose coverage')
   save('proof.json',string.format('{"passed":true,"frames":%d,"poses":%d,"scope":"Original boss room entered at its native initializer; player health replenished for observation. Controller collects offered sword. Native AI, script, OAM, palettes and CHR unchanged; not a campaign replay."}',f,snapshots))
   print('PASS original Meta observation, '..snapshots..' poses');emu.stop(0)
  end
 end
 assert(f<4200,'Bounded original boss observation')
end,emu.eventType.endFrame)
