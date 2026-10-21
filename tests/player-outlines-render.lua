-- Compare actual DMA OAM/CHR pixels, using controller-only roster navigation.
-- OFF may remove pure-black mask pixels; every other player pixel must match.
local frame=0
local slots={0,1,2,3,4,5,6,7,12,9,10,11}
local off,checked={},{}
local removed=0
local filterCalls={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 -- Admit the actual filter entry, since this CPU address is also executed
 -- by ExpandedPose in another swappable bank. Keep every original counter
 -- assertion strict; this guard changes only callback ownership admission.
 local physical=emu.convertAddress(L.PlayerRemoveOutlines)
 if not physical or physical.memType~=emu.memType.nesPrgRom or physical.address//8192~=10 then return end
 local fingerprint={0xa0,0x00,0xb1,L.R0 or -1,0xf0,0x08,0xc9,0x81}
 for i,b in ipairs(fingerprint)do
  if emu.read(L.PlayerRemoveOutlines+i-1,emu.memType.nesDebug)~=b then return end
 end
 local c=r('SelectedCharacter');filterCalls[c]=(filterCalls[c]or 0)+1
end,emu.callbackType.exec,L.PlayerRemoveOutlines)
local function pixels()
 local state=ROM_NAME:find('mmc5')and emu.getState()or nil
 local cache={}
 local function chr(a)
  if cache[a]==nil then
   cache[a]=state and emu.read(state['mapper.chrBanks'..math.floor(a/1024)]*1024+a%1024,emu.memType.nesChrRom)or emu.read(a,emu.memType.nesPpuDebug)
  end
  return cache[a]
 end
 local pic={};for i=1,96*64 do pic[i]=255 end
 for s=63,0,-1 do
  local y=emu.read(s*4,emu.memType.nesSpriteRam)
  local t=emu.read(s*4+1,emu.memType.nesSpriteRam)
  local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
  local x=emu.read(s*4+3,emu.memType.nesSpriteRam)
  if y<192 and y+16>128 then
   local base=(t&1)*4096+(t&254)*16
   for dy=0,15 do for dx=0,7 do
    local px,py=x+dx,y+dy
    if px>=80 and px<176 and py>=128 and py<192 then
     local row=a&128~=0 and 15-dy or dy
     local col=a&64~=0 and dx or 7-dx
     local address=base+math.floor(row/8)*16+row%8
     local color=((chr(address)>>col)&1)+2*((chr(address+8)>>col)&1)
     if color~=0 then pic[(py-128)*96+px-80+1]=emu.read(16+(a&3)*4+color,emu.memType.nesPaletteRam)&63 end
    end
   end end
  end
 end
 return pic
end
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==440 or frame==620,
  right=(frame>=100 and frame<=300 and frame%20==0)or(frame>=660 and frame<=860 and frame%20==0),
  b=frame==320 or frame==520,down=frame==420,a=frame==480},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==85 then assert(r('CrossoverBehaviorVersion')==0,'Pixel comparison preserves actual power-on1.0 default')end
 if frame==465 then assert(r('CrossoverMenuState')==4 and r('CrossoverOptionsFocus')==0,'Actual title Options page owns the shadow toggle')end
 if frame==500 then assert(r('PlayerOutlinesOff')==0,'Options A enables shadows before returning to the roster')end
 if frame>=85 and frame<=305 and(frame-85)%20==0 then
  assert(r('SelectedCharacter')==slots[(frame-85)//20+1] and r('PlayerOutlinesOff')==1,'Default OFF previews traverse the full roster')
  off[r('SelectedCharacter')]=pixels()
 end
 if frame>=645 and frame<=865 and(frame-645)%20==0 then
  local c=r('SelectedCharacter')
  assert(c==slots[(11+(frame-645)//20)%12+1] and r('PlayerOutlinesOff')==0,'Opt-in ON previews traverse the full roster')
  local on=pixels();local changed=0
  for i,v in ipairs(on)do
   if v~=off[c][i]then
    assert(v==0x0f and off[c][i]==255,'Outlines OFF preserves every colored/face pixel, character '..c..' pixel '..i..': '..v..'/'..off[c][i])
    changed=changed+1
   end
  end
  checked[c]=true;removed=removed+changed
  if c==2 then assert(changed>0,'Samus actually loses the extra black mask')end
 end
 if frame==880 then
  for _,c in ipairs(slots) do assert(checked[c],'Every player has independent ON/OFF pixel comparison')end
  for _,c in ipairs({0,1,3,6,7,12,10,11})do assert(not filterCalls[c],'Characters without added mask records bypass filtering: '..c)end
  for _,c in ipairs({2,4,5,9})do assert((filterCalls[c]or 0)>0,'Characters with added mask records retain the option: '..c)end
  assert(removed>0,'Outline preference changes real hardware sprite pixels')
  print('PASS all twelve ON/OFF player previews: '..removed..' extra black pixels removed, all colored and face pixels preserved');emu.stop(0)
 end
end,emu.eventType.endFrame)
