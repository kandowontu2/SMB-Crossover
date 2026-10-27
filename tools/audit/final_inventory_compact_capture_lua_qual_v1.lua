-- Encoder-only qualification. Exactly one test per endFrame, one startup
-- registration, no input/memory writes, screenshots or runtime registrations.
assert(_VERSION=='Lua 5.4','This qualification requires the existing Lua 5.4 host')
assert(type(OUTPUT)=='string' and OUTPUT:sub(-1)=='/','Runner output prefix')
local codec=dofile(TEST_DIR..'final_inventory_compact_capture_v1.lua')
local originalOpen=io.open
local FRAME_WORDS=256*240
local function json(v)
 if type(v)=='string' then
  return '"'..v:gsub('[%z\1-\31\\"]',function(c)
   local e={['"']='\\"',['\\']='\\\\',['\n']='\\n',['\r']='\\r',['\t']='\\t'}
   return e[c] or string.format('\\u%04x',c:byte())
  end)..'"'
 elseif type(v)=='table' then
  local out={}
  if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']' end
  local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys)
  for _,k in ipairs(keys)do out[#out+1]=json(k)..':'..json(v[k])end
  return '{'..table.concat(out,',')..'}'
 else return tostring(v) end
end
local function hex(s)return(s:gsub('.',function(c)return string.format('%02x',c:byte())end))end
local function noise(n)
 local out={};local x=731
 for i=1,n do x=(1664525*x+1013904223)&0xffffffff;out[i]=string.pack('<I4',x)end
 return table.concat(out)
end
local function repeated(n)return string.rep(string.pack('<I4',0xff102030),n)end
local function mixed(n)
 local out={}
 for i=0,n-1 do out[i+1]=string.pack('<I4',i%257<129 and 0xff102030 or (i*2654435761)&0xffffffff)end
 return table.concat(out)
end
local function change(raw,at,mask)
 local p=at*4+1;local word=string.unpack('<I4',raw,p)
 return raw:sub(1,p-1)..string.pack('<I4',word~mask)..raw:sub(p+4)
end
local function xor(raw,mask)
 local out={};for p=1,#raw,4 do out[#out+1]=string.pack('<I4',string.unpack('<I4',raw,p)~mask)end
 return table.concat(out)
end
local smallNoise=noise(257)
local micro={
 {'raw-one',noise(1),nil,true,0},
 {'repeat-two',repeated(2),nil,true,1},
 {'repeat-127',repeated(127),nil,true,1},
 {'repeat-128',repeated(128),nil,true,1},
 {'repeat-129',repeated(129),nil,true,1},
 {'literal-127',noise(127),nil,true,0},
 {'literal-128',noise(128),nil,true,0},
 {'literal-129',noise(129),nil,true,0},
 {'mixed-257',mixed(257),nil,true,1},
 {'xor-identical',smallNoise,smallNoise,false,2},
 {'xor-sparse',change(smallNoise,128,0x55aa0102),smallNoise,false,2},
 {'keyframe-forbids-xor',smallNoise,smallNoise,true,0},
 {'xor-constant',smallNoise,xor(smallNoise,0x55aa55aa),false,2},
}
local step=0
local adapter=codec.install(OUTPUT,{container_bytes=2000000,records=70},function()return{testcase=step}end)
local full=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local microRows,rejections,callbackFrames,callbackCpuSeconds={},{},{},{}
local fullNoise,solid,fullMixed
local function frame(n)
 if not fullNoise then fullNoise=noise(FRAME_WORDS);solid=repeated(FRAME_WORDS)end
 if n==1 then return solid end
 if n==4 then return change(fullNoise,257,0x55aa0102)end
 if n==5 then fullMixed=fullMixed or mixed(FRAME_WORDS);return fullMixed end
 if n==66 then return change(fullNoise,1023,0xa0ff00ff)end
 return fullNoise
end
local function named(name,raw)
 local f=assert(io.open(OUTPUT..name,'wb'));f:write(raw);f:close()
end
local function writeFull(n)
 local raw=frame(n)
 -- Exercise fragmented writes without creating individual frame files.
 full:write(raw:sub(1,17));full:write(raw:sub(18))
 if n==1 then named('first.argb',raw)
 elseif n==2 or n==3 then named('reused-name.argb',raw)
 elseif n==65 then named('keyframe.argb',raw)
 elseif n==66 then named('last-delta.argb',raw)
 elseif n==67 then named('final.argb',raw)end
end
local function oneTest()
 if step<=13 then
  local c=micro[step];local mode,payload,check=codec.encode(c[2],c[3],c[4])
  assert(mode==c[5],c[1]..' must exercise its intended codec mode')
  microRows[#microRows+1]={name=c[1],mode=mode,payload_hex=hex(payload),word_fnv1a32=check,decoded_bytes=#c[2]}
 elseif step==14 then
  local ok,why=pcall(codec.encode,'\0',nil,true)
  assert(not ok and tostring(why):find('unaligned ARGB/blob bytes',1,true),'Unaligned encoder input must fail')
  rejections[#rejections+1]={name='unaligned-input',rejected=true}
 elseif step==15 then
  local ok,why=pcall(codec.encode,noise(2),noise(1),false)
  assert(not ok and tostring(why):find('previous frame length',1,true),'Wrong XOR predecessor must fail')
  rejections[#rejections+1]={name='wrong-previous-length',rejected=true}
 elseif step<=81 then writeFull(step-15)
 elseif step==82 then
  local b={};for i=0,1023 do b[#b+1]=string.char(i%256)end
  named('diagnostic-CHR-0242.bin',table.concat(b))
 elseif step==83 then named('different-named.argb',solid)
 elseif step==84 then writeFull(67)
 else error('Unexpected qualification testcase')end
end
local finished=false
emu.addEventCallback(function()
 if finished then return end
 step=step+1
 local s=emu.getState();local f=math.tointeger(s['ppu.frameCount']);assert(f,'Actual integer callback frame')
 assert(#callbackFrames==0 or f>callbackFrames[#callbackFrames],'At most one test per actual endFrame')
 callbackFrames[#callbackFrames+1]=f
 local start=os.clock()
 if step<=84 then oneTest()
 else
  assert(step==85,'Fixed qualification bound')
  full:close();adapter.close();local stats=adapter.stats()
  assert(stats.records==69 and stats.full_frames==67 and stats.open_virtual_files==0 and stats.full_closed,'Complete compact capture endpoints')
  assert(stats.container_bytes<2000000 and stats.per_frame_files==0 and stats.screenshots==0,'Small-output contract')
  callbackCpuSeconds[#callbackCpuSeconds+1]=os.clock()-start
  local proof={passed=true,scope='Lua encoder and container I/O only; no native gameplay/74-callback qualification',lua_version=_VERSION,
   testcase_count=85,encoder_cases=microRows,rejection_cases=rejections,callback_frames=callbackFrames,callback_cpu_seconds=callbackCpuSeconds,
   adapter_stats=stats,registrations_at_startup=1,runtime_registration_calls=0,emulated_writes=0,input_calls=0,screenshots=0}
  local out=assert(originalOpen(OUTPUT..'lua-encoder-native.json','w'));out:write(json(proof)..'\n');out:close()
  finished=true;print('PASS Lua encoder only: 13 codec cases, 2 rejections, 67 full images, one CHR blob, aliases/keyframe; 3 small outputs')
  emu.stop(0);return
 end
 callbackCpuSeconds[#callbackCpuSeconds+1]=os.clock()-start
end,emu.eventType.endFrame)
