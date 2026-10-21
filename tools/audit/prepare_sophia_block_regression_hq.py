from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];O=R/'build/verification/root49-sophia-block-shift-hn'
src=(R/'tools/audit/sophia_block_shift_hn.lua').read_text(encoding='utf-8')
src=src.replace("local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end", """local authored=assert(io.open(OUTPUT..ROM_NAME..'-authored-setup.csv','w'))
authored:write('frame,case,symbol,index,value\\n')
local function w(n,v,i)
 authored:write(table.concat({frame,index,n,i or 0,v},',')..'\\n')
 emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)
end""")
src=src.replace(" c.seen=0;c.reward=false;c.begin=frame;", " c.seen=0;c.oam=0;c.sfx=0;c.reward=false;c.begin=frame;\n w('CrossoverBehaviorVersion',REGRESSION_MODE)\n")
src=src.replace("   assert(current.seen>=4,", "   assert(current.oam>=4,'Rendered halves remain at the contacted column: case '..index..' count '..current.oam)\n   assert(current.sfx>0,'Native bump sound is requested: case '..index)\n   assert(current.seen>=4,")
src=src.replace("if not cases[index] then f:close();", "if not cases[index] then f:close();authored:close();")
src+='''
emu.addMemoryCallback(function(address,value)
 if current and value~=0 then current.sfx=current.sfx+1 end
end,emu.callbackType.write,L.Square1SoundQueue)
emu.addMemoryCallback(function()
 if not current or r('CurrentBank')%128~=4 then return end
 for i=0,1 do if r('BlockMetasprite',i)==L.METASPRITE_MISC_BLOCK then
  local tile=emu.read(4*0x2000+(L.MetaspriteData_MISC_BLOCK_RIGHT+1)%0x2000,emu.memType.nesPrgRom)
  local count=0
  local expected=(current.tx-r('ScreenLeft_X_Pos')-256*r('ScreenLeft_PageLoc'))%256
  for offset=0,255,4 do
   if r('Sprite_Tilenumber',offset)==tile and r('Sprite_Y_Position',offset)<240 then
    local sx=r('Sprite_X_Position',offset)
    assert(sx==expected or sx==(expected+8)%256,'Actual OAM block halves cannot move to a neighboring column')
    count=count+1
   end
  end
  assert(count==2,'Both block halves must be present in OAM')
  current.oam=current.oam+1
 end end
end,emu.callbackType.exec,L.RosterOamReady)
'''
out=O/'sophia-block-regression-hq.lua';assert not out.exists();out.write_text(src,encoding='utf-8')
for mode in [0,1]:
 p=O/f'sophia-block-mode{mode}-hq.lua';p.write_text('REGRESSION_MODE='+str(mode)+'\ndofile('+json.dumps(out.as_posix())+')\n',encoding='utf-8')
print(out)
