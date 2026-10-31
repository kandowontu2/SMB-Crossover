-- Observe the descriptor while its real ROM/RAM source window is mapped.
local uiFile=assert(io.open(OUTPUT..'select-lives-OAM.csv','w'))
uiFile:write('frame,stage,variant,page,parts,pixels,P0,background,descriptor_age\n')
local chrUpper,bodyPage=0,-1
local lastUI,uiChecks,renderedUI={},{selected=0,lives=0},{}
local sourceDesc=nil
local function ppu(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function signed(v)return v>=128 and v-256 or v end
emu.addMemoryCallback(function(_,v)chrUpper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)bodyPage=chrUpper+v end,emu.callbackType.write,0x5120)
emu.addMemoryCallback(function()
 if bank(L.MetaspriteRenderLoop)~=B.MetaspriteRenderLoop then return end
 if r('SelectedCharacter')~=P.raw or r('ObjectMetasprite')~=233 then return end
 local ptr=r('R0')+256*emu.read(L.R0+1,emu.memType.nesDebug)
 local own=r('SmPosePtr')+256*emu.read(L.SmPosePtr+1,emu.memType.nesDebug)
 if ptr~=own then return end
 local size=emu.read(ptr,emu.memType.nesDebug)
 assert(size>=4 and size<=24 and size%4==0,'Complete original SMB3+ descriptor')
 local q={frame=frame,raw=r('SelectedCharacter'),variant=r('M3Variant'),parts={}}
 for k=1,size,4 do
  q.parts[#q.parts+1]={emu.read(ptr+k,emu.memType.nesDebug),emu.read(ptr+k+1,emu.memType.nesDebug),
   signed(emu.read(ptr+k+2,emu.memType.nesDebug)),signed(emu.read(ptr+k+3,emu.memType.nesDebug))}
 end
 sourceDesc=q
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
local function uiDMA(stage,page)
 if lastUI[stage]and frame-lastUI[stage].frame<8 then return end
 assert(bodyPage>=P.first_page and bodyPage<P.first_page+25,'Own original SMB3+ physical page')
 assert(r('Mirror_PPUCTRL')&32~=0,'Native8x16 sprites')
 for i=1,3 do assert(ppu(0x3f10+i)==P.colors[i],'Actual original SMB3+ P0 '..stage)end
 if stage=='lives'then assert(ppu(0x3f00)==15,'Native black lives background')end
 local desc=assert(sourceDesc,'Real mapped body descriptor was observed')
 assert(desc.raw==P.raw and desc.variant==P.variant,'Mapped descriptor belongs to selected source identity')
 local parts,expected,count={}, {},0
 local anchorX,anchorY=nil,nil
 local used={}
 for _,p in ipairs(desc.parts)do
  local tile,attr,dy,dx=p[1],p[2],p[3],p[4]
  local found=nil
  for at=0,252,4 do
   local base=page*256+at
   local y,t,a,x=emu.read(base,emu.memType.nesDebug),emu.read(base+1,emu.memType.nesDebug),
    emu.read(base+2,emu.memType.nesDebug),emu.read(base+3,emu.memType.nesDebug)
   if not used[at]and y<240 and t==tile and a==attr and(not anchorX or(x-dx)%256==anchorX and(y-dy)%256==anchorY)then
    found={oam=at,x=x,y=y,tile=t,attr=a};anchorX,anchorY=(x-dx)%256,(y-dy)%256;used[at]=true;break
   end
  end
  assert(found,'Every source body part reaches actual DMA '..stage)
  parts[#parts+1]=found
 end
 table.sort(parts,function(a,b)return a.oam<b.oam end)
 for _,part in ipairs(parts)do
  assert(part.tile<64 and part.attr&3==0,'Private window0/P0 body')
  for y=0,15 do
   local ty=part.attr&128~=0 and 15-y or y
   local at=bodyPage*1024+(part.tile&254)*16+(ty//8)*16+ty%8
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
 assert(count>40,'Visible complete original artwork')
 lastUI[stage]={frame=frame,pixels=expected,opaque=count};uiChecks[stage]=uiChecks[stage]+1
 uiFile:write(table.concat({frame,stage,P.variant,bodyPage,#parts,count,ppu(0x3f11)..':'..ppu(0x3f12)..':'..ppu(0x3f13),ppu(0x3f00),frame-desc.frame},',')..'\n');uiFile:flush()
end
emu.addMemoryCallback(function(_,page)
 if r('SelectedCharacter')~=P.raw or r('M3Variant')~=P.variant then return end
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
 assert(n>=2,'Actual colored original sprite')
 renderedUI[stage]={pixels=q.opaque,palette_roles=n,frame=frame}
end
