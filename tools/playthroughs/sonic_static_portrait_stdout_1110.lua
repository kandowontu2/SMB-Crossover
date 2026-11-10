-- Controller-only observation of the Sonic character-select and lives portraits.
local rom = os.getenv('SMB_STDOUT_ROM_SHA') or ''
local frame, pad, stopped = 0, 0, false
local chrPage, upper = -1, -1
local menuProof, livesProof
local observed

local function read(address)
  return emu.read(address, emu.memType.nesDebug)
end

local function proofAt(x, y)
  local cells, colors = {}, {}
  for offset = 0x200, 0x2fc, 4 do
    if read(offset)<240 and #cells<12 then
      cells[#cells+1]=string.format('%d/%d/%d/%d',read(offset),read(offset+1),read(offset+2),read(offset+3))
    end
  end
  for i=1,3 do colors[i]=emu.read(0x3f10+i,emu.memType.nesPpuDebug) end
  observed=string.format('CHR=%d upper=%d mode=%d page=%d wide=%d reload=%d colors=%s cells=%s',
    chrPage,upper,read(0x73e0),read(0x147),read(0x73ee),read(0x146),table.concat(colors,'/'),table.concat(cells,','))
  if upper ~= 0 or chrPage ~= 224 then return nil end
  local expected = {[0] = {x, y}, [2] = {x+8, y}, [32] = {x, y+16}, [34] = {x+8, y+16}}
  local count = 0
  for offset = 0x200, 0x2fc, 4 do
    local cell = expected[read(offset+1)]
    if cell and read(offset+3) == cell[1] and read(offset) == cell[2]
        and read(offset+2) & 0x43 == 0 then
      expected[read(offset+1)] = nil
      count = count+1
    end
  end
  if count ~= 4 then return nil end
  if colors[1] ~= 0x16 or colors[2] ~= 0x12 or colors[3] ~= 0x30 then return nil end
  return string.format('{"frame":%d,"x":%d,"y":%d,"cells":4,"CHR_page":224,"palette":[22,18,48]}',frame,x,y)
end

local function finish(passed, message)
  if stopped then return end
  stopped = true
  local escaped = message:gsub('[%z\1-\31\\"]',' ')
  print(string.format('SMB_NATIVE_RECEIPT {"passed":%s,"reason":"%s","ROM_SHA256":"%s",' ..
    '"physical_frames":%d,"menu":%s,"lives":%s,"output_files":0,"controller_only":true}',
    tostring(passed),escaped,rom,frame,menuProof or 'null',livesProof or 'null'))
  emu.stop(passed and 0 or 1)
end

local function guarded(callback)
  return function(...)
    if stopped then return end
    local ok, message = pcall(callback,...)
    if not ok then finish(false,tostring(message)) end
  end
end

local function frames(n)
  for _ = 1,n do coroutine.yield() end
end

local function press(bits)
  pad=bits
  frames(4)
  pad=0
  frames(8)
end

local function waitFor(predicate, limit, label)
  for _ = 1,limit do
    if predicate() then return end
    coroutine.yield()
  end
  error(label .. ' did not settle. ' .. (observed or 'No portrait snapshot'))
end

local route = coroutine.create(function()
  waitFor(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end,500,'Title')
  press(16)
  waitFor(function()return read(0x7307)==2 and read(0x775)==0 end,200,'Roster')
  for _,bits in ipairs({4,4,4,1}) do press(bits) end
  assert(read(0x7309)==25 and read(0x5ffe)==0,'Mr. Gimmick selection')
  for _=1,3 do press(32) end
  assert(read(0x6002)==43 and read(0x5ffe)==3,'Sonic selection')
  waitFor(function()menuProof=proofAt(120,160);return menuProof end,90,'Sonic menu OAM/CHR/palette')
  press(16)
  waitFor(function()
    if read(0x771)~=1 or read(0x773)==3 then return false end
    livesProof=proofAt(96,88)
    return livesProof
  end,650,'Sonic lives OAM/CHR/palette')
  finish(true,'Natural Sonic select and lives portraits')
end)

assert(#rom==64 and not rom:find('[^0-9a-f]'),'Expected exact ROM SHA supplied by runner')
emu.addMemoryCallback(guarded(function(_,value) upper=(value&3)*256 end),emu.callbackType.write,0x5130)
emu.addMemoryCallback(guarded(function(_,value) chrPage=value+upper end),emu.callbackType.write,0x5120)
emu.addEventCallback(guarded(function()
  emu.setInput({right=pad&1~=0,down=pad&4~=0,start=pad&16~=0,select=pad&32~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
  frame=frame+1
  assert(frame<=1600,'Bounded natural menu/lives replay')
  local ok, message=coroutine.resume(route)
  assert(ok,message)
end),emu.eventType.endFrame)
