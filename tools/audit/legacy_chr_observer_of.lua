-- Read-only legacy/expanded MMC5 bank ownership for actual player DMA parts.
-- Legacy pages use ChrPhysicalMap; explicit pages use X5ChrMode's high bits.
-- No SmPosePtr or explicit-page requirement is invented for native Mario.
return function(cfg)
 local folder=cfg.out or OUTPUT
 local target=cfg.character
 local frame,inside,prepared,displayed=0,nil,nil,nil
 local returns={};local rows,bad,draws=0,0,0
 local f=assert(io.open(folder..'chr-commit.csv','w'))
 f:write('frame,draw,window,expected,actual,bodyParts,bad\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(a)return emu.convertAddress(a).address//8192 end
 local function active()return r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==target end
 local function physical(window)
  local mode=r('X5ChrMode',window);local low=r('CurrentCHRBank',window)
  if mode&128~=0 then return low+256*(mode&3)end
  return emu.read(assert(L.ChrPhysicalMap)+low,emu.memType.nesDebug)
 end
 local function part(page,slot)
  local a=page+slot*4;local q={}
  for i=0,3 do q[i+1]=emu.read(a+i,emu.memType.nesDebug)end
  return q
 end
 local function same(a,b)for i=1,4 do if a[i]~=b[i]then return false end end;return true end
 local function finishBody()
  if not inside then return end
  local parts={};local expected={}
  for slot in pairs(inside.slots)do
   local q=part(0x200,slot)
   if q[1]>=31 and q[1]<239 then
    local window=(q[2]&1)*4+(q[2]&254)//64
    parts[#parts+1]={slot=slot,bytes=q,window=window}
    expected[window]=physical(window)
   end
  end
  prepared={parts=parts,expected=expected,draw=draws};draws=draws+1
  inside=nil
 end
 emu.addMemoryCallback(function()
  if bank(0xa000)==B.DrawAllMetasprites then prepared=nil end
 end,emu.callbackType.exec,L.DrawAllMetasprites)
 emu.addMemoryCallback(function()
  if not active()or bank(0xa000)~=B.DrawMetasprite then return end
  local state=emu.getState();if state['cpu.y']~=0 then return end
  assert(not inside,'Player render calls are not nested')
  local sp=state['cpu.sp']
  local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  inside={pc=pc,sp=(sp+2)%256,slots={}}
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if inside and inside.pc==pc and emu.getState()['cpu.sp']==inside.sp then finishBody()end
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,L.DrawMetasprite)
 emu.addMemoryCallback(function(address)
  if inside then inside.slots[(address-0x200)//4]=true end
 end,emu.callbackType.write,0x200,0x2ff)
 emu.addMemoryCallback(function()
  if inside and active()and target==2 and bank(0xa000)==B.MetaspriteRenderLoop then
   assert(r('CurrentCHRBank')==r('SmChrBank'),'Samus publishes her selected pose page before rendering')
  end
 end,emu.callbackType.exec,L.MetaspriteRenderLoop)
 emu.addMemoryCallback(function(_,page)
  displayed=nil
  if not active()or not prepared then return end
  local windows={};local count=0
  for _,p in ipairs(prepared.parts)do
   if same(part(page*256,p.slot),p.bytes)then windows[p.window]=prepared.expected[p.window];count=count+1 end
  end
  if count>0 then displayed={windows=windows,parts=count,draw=prepared.draw}end
 end,emu.callbackType.write,0x4014)
 emu.addEventCallback(function()
  frame=frame+1
  if not active()or not displayed then return end
  local state=emu.getState()
  for window,expected in pairs(displayed.windows)do
   local actual=assert(state['mapper.chrBanks'..window]);local wrong=actual~=expected
   rows=rows+1
   if wrong then
    bad=bad+1
    if bad<=8 then local out=assert(io.open(folder..'mismatch-'..frame..'.png','wb'));out:write(emu.takeScreenshot());out:close()end
   end
   f:write(table.concat({frame,displayed.draw,window,expected,actual,displayed.parts,wrong and 1 or 0},',')..'\n')
  end
 end,emu.eventType.endFrame)
 return{failure=function()return bad>0 and'Player CHR differs from actual DMA player-part mapping'or nil end,finish=function()
  f:close();assert(rows>40 or bad>0,'Actual committed legacy player-frame coverage')
  local out=assert(io.open(folder..'chr-commit.json','w'))
  out:write(string.format('{"passed":%s,"frames":%d,"mismatched_frames":%d,"body_constructions":%d,"scope":"Read-only MMC5 physical/legacy mapping versus matching actual DMA player parts on every observed active video frame. Source pose art, body visibility and full campaign are separate."}',tostring(bad==0),rows,bad,draws));out:close()
 end}
end
