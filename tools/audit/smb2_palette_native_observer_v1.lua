-- Read-only actual PPU palette inspection; independent of the route verdict.
return function(C)
 local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
 local samples,checked,mismatches,previous=0,0,0,nil
 local events=assert(io.open(C.prefix..'palette-events.csv','w'))
 events:write('ppu_frame,mode,task,engine,ready,ack,star,addrctrl,p0,visible,checked,mismatches\n')
 local function save(frame)
  local f=assert(io.open(C.prefix..'palette-result.json','w'))
  f:write(string.format('{"ROM_sha256":%q,"last_ppu_frame":%d,"observed_frames":%d,"visible_gameplay_checks":%d,"P0_mismatches":%d,"expected_P0":"011627","scope":"Actual PPU palette0 in raw25 variant0 visible gameplay; independent short-run palette check, not a level-clear or audio verdict."}\n',C.ROM_sha256,frame,samples,checked,mismatches))
  f:close()
 end
 emu.addEventCallback(function()
  local s=emu.getState();samples=samples+1
  local p0={}
  for i=0x11,0x13 do p0[#p0+1]=string.format('%02x',emu.read(i,emu.memType.nesPaletteRam)&63)end
  p0=table.concat(p0)
  local mode,task,engine=r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine')
  local visible=r('SelectedCharacter')==25 and r('S2Variant')==0 and r('S2Ready')==0xb2
   and mode==1 and task==3 and engine==8 and r('S2NativeCharacter')==0
   and r('StarInvincibleTimer')==0 and r('Mirror_PPUMASK')&0x10~=0
  if visible then checked=checked+1;if p0~='011627' then mismatches=mismatches+1 end end
  local fields={s['ppu.frameCount'],mode,task,engine,r('S2Ready'),r('S2PaletteAck'),r('StarInvincibleTimer'),r('VRAM_Buffer_AddrCtrl'),p0,visible and 1 or 0,checked,mismatches}
  local key=table.concat({mode,task,engine,fields[5],fields[6],fields[7],fields[8],p0,fields[10]},',')
  if key~=previous then
   events:write(table.concat(fields,',')..'\n');events:flush();previous=key
   save(s['ppu.frameCount'])
  elseif samples%60==0 then save(s['ppu.frameCount'])end
 end,emu.eventType.endFrame)
end
