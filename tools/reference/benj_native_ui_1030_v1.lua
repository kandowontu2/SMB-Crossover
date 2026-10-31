-- Read-only actual DMA, physical CHR, palette and visible pixel checks.
local uiFile=assert(io.open(OUTPUT..'select-lives-OAM.csv','w'))
uiFile:write('frame,stage,variant,page,parts,pixels,P0,background\n')
local chrUpper,bodyPage=0,-1
local lastUI,uiChecks,renderedUI={},{selected=0,lives=0},{}
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function signed(v)return v>=128 and v-256 or v end
emu.addMemoryCallback(function(_,v)chrUpper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)bodyPage=chrUpper+v end,emu.callbackType.write,0x5120)
local function uiDMA(stage,page)
 if lastUI[stage]and frame-lastUI[stage].frame<8 then return end
 assert(bodyPage>=P.first_page and bodyPage<P.first_page+7,'Own source body physical page')
 assert(r('Mirror_PPUCTRL')&32~=0,'Native8x16 sprites')
 for i=1,3 do assert(ppu(0x3f10+i)==P.colors[i],'Actual source Benj P0 '..stage)end
 if stage=='lives'then assert(ppu(0x3f00)==15,'Native black lives background')end
 local size=emu.read(0x5c6b,emu.memType.nesDebug)
 assert(size>=4 and size<=16 and size%4==0,'Complete own source body descriptor')
 local parts,expected,count={}, {},0
 local anchorX,anchorY=nil,nil
 for k=0,size-4,4 do
  local tile=emu.read(0x5c6c+k,emu.memType.nesDebug)
  local attr=emu.read(0x5c6d+k,emu.memType.nesDebug)
  local dy=signed(emu.read(0x5c6e+k,emu.memType.nesDebug))
  local dx=signed(emu.read(0x5c6f+k,emu.memType.nesDebug))
  local found=nil
  for at=0,252,4 do
   local base=page*256+at
   local y,t,a,x=emu.read(base,emu.memType.nesDebug),emu.read(base+1,emu.memType.nesDebug),emu.read(base+2,emu.memType.nesDebug),emu.read(base+3,emu.memType.nesDebug)
   if y<240 and t==tile and a==attr and (not anchorX or(x-dx)%256==anchorX and(y-dy)%256==anchorY)then
    found={oam=at,x=x,y=y,tile=t,attr=a};anchorX,anchorY=(x-dx)%256,(y-dy)%256;break
   end
  end
  assert(found,'Every original Benj descriptor part reaches actual DMA '..stage)
  parts[#parts+1]=found
 end
 table.sort(parts,function(a,b)return a.oam<b.oam end)
 for _,part in ipairs(parts)do
  assert(part.tile<64 and part.attr&3==0,'Private window0/P0 body')
  for y=0,15 do
   local at=bodyPage*1024+(part.tile&254)*16+(y//8)*16+y%8
   local lo,hi=emu.read(at,emu.memType.nesChrRom),emu.read(at+8,emu.memType.nesChrRom)
   for x=0,7 do
    local value=((lo>>x)&1)|(((hi>>x)&1)<<1)
    if value~=0 then
     local px=part.x+(part.attr&64~=0 and x or 7-x)
     local py=part.y+1+y
     assert(px<256 and py<240,'Complete body on screen')
     local pos=py*256+px
     if expected[pos]==nil then expected[pos]=ppu(0x3f10+value);count=count+1 end
    end
   end
  end
 end
 assert(count>40,'Visible complete source artwork')
 lastUI[stage]={frame=frame,pixels=expected,opaque=count};uiChecks[stage]=uiChecks[stage]+1
 uiFile:write(table.concat({frame,stage,P.variant,bodyPage,#parts,count,ppu(0x3f11)..':'..ppu(0x3f12)..':'..ppu(0x3f13),ppu(0x3f00)},',')..'\n');uiFile:flush()
end
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=0 or r('MarioVariant')~=P.variant then return end
 if phase=='browse'and step>#plan and age>=8 and r('CrossoverMenuState')==2 then uiDMA('selected',page)
 elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then uiDMA('lives',page)end
end,emu.callbackType.write,0x4014)
local function stableUI(stage)local q=lastUI[stage];return q and frame-q.frame>=2 and frame-q.frame<=7 end
local function renderedBody(stage)
 local q=assert(lastUI[stage]);assert(stableUI(stage),'Stable actual DMA precedes capture')
 local screen=emu.getScreenBuffer();assert(#screen==61440)
 local colors={}
 for at,nes in pairs(q.pixels)do
  local rgb=screen[at+1]&0xffffff
  if colors[nes]then assert(colors[nes]==rgb,'Complete current hardware color roles '..stage)else colors[nes]=rgb end
 end
 local unique,n={},0
 for _,rgb in pairs(colors)do assert(not unique[rgb],'Distinct body colors');unique[rgb]=true;n=n+1 end
 assert(n>=2,'Actual colored source sprite')
 renderedUI[stage]={pixels=q.opaque,palette_roles=n,frame=frame}
end
