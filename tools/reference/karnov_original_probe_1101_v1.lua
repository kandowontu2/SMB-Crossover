-- Read-only original-ROM research. One initial fixture, aggregate code coverage,
-- compact field trace and four screenshots; no frame-image/state dump sequence.
local frames,updates,shots=0,0,0
local initial,done=nil,false
local counts,entries={},{}
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
 for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local csv=assert(io.open(OUTPUT..'player-fields.csv','w'));csv:write('frame,update,mode,held,fresh,state,x,y,timer,field65,tile89,tile8a,tile8b,tile8c,tile8d,cameraX,cameraY\n')
local function shot(name)shots=shots+1;assert(shots<=4,'Four PNG cap');local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function finish()
 if done then return end;done=true;csv:close();shot('endpoint')
 local f=assert(io.open(OUTPUT..'reference.json','w'));f:write(json({passed=updates>=620,ROM_sha256=KARNOV_SHA,frames=frames,player_updates=updates,initial_fixture=initial,entries=entries,executed_instructions=counts,scope='Original NES Karnov cold controller research: idle/right/jump/duck/fire/left. One initial RAM fixture and aggregate code coverage; not a port, host admission or campaign qualification.'})..'\n');f:close();print('KARNOV_REFERENCE '..updates);emu.stop(updates>=620 and 0 or 1)
end
emu.addEventCallback(function()
 local t=updates;local p={}
 if r(0x10)~=11 then p.start=frames>=120 and frames%60<3
 elseif t>=40 and t<100 then p.right=true
 elseif t>=120 and t<145 then p.a=true
 elseif t>=200 and t<240 then p.down=true
 elseif t>=260 and t<325 then p.b=true
 elseif t>=350 and t<410 then p.left=true
 elseif t>=440 and t<510 then p.a=true;p.b=true;p.right=true
 elseif t>=550 and t<580 then p.down=true;p.b=true end
 emu.setInput(p,0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if done or r(0x10)~=11 then return end
 updates=updates+1
 if updates==35 then
  initial={};for i=0,2047 do initial[#initial+1]=r(i)end
 end
 if updates==1 or updates==40 or updates==100 or updates==120 or updates==145 or updates==200 or updates==240 or updates==260 or updates==325 or updates==350 or updates==410 or updates==440 or updates==510 or updates==550 or updates==580 then
  local fields={};for _,a in ipairs({0x10,0x21,0x22,0x1b,0x62,0x63,0x64,0x65,0x66,0x89,0x8a,0x8b,0x8c,0x8d,0x0c,0x0d})do fields[string.format('%02x',a)]=r(a)end
  entries[#entries+1]={update=updates,frame=frames,fields=fields,sp=emu.getState()['cpu.sp']}
 end
 if updates%2==0 then local row={frames,updates};for _,a in ipairs({0x10,0x21,0x22,0x62,0x63,0x64,0x66,0x65,0x89,0x8a,0x8b,0x8c,0x8d,0x0c,0x0d})do row[#row+1]=r(a)end;csv:write(table.concat(row,',')..'\n')end
end,emu.callbackType.exec,0xf297)
emu.addMemoryCallback(function(a)
 if done or r(0x10)~=11 then return end
 local key=string.format('%04X',a);counts[key]=(counts[key]or 0)+1
end,emu.callbackType.exec,0xf297,0xfcff)
emu.addEventCallback(function()
 if done then return end;frames=frames+1
 if updates>=38 and shots==0 then shot('standing')elseif updates>=135 and shots==1 then shot('jump')elseif updates>=290 and shots==2 then shot('fire')end
 if updates>=620 or frames>=2400 then finish()end
end,emu.eventType.endFrame)
