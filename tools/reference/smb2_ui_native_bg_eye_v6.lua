-- Read-only UI observer v6; actual OAM priority and authenticated red-eye role.
-- P0 is original. Remapped eye index1 uses unchanged native P2 red $16.
local uiSource=assert(S2_UI_SOURCE)
local uiFile=assert(io.open(OUTPUT..'select-lives-OAM.csv','w'))
uiFile:write('frame,stage,variant,nativeClass,physicalPage,parts,visible,opaquePixels,P0,eyeP2,background\n')
local chrUpper,bodyPhysicalPage=0,-1
local lastUI,uiChecks,renderedUI={},{selected=0,lives=0},{}
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local romFile=assert(io.open(uiSource.rom,'rb'))
local sourceROM=romFile:read('*a');romFile:close()
local function signed(v)return v>=128 and v-256 or v end
local function paletteText(a)return string.format('%02x%02x%02x',ppu(a),ppu(a+1),ppu(a+2))end
emu.addMemoryCallback(function(_,v)chrUpper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)bodyPhysicalPage=chrUpper+v end,emu.callbackType.write,0x5120)
local function uiDMA(stage,page)
 local previous=lastUI[stage]
 if previous and frame-previous.frame<8 then return end
 assert(r('S2NativeCharacter')==P.native_class and r('S2Size')==0,'Actual UI fresh source class/form')
 assert(bodyPhysicalPage==uiSource.page,'Actual UI physical window0 is the original class ART')
 assert(r('Mirror_PPUCTRL')&0x20~=0,'Native8x16 sprite mode')
 for i=1,3 do assert(ppu(0x3f10+i)==uiSource.p0[i],'Actual original source body P0 '..stage)end
 assert(ppu(0x3f19)==0x16,'Authenticated original red eye uses unchanged native P2')
 if stage=='lives'then assert(ppu(0x3f00)==15 and ppu(0x3f10)==15,'Native lives black universal backdrop')end
 local all={};local visible=0
 for at=0,255 do all[at]=emu.read(page*256+at,emu.memType.nesDebug)end
 for at=0,252,4 do if all[at]<240 then visible=visible+1 end end
 local px=(r('Player_X_Position')-r('ScreenLeft_X_Pos'))&255
 local py=r('Player_Y_Position')
 local expected,matched,opaque,drawParts={},0,0,{}
 for _,part in ipairs(uiSource.parts)do
  local tile,attr=part[1],part[2]&0xdf
  local y,x=(py+signed(part[3]))&255,(px+signed(part[4]))&255
  assert(tile<64 and attr&0x20==0,'Actual UI original source window0/in-front record')
  local found=nil
  for at=0,252,4 do
   if all[at]==y and all[at+1]==tile and all[at+2]==attr and all[at+3]==x then found=at;break end
  end
  assert(found,'Every original source UI quad reaches actual DMA '..stage)
  matched=matched+1
  drawParts[#drawParts+1]={physical=found,tile=tile,attr=attr,x=x,y=y}
 end
 table.sort(drawParts,function(a,b)return a.physical<b.physical end)
 for _,part in ipairs(drawParts)do
  local tile,attr,x,y=part.tile,part.attr,part.x,part.y
  for row=0,15 do
   local pattern=(tile&254)*16+(row//8)*16+row%8
   local source=uiSource.chr_offset+bodyPhysicalPage*1024+pattern
   local lo,hi=sourceROM:byte(source+1),sourceROM:byte(source+9)
   assert(emu.read(bodyPhysicalPage*1024+pattern,emu.memType.nesChrRom)==lo and emu.read(bodyPhysicalPage*1024+pattern+8,emu.memType.nesChrRom)==hi,'Physical sprite CHR equals the bound original S2 bytes')
   for bit=0,7 do
    local value=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
    if value~=0 then
     local dx=attr&64~=0 and bit or 7-bit
     local dy=attr&128~=0 and 15-row or row
     local at=(y+1+dy)*256+x+dx
     assert(x+dx<256 and y+1+dy<240,'Entire original UI body is on screen')
     -- NES priority is the lowest actual physical OAM index, not descriptor order.
     if expected[at]==nil then expected[at]=ppu(0x3f10+(attr&3)*4+value);opaque=opaque+1 end
    end
   end
  end
 end
 assert(matched==5 and visible>=matched and visible<=8 and opaque>150,'Complete visible source body within normal hardware sprite budget')
 lastUI[stage]={frame=frame,pixels=expected,opaque=opaque}
 uiChecks[stage]=uiChecks[stage]+1
 uiFile:write(table.concat({frame,stage,P.variant,P.native_class,bodyPhysicalPage,matched,visible,opaque,paletteText(0x3f11),paletteText(0x3f19),ppu(0x3f00)},',')..'\n');uiFile:flush()
end
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=25 or r('S2Variant')~=P.variant or r('S2Ready')~=178 then return end
 if phase=='browse'and step>#plan and age>=8 and r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==P.slot then uiDMA('selected',page)
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then uiDMA('lives',page)end
end,emu.callbackType.write,0x4014)
local function stableUI(stage)
 local q=lastUI[stage]
 return q and frame-q.frame>=2 and frame-q.frame<=7
end
local function renderedBody(stage)
 local q=assert(lastUI[stage],'Actual completed UI DMA before screenshot')
 assert(stableUI(stage),'Stable completed UI DMA precedes actual rendered frame')
 local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual256x240 PPU pixel buffer')
 local colors,count={},0
 for at,nes in pairs(q.pixels)do
  assert(at>=0 and at<61440,'Original UI source pixels are within actual screen')
  local rgb=screen[at+1]&0xffffff
  if colors[nes]then assert(colors[nes]==rgb,'Actual opaque UI pixels preserve their complete current PPU palette role '..stage)
  else colors[nes]=rgb end
  count=count+1
 end
 local unique,n={},0
 for _,rgb in pairs(colors)do assert(not unique[rgb],'Distinct current PPU colors remain visibly distinct');unique[rgb]=true;n=n+1 end
 assert(n>=3 and count>150,'Actual source body is rendered in color, not a blank panel')
 renderedUI[stage]={pixels=count,palette_roles=n,frame=frame}
 if stage=='selected'then
  for i,value in ipairs(uiSource.name)do assert(ppu(0x2328+i-1)==value,'Actual complete hardware SMB2 class name')end
 end
end
