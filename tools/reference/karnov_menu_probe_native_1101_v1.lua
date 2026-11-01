local frame,age,phase,done=0,0,'title',false
local upper,pages,rows,registers=0,{},{},{}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function p(a)return emu.read(a,emu.memType.nesPpuDebug)end
local function json(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
 for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function sample(label)
 local q={phase=label,frame=frame,selected=r('SelectedCharacter'),slot=r('CrossoverMenuIndex'),control=r('Mirror_PPUCTRL'),hscroll=r('HorizontalScroll'),vscroll=r('VerticalScroll'),registers={},pages=pages,tiles={},sprite_samples={},palette={},exram={}}
 for k,v in pairs(registers)do q.registers[k]=v end
 for _,a in ipairs({0x2202,0x2282,0x228a,0x2292,0x229a,0x23e0,0x23e8,0x23ea,0x2602,0x2682,0x2a02,0x2a82,0x2e02,0x2e82})do
  local t=p(a);local v={address=a,value=t}
  if(a&0x3ff)<0x3c0 then local at=(q.control&16)*256+t*16;local page=pages[8+(at//1024)%4];v.physical=page;v.pattern={}
   for i=0,15 do v.pattern[#v.pattern+1]=emu.read(page*1024+(at&1023)+i,emu.memType.nesChrRom)end
  end;q.tiles[#q.tiles+1]=v
 end
 for _,a in ipairs({0x5e02,0x5e82,0x5e90,0x5f20})do q.exram[tostring(a)]=emu.read(a,emu.memType.nesDebug)end
 for i=0,31 do q.palette[#q.palette+1]=p(0x3f00+i)end
 for i=0,252,4 do local y=emu.read(0x200+i,emu.memType.nesDebug);local x=emu.read(0x203+i,emu.memType.nesDebug)
  if x<64 and y>=128 and y<208 then q.sprite_samples[#q.sprite_samples+1]={offset=i,y=y,x=x,t=emu.read(0x201+i,emu.memType.nesDebug),attr=emu.read(0x202+i,emu.memType.nesDebug)}end
 end
 -- Copy the twelve scalar latches so later callbacks cannot change evidence.
 q.pages={};for i=0,11 do q.pages[tostring(i)]=pages[i]end
 rows[#rows+1]=q;local f=assert(io.open(OUTPUT..label..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
for _,reg in ipairs({0x5100,0x5101,0x5104,0x5105,0x5106,0x5107,0x5200,0x5201,0x5202})do emu.addMemoryCallback(function(_,v)registers[tostring(reg)]=v end,emu.callbackType.write,reg)end
for i=0,11 do emu.addMemoryCallback(function(_,v)pages[i]=upper+v end,emu.callbackType.write,0x5120+i)end
emu.addEventCallback(function()
 local pad={}
 if phase=='open'and age<4 then pad.start=true elseif phase=='left'and age<4 then pad.left=true elseif phase=='select'and age<4 then pad.select=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then phase='open';age=0
 elseif phase=='open'and age>=50 then assert(r('CrossoverMenuState')==2);sample('mario');phase='left';age=0
  if MARIO_ONLY then done=true;local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({diagnostic_only=true,ROM_sha256=EXPECTED_SHA,rows=rows})..'\n');f:close();emu.stop(0)end
 elseif phase=='left'and age>=30 then assert(r('CrossoverMenuIndex')==7);phase='select';age=0
 elseif phase=='select'and age>=30 then assert(r('SelectedCharacter')==34);sample('karnov');done=true
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({diagnostic_only=true,ROM_sha256=EXPECTED_SHA,rows=rows})..'\n');f:close();emu.stop(0)
 end
 if frame>=500 then error('Menu probe bound')end
end,emu.eventType.endFrame)
