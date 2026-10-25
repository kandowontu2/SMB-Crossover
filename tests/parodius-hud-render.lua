-- Native UI component test: real selection, staged cursor at GameLoop entry.
-- Cursor/font flags are UI staging only; no gameplay/equipment/clear claim.
local C=assert(PN_HUD_CONFIG)
local wall,ticks,index,age=0,0,0,0
local entered,done=false,false
local checks={};local fontWrites,nmis=0,0
local masks={0,1,2,4,8,16,32,64,0}
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function w(n,v)emu.write(assert(C.ram[n],n),v,emu.memType.nesDebug)end
local function actual(h)
 local p=emu.convertAddress(h.address)
 return p and p.address//8192==h.physical_bank
end
local function bound(h)
 for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Native UI hook opcodes')end
end
local function native()
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
local glyphs={}
for tile=0,63 do
 glyphs[tile]={}
 for y=0,7 do
  local at=C.font*1024+tile*16+y
  glyphs[tile][y+1]=emu.read(at,emu.memType.nesChrRom)|emu.read(at+8,emu.memType.nesChrRom)
 end
end
local publication=assert(io.open(OUTPUT..'font-writes.csv','w'))
publication:write('frame,case,physical,active,scanline,cycle,pc\n')
local upper=0
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)
 if not entered then return end
 local s=emu.getState();local physical=v+256*upper
 publication:write(table.concat({wall,index,physical,r('InvHudActive'),s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc']},',')..'\n')
 if physical==C.font then
  fontWrites=fontWrites+1
  assert(s['ppu.scanline']<8 or s['ppu.scanline']>=240,'Private HUD font publication remains outside stage scanlines')
 end
end,emu.callbackType.write,0x5128)
local saved
emu.addMemoryCallback(function()
 if not entered then return end
 saved={a=emu.convertAddress(0xa000).address//8192,c=emu.convertAddress(0xc000).address//8192,fields={}}
 for _,a in ipairs(C.smc_fields)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1
end,emu.callbackType.exec,C.nmi.address)
emu.addMemoryCallback(function()
 if not saved then return end
 assert(emu.convertAddress(0xa000).address//8192==saved.a and emu.convertAddress(0xc000).address//8192==saved.c,'Native NMI restores foreground A/C banks')
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'Native NMI retains all five farcall operand fields')end
 saved=nil
end,emu.callbackType.exec,C.nmi_return.address)
emu.addMemoryCallback(function()
 if not actual(C.loop)or not native()then return end
 bound(C.loop)
 assert(r('SelectedCharacter')==18 and r('VvVariant')==C.variant,'Actual menu selected intended Parodius ship')
 entered=true;ticks=ticks+1
 if ticks>108 then done=true;return end
 index=(ticks-1)//12+1;age=(ticks-1)%12
 if age==0 then
  w('VvMeter',masks[index]);w('VvHudDirty',1)
  if index==9 then w('InvHudActive',0)end
 end
end,emu.callbackType.exec,C.loop.address)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=C.variant then b.select=true else b.a=true end
  end
 else b.up=ticks<30 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
local function attrs(cursor)
 local out={}
 for j=0,7 do
  local v=0xaa
  if cursor&(1<<j)~=0 then v=(v&0xf3)|4 end
  if j>0 and cursor&(1<<(j-1))~=0 then v=(v&0xfc)|1 end
  out[#out+1]=v
 end
 return out
end
emu.addEventCallback(function()
 wall=wall+1
 assert(wall<1800,'Bounded native HUD component test')
 if entered and index>0 and age>=5 and native()then
  assert(r('InvHudActive')~=0 and r('InvHudPhysical')+256*r('X5HudChrUpper')==C.font,'Current full physical font ownership')
  local expected=attrs(masks[index])
  for i=1,8 do assert(emu.read(0x23c0+i-1,emu.memType.nesPpuDebug)==expected[i],'All32pixels of native cursor cover their actual two attribute halves, case'..index)end
  for i,tile in ipairs(C.cells)do assert(emu.read(0x2022+i-1,emu.memType.nesPpuDebug)==tile,'Actual native nametable uses intended graphical label tile')end
  local screen=emu.getScreenBuffer()
  local background=screen[8*256+1]&0xffffff
  for y=0,7 do for x=0,223 do
   local tile=C.cells[x//8+1];local want=glyphs[tile][y+1]&(128>>(x%8))~=0
   local actualPixel=screen[(8+y)*256+16+x+1]&0xffffff
   assert((actualPixel~=background)==want,'Actual PPU bar-mask pixel mismatch case'..index..' x'..x..' y'..y)
  end end
  checks[index]=(checks[index]or 0)+1
  if checks[index]==1 then
   local f=assert(io.open(OUTPUT..'case-'..index..'.argb','wb'))
   for _,v in ipairs(screen)do f:write(string.pack('<I4',v))end
   f:close()
  end
 end
 if done then
  for i=1,9 do assert((checks[i]or 0)>=4,'Each empty/native cursor and font reacquisition has multiple actual PPU checks')end
  assert(fontWrites>50 and nmis>50,'Native font publication/NMI guards exercised')
  publication:close()
  local total=0;for _,v in ipairs(checks)do total=total+v end
  local f=assert(io.open(OUTPUT..'proof.json','w'))
  f:write(string.format('{"passed":true,"goal_complete":false,"variant":%d,"physical_font":%d,"native_updates":%d,"pixel_frames":%d,"pixels_compared":%d,"font_publications":%d,"guarded_NMIs":%d,"UI_staging":true,"gameplay_or_equipment_writes":false,"scope":"Real menu then native cursor/font UI staging at exact GameLoop entries; all seven cursor positions plus empty and reacquisition, actual direct PPU mask pixels, nametables/attributes, font timing, five operand fields and A/C bank restoration. No campaign/all-upgrade or MMC3 graphical-bar claim."}',C.variant,C.font,ticks,total,total*1792,fontWrites,nmis))
  f:close();print('PASS native graphical Parodius HUD '..C.variant);emu.stop(0)
 end
end,emu.eventType.endFrame)
