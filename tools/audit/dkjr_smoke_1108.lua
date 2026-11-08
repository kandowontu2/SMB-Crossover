-- Controller-only smoke. Report real frame cadence without state writes.
local frame, step, updates, draws, polled = 0, 1, 0, 0, false
local phase, previous, priorUpdates, startX, minimumY = 'menu', nil, 0, nil, 255
local phaseStart, startLives = 0,nil
local cadence = {}
local body = {returns=0,writes=0}
local route = {{'down',8},{'down',16},{'right',17},{'right',18},{'right',19},{'down',27},{'select',27},{'start',27}}
local menuX, lastSkipped, sent, switched, done
local function read(a) return emu.read(a,emu.memType.nesDebug) end
local function private(bank,a) return emu.read(bank*8192+a,emu.memType.nesWorkRam) end
local function xpos() return read(0x75)+256*read(0x5c) end
local function active() return read(0x6002)==40 and read(0x0f)==8 and private(2,0x8fe)==2 end
local function inram(pc,bank,base)
 local m=emu.convertAddress(pc)
 return m and m.memType==emu.memType.nesWorkRam and m.address==bank*8192+pc-base
end
local function json(v)
 if type(v)=='table' then local list={};for k,x in pairs(v) do list[#list+1]=string.format('%q',k)..':'..json(x) end;return '{'..table.concat(list,',')..'}' end
 if type(v)=='string' then return string.format('%q',v) end
 return tostring(v)
end
local function shot(name)
 local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function begin(name)
 phase=name;phaseStart=updates;startX=xpos()
end
emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4016)
emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4017)
emu.addMemoryCallback(function()
 if inram(C.main,2,0xc000) and active() then updates=updates+1 end
end,emu.callbackType.exec,C.main)
emu.addMemoryCallback(function()
 if inram(C.draw,3,0xa000) and active() then draws=draws+1 end
end,emu.callbackType.exec,C.draw)
emu.addMemoryCallback(function()
 if not inram(C.draw,3,0xa000) or not active() then return end
 body.offset_before=read(0x6de)
end,emu.callbackType.exec,C.draw)
emu.addMemoryCallback(function()
 if not inram(C.draw+3,3,0xa000) or not active() then return end
 body.returns=body.returns+1
 if private(2,0x8fa)~=0 then body.writes=body.writes+1 end
 if body.first then return end
 body.first={offset_before=body.offset_before,offset_after=read(0x6de),result=private(2,0x8fa),
  rotation=read(0x6c08),rotation_enabled=read(0x6c0b),source_oam={},shadow_chr={}}
 for i=0,31 do body.first.source_oam[tostring(i)]=private(2,0x210+i) end
 for i=0,7 do body.first.shadow_chr[tostring(i)]=read(0x147+i) end
end,emu.callbackType.exec,C.draw+3)
emu.addEventCallback(function()
 local keys={}
 if phase=='menu' and frame>=120 and frame%24==0 and step<=#route then
  if read(0x7307)~=2 then keys.start=true
  else
   if sent then
    assert(read(0x7309)==route[step-1][2],'Actual menu navigation')
    if step==8 then
     assert(read(0x6002)==40,'Select must resolve to DK Jr')
     local name=' DONKEY KONG JR '
     for i=1,#name do
      local c=name:byte(i);local tile=c==32 and 36 or c-55
      assert(emu.read(0x2327+i,emu.memType.nesPpuDebug)==tile,'Actual DK Jr menu name')
     end
     shot('dkjr-menu');switched=true
    end
   end
   local key=route[step][1];keys[key]=true;step=step+1;sent=true
  end
 elseif phase=='right' then keys.right=true
 elseif phase=='left' then keys.left=true
 elseif phase=='jump' and updates-phaseStart<8 then keys.a=true end
 emu.setInput(keys,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;assert(frame<3000,'Bounded DK Jr launch and motion')
 local skipped=read(0x013a)
 if active() and switched then
  if phase=='menu' then
   for _,bank in ipairs({2,3}) do for i,byte in ipairs(C.cookie) do
    assert(private(bank,0x1fdf+i)==byte,'Real authenticated DK Jr cold payload')
   end end
   startLives=read(0x75f);menuX=xpos();begin('idle')
  elseif previous==phase then
   local q=cadence[phase] or {physical=0,updates=0,lag_nmi=0,no_controller_read=0}
   q.physical=q.physical+1;q.updates=q.updates+updates-priorUpdates
   q.lag_nmi=q.lag_nmi+((skipped-lastSkipped)&255)
   if not polled then q.no_controller_read=q.no_controller_read+1 end
   cadence[phase]=q
  end
  assert(read(0x75f)==startLives,'Original lives retained')
  local n=updates-phaseStart
  if phase=='idle' then
   assert(xpos()==menuX,'DK Jr idle anchor')
   if n>=120 then begin('right') end
  elseif phase=='right' and n>=32 then
   assert(xpos()>startX+8,'Actual right movement');begin('left')
  elseif phase=='left' and n>=16 then
   assert(xpos()<startX-4,'Actual left movement');begin('jump')
  elseif phase=='jump' then
   minimumY=math.min(minimumY,read(0xbd))
   if n>=64 then
    assert(minimumY<=164 and read(0xbd)==176 and draws>0,'Original hop, landing and mapped draw')
    shot('dkjr-gameplay')
    body.visible_oam={}
    for i=0,63 do
     local a=i*4
     local y=emu.read(a,emu.memType.nesSpriteRam)
     if y<240 then
      local row={y=y}
      for j,n in ipairs({'tile','attribute','x'}) do row[n]=emu.read(a+j,emu.memType.nesSpriteRam) end
      body.visible_oam[tostring(i)]=row
     end
    end
    local f=assert(io.open(OUTPUT..'result.json','w'))
    f:write(json({passed=true,ROM_sha256=C.pin,controller_only=true,frames=frame,
     source_main_calls=updates,source_draw_calls=draws,cadence=cadence,minY=minimumY,body=body,full_stage=false})..'\n');f:close()
    done=true;emu.stop(0)
   end
  end
 end
 previous=phase;priorUpdates=updates;lastSkipped=skipped;polled=false
end,emu.eventType.endFrame)
